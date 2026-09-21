"""P4-r2 event-driven driver: authoritative deadline events + durable recovery.

Repairs three parent failures: stale worker deadline interrupting CHECKING,
early current-deadline callbacks interrupting before due time, and reopen
duplicating stop/wake. All three are fixed by checking authoritative
ledger facts (package / current action / phase / deadline) plus current UTC
time before any interrupt or external action, and by persisting handled /
acknowledged external effects durably (SQLite driver_kv table in the same
ledger database) instead of an in-memory set.

Incapable defaults: no subprocess, socket, signal, network, or model calls
exist here. External state is simulated by FakeExternalWorld, an object held
independently of any Driver (tests keep it across Driver reopen, and it can
persist to a /tmp JSON file). Worker prose never supplies authoritative actor
identity. No polling: progress only via explicit calls and one-shot timer
events reconstructed from ledger facts on restart.
"""
from __future__ import annotations

import json
import os

import store as store_mod
import lifecycle as lc
import validator as validator_mod
import fake as fake_mod


class FakeClock:
    def __init__(self, start="2026-09-21T12:00:00Z"):
        self.now = start

    def advance(self, seconds):
        import datetime
        cur = validator_mod._instant(self.now)
        nxt = cur + datetime.timedelta(seconds=seconds)
        self.now = nxt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.now


class FakeExternalWorld:
    """Independent simulation of external delivery state.

    Held by the test/harness, NOT by the Driver. Fresh Drivers and fresh
    adapters share the same world across reopen, so crash-boundary behavior is
    genuine. Optionally persists to a JSON file (default under /tmp).
    """

    def __init__(self, path=None):
        self.path = path
        self.state = {}  # action_id -> {"delivery": ...}
        if path and os.path.exists(path):
            with open(path) as fh:
                self.state = json.load(fh)

    def _save(self):
        if self.path:
            tmp = self.path + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(self.state, fh, sort_keys=True)
            os.replace(tmp, self.path)

    def record(self, action_id, delivery):
        self.state[action_id] = {"delivery": delivery}
        self._save()

    def delivery(self, action_id):
        return self.state.get(action_id, {}).get("delivery", "unknown")


class FakeLaunchAdapter:
    """Incapable default: records launches, returns canned artifact hashes."""

    def __init__(self, world, artifacts=None):
        self.world = world
        self.artifacts = artifacts or {}
        self.launches = []  # action_ids launched

    def launch(self, action):
        self.launches.append(action["action_id"])
        arts = dict(self.artifacts.get(
            action["action_id"],
            {"output_hash": "sha256:fake-" + action["action_id"]}))
        self.world.record(action["action_id"], "dispatched")
        return arts


class FakeInspectAdapter:
    def __init__(self, world):
        self.world = world
        self.calls = []

    def inspect(self, action_id):
        self.calls.append(action_id)
        return {"action_id": action_id,
                "delivery": self.world.delivery(action_id)}


class FakeStopWakeAdapter:
    """Records stop/wake into the independent world; sends nothing."""

    def __init__(self, world):
        self.world = world
        self.stops = []
        self.wakes = []
        self.notifications = []  # (to, text) fake only; never sent

    def stop(self, action_id, reason):
        self.stops.append((action_id, reason))
        self.world.record("stop:" + action_id, "delivered")
        return {"action_id": action_id, "delivery": "stop-recorded"}

    def wake(self, seat, reason):
        self.wakes.append((seat, reason))
        self.world.record("wake:" + seat + ":" + reason, "delivered")
        return {"seat": seat, "delivery": "wake-recorded"}

    def notify(self, to, text):
        assert to != "brian", "no Brian notification permitted"
        self.notifications.append((to, text))
        return {"to": to, "delivery": "fake-queued"}


class FakeTimer:
    """One-shot arming. In-memory only: authority lives in the ledger plus
    the durable handled-effect table, NOT in this set."""

    def __init__(self, clock):
        self.clock = clock
        self.armed = {}  # timer_id -> deadline iso
        self.fired = set()
        self.removed = set()

    def arm(self, timer_id, deadline):
        if timer_id not in self.fired:
            self.armed[timer_id] = deadline

    def remove(self, timer_id):
        self.armed.pop(timer_id, None)
        self.removed.add(timer_id)

    def due(self):
        now = validator_mod._instant(self.clock.now)
        return sorted(t for t, d in self.armed.items()
                      if t not in self.fired and validator_mod._instant(d) <= now)

    def fire(self, timer_id):
        self.fired.add(timer_id)
        self.armed.pop(timer_id, None)
        return timer_id


# Authoritative actor mapping: worker prose never supplies identity.
ACTOR = {
    "director": {"seat": "tern", "role": "director"},
    "duty": {"seat": "cairn", "role": "duty"},
    "worker": {"seat": "kiln", "role": "worker"},
    "verifier": {"seat": "corvid", "role": "verifier"},
}


class Driver:
    """Owns Store + fake adapters + durable intent/effect reconciliation.

    Durable driver state lives in the ``driver_kv`` table of the same SQLite
    database as the ledger, so reopening a fresh Driver (with fresh adapters)
    recovers intents and handled/acknowledged effects:
      intent:<action_id>      -> "intended" | "acknowledged"
      handled:<effect_id>     -> "handled-acked" (stop/wake/trigger effects)
      trigger-seen:<trigger>  -> "seen" (ACTION_DUE dedup across restart)
    """

    def __init__(self, db_path, clock=None, world=None, artifacts=None):
        self.clock = clock or FakeClock()
        self.world = world if world is not None else FakeExternalWorld()
        self.store = store_mod.Store(db_path)
        self.launch = FakeLaunchAdapter(self.world, artifacts)
        self.inspect = FakeInspectAdapter(self.world)
        self.ext = FakeStopWakeAdapter(self.world)
        self.timer = FakeTimer(self.clock)
        self.executor = fake_mod.FakeExecutor(artifacts)
        self.budget = {"attempts": 1, "repairs": 1, "verifier_s": 1800,
                       "passes": {"verify": {"max_s": 1800},
                                  "controller_recovery": {"max_s": 600}}}
        self._ensure_kv()
        self.kv = self._load_kv()
        self.reconstruct_timers()  # arming from ledger facts, never caller stale data

    # -- durable kv ------------------------------------------------------
    def _ensure_kv(self):
        with self.store.conn:
            self.store.conn.execute(
                "CREATE TABLE IF NOT EXISTS driver_kv (key TEXT PRIMARY KEY, value TEXT)")

    def _load_kv(self):
        cur = self.store.conn.execute("SELECT key, value FROM driver_kv")
        return dict(cur.fetchall())

    def _kv_put(self, key, value):
        self.kv[key] = value
        with self.store.conn:
            self.store.conn.execute(
                "INSERT OR REPLACE INTO driver_kv (key, value) VALUES (?, ?)",
                (key, value))

    def handled(self, effect_id):
        return self.kv.get("handled:" + effect_id) == "handled-acked"

    def mark_handled(self, effect_id):
        self._kv_put("handled:" + effect_id, "handled-acked")

    # -- events ----------------------------------------------------------
    def _ev(self, eid, qid, typ, who, body=None):
        ev = {"event_id": eid, "question_id": qid, "revision": 1,
              "type": typ, "actor": dict(ACTOR[who]), "at": self.clock.now}
        ev.update(body or {})
        return ev

    def admit_authorize(self, qid):
        ev = self._ev(qid + "-admit", qid, "admit", "verifier")
        ev["actor"] = {"seat": "corvid", "role": "reader"}
        self.store.append(ev, self.budget)
        self.store.append(self._ev(qid + "-authz", qid, "authorize", "director",
                                   {"contract": "P4-r2-fixture-v1"}), self.budget)

    def start_dispatch(self, qid, action_id, deadline, owner_seat="kiln"):
        """Start precedes fake dispatch; duplicate delivery cannot create attempts."""
        self._kv_put("intent:" + action_id, "intended")
        action = {"action_id": action_id, "question_id": qid, "revision": 1,
                  "deadline": deadline, "at": self.clock.now}
        res, dup = fake_mod.dispatch(self.store, action, self.executor,
                                     self.budget, self.clock.now)
        if not dup:
            self.launch.launch(action)
            self.timer.arm("deadline:" + action_id, deadline)
        return res, dup

    def acknowledge(self, action_id):
        self.store.set_ack(action_id, "acknowledged")
        self._kv_put("intent:" + action_id, "acknowledged")

    def publish_completion(self, qid, action_id, hashes, verify=None,
                           handoff=None, eid=None):
        body = {"artifact_hashes": hashes}
        if verify is not None:
            body["verify"] = verify
        if handoff is not None:
            body.update(handoff)
        assert hashes, "immutable outputs must precede completion"
        ev = self._ev(eid or (action_id + "-pub"), qid, "publish", "worker", body)
        out = self.store.append(ev, self.budget)
        # Rotation: the worker timer is cancelled; the current verifier or
        # handoff deadline is armed from ledger facts (never stale).
        self.timer.remove("deadline:" + action_id)
        rec = self.store.revisions.get((qid, 1)) or {}
        fl = rec.get("flight") or {}
        ho = rec.get("handoff") or {}
        if fl.get("action_id") and fl.get("deadline"):
            self.timer.arm("deadline:" + fl["action_id"], fl["deadline"])
            self._kv_put("intent:" + fl["action_id"], "intended")
        elif ho.get("deadline"):
            self.timer.arm("handoff:" + qid, ho["deadline"])
        return out

    def verify(self, qid, eid, passed, elapsed_s=60,
               hold_deadline="2026-09-21T15:00:00Z", **kw):
        typ = "verify_pass" if passed else "verify_fail"
        body = {"elapsed_s": elapsed_s, "pass_budget_s": 1800,
                "finding": kw.get("finding", "positive" if passed else "defect")}
        body.update({k: v for k, v in kw.items() if k != "finding"})
        return self.store.append(self._ev(eid, qid, typ, "verifier", body),
                                 self.budget, atomic={"hold": hold_deadline})

    def terminal_close(self, qid, verdict_eid, decide_eid, verdict_body,
                       disposition):
        v = self._ev(verdict_eid, qid, verdict_body["type"], verdict_body["who"],
                     verdict_body.get("body", {}))
        d = self._ev(decide_eid, qid, "decide", "director",
                     {"disposition": disposition})
        return self.store.record_terminal(v, d, self.budget)

    # -- authoritative deadline handling ---------------------------------
    def _current_flight(self, qid):
        """Authoritative current action/phase/deadline from the ledger."""
        rec = self.store.revisions.get((qid, 1))
        if rec is None or rec.get("phase") in ("COMPLETE", "EXHAUSTED",
                                               "TERMINATED", "SUPERSEDED"):
            return None
        fl = rec.get("flight") or {}
        if fl.get("action_id") and fl.get("deadline"):
            return {"kind": "flight", "action_id": fl["action_id"],
                    "deadline": fl["deadline"], "phase": rec["phase"]}
        ho = rec.get("handoff") or {}
        if ho.get("deadline"):
            return {"kind": "handoff", "action_id": None,
                    "deadline": ho["deadline"], "phase": rec["phase"]}
        return None

    def on_deadline(self, action_id, qid):
        """Handle one deadline event against authoritative ledger facts.

        No-ops (never interrupts, never calls stop/wake) for: removed or
        never-armed timers, old-generation/stale actions, wrong packages,
        early callbacks (now < current deadline), non-running phases, and
        already-handled effects (durable across reopen). Only a genuinely due
        current-action deadline interrupts, stops once, and wakes Tern once.
        """
        tid = "deadline:" + action_id
        cur = self._current_flight(qid)
        if cur is None:
            return ("no-op-no-current-action", True)
        if cur["kind"] == "handoff":
            # Handoff deadlines are owned by duty/director, not by a worker
            # action: a worker-action callback never interrupts them (use
            # on_handoff_deadline for the genuine handoff path).
            return ("no-op-handoff-owned", True)
        if cur.get("action_id") != action_id:
            return ("no-op-stale-action", True)
        now = validator_mod._instant(self.clock.now)
        dl = validator_mod._instant(cur["deadline"])
        if now is None or dl is None or now < dl:
            return ("no-op-early", True)
        effect = "deadline:" + qid + ":" + action_id
        if self.handled(effect):
            return ("already-handled", True)
        self.timer.fire(tid)
        try:
            self.store.append(self._ev(action_id + "-int", qid, "interrupt",
                                       "duty", {"reason": "deadline-expired"}),
                              self.budget)
        except lc.TransitionError as e:
            return ("interrupt-rejected:%s" % e.code, True)
        self.ext.stop(action_id, "deadline-expired")
        self.ext.wake("tern", "deadline-expired:" + qid)
        self.mark_handled(effect)  # durable ack: reopen cannot repeat
        return ("interrupted", False)

    def on_handoff_deadline(self, qid):
        """Genuine due handoff-deadline path (duty-owned)."""
        cur = self._current_flight(qid)
        if cur is None or cur["kind"] != "handoff":
            return ("no-op-no-handoff", True)
        now = validator_mod._instant(self.clock.now)
        dl = validator_mod._instant(cur["deadline"])
        if now is None or dl is None or now < dl:
            return ("no-op-early", True)
        effect = "handoff:" + qid
        if self.handled(effect):
            return ("already-handled", True)
        try:
            self.store.append(self._ev(qid + "-handoff-int", qid, "interrupt",
                                       "duty", {"reason": "handoff-expired"}),
                              self.budget)
        except lc.TransitionError as e:
            return ("interrupt-rejected:%s" % e.code, True)
        self.ext.wake("tern", "handoff-expired:" + qid)
        self.mark_handled(effect)
        return ("interrupted", False)

    # -- restart / reconciliation ----------------------------------------
    def reconstruct_timers(self):
        """Re-arm one-shot timers purely from ledger facts."""
        for (q, _rev), rec in self.store.revisions.items():
            if rec.get("phase") in ("COMPLETE", "EXHAUSTED", "TERMINATED",
                                    "SUPERSEDED"):
                continue
            fl = rec.get("flight") or {}
            ho = rec.get("handoff") or {}
            if fl.get("action_id") and fl.get("deadline"):
                self.timer.arm("deadline:" + fl["action_id"], fl["deadline"])
            elif ho.get("deadline"):
                self.timer.arm("handoff:" + q, ho["deadline"])

    def reconcile_restart(self, qid, action_id):
        """Bounded owned reconciliation of intent vs independent world state.

        Never a blind redispatch and never an unsafe exactly-once claim:
        ambiguous delivery holds for owned reconciliation.
        """
        self.reconstruct_timers()
        insp = self.inspect.inspect(action_id)
        ack = self.store.acks.get(action_id)
        intent = self.kv.get("intent:" + action_id)
        if self.handled("deadline:" + qid + ":" + action_id):
            return {"decision": "effect-already-handled", "ack": ack,
                    "external": insp["delivery"]}
        if ack == "acknowledged" and insp["delivery"] in ("acknowledged",
                                                          "dispatched"):
            return {"decision": "settled-acknowledged"}
        if insp["delivery"] == "unknown" or ack == "intended" or \
                intent == "intended":
            return {"decision": "hold-for-reconciliation",
                    "ack": ack, "external": insp["delivery"]}
        return {"decision": "hold-for-reconciliation", "ack": ack,
                "external": insp["delivery"]}

    def dedupe_trigger(self, trigger_id):
        """Durable ACTION_DUE dedup across restart (ledger facts stay first)."""
        if self.kv.get("trigger-seen:" + trigger_id) == "seen":
            return True
        self._kv_put("trigger-seen:" + trigger_id, "seen")
        return False

    def ledger(self):
        pkgs = {}
        for q, revs in self.store.ledger_view().items():
            for rev, r in revs.items():
                pkgs["%s-r%d" % (q, rev)] = r
        return {"revision": self.store.ledger_revision(), "packages": pkgs}

    def snapshot(self, path="/tmp/p4r2-snap.json"):
        return self.store.publish_snapshot(path)

    def close(self):
        self.store.close()
