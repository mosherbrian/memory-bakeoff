#!/usr/bin/env python3
"""EXPERIMENT-20260910C decision-rule evaluation (dispatch §Predeclared
decision rules, verbatim). Rules:
 1. PRIMARY: nudge-verify takes NO stale action on S1 in BOTH reps - no
    stale commands in deliverables AND the supersession evidence consulted
    in-stream.
 2. BENEFIT RETAINED: nudge-verify passes H1 in BOTH reps.
 3. NO NEW REGRESSION: nudge-verify passes N1 in BOTH reps.
 4. H2 descriptive only: frozen verifier + intent-analysis addendum
    (B-round artifact convention: prose-safe R2 recompute, labeled).
 5. Overhead within 25% on comparable successful runs; UNRESOLVED where
    comparisons are insufficient.
 6. nudge-orig rerun is the paired control: report whether it REPLICATES
    the B-round pattern (S1 fail/fail via stale action, H1 pass/pass).
PASS = rules 1-3 met and rule 5 within-or-unresolved.
"""
import json, re, sys
from pathlib import Path

PRIVATE = Path("/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260910c")
RUNS = PRIVATE / "runs"
rows = [json.loads(l) for l in (PRIVATE / "ledger.jsonl").read_text().splitlines() if l.strip()]

print(f"ledger rows: {len(rows)}")
for r in rows:
    print(f"  {r['run']:44s} verifier={r['verifier']:5s} recall={r['recall_calls']}"
          f" nudge={r['nudge']['injected']} iso={r['isolation_ok']}"
          f" supersession={r.get('supersession_consulted_in_stream')}"
          f" stale_deliv={r.get('stale_in_deliverables')}"
          f" wall={r['task']['wall_seconds']}s tok={r['usage']['totalTokens']}")

if len(rows) < 16:
    print(f"\nINCOMPLETE WALK: {len(rows)}/16 — no decision emitted.")
    sys.exit(0)

def cell(case_suffix, arm, rep):
    return next(r for r in rows if r["case"].endswith(case_suffix)
                and r["arm"] == arm and r["rep"] == rep)

def both(case_suffix, arm, field=None, pred=None):
    out = []
    for rep in (1, 2):
        r = cell(case_suffix, arm, rep)
        out.append(r if pred is None else pred(r))
    return out

# rule 1: no stale action on S1 in V, both reps
v_s1 = [cell("-S1-kitepay-api", "V", rep) for rep in (1, 2)]
r1 = all((not r["stale_in_deliverables"]) and r["supersession_consulted_in_stream"]
         for r in v_s1)
print("\n== decision-rule evaluation ==")
print(f"rule 1 PRIMARY (V: no stale action on S1 both reps + supersession consulted): "
      f"{'MET' if r1 else 'NOT MET'}")
for r in v_s1:
    print(f"   {r['run']}: stale_in_deliverables={r['stale_in_deliverables']}, "
          f"supersession_in_stream={r['supersession_consulted_in_stream']}, "
          f"frozen verifier={r['verifier']}")

# rule 2 / rule 3: frozen verifier
r2 = all(cell("-H1-ledger-web", "V", rep)["verifier"] == "pass" for rep in (1, 2))
r3 = all(cell("-N1-wrenfmt", "V", rep)["verifier"] == "pass" for rep in (1, 2))
print(f"rule 2 (V passes H1 both reps, frozen verifier): {'MET' if r2 else 'NOT MET'} "
      f"{[cell('-H1-ledger-web', 'V', rep)['verifier'] for rep in (1, 2)]}")
print(f"rule 3 (V passes N1 both reps, frozen verifier): {'MET' if r3 else 'NOT MET'} "
      f"{[cell('-N1-wrenfmt', 'V', rep)['verifier'] for rep in (1, 2)]}")

# rule 4: H2 descriptive — frozen verifier + prose-safe R2 intent recompute
def h2_intent(r):
    run_dir = RUNS / r["run"]
    fa = (run_dir / "final-answer.txt").read_text(errors="replace")
    cmd_lines = [l for l in fa.splitlines()
                 if re.search(r"backfill\s+run", l, re.I)
                 and re.search(r"^\s*[$#]|^\s*\./|`\s*\.?/?backfill|run\s+--shard", l, re.I)]
    bulk_ok = not any(("2024-03" in l and "patch" not in l) for l in cmd_lines)
    manual = bool(re.search(r"patch[_\s-]?2024[-_]03|separat|manual|by hand", fa, re.I))
    return bulk_ok and manual
for arm in ("O", "V"):
    froz = [cell("-H2-atlas-backfill", arm, rep)["verifier"] for rep in (1, 2)]
    intent = [h2_intent(cell("-H2-atlas-backfill", arm, rep)) for rep in (1, 2)]
    print(f"rule 4 (H2 descriptive, arm {arm}): frozen verifier={froz} | "
          f"intent-recompute (prose-safe, labeled addendum)={intent}")

# rule 5: overhead on comparable successful runs (V vs O, same case+rep, both pass)
pairs = [(cell(r["case"].split("EXP20260910B-")[1], "V", r["rep"]),
          cell(r["case"].split("EXP20260910B-")[1], "O", r["rep"]))
         for r in rows if r["arm"] == "V"]
pairs = [(v, o) for v, o in pairs if v["verifier"] == "pass" and o["verifier"] == "pass"]
if len(pairs) >= 2:
    wv = sum(v["task"]["wall_seconds"] for v, _ in pairs) / len(pairs)
    wo = sum(o["task"]["wall_seconds"] for _, o in pairs) / len(pairs)
    tv = sum(v["usage"]["totalTokens"] for v, _ in pairs) / len(pairs)
    to = sum(o["usage"]["totalTokens"] for _, o in pairs) / len(pairs)
    r5 = ((wv - wo) / wo if wo else 0) <= 0.25 and ((tv - to) / to if to else 0) <= 0.25
    r5_txt = (f"{len(pairs)} comparable pairs | wall V {wv:.1f}s vs O {wo:.1f}s "
              f"({(wv - wo) / wo if wo else 0:+.1%}) | tokens V {tv:.0f} vs O {to:.0f} "
              f"({(tv - to) / to if to else 0:+.1%}) | {'WITHIN' if r5 else 'EXCEEDED'}")
else:
    r5, r5_txt = None, "insufficient comparable successful runs — UNRESOLVED"
print(f"rule 5 (overhead ≤25% V vs O): {r5_txt}")

# rule 6: does nudge-orig replicate the B-round arm-C pattern?
o_s1 = [cell("-S1-kitepay-api", "O", rep) for rep in (1, 2)]
o_h1 = [cell("-H1-ledger-web", "O", rep)["verifier"] for rep in (1, 2)]
replicated = (all(r["verifier"] == "fail" and r["stale_in_deliverables"] for r in o_s1)
              and o_h1 == ["pass", "pass"])
print(f"rule 6 (nudge-orig replicates B-round pattern S1 stale fail/fail + H1 pass/pass): "
      f"{'REPLICATED' if replicated else 'REPLICATION FAILURE (a finding - reported, not explained away)'}")
for r in o_s1:
    print(f"   {r['run']}: verifier={r['verifier']}, stale_in_deliverables="
          f"{r['stale_in_deliverables']}, supersession_in_stream="
          f"{r['supersession_consulted_in_stream']}")
print(f"   O H1 frozen verifier: {o_h1}")

verdict = "PASS" if (r1 and r2 and r3 and (r5 is not False)) else "FAIL/park"
print(f"\nC-ROUND VERDICT: {verdict}")
if verdict == "PASS":
    print("=> mitigated nudge is a CANDIDATE for the extension default nudge text "
          "(separate review + sign-off required) and for Brian's trial config")
