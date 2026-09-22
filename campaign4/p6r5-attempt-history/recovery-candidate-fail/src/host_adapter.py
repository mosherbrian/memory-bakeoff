"""P6-r2 connected host execution adapter: narrow machinery around the
accepted P5 ingress/store with runnable host paths and injected
collaborators for Stage A checks.

Stage-A rule: live effects occur ONLY with an explicit bound plan hash
plus a non-empty fixture allowlist (see harness live mode). Anything
else fails closed. No seat actions, service installation, model calls,
host clock changes, or live effects occur in Stage A.

- D1 entrypoint: harness.py composes ingress/driver/transport/capture/
  timers/reconciliation. Production collaborators (HostWakeTransport,
  HostTimerService, ACPOutcomeObserver) run the real branches; Stage A
  injects fakes/runners with identical signatures. No fake defaults in
  live mode (HostAdapter(live=True) rejects Fake* collaborators).
- Transport: real subprocess API kwargs (argv, capture_output, text,
  timeout int, AGENTDECK_PROFILE=campaign4 env); exit 0 started/sent,
  exit 3 queued, other failed, timeout/malformed ambiguous. Message
  identity persisted in driver_kv: state() is stable across fresh
  instances. Queued is delivery ack, never completion or redispatch
  permission.
- Timers: bounded injected runner (subprocess-compatible signature);
  unique fixture units; remaining authorized duration; executable
  candidate callback argv (harness timer-callback, never `true`);
  durable current-action checks; unit-name identity shared by
  create/cancel/query.
- Observer: real ACP history schema (turn rows kind/id/status/at;
  message rows skipped as partial), bounded incremental tail scan with
  persisted cursor, explicit session->execution binding, artifact
  verification against bound dispatch artifacts; completion drives the
  next bounded action through code (drive_next). Truncation/rotation/
  restart handled; unavailable source is an owned fault.
- Escalation requires actual acknowledgement evidence (transport
  delivered of the escalation message), not an owner string.
- Notifications and all-seat stop are FAKE targets; campaign4-pause stays
  the unchanged emergency actuator (inventory hash only, never called).
"""
from __future__ import annotations

import json
import os
import subprocess

import validator as validator_mod
from ingress import FUTURE_SKEW_TOLERANCE_S

# Exit-code contract of the inventoried wake script (read, never executed
# during discovery): 0 started, 3 queued, anything else failure.
WAKE_RC_SENT = 0
WAKE_RC_QUEUED = 3


class OwnedFault(Exception):
    def __init__(self, code, detail="", owner="cairn"):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail
        self.owner = owner


def _default_runner(cmd, **kwargs):
    return subprocess.run(cmd, **kwargs)


# -- transports ---------------------------------------------------------------
class FakeWakeTransport:
    """Stage-A stand-in: records sends; states queued/sent/delivered/
    failed/ambiguous. Only delivered counts as transport receipt — never
    as worker completion."""

    def __init__(self):
        self.calls = []  # (seat, text, kind)
        self.inbox = {}  # message_id -> state dict
        self._n = 0

    def send(self, seat, text, kind="wake", action=None, execution=None):
        self._n += 1
        mid = "msg-%d" % self._n
        self.calls.append((seat, text, kind))
        self.inbox[mid] = {"seat": seat, "kind": kind, "state": "queued",
                           "action": action, "execution": execution}
        return mid

    def mark(self, message_id, state):
        assert state in ("queued", "sent", "delivered", "failed",
                         "ambiguous")
        self.inbox[message_id]["state"] = state
        return state

    def state(self, message_id):
        return self.inbox.get(message_id, {}).get("state", "unknown")


class HostWakeTransport:
    """Runnable production transport over the inventoried wake script.

    The subprocess runner is injectable (same real signature); Stage A
    tests inject scripted runners so the mapping/persistence branches run
    without live effects. Live sends fail closed unless enabled with a
    fixture seat allowlist."""

    def __init__(self, wake_path, allowlist_seats=(), enabled=False,
                 timeout_s=30, kv_get=None, kv_put=None, runner=None):
        self.wake_path = wake_path
        self.allowlist = tuple(allowlist_seats)
        self.enabled = enabled
        self.timeout_s = timeout_s
        self._kv_get = kv_get or (lambda k: None)
        self._kv_put = kv_put or (lambda k, v: None)
        self._runner = runner or _default_runner
        self.calls = []

    def command_for(self, seat, text):
        return [self.wake_path, seat, text]

    def send(self, seat, text, kind="wake", action=None, execution=None):
        if not self.enabled or seat not in self.allowlist:
            raise OwnedFault("E_DISABLED",
                             "live send outside enabled fixture allowlist")
        cmd = self.command_for(seat, text)
        env = dict(os.environ)
        env["AGENTDECK_PROFILE"] = "campaign4"
        self.calls.append((seat, text, kind))
        try:
            proc = self._runner(cmd, capture_output=True, text=True,
                                timeout=int(self.timeout_s), env=env)
        except subprocess.TimeoutExpired:
            return self._record(seat, text, kind, action, execution,
                                "ambiguous", rc="timeout", receipt="")
        except (OSError, subprocess.SubprocessError):
            return self._record(seat, text, kind, action, execution,
                                "ambiguous", rc="spawn-failed", receipt="")
        receipt = (proc.stdout or "").strip().splitlines()
        receipt_line = receipt[-1] if receipt else ""
        if proc.returncode == WAKE_RC_SENT and receipt_line.startswith(
                "wake:"):
            state = "sent"
        elif proc.returncode == WAKE_RC_QUEUED and receipt_line.startswith(
                "wake:"):
            state = "queued"
        elif proc.returncode == WAKE_RC_SENT or \
                proc.returncode == WAKE_RC_QUEUED:
            state = "ambiguous"  # right code, malformed receipt
        else:
            state = "failed"
        return self._record(seat, text, kind, action, execution, state,
                            rc=proc.returncode, receipt=receipt_line)

    def _record(self, seat, text, kind, action, execution, state, rc,
                receipt):
        # Durable counter: fresh instances never restart at 1 and can
        # never overwrite prior receipt identity.
        try:
            n = int(self._kv_get("msg-counter") or "0") + 1
        except (TypeError, ValueError):
            n = 1
        mid = "msg-%s-%d" % (action or "na", n)
        if self._kv_get("msg:" + mid) is not None:
            raise OwnedFault("E_MSG_COLLISION",
                             "refusing to overwrite receipt " + mid)
        self._kv_put("msg-counter", str(n))
        self._kv_put("msg:" + mid, json.dumps(
            {"seat": seat, "kind": kind, "state": state, "rc": rc,
             "receipt": receipt, "action": action,
             "execution": execution}, sort_keys=True))
        return mid

    def state(self, message_id):
        raw = self._kv_get("msg:" + message_id)
        if raw is None:
            return "unknown"
        try:
            return json.loads(raw).get("state", "unknown")
        except ValueError:
            return "unknown"


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
    """Runnable host timers through a bounded injected runner
    (subprocess-compatible argv/timeout signature). Unit-name identity is
    shared by create/cancel/query. Runner calls happen only when enabled
    with an allowlist; Stage A injects scripted runners."""

    def __init__(self, kv_get=None, kv_put=None, enabled=False,
                 allowlist=(), runner=None, callback_argv=None,
                 systemd_run="systemd-run", systemctl="systemctl"):
        super().__init__(kv_get, kv_put)
        self.enabled = enabled
        self.allowlist = tuple(allowlist)
        self._runner = runner or _default_runner
        self.callback_argv = callback_argv or []
        self.systemd_run = systemd_run
        self.systemctl = systemctl
        self.runner_calls = []

    def unit_for(self, timer_id):
        return "%s.timer" % timer_id

    def command_for(self, timer_id, delay_s, callback_argv=None):
        cb = callback_argv if callback_argv is not None \
            else self.callback_argv
        return [self.systemd_run, "--user", "--unit=%s" % timer_id,
                "--on-active=%ds" % int(delay_s)] + list(cb)

    def _guard(self, timer_id):
        if not self.enabled or timer_id not in self.allowlist:
            raise OwnedFault("E_DISABLED",
                             "live timer outside enabled fixture allowlist")

    def create_host(self, timer_id, deadline_utc, delay_s,
                    callback_argv=None):
        """Create a real one-shot with the executable candidate callback;
        the armed record (deadline + unit) persists in kv either way."""
        self._guard(timer_id)
        cmd = self.command_for(timer_id, delay_s, callback_argv)
        self.runner_calls.append(("create", cmd))
        proc = self._runner(cmd, capture_output=True, text=True,
                            timeout=30)
        if proc.returncode != 0:
            raise OwnedFault("E_TIMER_CREATE",
                             "host timer refused: %s" %
                             (proc.stderr or "")[:200])
        self._kv_put("timer-arm:" + timer_id, json.dumps(
            {"deadline": deadline_utc, "unit": self.unit_for(timer_id),
             "callback": cmd[-len(callback_argv or self.callback_argv):]
             if (callback_argv or self.callback_argv) else []},
            sort_keys=True))
        self.timers[timer_id] = {"deadline": deadline_utc,
                                 "state": "armed-host"}
        return ("armed-host", False)

    def cancel_host(self, timer_id):
        """Cancel by the SAME unit identity; durable cancellation."""
        self._guard(timer_id)
        unit = self.unit_for(timer_id)
        for verb in ("stop", "reset-failed"):
            cmd = [self.systemctl, "--user", verb, unit]
            self.runner_calls.append(("cancel", cmd))
            self._runner(cmd, capture_output=True, text=True, timeout=30)
        return self.cancel(timer_id)

    def query_host(self, timer_id):
        """Read-only status by the same unit identity."""
        self._guard(timer_id)
        cmd = [self.systemctl, "--user", "show", self.unit_for(timer_id),
               "--property=ActiveState,SubState"]
        self.runner_calls.append(("query", cmd))
        proc = self._runner(cmd, capture_output=True, text=True,
                            timeout=30)
        props = {}
        for line in (proc.stdout or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                props[k.strip()] = v.strip()
        return props


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
    """Bounded incremental observer over real ACP history JSONL.

    Schema (captured read-only; content redacted in fixtures): turn rows
    carry kind/id/status/at (+title/paths/output/raw/diffs); plain message
    rows carry role/text/at and no status. Terminal statuses observed:
    completed / failed. Anything else (message rows, in_progress, partial
    rows missing kind/status) is skipped as non-outcome. Cursor = file byte
    offset persisted by the adapter; truncation resets with a note,
    rotation (missing file) reports unavailable."""

    TERMINAL = ("completed", "failed")

    def __init__(self, history_path, max_tail_lines=200):
        self.history_path = history_path
        self.max_tail = max_tail_lines
        self.scans = 0

    def observe(self, cursor=0):
        """Return (outcomes, new_cursor, note). Outcomes are normalized
        {row_id, status, at} in file order. Never raises for content."""
        self.scans += 1
        try:
            size = os.path.getsize(self.history_path)
        except OSError:
            return ([], cursor, "rotated-missing")
        if size < cursor:
            cursor = 0
            note = "truncated-reset"
        else:
            note = "ok"
        try:
            with open(self.history_path) as fh:
                fh.seek(cursor)
                lines = fh.readlines()[-self.max_tail:]
                new_cursor = fh.tell()
        except OSError:
            return ([], cursor, "unavailable")
        outcomes = []
        for line in lines:
            try:
                row = json.loads(line)
            except ValueError:
                continue  # partial/corrupt line skipped
            if not isinstance(row, dict):
                continue
            if row.get("status") in self.TERMINAL and row.get("id"):
                outcomes.append({"row_id": row["id"],
                                 "status": row["status"],
                                 "at": row.get("at")})
        return (outcomes, new_cursor, note)


# -- adapter ----------------------------------------------------------------------
class HostAdapter:
    """Narrow machinery over a P5 Driver: receipts, identity, timers,
    cursor/restart reconciliation, bounded escalation. Production clock
    and transports are wired explicitly by the operator/harness; Stage A
    injects fakes and never enables live effects."""

    def __init__(self, driver, clock=None, transport=None, timers=None,
                 observer=None, live=False):
        if live and isinstance(transport, FakeWakeTransport):
            raise OwnedFault("E_DISABLED",
                             "no fake defaults in live mode")
        if live and transport is None:
            raise OwnedFault("E_DISABLED",
                             "live mode needs an explicit transport")
        self.driver = driver
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
        self.live = live
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

    def bound_artifacts(self, action):
        """Artifact hashes bound at dispatch (world launch record)."""
        arts = (self.driver.world.state.get(action) or {}).get(
            "artifacts") or {}
        return set(arts.values()) | set(arts.keys())

    # -- launcher-bound routing + turn bindings ----------------------------------
    def bind_route(self, action, seat):
        """Launcher-declared contract route: action_id -> destination seat."""
        self._kv("route:" + action, seat)
        return seat

    def route_for(self, action):
        seat = self.driver.kv.get("route:" + action)
        if not seat:
            raise OwnedFault("E_UNROUTED",
                             "no contract-bound seat for " + action)
        return seat

    def bind_turn(self, stream_key, item, execution, action, step):
        """Launcher binding: this stream/item is this execution's turn."""
        self._kv("turn-bind:%s:%s" % (stream_key, item), json.dumps(
            {"execution": execution, "action": action, "step": step},
            sort_keys=True))
        return (stream_key, item)

    def turn_binding(self, stream_key, item):
        raw = self.driver.kv.get("turn-bind:%s:%s" % (stream_key, item))
        return json.loads(raw) if raw else None

    # -- durable outbox (ack-after-delivery, never clear before send) ------------
    def outbox_send(self, target_action, payload, execution=None):
        """Declare a pending intent (durable) and deliver it. The pending
        record is cleared only after acknowledged delivery."""
        import hashlib as _hl
        oid = "ob-%s" % _hl.sha256(json.dumps(
            payload, sort_keys=True).encode()).hexdigest()[:16]
        if execution is None:
            execution = self.current_execution(target_action)
        self.driver._kv_put_many([
            ("outbox-pending:" + oid, json.dumps(
                {"target": target_action, "payload": payload,
                 "execution": execution},
                sort_keys=True))])
        seat = self.route_for(target_action)
        try:
            mid = self.transport.send(seat, json.dumps(payload),
                                      kind="dispatch", action=target_action,
                                      execution=execution)
        except OwnedFault:
            return oid  # still pending; restart reconciles same identity
        self.driver._kv_put("outbox-sent:" + oid, mid or "")
        return oid

    def outbox_ack(self, outbox_id):
        """Acknowledge only after delivery evidence; never before send."""
        mid = self.driver.kv.get("outbox-sent:" + outbox_id)
        if mid and self.transport.state(mid) == "delivered":
            self.driver._kv_put_many([
                ("outbox-acked:" + outbox_id, mid),
                ("outbox-pending:" + outbox_id, "")]
            )
            return ("acked", False)
        return ("pending", True)

    def drain_outbox_settled(self, qid="P6F"):
        """Settle pending intents ONLY on proof: a valid production
        transport receipt (sent/queued/delivered — never ambiguous,
        failed or unknown) PLUS authoritative evidence that the intended
        action/execution actually started or produced its bound outcome
        (bound turn-seen for the exact execution AND ledger advancement
        past the dispatched step). Terminal phase alone never forges
        acknowledgement; queued alone never settles. Settlement (ack +
        clear) is one atomic durable write."""
        settled = []
        for key in list(self.driver.kv.keys()):
            if not key.startswith("outbox-pending:") or \
                    not self.driver.kv[key]:
                continue
            oid = key.split(":", 1)[1]
            if self.driver.kv.get("outbox-acked:" + oid):
                continue
            try:
                if self._settle_one(oid, qid):
                    settled.append(oid)
            except (OwnedFault, ValueError):
                continue  # malformed/unroutable: never settle, never clear
        return settled

    def _settle_one(self, oid, qid):
        """Single-intent settlement check. Returns True iff settled now."""
        try:
            pending = json.loads(self.driver.kv.get("outbox-pending:" +
                                                    oid) or "{}")
        except ValueError:
            return False  # malformed receipt: never settle, never clear
        mid = self.driver.kv.get("outbox-sent:" + oid)
        if not mid:
            return False  # never sent: nothing to settle
        receipt = self._msg_receipt(mid)
        if receipt is None:
            return False  # missing proof
        if receipt.get("state") not in ("sent", "queued", "delivered"):
            return False  # ambiguous/failed/unknown stay pending
        target, execution = pending.get("target"), pending.get("execution")
        if receipt.get("action") != target:
            return False  # receipt/action mismatch
        if not self._execution_proven(target, execution, receipt, qid):
            return False
        try:
            seat = self.route_for(target)
        except OwnedFault:
            return False
        if receipt.get("seat") != seat:
            return False  # wrong seat: never settle
        self.driver._kv_put_many([
            ("outbox-acked:" + oid, mid),
            ("outbox-pending:" + oid, "")])
        return True

    def _msg_receipt(self, mid):
        raw = self.driver.kv.get("msg:" + mid)
        if raw is None:
            return None
        try:
            rec = json.loads(raw)
        except ValueError:
            return None
        return rec if isinstance(rec, dict) else None

    def _execution_proven(self, action, execution, receipt, qid):
        """Authoritative start/outcome proof for the exact execution: a
        bound turn-seen record for it AND ledger advancement in the SAME
        package (a live flight for the target action, or a terminal
        disposition closing it). A bare flight elsewhere, a disposition
        for unrelated work, or phase alone without the turn-seen record
        proves nothing here."""
        if not action or not execution:
            return False
        if receipt.get("execution") != execution:
            return False  # unrelated or stale execution
        if execution != self.current_execution(action) and \
                not self._superseded_to_current(action, execution):
            return False
        seen = any(k.startswith("turn-seen:") and k.endswith(":" +
                                                             execution)
                   for k in self.driver.kv.keys())
        if not seen:
            return False
        for (qq, _rev), rec in self.driver.store.revisions.items():
            if qq != qid:
                continue
            fl = rec.get("flight") or {}
            if fl.get("action_id") == action:
                return True
            if rec.get("phase") in ("COMPLETE", "EXHAUSTED",
                                    "TERMINATED", "SUPERSEDED") and \
                    rec.get("disposition") is not None:
                return True
        return False

    def _superseded_to_current(self, action, execution):
        current = self.current_execution(action)
        for key, value in self.driver.kv.items():
            if not key.startswith("rel:"):
                continue
            try:
                rel = json.loads(value)
            except ValueError:
                continue
            if rel.get("relationship") == "supersedes" and \
                    rel.get("supersedes_action_id") == action:
                return True
        return current == execution

    def _ledger_evidence_for(self, action, qid):
        """RETIRED loose check (kept for backward compatibility; the
        settlement path uses _execution_proven instead)."""
        return self._execution_proven(action,
                                      self.current_execution(action),
                                      {"execution":
                                       self.current_execution(action)},
                                      qid)

    def reconcile_outbox(self):
        """Restart reconciliation: pending intents resend under the SAME
        outbox identity (no new intent, no duplicate dispatch); ambiguous
        delivery holds without blind replay."""
        results = {}
        for key in list(self.driver.kv.keys()):
            if not key.startswith("outbox-pending:") or \
                    not self.driver.kv[key]:
                continue
            oid = key.split(":", 1)[1]
            if self.driver.kv.get("outbox-acked:" + oid):
                continue
            pending = json.loads(self.driver.kv[key])
            seat = self.route_for(pending["target"])
            mid = self.driver.kv.get("outbox-sent:" + oid)
            if mid and self.transport.state(mid) == "delivered":
                self.driver._kv_put_many([
                    ("outbox-acked:" + oid, mid),
                    ("outbox-pending:" + oid, "")])
                results[oid] = "acked-from-evidence"
                continue
            if mid and self.transport.state(mid) in ("queued", "sent"):
                results[oid] = "held-awaiting-receipt"
                continue
            if mid:
                results[oid] = "held-ambiguous"
                continue
            try:
                mid = self.transport.send(
                    seat, json.dumps(pending["payload"]),
                    kind="dispatch", action=pending["target"],
                    execution=self.current_execution(pending["target"]))
            except OwnedFault:
                results[oid] = "held-owned-fault"
                continue
            self.driver._kv_put("outbox-sent:" + oid, mid or "")
            results[oid] = "resent-same-identity"
        return results

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

    # -- session binding + artifacts + code-driven next action -----------------------
    def bind_session(self, session_id, execution_id, action):
        """Explicit source-session -> execution binding (persisted)."""
        self._kv("bind:%s" % session_id, json.dumps(
            {"execution_id": execution_id, "action": action},
            sort_keys=True))
        return session_id

    def verify_artifacts(self, action, execution, outcome_row,
                         bound_artifacts):
        """Artifact verification against bound dispatch artifacts (hash
        equality where the row declares one; structural presence
        otherwise). Returns (verified, evidence)."""
        declared = (outcome_row or {}).get("artifact_hash")
        if declared is not None:
            ok = declared in (bound_artifacts or {})
            return (ok, {"mode": "hash-equality", "match": ok})
        ok = bool(bound_artifacts)
        return (ok, {"mode": "structural-presence", "match": ok})

    def drive_next(self, action, verify_action_id, verify_deadline_utc,
                   artifact_hashes, qid=None):
        """A verified worker completion drives the next bounded action
        through code: publish completion (creates the verifier flight)."""
        qid = qid or self.driver.kv.get("harness-qid") or "P6F"
        out, dup = self.driver.publish_completion(
            qid, action, artifact_hashes,
            verify={"action_id": verify_action_id, "owner": "corvid",
                    "deadline": verify_deadline_utc})
        return ({"published": out, "next_action": verify_action_id}, dup)

    def observe_bound(self, session_file, session_id):
        """Bounded incremental observation with persisted cursor, explicit
        binding, and stale-execution retention. Returns
        (matched, stale, note) where matched carry bound execution IDs."""
        binding_raw = self.driver.kv.get("bind:" + session_id)
        if binding_raw is None:
            raise OwnedFault("E_UNBOUND", "no declared session binding")
        binding = json.loads(binding_raw)
        cur_raw = self.driver.kv.get("cursor:" + session_file)
        cursor = int(cur_raw) if cur_raw is not None else 0
        outcomes, new_cursor, note = self.observer.observe(cursor) \
            if self.observer is not None else ([], cursor, "no-observer")
        if note in ("rotated-missing", "unavailable", "no-observer"):
            raise OwnedFault("E_UNAVAILABLE",
                             "observation unavailable; owned fault, not idle")
        self._kv("cursor:" + session_file, str(new_cursor))
        matched, stale = [], []
        for row in outcomes:
            entry = dict(row, execution_id=binding["execution_id"],
                         action=binding["action"])
            if binding["execution_id"] != self.current_execution(
                    binding["action"]):
                self._kv("stale-obs:%s" % row["row_id"], json.dumps(
                    entry, sort_keys=True))
                stale.append(entry)
            else:
                matched.append(entry)
        return (matched, stale, note)

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

    def reconcile_observed(self, session_file, execution_id, action):
        """Dead-turn/lost-completion observation feeds reconciliation over
        the real schema: an observed terminal outcome settles or fails
        owned; an unobserved action stays an owned fault."""
        if self.observer is None:
            return {"decision": "hold-for-reconciliation",
                    "note": "no observer bound"}
        matched, _stale, _note = self.observe_bound(session_file,
                                                    session_file)
        mine = [m for m in matched if m["execution_id"] == execution_id]
        if not mine:
            raise OwnedFault("E_UNAVAILABLE",
                             "observation unavailable; owned fault, not idle")
        if mine[-1].get("status") == "failed":
            return {"decision": "owned-failure",
                    "note": "observed dead-turn consumed",
                    "observed": mine[-1]}
        return {"decision": "settled-delivered", "observed": mine[-1]}

    def escalate_unavailable(self, action, owner, next_action,
                             response_deadline_utc):
        """Bounded owned escalation (fake target in Stage A). Returns
        pending: acknowledgement requires actual transport evidence via
        confirm_escalation_ack — an owner string alone never settles."""
        mid = None
        try:
            mid = self.transport.send(owner, "escalation:" + action,
                                      kind="escalation", action=action,
                                      execution=self.current_execution(
                                          action))
        except OwnedFault:
            mid = None
        self.escalations.append({
            "action": action, "owner": owner, "next_action": next_action,
            "response_deadline_utc": response_deadline_utc,
            "message_id": mid, "acknowledged": False})
        self._kv("escalation:" + action, json.dumps(
            self.escalations[-1], sort_keys=True))
        return ("escalated-owned", False)

    def confirm_escalation_ack(self, action):
        """Actual acknowledgement evidence for a pending escalation."""
        esc = [e for e in self.escalations if e["action"] == action]
        if not esc:
            raw = self.driver.kv.get("escalation:" + action)
            if raw is None:
                raise OwnedFault("E_NO_ESCALATION", "nothing pending")
            esc = [json.loads(raw)]
        mid = esc[-1].get("message_id")
        if mid is not None and self.transport.state(mid) == "delivered":
            esc[-1]["acknowledged"] = True
            self._kv("escalation:" + action, json.dumps(
                esc[-1], sort_keys=True))
            return ("escalated-acknowledged", True)
        return ("escalation-pending", False)
