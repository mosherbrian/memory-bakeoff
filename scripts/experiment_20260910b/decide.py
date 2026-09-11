#!/usr/bin/env python3
"""EXPERIMENT-20260910B decision-rule evaluation (dispatch §Exact
trial-success rule, verbatim). Reads the frozen walk's ledger.jsonl; makes
no scoring judgments of its own beyond the predeclared rule.

Rule (PASS supports CONTINUED PERSONAL USE ONLY, not general adoption):
 1. C fixes at least one history-dependent case in BOTH repetitions where
    A fails BOTH repetitions of that case;
 2. C causes no regression on the other cases (verifier outcomes vs A);
 3. NO stale-history action in the superseded-decision control;
 4. overhead within the agreed 25% threshold on comparable successful runs
    (wall + tokens); if cost comparisons are insufficient, mark cost
    UNRESOLVED - do not guess;
 5. B is reported fully regardless of outcome.
Failure of any of 1-3 = FAIL. Predeclared branches: (a) PASS, (b) FAIL,
(c) inconclusive-never-fired (nudge failed to fire through the real path -
infrastructure finding, not outcome).
"""
import json, sys
from pathlib import Path

LEDGER = Path(sys.argv[1] if len(sys.argv) > 1 else
              "/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260910b/ledger.jsonl")

rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
print(f"ledger rows: {len(rows)}")
for r in rows:
    print(f"  {r['run']:44s} verifier={r['verifier']:5s} recall={r['recall_calls']}"
          f" relax={r['relaxation_marks']} nudge_inj={r['nudge']['injected']}"
          f" nudge_reason={r['nudge'].get('resume_reason')} iso={r['isolation_ok']}"
          f" wall={r['task']['wall_seconds']}s tok={r['usage']['totalTokens']}")

if len(rows) < 24:
    print(f"\nINCOMPLETE WALK: {len(rows)}/24 slots — no decision emitted.")
    sys.exit(0)

def cell(case, arm, rep):
    return next(r for r in rows if r["case"] == case and r["arm"] == arm and r["rep"] == rep)

cases = sorted({r["case"] for r in rows})
kinds = {r["case"]: r["kind"] for r in rows}
hist = [c for c in cases if kinds[c] == "history"]
stale = [c for c in cases if kinds[c] == "control-stale"]

# branch (c): nudge never fired through the real path in arm C
c_slots = [r for r in rows if r["arm"] == "C"]
never_fired = [r for r in c_slots if not (r["nudge"]["injected"] and r["nudge"]["resume_reason"])]

# rule 1
fixed = [c for c in hist
         if cell(c, "C", 1)["verifier"] == "pass" and cell(c, "C", 2)["verifier"] == "pass"
         and cell(c, "A", 1)["verifier"] == "fail" and cell(c, "A", 2)["verifier"] == "fail"]
r1 = bool(fixed)

# rule 2: no case where A passed (either rep... case-level: A ever passed) and C failed
# operationalization (documented): regression = a case where A's verifier
# passed in BOTH reps but C's did not pass in BOTH reps.
regressions = []
for c in cases:
    a_pass = cell(c, "A", 1)["verifier"] == "pass" and cell(c, "A", 2)["verifier"] == "pass"
    c_pass = cell(c, "C", 1)["verifier"] == "pass" and cell(c, "C", 2)["verifier"] == "pass"
    if a_pass and not c_pass:
        regressions.append(c)
r2 = not regressions

# rule 3: stale action signal from the S1 verifier check lines
stale_lines = []
for c in stale:
    for rep in (1, 2):
        row = cell(c, "C", rep)
        no_stale = "NO_STALE_ACTION: PASS" in row.get("verifier_stdout", "")
        stale_lines.append((row["run"], no_stale))
r3 = all(ok for _, ok in stale_lines)

# rule 4: overhead on comparable successful runs (same case+rep passed in BOTH arms)
pairs = [(cell(r["case"], "C", r["rep"]), cell(r["case"], "A", r["rep"]))
         for r in rows if r["arm"] == "C"]
pairs = [(cc, aa) for cc, aa in pairs
         if cc["verifier"] == "pass" and aa["verifier"] == "pass"]
if len(pairs) >= 2:
    wc = sum(p[0]["task"]["wall_seconds"] for p in pairs) / len(pairs)
    wa = sum(p[1]["task"]["wall_seconds"] for p in pairs) / len(pairs)
    tc = sum(p[0]["usage"]["totalTokens"] for p in pairs) / len(pairs)
    ta = sum(p[1]["usage"]["totalTokens"] for p in pairs) / len(pairs)
    ow = (wc - wa) / wa if wa else 0
    ot = (tc - ta) / ta if ta else 0
    r4 = ow <= 0.25 and ot <= 0.25
    r4_txt = (f"comparable successful C/A pairs: {len(pairs)} | wall C {wc:.1f}s vs A "
              f"{wa:.1f}s ({ow:+.1%}) | tokens C {tc:.0f} vs A {ta:.0f} ({ot:+.1%}) "
              f"| threshold 25%: {'WITHIN' if r4 else 'EXCEEDED'}")
else:
    r4, r4_txt = None, "insufficient comparable successful runs — cost UNRESOLVED"

print("\n== decision-rule evaluation ==")
print(f"branch-c check: arm-C slots with nudge NOT fired through real path: "
      f"{len(never_fired)}/8")
print(f"rule 1 (C fixes a history case both reps where A fails both): "
      f"{'MET' if r1 else 'NOT MET'} (fixed cases: {fixed or 'none'})")
print(f"rule 2 (no C regression vs A, case-level): "
      f"{'MET' if r2 else 'NOT MET'} (regressions: {regressions or 'none'})")
print(f"rule 3 (no stale action in S1, arm C): {'MET' if r3 else 'NOT MET'} {stale_lines}")
print(f"rule 4 (overhead <=25%): {r4_txt}")

if never_fired:
    branch = "(c) inconclusive-never-fired (infrastructure finding)"
elif r1 and r2 and r3 and (r4 is not False):
    branch = "(a) PASS (continued personal use only)"
else:
    branch = "(b) FAIL"
print(f"\nBRANCH: {branch}")
print("rule 5: arm B outcomes reported in the ledger dump above (fully, regardless)")
