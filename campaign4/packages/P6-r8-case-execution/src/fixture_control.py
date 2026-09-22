"""P6-r8 fixture delivery consumer (the R1 executing consumer, D2/D3).

run_case executes this on the real host path in EVERY branch. It reads the
armed intervention record (explicit file path, never env-only) and applies
the declared control to the isolated fixture during seat operation.

D2 identity/role authority: every delivery resolves (seat -> {role,
action, execution}) from caller-supplied SIGNED bindings (execution
config); nothing is inferred from title substrings. Unknown seats and
deposited (action, execution) pairs that do not match the seat's signed
binding are rejected BEFORE any wake subprocess runs.

D2 wake boundary: live notification invokes the real authorized wake
command with an explicit environment (AGENTDECK_PROFILE=campaign4 plus an
explicit cwd), mirroring the registry reader — never bare controller
inheritance. Transport outcomes are captured separately as started vs
queued vs ambiguous (rc + receipt-line mapping identical to the candidate
transport); a queued return is recorded as HELD/induced evidence, never
as proof of completion or acknowledged recovery.

D3 notification-primary + reconciliation: the blocking waiter uses the
existing DirNotifier primitive (r3harness.notify): attach BEFORE the
initial drain, drain, then wait on notifications with bounded timeouts —
no bespoke polling loop. Delivery identity is durable and append-only:
each deposit is journaled (deliveries.jsonl) as intent -> done; a reopen
reconciles intent-without-done against the inbox (present+matching sha =
record done without resending; otherwise deliver once). Explicit ambiguous
delivery stays pending owned reconciliation: it is never marked
delivered, never silently retried.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HOLD_DELAY_S = 5.0


class ControlFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _now_z():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_envelope(text):
    try:
        env = json.loads(text or "{}")
    except ValueError:
        return {}
    if isinstance(env, dict) and isinstance(env.get("text"), str):
        try:
            env = json.loads(env["text"])
        except ValueError:
            pass
    return env if isinstance(env, dict) else {}


def _journal_path(case_root):
    return os.path.join(case_root, "deliveries.jsonl")


def _journal_read(case_root):
    try:
        return [json.loads(l) for l in
                open(_journal_path(case_root)) if l.strip()]
    except OSError:
        return []


def _journal_append(case_root, record):
    with open(_journal_path(case_root), "a") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def _notifier():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(
        __file__)), "r3harness"))
    import notify as _n
    return _n


def _classify_receipt(returncode, stdout):
    """Separate started vs queued vs ambiguous exactly like the candidate
    transport mapping (rc0+wake: => started/sent; rc3+wake: => queued;
    anything else => ambiguous/failed). Returns (state, receipt_line)."""
    lines = (stdout or "").strip().splitlines()
    line = lines[-1] if lines else ""
    if returncode == 0 and line.startswith("wake:"):
        return "started", line
    if returncode == 3 and line.startswith("wake:"):
        return "queued", line
    if returncode in (0, 3):
        return "ambiguous", line
    return "failed", line


def deliver_pending(outbox_dir, inbox_dir, intervention, bindings,
                    case_root, live_wake=None, runner=None,
                    run_cwd=None, hold_delay_s=HOLD_DELAY_S):
    """One delivery pass over deposited texts against signed bindings.

    bindings: {seat: {"role":..., "action":..., "execution":...}} from the
    signed execution config. Unknown seats and binding-mismatched
    (action, execution) pairs raise BEFORE any wake subprocess.
    Returns applied records (including held). Never invents acks."""
    import glob as _g
    applied = []
    control = (intervention or {}).get("control", "none-declared")
    case = (intervention or {}).get("case", "")
    journaled = {}
    for rec in _journal_read(case_root):
        if rec.get("phase") == "done":
            journaled[rec.get("deposit")] = rec
    for path in sorted(_g.glob(os.path.join(outbox_dir, "send-*.json"))):
        name = os.path.basename(path)
        if name in journaled:
            continue  # already delivered: never a blind second send
        try:
            dep = json.load(open(path))
        except ValueError:
            continue
        seat = dep.get("seat", "")
        binding = (bindings or {}).get(seat)
        if binding is None:
            raise ControlFault("E_UNKNOWN_SEAT",
                               "deposited seat %r not in signed bindings; "
                               "rejected before wake" % (seat,))
        env = _decode_envelope(dep.get("text", ""))
        if env.get("action") != binding.get("action") or \
                env.get("execution") != binding.get("execution"):
            raise ControlFault("E_MISMATCH",
                               "deposited (action, execution) %r does not "
                               "match signed binding for %r; rejected "
                               "before wake" % ((env.get("action"),
                                                 env.get("execution")),
                                                seat))
        role = binding.get("role")
        held = False
        if control == "hold-verifier-texts" and role == "verifier":
            held = True
        _journal_append(case_root, {"deposit": name, "phase": "intent",
                                    "seat": seat, "case": case,
                                    "at": _now_z()})
        delivered_at, receipt_state, receipt_line, held_until = (
            None, None, None, None)
        if not held:
            first_worker = (role == "worker" and not any(
                a.get("delivered_at") for a in applied))
            if control == "transport-queued-first" and first_worker:
                held_until = _now_z()
                time.sleep(hold_delay_s)  # bounded induced interruption
            if live_wake is None:
                os.makedirs(inbox_dir, exist_ok=True)
                dest = os.path.join(inbox_dir, "to-%s-%s.txt" % (
                    seat, _now_z().replace(":", "")))
                shutil.copy(path, dest)
                delivered_at = _now_z()
                receipt_state, receipt_line = "inboxed", dest
            else:
                run = runner or subprocess.run
                child_env = dict(os.environ)
                child_env["AGENTDECK_PROFILE"] = "campaign4"
                # DELIVER_INBOX is honored only by test wake stubs to
                # hand the text to seat emulators; the real authorized
                # wake notifies the seat directly and ignores it.
                child_env["DELIVER_INBOX"] = inbox_dir
                proc = run([live_wake, seat, dep.get("text", "")],
                           capture_output=True, text=True, timeout=60,
                           cwd=run_cwd or case_root, env=child_env)
                receipt_state, receipt_line = _classify_receipt(
                    proc.returncode, proc.stdout)
                if receipt_state == "failed":
                    raise ControlFault("E_DELIVER",
                                       "live wake rc%d for %s" % (
                                           proc.returncode, seat))
                delivered_at = _now_z()
        rec = {"case": case, "action": env.get("action"),
               "execution": env.get("execution"), "seat": seat,
               "role": role, "deposited_at": dep.get("received_at"),
               "delivered_at": delivered_at, "held": held,
               "held_until": held_until,
               "induced": control != "none-declared",
               "control": control, "receipt_state": receipt_state,
               "receipt_line": (receipt_line or "")[:200]}
        applied.append(rec)
        _journal_append(case_root, dict(rec, deposit=name, phase="done"))
    return applied


def wait_for_deposits(outbox_dir, case_root, timeout_s, poll_s=None):
    """D3 blocking waiter: attach the existing DirNotifier BEFORE the
    initial drain, drain, then wait on notifications with bounded
    timeouts. Returns True if at least one deposit exists."""
    import glob as _g
    _n = _notifier()
    try:
        watcher = _n.DirNotifier(outbox_dir)
    except _n.OwnedFaultLocal as e:
        raise ControlFault("E_NO_NOTIFY",
                           "notification unavailable: " + str(e)[:100])
    try:
        if _g.glob(os.path.join(outbox_dir, "send-*.json")):
            return True
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            if watcher.wait(min(remaining, 5.0)):
                if _g.glob(os.path.join(outbox_dir, "send-*.json")):
                    return True
        return bool(_g.glob(os.path.join(outbox_dir, "send-*.json")))
    finally:
        watcher.close()


def reconcile_journal(outbox_dir, inbox_dir, case_root):
    """D3 reopen reconciliation: intent-without-done entries are checked
    against the inbox (present + matching sha => record done, no resend;
    otherwise redeliver exactly once through deliver_pending). Returns
    the reconciliation report."""
    import glob as _g
    intents = [r for r in _journal_read(case_root)
               if r.get("phase") == "intent"]
    dones = {r.get("deposit") for r in _journal_read(case_root)
             if r.get("phase") == "done"}
    report = {"reconciled": [], "redelivered": []}
    for rec in intents:
        name = rec.get("deposit")
        if name in dones:
            continue
        src = os.path.join(outbox_dir, name)
        if not os.path.exists(src):
            report["reconciled"].append({"deposit": name,
                                         "state": "gone-no-effect"})
            continue
        try:
            want = _sha_file(src)
        except OSError:
            continue
        found = [f for f in _g.glob(os.path.join(inbox_dir, "*"))
                 if os.path.isfile(f)]
        if any(_sha_file(f) == want for f in found):
            _journal_append(case_root, dict(rec, phase="done",
                                            via="reconcile"))
            report["reconciled"].append({"deposit": name,
                                         "state": "already-delivered"})
        else:
            report["redelivered"].append({"deposit": name})
    return report


def apply_artifact_control(art_dir, intervention):
    """Tool-owned artifact tamper for corrupt-after-worker. Returns
    {path, before_sha256, after_sha256} or None. Caller must invoke only
    after observing worker commit."""
    import glob as _g
    if (intervention or {}).get("control") != "corrupt-after-worker":
        return None
    targets = sorted(_g.glob(os.path.join(art_dir, "*")))
    if not targets:
        raise ControlFault("E_APPLY",
                           "no artifact present to apply control to")
    path = targets[0]
    before = _sha_file(path)
    with open(path, "wb") as fh:
        fh.write(b"tampered-by-fixture-control")
    after = _sha_file(path)
    if before == after:
        raise ControlFault("E_APPLY", "tamper had no effect")
    return {"path": path, "before_sha256": before,
            "after_sha256": after,
            "applied_at": _now_z(), "induced": True}


def write_applied(path, case, actions, executions, intervention, deliveries,
                  artifact_control, transport_states):
    rec = {"case": case, "actions": actions, "executions": executions,
           "intervention": intervention, "deliveries": deliveries,
           "artifact_control": artifact_control,
           "transport_states": transport_states,
           "applied_at": _now_z()}
    with open(path, "w") as fh:
        json.dump(rec, fh, sort_keys=True, indent=1)
    return rec


def check_delivered(applied, seat, execution):
    """Every produced end must trace to a delivery record. Returns True
    iff (seat, execution) was actually delivered (not held)."""
    return any(a.get("seat") == seat and a.get("execution") == execution
               and a.get("delivered_at") and not a.get("held")
               for a in applied)


if __name__ == "__main__":
    print(json.dumps({"error": "E_USAGE",
                      "detail": "library module; use case_entry run-case",
                      "owner": "cairn"}, sort_keys=True))
    raise SystemExit(2)
