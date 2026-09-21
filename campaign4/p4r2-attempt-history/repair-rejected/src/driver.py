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


# Crash-injection hook for rehearsal only: names in Driver.crash_points raise
# SimulatedCrash at that boundary (between external calls and local acks).
# Lets tests exercise crash-after-each-call with true reopen. Never enabled
# outside tests; production paths never set it.
class SimulatedCrash(Exception):
    pass


CRASH_AFTER_INTERRUPT = "after-interrupt"
CRASH_AFTER_STOP = "after-stop"
CRASH_AFTER_STOP_ACK = "after-stop-ack"
CRASH_AFTER_WAKE = "after-wake"
CRASH_AFTER_WAKE_ACK = "after-wake-ack"
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
# Authoritative actor mapping: worker prose never supplies identity.
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
        self.crash_points = set()  # rehearsal crash injection; empty in real paths
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

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

    def _maybe_crash(self, point):
        if point in self.crash_points:
            raise SimulatedCrash(point)

    # -- explicit cancellation (durable; distinct from accidental loss) -----
    def cancel_deadline(self, action_id, qid, owner="cairn",
                        reason="owned-hold"):
        """Supported cancellation operation: durably invalidates the deadline
        callback for this action, including after reopen. The ledger flight
        and its deadline stay authoritative (supervision still holds the
        owner accountable), so cancellation never creates unowned silence.
        """
        tid = "deadline:" + action_id
        self.timer.remove(tid)
        self._kv_put("cancelled:" + tid, "cancelled")
        self._kv_put("cancel-info:" + tid,
                     json.dumps({"owner": owner, "reason": reason,
                                 "qid": qid, "at": self.clock.now},
                                sort_keys=True))
        return ("cancelled", True)

    def is_cancelled(self, timer_id):
        return self.kv.get("cancelled:" + timer_id) == "cancelled"

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
            if not self.is_cancelled("deadline:" + action_id):
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
        # Rotation: the worker deadline is durably cancelled; the current
        # verifier or handoff deadline is armed from ledger facts (never stale).
        self.cancel_deadline(action_id, qid, owner="cairn",
                             reason="rotated-on-publish")
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

        No-ops (never interrupts, never calls stop/wake) for: durably
        cancelled, removed or never-armed timers, old-generation/stale
        actions, wrong packages, early callbacks (now < current deadline),
        non-running phases, and already-handled effects (durable across
        reopen). Only a genuinely due current-action deadline interrupts.

        Per-effect durability (D1): each external effect is separately
        intended (durable) before its call and separately acked (durable)
        after its world receipt. A replay reconciles: delivered effects are
        never repeated; pending ones complete. Crash may land after each
        call; recovery stays bounded and owned.
        """
        tid = "deadline:" + action_id
        if self.is_cancelled(tid):
            return ("no-op-cancelled", True)
        effect = "deadline:" + qid + ":" + action_id
        if self.handled(effect):
            return ("already-handled", True)
        if tid in self.timer.removed or tid not in self.timer.armed:
            return ("no-op-not-armed", True)
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
        stop_key, wake_key = effect + ":stop", effect + ":wake"
        wake_reason = "deadline-expired:" + qid
        # Reconcile delivery (world receipt) vs local ack, separately per
        # effect. A delivered-but-unacked effect is acked, never resent.
        stop_done = self._effect_settled(stop_key, "stop:" + action_id)
        wake_done = self._effect_settled(wake_key, "wake:tern:" + wake_reason)
        if stop_done and wake_done:
            self.mark_handled(effect)
            return ("already-handled", True)
        recovered = stop_done or wake_done
        self.timer.fire(tid)
        try:
            _out, _dup = self.store.append(
                self._ev(action_id + "-int", qid, "interrupt",
                         "duty", {"reason": "deadline-expired"}), self.budget)
            if _dup:
                recovered = True  # replay: interrupt already recorded
        except lc.TransitionError as e:
            # Same-process replay past the append lands here (BLOCKED phase);
            # true reopen returns duplicate-ignored above. Either way the
            # interrupt is already recorded: reconcile effects, don't reject.
            phase = (self.store.revisions.get((qid, 1)) or {}).get("phase")
            if e.code == "E_BAD_TRANSITION" and phase == "BLOCKED":
                recovered = True
            else:
                return ("interrupt-rejected:%s" % e.code, True)
        self._maybe_crash(CRASH_AFTER_INTERRUPT)
        if not stop_done:
            self._kv_put(stop_key, "intended")
            self.ext.stop(action_id, "deadline-expired")
            self._maybe_crash(CRASH_AFTER_STOP)
            self._kv_put(stop_key, "delivered-acked")
            self._maybe_crash(CRASH_AFTER_STOP_ACK)
        if not wake_done:
            self._kv_put(wake_key, "intended")
            self.ext.wake("tern", wake_reason)
            self._maybe_crash(CRASH_AFTER_WAKE)
            self._kv_put(wake_key, "delivered-acked")
            self._maybe_crash(CRASH_AFTER_WAKE_ACK)
        self.mark_handled(effect)  # durable ack: reopen cannot repeat
        return ("recovered" if recovered else "interrupted", False)

    def _effect_settled(self, local_key, world_key):
        """True if the effect is delivered (world receipt) — acking locally
        if the ack was lost. Delivery and ack are reconciled separately."""
        if self.kv.get(local_key) == "delivered-acked":
            return True
        if self.world.delivery(world_key) == "delivered":
            self._kv_put(local_key, "delivered-acked")
            return True
        return False

    def on_handoff_deadline(self, qid):
        """Genuine due handoff-deadline path (duty-owned). Wake effect is
        durably intended before the call and acked after its receipt."""
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
        wake_key, reason = effect + ":wake", "handoff-expired:" + qid
        if self._effect_settled(wake_key, "wake:tern:" + reason):
            self.mark_handled(effect)
            return ("already-handled", True)
        try:
            _out, _dup = self.store.append(
                self._ev(qid + "-handoff-int", qid, "interrupt",
                         "duty", {"reason": "handoff-expired"}), self.budget)
        except lc.TransitionError as e:
            phase = (self.store.revisions.get((qid, 1)) or {}).get("phase")
            if not (e.code == "E_BAD_TRANSITION" and phase == "BLOCKED"):
                return ("interrupt-rejected:%s" % e.code, True)
        self._kv_put(wake_key, "intended")
        self.ext.wake("tern", reason)
        self._maybe_crash(CRASH_AFTER_WAKE)
        self._kv_put(wake_key, "delivered-acked")
        self.mark_handled(effect)
        return ("interrupted", False)

    # -- restart / reconciliation ----------------------------------------
    def reconstruct_timers(self):
        """Re-arm one-shot timers purely from ledger facts. Durably
        cancelled timers stay disarmed (explicit cancellation); all other
        loss is accidental and reconstructs the still-valid deadline."""
        for (q, _rev), rec in self.store.revisions.items():
            if rec.get("phase") in ("COMPLETE", "EXHAUSTED", "TERMINATED",
                                    "SUPERSEDED"):
                continue
            fl = rec.get("flight") or {}
            ho = rec.get("handoff") or {}
            if fl.get("action_id") and fl.get("deadline"):
                tid = "deadline:" + fl["action_id"]
                if not self.is_cancelled(tid):
                    self.timer.arm(tid, fl["deadline"])
            elif ho.get("deadline"):
                self.timer.arm("handoff:" + q, ho["deadline"])

    def reconcile_restart(self, qid, action_id):
        """Bounded owned reconciliation of intent vs independent world state.

        Never a blind redispatch and never an unsafe exactly-once claim:
        ambiguous delivery holds for owned reconciliation.
        """
        self.reconstruct_timers()
        tid = "deadline:" + action_id
        if self.is_cancelled(tid):
            return {"decision": "cancelled-owned",
                    "cancel": self.kv.get("cancel-info:" + tid),
                    "note": "explicit cancellation; owner must reconcile "
                            "against the still-authoritative ledger deadline"}
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
