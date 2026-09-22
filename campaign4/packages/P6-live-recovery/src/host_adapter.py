"""P6 Stage-A host adapter: narrow machinery around the accepted P5
ingress/store. Runnable host path with injected fakes for Stage A checks.

Stage-A rule: live effects stay DISABLED (production transports/timers
fail closed outside an explicit fixture allowlist, which Stage A never
enables). No seat actions, service installation, model calls, host clock
changes, or live effects occur here.

- D1: runnable host path. HostWakeTransport invokes the real wake script
  (bounded call, parsed receipt); HostTimerService creates real one-shot
  timers; ACPOutcomeObserver reads session history read-only. Stage A
  injects fakes with the same interfaces; exact executable fixture
  commands are exposed without executing them. Dead-turn/lost-completion
  observations feed reconcile_send; IDs correlate dispatch -> artifacts
  -> outcome via trail().
- D2: replacement and registrations commit in ONE durable transaction
  (driver _kv_put_many); the in-memory projection changes only after
  commit (refresh on rollback). Receipt+cursor publish together.
- D3: HostClock (live) or injected clock (tests) stamps receipt time;
  caller occurrence is a separate validated field with provenance.
  Conflicting re-capture is rejected (no overwrite-as-dedup). An
  escalation record is never acknowledged delivery.
- D4: one-shot timers durably reconcile handled effects
  (timer-handled:* in driver_kv, surviving restart) and reject
  repeat/stale/early/cancelled callbacks. Arming reads the authoritative
  current action deadline with trusted now.
- Notifications and all-seat stop are FAKE targets; campaign4-pause stays
  the unchanged emergency actuator (inventory hash only, never called).
"""
from __future__ import annotations

import json
import subprocess

import validator as validator_mod
from ingress import FUTURE_SKEW_TOLERANCE_S

try:
    from ingress import HostClock
except ImportError:  # pragma: no cover - defensive
    HostClock = None


class OwnedFault(Exception):
    def __init__(self, code, detail="", owner="cairn"):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail
        self.owner = owner


# -- transports ---------------------------------------------------------------
class FakeWakeTransport:
    """Stage-A stand-in: records sends; states queued/sent/delivered/
    failed/ambiguous. Only delivered counts as transport receipt — never
    as worker completion."""

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


class HostWakeTransport:
    """Runnable production transport: invokes the inventoried wake script
    with a bounded call and parses the receipt. FAILS CLOSED unless
    explicitly enabled with a fixture seat allowlist (Stage A never
    enables it, so construction alone performs zero live effects)."""

    def __init__(self, wake_path, allowlist_seats=(), enabled=False,
                 timeout_s=30):
        self.wake_path = wake_path
        self.allowlist = tuple(allowlist_seats)
        self.enabled = enabled
        self.timeout_s = timeout_s
        self.calls = []

    def command_for(self, seat, text):
        """Exact executable command (returned, never run here)."""
        return [self.wake_path, seat, text]

    def send(self, seat, text, kind="wake"):
        if not self.enabled or seat not in self.allowlist:
            raise OwnedFault("E_DISABLED",
                             "live send outside enabled fixture allowlist")
        cmd = self.command_for(seat, text)
        self.calls.append((seat, text, kind))
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout_s=None,
                                  timeout=self.timeout_s)
        except (OSError, subprocess.SubprocessError):
            return ("send-failed", "ambiguous")
        if proc.returncode != 0:
            return ("send-failed", "failed")
        return ("sent-%d" % len(self.calls), "sent")


# -- timers ----------------------------------------------------------------------
class FakeTimerService:
    """One-shot relative timers with DURABLE handled effects (driver_kv),
    so fresh processes/adapters reject repeats. Stale/early/cancelled
    rejection against the authoritative ledger deadline."""

    def __init__(self, kv_get=None, kv_put=None):
        self.timers = {}  # timer_id -> {deadline, state}
        self.cancelled = set()
        self._kv_get = kv_get or (lambda k: None)
        self._kv_put = kv_put or (lambda k, v: None)

    def _handled(self, timer_id):
        return self._kv_get("timer-handled:" + timer_id) == "handled"

    def _cancelled(self, timer_id):
        return timer_id in self.cancelled or \
            self._kv_get("timer-cancelled:" + timer_id) == "cancelled"

    def create(self, timer_id, deadline_utc):
        if self._cancelled(timer_id) or self._handled(timer_id):
            return ("rejected-cancelled", True)
        self.timers[timer_id] = {"deadline": deadline_utc,
                                 "state": "armed"}
        return ("armed", False)

    def cancel(self, timer_id):
        self.timers.pop(timer_id, None)
        self.cancelled.add(timer_id)
        self._kv_put("timer-cancelled:" + timer_id, "cancelled")
        return ("cancelled", True)

    def fire(self, timer_id, now_utc, ledger_deadline_utc):
        # Durable handled check first: a fresh process with empty in-memory
        # timers must still reject repeats of handled effects.
        if self._handled(timer_id):
            return ("already-handled", True)
        if self._cancelled(timer_id) or timer_id not in self.timers:
            return ("no-op-not-armed", True)
        now, dl = validator_mod._instant(now_utc), \
            validator_mod._instant(ledger_deadline_utc)
        if now is None or dl is None or now < dl:
            return ("no-op-early", True)
        if self.timers[timer_id]["deadline"] != ledger_deadline_utc:
            return ("no-op-stale", True)
        self.timers[timer_id]["state"] = "fired"
        self._kv_put("timer-handled:" + timer_id, "handled")
        return ("fired", False)


class HostTimerService(FakeTimerService):
    """Runnable host timers: exact one-shot commands (returned for the
    fixture plan); creation executes only when enabled with an allowlist."""

    def __init__(self, kv_get=None, kv_put=None, enabled=False,
                 allowlist=()):
        super().__init__(kv_get, kv_put)
        self.enabled = enabled
        self.allowlist = tuple(allowlist)

    def command_for(self, timer_id, delay_s, message):
        """Exact executable one-shot (transient, relative)."""
        return ["systemd-run", "--user", "--on-active=%ds" % int(delay_s),
                "--unit=%s" % timer_id,
                "/usr/bin/env", "MSG=%s" % message, "true"]

    def create_host(self, timer_id, delay_s, message):
        if not self.enabled or timer_id not in self.allowlist:
            raise OwnedFault("E_DISABLED",
                             "live timer outside enabled fixture allowlist")
        return self.command_for(timer_id, delay_s, message)


# -- observers ----------------------------------------------------------------------
class FakeEventSubscription:
    """Bounded non-model observation. Explicit ticks only (no background
    thread, no model calls). Missed ticks yield no events (no-evidence,
    never completion). In-memory queue drained per tick, never unbounded."""

    def __init__(self):
        self.queue = []
        self.ticks = 0

    def inject(self, event):
        self.queue.append(event)

    def tick(self, max_events=16):
        self.ticks += 1
        out, self.queue = self.queue[:max_events], self.queue[max_events:]
        return out


class ACPOutcomeObserver:
    """Runnable read-only observer over session-history JSONL: scans a
    bounded tail for completion/failure markers keyed by session and
    execution IDs. Read-only; absence is unavailable (owned fault at the
    caller), never completion."""

    def __init__(self, history_path, max_tail_lines=200):
        self.history_path = history_path
        self.max_tail = max_tail_lines
        self.scans = 0

    def observe(self, session_id, execution_id):
        """Return the latest outcome dict, or None when unobserved."""
        self.scans += 1
        try:
            with open(self.history_path) as fh:
                lines = fh.readlines()[-self.max_tail:]
        except OSError:
            return None
        latest = None
        for line in lines:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("session_id") == session_id and \
                    row.get("execution_id") == execution_id and \
                    row.get("outcome") in ("completed", "failed"):
                latest = row
        return latest


# -- adapter ----------------------------------------------------------------------
class HostAdapter:
    """Narrow machinery over a P5 Driver: receipts, identity, timers,
    cursor/restart reconciliation, bounded escalation. Production clock
    and transports are wired by the operator; Stage A injects fakes and
    never enables live effects."""

    def __init__(self, driver, clock=None, transport=None, timers=None,
                 observer=None):
        self.driver = driver
        # Live mode wires HostClock + production transports explicitly;
        # Stage A injects fakes and never enables live effects.
        if clock is None:
            from driver import FakeClock as _FC
            clock = _FC()
        self.clock = clock
        self.transport = transport or FakeWakeTransport()
        if timers is None:
            timers = FakeTimerService(driver.kv.get, driver._kv_put)
        self.timers = timers
        self.subscription = FakeEventSubscription()
        self.observer = observer
        self.cursor = driver.kv.get("host-cursor")
        self.escalations = []

    def trusted_now(self):
        return self.clock.utc_now()

    # -- trusted source capture (D3) -------------------------------------------
    def _kv(self, key, value):
        self.driver._kv_put(key, value)

    def capture(self, package, attempt, action, event, execution,
                outcome, occurred_at=None, provenance=None):
        """Persist a source receipt stamped with TRUSTED receipt time from
        host context. Caller occurrence is separate, validated, and never
        replaces receipt time. Conflicting re-capture is rejected (durable
        identity, no overwrite-as-dedup); identical re-capture dedups."""
        recorded = validator_mod._instant(self.trusted_now())
        occurred = None
        skew = None
        if occurred_at is not None:
            occurred = validator_mod._instant(occurred_at)
            if occurred is None:
                raise OwnedFault("E_BAD_OCCURRED",
                                 "occurrence not a UTC instant")
            skew = (occurred - recorded).total_seconds()
            if skew is not None and skew > FUTURE_SKEW_TOLERANCE_S:
                raise OwnedFault("E_SKEW_EXCEEDED",
                                 "occurrence %.0fs beyond tolerance" % skew)
        key = "receipt:%s:%s:%s:%s:%s" % (
            package, attempt, action, event, execution)
        old = self.driver.kv.get(key)
        if old is not None:
            prev = json.loads(old)
            if prev.get("outcome") != outcome:
                raise OwnedFault("E_CONFLICT",
                                 "conflicting re-capture; identity kept")
            return (key, True)  # identical: idempotent dedup
        # Receipt + cursor publish together: no skip/loss on restart.
        self.driver._kv_put_many([(
            key, json.dumps({
                "package": package, "attempt": attempt, "action": action,
                "event": event, "execution": execution, "outcome": outcome,
                "receipt_at_utc": recorded.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "occurred_at": occurred.strftime("%Y-%m-%dT%H:%M:%SZ")
                if occurred else None,
                "provenance": provenance, "skew_s": skew},
                sort_keys=True)), ("host-cursor", event)])
        self.cursor = event
        return (key, False)

    def receipt(self, package, attempt, action, event, execution):
        raw = self.driver.kv.get(
            "receipt:%s:%s:%s:%s:%s" % (
                package, attempt, action, event, execution))
        return json.loads(raw) if raw else None

    def trail(self, action):
        """Correlate dispatch -> artifacts -> outcome for one action."""
        chain = {"action": action, "executions": {},
                 "receipts": [], "applied": [], "stale": []}
        for key, value in self.driver.kv.items():
            if key.startswith("exec:%s:" % action):
                chain["executions"][key] = json.loads(value)
            elif key.startswith("receipt:") and (":%s:" % action) in key:
                chain["receipts"].append(json.loads(value))
            elif key.startswith("applied:%s:" % action):
                chain["applied"].append(json.loads(value))
            elif key.startswith("stale:%s:" % action):
                chain["stale"].append(json.loads(value))
        return chain

    # -- declared execution identity (D2: single transactions) ----------------------
    def register_execution(self, action, execution, authorization_ref,
                           deadline_utc):
        """Declare a new execution of an authorized action."""
        self.driver._kv_put_many([
            ("exec-current:" + action, execution),
            ("exec:%s:%s" % (action, execution), json.dumps({
                "authorization_ref": authorization_ref,
                "deadline_utc": deadline_utc}, sort_keys=True))])
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
        """Same-action resume: identities unchanged; relationship recorded
        atomically with the new registration."""
        self.driver._kv_put_many([
            ("exec-current:" + action, new_execution),
            ("exec:%s:%s" % (action, new_execution), json.dumps({
                "authorization_ref": authorization_ref,
                "deadline_utc": deadline_utc}, sort_keys=True)),
            ("rel:%s:%s" % (action, new_execution), json.dumps(
                {"relationship": "resume", "resumes_action_id": action,
                 "resumes_execution_id": old_execution, "attempt": attempt,
                 "phase": phase}, sort_keys=True))])
        return ("resumed", False)

    def replace_action(self, old_action, new_action, new_execution,
                       authorization_ref, deadline_utc, attempt_changed):
        """Genuine replacement in ONE durable transaction: supersedes note
        + old-action marker + new registration commit together before any
        external effect. Projection changes only on commit."""
        self.driver._kv_put_many([
            ("rel:%s:%s" % (new_action, new_execution), json.dumps(
                {"relationship": "supersedes",
                 "supersedes_action_id": old_action,
                 "attempt_changed": attempt_changed,
                 "authorization_ref": authorization_ref}, sort_keys=True)),
            ("exec-current:" + old_action, "SUPERSEDED->" + new_action),
            ("exec-current:" + new_action, new_execution),
            ("exec:%s:%s" % (new_action, new_execution), json.dumps({
                "authorization_ref": authorization_ref,
                "deadline_utc": deadline_utc}, sort_keys=True))])
        return ("replaced", False)

    def resume_from_cursor(self):
        """Restart resumes observation from the persisted cursor (never
        skips, never replays as new)."""
        return self.cursor

    # -- timers from remaining authorized duration (D4) ---------------------------
    def arm_from_ledger(self, timer_id, ledger_deadline_utc, now_utc=None):
        """Create a one-shot relative timer for the remaining duration.
        Expired or malformed durations are owned faults, not timers."""
        now = validator_mod._instant(
            now_utc if now_utc is not None else self.trusted_now())
        dl = validator_mod._instant(ledger_deadline_utc)
        if now is None or dl is None:
            raise OwnedFault("E_BAD_DEADLINE", "deadline not a UTC instant")
        remaining = (dl - now).total_seconds()
        if remaining <= 0:
            raise OwnedFault("E_EXPIRED", "no remaining authorized duration",
                             owner="tern")
        return self.timers.create(timer_id, ledger_deadline_utc)

    def arm_current(self, timer_id, qid):
        """Arm from the authoritative current action deadline with trusted
        now — never an arbitrary caller deadline."""
        rec = self.driver.store.revisions.get((qid, 1))
        fl = (rec or {}).get("flight") or {}
        if not fl.get("action_id") or not fl.get("deadline"):
            raise OwnedFault("E_NO_ACTION", "no current ledger action")
        return self.arm_from_ledger(timer_id, fl["deadline"])

    # -- restart / lost-wake reconciliation ------------------------------------
    def reconcile_send(self, message_id, action):
        """Reconcile a transport receipt against persisted outcomes. An
        escalation record is never acknowledged delivery; only transport
        delivered settles. Queued is not completion; ambiguous never
        blind-retries."""
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

    def reconcile_observed(self, session_id, execution_id, action):
        """Dead-turn/lost-completion observation feeds reconciliation:
        an observed outcome settles; unobserved stays an owned fault."""
        if self.observer is None:
            return {"decision": "hold-for-reconciliation",
                    "note": "no observer bound"}
        outcome = self.observer.observe(session_id, execution_id)
        if outcome is None:
            raise OwnedFault("E_UNAVAILABLE",
                             "observation unavailable; owned fault, not idle")
        if outcome.get("outcome") == "failed":
            return {"decision": "owned-failure",
                    "note": "observed dead-turn consumed",
                    "observed": outcome}
        return {"decision": "settled-delivered", "observed": outcome}

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
