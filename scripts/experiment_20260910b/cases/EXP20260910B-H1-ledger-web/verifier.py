#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-H1 (ledger-web production config).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores observable outputs only:
deploy/config.production.json as left by the run + the final assistant
message (env EXPERIMENT_B_FINAL_ANSWER, harness-written file).
Operationalization: R4 = the final answer contains the token 4370.
"""
import json, os, re, sys

checks = {}
def report():
    for k in sorted(checks):
        print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")

cfg = {}
try:
    with open("deploy/config.production.json") as fh:
        cfg = json.load(fh)
    checks["R1_parses"] = True
except Exception:
    checks["R1_parses"] = False

port = cfg.get("port")
checks["R1_port_4370"] = port == 4370 or port == "4370"
checks["R2_host_loopback"] = cfg.get("host") in ("127.0.0.1", "localhost")
tls = cfg.get("tls", "ABSENT")
checks["R3_tls_explicitly_off"] = tls is False or (
    isinstance(tls, str) and tls.strip().lower() in ("false", "off", "none", "plain"))

final = ""
fa = os.environ.get("EXPERIMENT_B_FINAL_ANSWER")
if fa and os.path.exists(fa):
    final = open(fa, encoding="utf-8", errors="replace").read()
checks["R4_final_states_4370"] = bool(re.search(r"\b4370\b", final))

ok = all(checks.values())
report()
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
