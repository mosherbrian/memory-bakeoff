"""P6-r8 fixture delivery consumer (the R1 executing consumer).

This module is the missing production consumer: run_case executes it on
the real host path in EVERY branch. It reads the armed intervention record
(explicit file path, never env-only) and applies the declared control to
the isolated fixture during seat operation:

- Texts arrive ONLY via the fixture wake-deposit wrapper into the case
  outbox. This loop moves each text to seat delivery and records an
  applied receipt per text: {case/action/execution/seat, deposited_at,
  delivered_at|held, induced, transport_ref}.
- hold-verifier-texts: verifier texts are recorded HELD and never
  delivered (genuinely lost → verifier never acts; no fabrication).
- transport-queued-first: the first worker text is held for a bounded
  induced delay (default 5s), then delivered; both timestamps recorded
  with the induced label. True transport receipts are preserved as-is;
  a hold is reported as HELD, never as a queued acknowledgement.
- Delivery itself: injected branch copies the text into the seat inbox
  dir; live branch invokes the real authorized wake command and captures
  its real receipt. A runner seam exists ONLY for tests to intercept the
  live subprocess boundary (production always passes the real runner).
- corrupt-after-worker is applied by run_case (artifact paths are
  tool-owned): after the worker claim shows completed, the artifact is
  tampered with before/after hashes recorded. The independent verifier
  check then fails honestly.

Fail-closed: ends resolved for witness must each trace to a delivery
record for (seat, execution); production without delivery is rejected
(E_UNDELIVERED) — a fabricated end/claim the candidate alone would accept
cannot pass this layer.
"""
from __future__ import annotations

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


def deliver_pending(outbox_dir, inbox_dir, intervention, live_wake=None,
                    runner=None, hold_delay_s=HOLD_DELAY_S):
    """One delivery pass over deposited texts. Returns applied records.
    live_wake=None selects the injected inbox-copy branch; a live wake
    path selects real seat notification. Pure file+record behavior either
    way; no transport states are invented here."""
    import glob as _g
    applied = []
    control = (intervention or {}).get("control", "none-declared")
    case = (intervention or {}).get("case", "")
    for path in sorted(_g.glob(os.path.join(outbox_dir, "send-*.json"))):
        try:
            dep = json.load(open(path))
        except ValueError:
            continue
        if dep.get("_delivered"):
            continue
        seat = dep.get("seat", "")
        env = _decode_text_content(dep.get("text", ""))
        action, execution = env.get("action"), env.get("execution")
        is_verifier = "verifier" in seat
        is_first_worker = (not is_verifier and not any(
            a.get("delivered_at") for a in applied))
        held = False
        if control == "hold-verifier-texts" and is_verifier:
            held = True
        delivered_at = None
        transport_ref = None
        if not held:
            if control == "transport-queued-first" and is_first_worker:
                time.sleep(hold_delay_s)  # bounded induced interruption
            if live_wake is None:
                os.makedirs(inbox_dir, exist_ok=True)
                dest = os.path.join(inbox_dir, "to-%s-%s.txt" % (
                    seat, _now_z().replace(":", "")))
                shutil.copy(path, dest)
                delivered_at = _now_z()
            else:
                run = runner or subprocess.run
                proc = run([live_wake, seat, dep.get("text", "")],
                           capture_output=True, text=True, timeout=60)
                transport_ref = ((proc.stdout or "").strip().splitlines()
                                 or [""]) [-1][:200]
                if proc.returncode not in (0, 3):
                    raise ControlFault("E_DELIVER",
                                       "live wake rc%d for %s" % (
                                           proc.returncode, seat))
                delivered_at = _now_z()
        rec = {"case": case, "action": action, "execution": execution,
               "seat": seat, "deposited_at": dep.get("received_at"),
               "delivered_at": delivered_at, "held": held,
               "induced": control != "none-declared",
               "control": control,
               "transport_ref": transport_ref}
        applied.append(rec)
        dep["_delivered"] = rec
        with open(path, "w") as fh:
            json.dump(dep, fh, sort_keys=True)
    return applied


def _decode_text_content(text):
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


def apply_artifact_control(art_dir, intervention):
    """Tool-owned artifact tamper for corrupt-after-worker. Returns
    {path, before_sha256, after_sha256} or None. Caller must invoke only
    after observing worker commit."""
    import glob as _g
    import hashlib as _hl
    if (intervention or {}).get("control") != "corrupt-after-worker":
        return None
    targets = sorted(_g.glob(os.path.join(art_dir, "*")))
    if not targets:
        raise ControlFault("E_APPLY",
                           "no artifact present to apply control to")
    path = targets[0]
    with open(path, "rb") as fh:
        before = _hl.sha256(fh.read()).hexdigest()
    with open(path, "wb") as fh:
        fh.write(b"tampered-by-fixture-control")
    with open(path, "rb") as fh:
        after = _hl.sha256(fh.read()).hexdigest()
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
