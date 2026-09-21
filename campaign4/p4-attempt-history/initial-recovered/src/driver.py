"""Event-driven rehearsal driver: accepted store/core/validator + FAKE adapters.

Defaults are incapable of live effects: no subprocess, socket, signal, file
watch, or model call exists in this module. Fake adapters record calls and
return canned responses carrying recorded action identity + delivery state.
Worker prose never supplies authoritative actor identity: actor seat/role for
ledger events comes from the driver mapping, never from worker output text.
No polling: all progress is via explicit driver.deliver(event) calls and
one-shot fake-timer events reconstructed on restart.
"""
from __future__ import annotations

import hashlib
import json

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


class FakeLaunchAdapter:
    """Incapable default: records launches, returns canned artifact hashes."""

    def __init__(self, artifacts=None):
        self.artifacts = artifacts or {}
        self.launches = []  # action_ids launched

    def launch(self, action):
        self.launches.append(action["action_id"])
        return dict(self.artifacts.get(action["action_id"],
                                       {"output_hash": "sha256:fake-" + action["action_id"]}))


class FakeInspectAdapter:
    def __init__(self):
        self.calls = []

    def inspect(self, action_id, external_state):
        self.calls.append(action_id)
        st = external_state.get(action_id, {})
        return {"action_id": action_id, "delivery": st.get("delivery", "unknown")}


class FakeStopWakeAdapter:
    """Records stop/wake; sends nothing. Notification is fake output only."""

    def __init__(self):
        self.stops = []
        self.wakes = []
        self.notifications = []  # (to, text) fake only; never sent

    def stop(self, action_id, reason):
        self.stops.append((action_id, reason))
        return {"action_id": action_id, "delivery": "stop-recorded"}

    def wake(self, seat, reason):
        self.wakes.append((seat, reason))
        return {"seat": seat, "delivery": "wake-recorded"}

    def notify(self, to, text):
        assert to != "brian", "no Brian notification permitted"
        self.notifications.append((to, text))
        return {"to": to, "delivery": "fake-queued"}


class FakeTimer:
    """One-shot deadlines. fire() delivers each due id once; restart rebuilds."""

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
    """Owns Store + fake adapters + durable intent/ack reconciliation."""

    def __init__(self, db_path, clock=None, artifacts=None):
        self.clock = clock or FakeClock()
        self.store = store_mod.Store(db_path)
        self.launch = FakeLaunchAdapter(artifacts)
        self.inspect = FakeInspectAdapter()
        self.ext = FakeStopWakeAdapter()
        self.timer = FakeTimer(self.clock)
        self.external_state = {}  # action_id -> {"delivery": ...}
        self.executor = fake_mod.FakeExecutor(artifacts)
        self.budget = {"attempts": 1, "repairs": 1, "verifier_s": 1800,
                       "passes": {"verify": {"max_s": 1800},
                                  "controller_recovery": {"max_s": 600}}}

    def _ev(self, eid, qid, typ, who, body=None):
        ev = {"event_id": eid, "question_id": qid, "revision": 1,
              "type": typ, "actor": dict(ACTOR[who]), "at": self.clock.now}
        ev.update(body or {})
        return ev

    def admit_authorize(self, qid):
        ev = self._ev(qid + "-admit", qid, "admit", "verifier"); ev["actor"] = {"seat": "corvid", "role": "reader"}
        self.store.append(ev, self.budget)
        self.store.append(self._ev(qid + "-authz", qid, "authorize", "director",
                                   {"contract": "P4-fixture-v1"}), self.budget)

    def start_dispatch(self, qid, action_id, deadline, owner_seat="kiln"):
        """Start precedes fake dispatch; duplicate delivery cannot create attempts."""
        action = {"action_id": action_id, "question_id": qid, "revision": 1,
                  "deadline": deadline, "at": self.clock.now}
        res, dup = fake_mod.dispatch(self.store, action, self.executor,
                                     self.budget, self.clock.now)
        if not dup:
            arts = self.launch.launch(action)
            self.external_state[action_id] = {"delivery": "dispatched",
                                              "artifacts": arts}
            self.timer.arm("deadline:" + action_id, deadline)
        return res, dup

    def acknowledge(self, action_id):
        self.store.set_ack(action_id, "acknowledged")
        if action_id in self.external_state:
            self.external_state[action_id]["delivery"] = "acknowledged"

    def publish_completion(self, qid, action_id, hashes, verify=None, handoff=None, eid=None):
        body = {"artifact_hashes": hashes}
        if verify is not None:
            body["verify"] = verify
        if handoff is not None:
            body.update(handoff)
        # Immutable outputs/hashes precede completion: require non-empty hashes
        # (core enforces E_MISSING_ARTIFACTS) and record hash manifest first.
        assert hashes, "immutable outputs must precede completion"
        ev = self._ev(eid or (action_id + "-pub"), qid, "publish", "worker", body)
        return self.store.append(ev, self.budget)

    def verify(self, qid, eid, passed, elapsed_s=60, hold_deadline="2026-09-21T15:00:00Z", **kw):
        typ = "verify_pass" if passed else "verify_fail"
        body = {"elapsed_s": elapsed_s, "pass_budget_s": 1800,
                "finding": kw.get("finding", "positive" if passed else "defect")}
        body.update({k: v for k, v in kw.items() if k != "finding"})
        # Terminal verdicts commit atomically with a bounded director hold.
        return self.store.append(self._ev(eid, qid, typ, "verifier", body),
                                 self.budget, atomic={"hold": hold_deadline})

    def terminal_close(self, qid, verdict_eid, decide_eid, verdict_body, disposition):
        v = self._ev(verdict_eid, qid, verdict_body["type"], verdict_body["who"],
                     verdict_body.get("body", {}))
        d = self._ev(decide_eid, qid, "decide", "director",
                     {"disposition": disposition})
        return self.store.record_terminal(v, d, self.budget)

    def on_deadline(self, action_id, qid):
        """Finite owned handling: interrupt once, stop once, wake Tern once."""
        tid = "deadline:" + action_id
        if tid in self.timer.fired:
            return ("already-handled", True)
        self.timer.fire(tid)
        try:
            self.store.append(self._ev(action_id + "-int", qid, "interrupt", "duty",
                                       {"reason": "deadline-expired"}), self.budget)
        except lc.TransitionError as e:
            return ("interrupt-rejected:%s" % e.code, True)
        self.ext.stop(action_id, "deadline-expired")
        self.ext.wake("tern", "deadline-expired:" + qid)
        return ("interrupted", False)

    def reconcile_restart(self, qid, action_id, deadline):
        """Restart: durable intent/ack vs fake external state. Ambiguous holds."""
        self.timer.arm("deadline:" + action_id, deadline)  # reconstruct one-shot
        insp = self.inspect.inspect(action_id, self.external_state)
        ack = self.store.acks.get(action_id)
        if ack == "acknowledged" and insp["delivery"] in ("acknowledged", "dispatched"):
            return {"decision": "settled-acknowledged"}
        if insp["delivery"] == "unknown" or ack == "intended":
            # Ambiguous: hold for owned reconciliation, never blind redispatch.
            return {"decision": "hold-for-reconciliation",
                    "ack": ack, "external": insp["delivery"]}
        return {"decision": "hold-for-reconciliation", "ack": ack,
                "external": insp["delivery"]}

    def ledger(self):
        pkgs = {}
        for q, revs in self.store.ledger_view().items():
            for rev, r in revs.items():
                pkgs["%s-r%d" % (q, rev)] = r
        return {"revision": self.store.ledger_revision(), "packages": pkgs}

    def snapshot(self, path="/tmp/p4-snap.json"):
        return self.store.publish_snapshot(path)

    def close(self):
        self.store.close()
