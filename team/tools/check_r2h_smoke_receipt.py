#!/usr/bin/env python3
"""Verify Brian's R2H day-0 smoke receipt, so the go-ahead is mechanical.

WHY. Brian, 2026-09-17: "I have the first smoke test json that the runbook tells
me I need to send back to the fleet. The fleet asked me to do this 2-3 days ago
pre-furlough, and I have no idea if any of the current team even remembers this,
or who I should send it to."

Nobody did. `team/R2H-RUNBOOK.md` step 6 says "send back the one file it names
... Day 1 does not count until the fleet has verified that receipt. You will get
a one-word go-ahead", and it routes questions to GiLMore and the blind rating to
Verity - both furloughed on 2026-09-15, along with Assay who built the deploy
script and Alice who verified it. The obligation survived; every seat named in
it did not, and no QUEUE row carried it.

So the verification is a CHECK rather than a person. The hard gate is the same
conjunction r2h_deploy.py computes at line 197:

    pi_ran AND nudge_delivered AND recall_registered AND store_unmodified

and it is re-derived here from the receipt rather than trusting its own
`verdict` field - a receipt that reports its own verdict is the same shape as a
row that declares itself done. The three warnings (recall_invoked, store_named,
prior_id_surfaced) are NOT failures; the runbook and Assay's power check both
say so, and prior_id/store_named depend on query match.

Exit 0 = go-ahead, day 1 counts. Exit 1 = do not proceed, with the reason named.

  check_r2h_smoke_receipt.py [team/INTAKE/r2h-smoke-receipt.json]
  check_r2h_smoke_receipt.py --selftest
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Absolute on purpose: the declared check must mean the same thing from every
# seat. Path.home() resolved inside sandboxed worker seats, where the no-arg
# invocation gave a spurious [NOT-ARRIVED] rc 1 while the same invocation
# exited 0 canonically (kiln D-10 verify, 2026-09-17; same class as the
# check_plain_language DIR fix, CORVID-D-9-VERIFY).
DEFAULT = Path("/home/bmosher/memory-bake-off/team/INTAKE/r2h-smoke-receipt.json")
HARD = ("pi_ran", "nudge_delivered", "recall_registered", "store_unmodified")
WARN = ("recall_invoked", "store_named", "prior_id_surfaced")
SHA = re.compile(r"^[0-9a-f]{64}$")


def findings(rec):
    f = []
    checks = rec.get("checks")
    if not isinstance(checks, dict):
        return ["[NO-CHECKS] the receipt has no `checks` object - this is not an "
                "r2h smoke receipt, or it was edited"]
    for k in HARD:
        if k not in checks:
            f.append(f"[MISSING-CHECK] {k} is absent from the receipt")
        elif not checks[k]:
            f.append(f"[HARD-FAIL] {k} is false")
    # Re-derive rather than trust the receipt's own verdict.
    if all(checks.get(k) for k in HARD) and rec.get("verdict") != "PASS":
        f.append(f"[VERDICT-DISAGREES] every hard check passes but the receipt "
                 f"says {rec.get('verdict')!r}; the receipt was edited or the "
                 f"script differs from the one the fleet froze")
    if any(not checks.get(k) for k in HARD) and rec.get("verdict") == "PASS":
        f.append("[VERDICT-DISAGREES] the receipt claims PASS while a hard "
                 "check is false - do not accept its own verdict")
    # The store must be provably untouched, not merely asserted.
    pre, post = rec.get("store_sha_pre"), rec.get("store_sha_post")
    if not (isinstance(pre, str) and SHA.match(pre or "")):
        f.append("[NO-STORE-HASH] store_sha_pre is not a sha256 - the read-only "
                 "promise is unverifiable")
    elif pre != post:
        f.append(f"[STORE-MODIFIED] the store hash changed during the smoke run "
                 f"({pre[:12]}... -> {str(post)[:12]}...). The arm is supposed "
                 f"to be read-only; this is the failure the smoke exists to catch")
    if not rec.get("session_file"):
        f.append("[NO-SESSION] session_file is null, so nudge_delivered was "
                 "read from nothing")
    if not rec.get("ts"):
        f.append("[NO-TIMESTAMP] the receipt carries no ts, so day 0 cannot be "
                 "dated")
    return f


def selftest():
    good = {"verdict": "PASS", "ts": "2026-09-17T20:00:00+00:00",
            "session_file": "/x/s.jsonl", "store_sha_pre": "a" * 64,
            "store_sha_post": "a" * 64,
            "checks": {k: True for k in HARD + WARN}}
    if findings(good):
        print("selftest: FAIL - a good receipt was rejected: %s" % findings(good)[0])
        return 1
    warn_only = json.loads(json.dumps(good))
    for k in WARN:
        warn_only["checks"][k] = False
    if findings(warn_only):
        print("selftest: FAIL - warnings were treated as failures, which the "
              "runbook forbids")
        return 1
    cases = {}
    for k in HARD:
        c = json.loads(json.dumps(good))
        c["checks"][k] = False
        c["verdict"] = "FAIL"
        cases[f"hard {k} false"] = ("HARD-FAIL", c)
    c = json.loads(json.dumps(good)); c["store_sha_post"] = "b" * 64
    c["checks"]["store_unmodified"] = True                 # lying receipt
    cases["store hash changed but check says unmodified"] = ("STORE-MODIFIED", c)
    c = json.loads(json.dumps(good)); c["checks"]["pi_ran"] = False
    cases["claims PASS with a hard check false"] = ("VERDICT-DISAGREES", c)
    c = json.loads(json.dumps(good)); c["session_file"] = None
    cases["no session file"] = ("NO-SESSION", c)
    for name, (marker, rec) in cases.items():
        got = findings(rec)
        if not any(marker in g for g in got):
            print(f"selftest: FAIL - {name} was ACCEPTED (wanted {marker})")
            return 1
    print("selftest: PASS (a good receipt accepted, warnings ignored as the "
          "runbook requires, and each hard failure, a lying store hash, a "
          "disagreeing verdict and a missing session file rejected by name)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt", nargs="?", default=str(DEFAULT))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    p = Path(a.receipt)
    try:
        rec = json.loads(p.read_text())
    except OSError:
        print(f"[NOT-ARRIVED] {p} does not exist yet - Brian has not dropped the "
              f"receipt, or it went somewhere else")
        return 1
    except json.JSONDecodeError as exc:
        print(f"[NOT-JSON] {p}: {exc}")
        return 1
    f = findings(rec)
    for x in f:
        print(x)
    if f:
        print(f"\n{len(f)} problem(s). DO NOT give the go-ahead; day 1 must not "
              f"count. Tell Brian which check failed and what to re-run.")
        return 1
    warned = [k for k in WARN if not (rec.get("checks") or {}).get(k)]
    print("GO-AHEAD: every hard check passes and the store is provably "
          "unchanged. Day 1 counts.")
    if warned:
        print(f"  warnings, not blockers: {', '.join(warned)} - the runbook says "
              f"these depend on query match; report, do not retry.")
    print(f"  day 0 dated {rec.get('ts')}, store {str(rec.get('store'))[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
