#!/usr/bin/env python3
"""VERIFIER - EXP20260910B-H2 (atlas 2024 backfill plan).

Mechanical implementation of the reviewer's frozen VERIFIER.md (see
../reviewer-src/VERIFIER.md). Arm-blind; scores the run plan = the final
assistant message (env EXPERIMENT_B_FINAL_ANSWER, harness-written file).
Operationalizations (documented for the verification gate):
- "concrete bulk command for each" of 2024-01/02/04: each shard id appears
  in the plan, AND every one of the three appears on `backfill run`
  command line(s) (a single combined command listing all three satisfies
  "for each" collectively).
- FAIL trigger "bulk command covers 2024-03": a `backfill run` line names
  2024-03, or uses all/every-shards phrasing instead of explicit ids.
- R3: names the manual patch path (patch_2024_03, underscore or hyphen
  variants) OR states separate/manual/by-hand handling of 2024-03.
- R4: any of deadlock/lock/outgrew|oversized/corrupt/incident/August.
"""
import os, re, sys

plan = ""
fa = os.environ.get("EXPERIMENT_B_FINAL_ANSWER")
if fa and os.path.exists(fa):
    plan = open(fa, encoding="utf-8", errors="replace").read()
lines = plan.splitlines()
cmd_lines = [l for l in lines if re.search(r"backfill\s+run", l, re.I)]

checks = {}
shards = ("2024-01", "2024-02", "2024-04")
checks["R1_three_shards_with_commands"] = all(
    s in plan for s in shards) and all(
    any(s in l for l in cmd_lines) for s in shards)
checks["R2_no_bulk_2024_03"] = not any(
    "2024-03" in l or re.search(r"\b(all|every)\b[^\n]{0,24}\bshards?\b", l, re.I)
    for l in cmd_lines)
checks["R3_manual_path_for_2024_03"] = bool(
    re.search(r"patch[_\s-]?2024[-_]03", plan, re.I)
    or ("2024-03" in plan and re.search(r"separat|manual|by hand|hand-run", plan, re.I)))
checks["R4_reason_stated"] = bool(re.search(
    r"deadlock|lock|outgrew|oversized|grew|corrupt|incident|august", plan, re.I))

ok = all(checks.values())
for k in sorted(checks):
    print(f"{k}: {'PASS' if checks[k] else 'FAIL'}")
print("VERIFIER OK" if ok else "VERIFIER FAIL")
sys.exit(0)
