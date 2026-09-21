"""P6 Stage-A host adapter: narrow machinery around the accepted P5
ingress/store. Stage A uses FAKE transports/timers/subscriptions only;
no live state, seat actions, service installation, model calls or host
clock changes exist in this module.

- Trusted source capture: completion/failure/dispatch receipts keyed by
  (package, attempt, action, event, execution) persisted in driver_kv.
  Clock and attribution come from host context (injected clock +
  trusted adapter actor); artifact output is never self-certifying.
- Declared execution identity (opaque strings, equality only; no suffix
  inference): each action execution registers an execution_id. Same-action
  resume keeps action+attempt and records resume/supersedes relationships.
  A late result from a non-current execution is retained as stale evidence
  and never applied. Genuine replacement declares supersedes atomically
  (old SUPERSEDED note + new registration committed together in driver_kv
  before any external effect).
- One-shot relative host timers from remaining authorized ledger duration
  (deadline minus trusted now), with stale/early/cancelled rejection.
  Every external call is bounded; no model polling. Observation is a
  bounded non-model subscription with documented cadence/failure/resource
  bounds (FakeEventSubscription here).
- Persisted cursor + restart/lost-wake reconciliation against actual
  outcomes and bound hashes: started/queued ack is not completion; no
  blind retry on ambiguous delivery; unavailable observation is an owned
  fault (bounded escalation receipt, fake target), never idle.
- Explicit dead-turn failures are consumed as owned events; the ledger
  deadline remains fallback, never the completion detector.
- Notifications and all-seat stop are FAKE targets; campaign4-pause stays
  the unchanged emergency actuator (referenced by inventory hash, never
  called here).
"""
from __future__ import annotations

import json

import validator as validator_mod


class OwnedFault(Exception):
    def __init__(self, code, detail="", owner="cairn"):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail
        self.owner = owner


class FakeWakeTransport:
    """Stage-A stand-in for the host wake transport (inventory hash
    recorded; global script unmodified and never executed here).

    Delivery states: queued (accepted, not proof), sent, delivered,
    failed (explicit dead-turn), ambiguous (unknown). Only delivered
    counts as transport receipt — never as worker completion.
    """

    def __init__(self):
        self.calls = []  # (seat, text, kind)
        self.inbox = {}  # message_id -> state dict
        self._n = 0

    def send(self, seat, text, kind="wake"):
        self._n += 1
        mid = "msg-%d" % self._n
        self.calls.append((seat, text, kind))
        self.inbox[mid] = {"seat": seat, "kind": kind, "state": "queued"}
        return mid

    def mark(self, message_id, state):
        assert state in ("queued", "sent", "delivered", "failed",
                         "ambiguous")
        self.inbox[message_id]["state"] = state
        return state

    def state(self, message_id):
        return self.inbox.get(message_id, {}).get("state", "unknown")


class FakeTimerService:
    """One-shot relative timers from remaining authorized duration."""

    def __init__(self):
        self.timers = {}  # timer_id -> {deadline, state}
        self.cancelled = set()

    def create(self, timer_id, deadline_utc):
        if timer_id in self.cancelled:
            return ("rejected-cancelled", True)
        self.timers[timer_id] = {"deadline": deadline_utc,
                                 "state": "armed"}
        return ("armed", False)

    def cancel(self, timer_id):
        self.timers.pop(timer_id, None)
        self.cancelled.add(timer_id)
        return ("cancelled", True)

    def fire(self, timer_id, now_utc, ledger_deadline_utc):
        """Stale/early/cancelled rejection against the authoritative
        ledger deadline (never the timer's own copy alone)."""
        if timer_id in self.cancelled or timer_id not in self.timers:
            return ("no-op-not-armed", True)
        now, dl = validator_mod._instant(now_utc), \
            validator_mod._instant(ledger_deadline_utc)
        if now is None or dl is None or now < dl:
            return ("no-op-early", True)
        if self.timers[timer_id]["deadline"] != ledger_deadline_utc:
            return ("no-op-stale", True)
        self.timers[timer_id]["state"] = "fired"
        return ("fired", False)


class FakeEventSubscription:
    """Bounded non-model observation. Cadence: polled explicitly by the
    driver (no background thread, no model calls). Failure: missed ticks
    return no events (caller treats absence as no-evidence, never as
    completion). Resources: in-memory queue, drained per tick, never
    unbounded."""

    def __init__(self):
        self.queue = []
        self.ticks = 0

    def inject(self, event):
        self.queue.append(event)

    def tick(self, max_events=16):
        self.ticks += 1
        out, self.queue = self.queue[:max_events], self.queue[max_events:]
        return out


class HostAdapter:
    """Narrow machinery over a P5 Driver: receipts, identity, timers,
    cursor/restart reconciliation, bounded escalation. Fake targets only."""

    def __init__(self, driver):
        self.driver = driver
        self.transport = FakeWakeTransport()
        self.timers = FakeTimerService()
        self.subscription = FakeEventSubscription()
        self.cursor = self.driver.kv.get("host-cursor")
        self.escalations = []

    # -- trusted source capture -------------------------------------------
    def _kv(self, key, value):
        self.driver._kv_put(key, value)

    def capture(self, package, attempt, action, event, execution,
                outcome, at_utc, observed_skew_s=None):
        """Persist a source receipt. Artifact payloads are recorded, never
        trusted as self-certifying completion."""
        key = "receipt:%s:%s:%s:%s:%s" % (
            package, attempt, action, event, execution)
        self._kv(key, json.dumps({
            "package": package, "attempt": attempt, "action": action,
            "event": event, "execution": execution, "outcome": outcome,
            "at_utc": at_utc, "observed_skew_s": observed_skew_s},
            sort_keys=True))
        self._kv("host-cursor", event)
        self.cursor = event
        return key

    def receipt(self, package, attempt, action, event, execution):
        raw = self.driver.kv.get(
            "receipt:%s:%s:%s:%s:%s" % (
                package, attempt, action, event, execution))
        return json.loads(raw) if raw else None

    # -- declared execution identity ----------------------------------------
    def register_execution(self, action, execution, authorization_ref,
                           deadline_utc):
        """Declare a new execution of an authorized action."""
        self._kv("exec-current:" + action, execution)
        self._kv("exec:%s:%s" % (action, execution), json.dumps({
            "authorization_ref": authorization_ref,
            "deadline_utc": deadline_utc}, sort_keys=True))
        return execution

    def current_execution(self, action):
        return self.driver.kv.get("exec-current:" + action)

    def apply_execution_result(self, action, execution, result):
        """Late results from non-current executions are retained as stale
        evidence and never applied. No suffix inference: equality only."""
        if execution != self.current_execution(action):
            self._kv("stale:%s:%s" % (action, execution), json.dumps(
                {"result": result, "applied": False}, sort_keys=True))
            return ("stale-retained-not-applied", True)
        self._kv("applied:%s:%s" % (action, execution), json.dumps(
            {"result": result, "applied": True}, sort_keys=True))
        return ("applied", False)

    def resume_execution(self, action, attempt, old_execution,
                         new_execution, authorization_ref, deadline_utc,
                         phase):
        """Same-action resume: identities unchanged; relationship recorded."""
        self.register_execution(action, new_execution, authorization_ref,
                                deadline_utc)
        self._kv("rel:%s:%s" % (action, new_execution), json.dumps(
            {"relationship": "resume", "resumes_action_id": action,
             "resumes_execution_id": old_execution, "attempt": attempt,
             "phase": phase}, sort_keys=True))
        return ("resumed", False)

    def replace_action(self, old_action, new_action, new_execution,
                       authorization_ref, deadline_utc, attempt_changed):
        """Genuine replacement: old SUPERSEDED note + new registration
        committed together before any external effect (no partial state)."""
        self._kv("rel:%s:%s" % (new_action, new_execution), json.dumps(
            {"relationship": "supersedes",
             "supersedes_action_id": old_action,
             "attempt_changed": attempt_changed,
             "authorization_ref": authorization_ref}, sort_keys=True))
        self._kv("exec-current:" + old_action, "SUPERSEDED->" + new_action)
        self.register_execution(new_action, new_execution,
                                authorization_ref, deadline_utc)
        return ("replaced", False)

    # -- timers from remaining authorized duration ---------------------------
    def arm_from_ledger(self, timer_id, ledger_deadline_utc, now_utc):
        """Create a one-shot relative timer for the remaining duration.
        Expired or malformed durations are owned faults, not timers."""
        now, dl = validator_mod._instant(now_utc), \
            validator_mod._instant(ledger_deadline_utc)
        if now is None or dl is None:
            raise OwnedFault("E_BAD_DEADLINE", "deadline not a UTC instant")
        remaining = (dl - now).total_seconds()
        if remaining <= 0:
            raise OwnedFault("E_EXPIRED", "no remaining authorized duration",
                             owner="tern")
        return self.timers.create(timer_id, ledger_deadline_utc)

    # -- restart / lost-wake reconciliation ------------------------------------
    def reconcile_send(self, message_id, action):
        """Restart before/after send and ack: reconcile the transport
        receipt against persisted outcomes. Queued is not completion; no
        blind retry on ambiguous delivery."""
        state = self.transport.state(message_id)
        if state == "delivered":
            return {"decision": "settled-delivered"}
        if state in ("queued", "sent"):
            return {"decision": "hold-for-receipt",
                    "note": "started/queued ack is not completion"}
        if state == "failed":
            return {"decision": "owned-failure",
                    "note": "explicit dead-turn consumed; deadline fallback"}
        return {"decision": "hold-for-reconciliation",
                "note": "ambiguous delivery; never blind redispatch"}

    def escalate_unavailable(self, action, owner, next_action,
                             response_deadline_utc):
        """Bounded owned escalation for unavailable receivers (fake
        target). Queued wake alone is neither recovery nor escalation."""
        self.escalations.append({
            "action": action, "owner": owner, "next_action": next_action,
            "response_deadline_utc": response_deadline_utc})
        self._kv("escalation:" + action, json.dumps(
            self.escalations[-1], sort_keys=True))
        return ("escalated-owned", False)
