#!/usr/bin/env python3
"""STUDY-20260911-P1 decision-rule evaluation (dispatch §Success = mechanism
AND practical, planner's four, verbatim):

 1. C retrieves the applicable replacement without presenting the
    superseded instruction as current, while preserving valid
    differently-scoped records.
 2. C prevents a stale-action failure observed in B.
 3. C improves >=1 history-dependent case over A in BOTH repetitions, no
    regression elsewhere.
 4. Runtime and token overhead within 25% where comparable successful pairs
    exist; insufficient comparisons remain UNRESOLVED (stated, never guessed).

Predeclared branches: (i) B never exhibits the failure -> study CANNOT
establish prevention (reported as such, not as success); (ii) C suppresses
stale records but fails the task -> retrieval success WITHOUT workflow
success (distinct outcome); (a) PASS / (b) FAIL / (c) inconclusive-never-
fired (nudge/infrastructure), per prior-round conventions.

Operationalizations (documented for the reviewer):
- Rule 1 retrieval evidence: per C slot, which vault record KEYS surfaced
  in the run's event stream (the adapter's formatted output carries
  `key=record-...`). P1-2/P1-3 C: d2-current surfaced, c1 (deprecated D1)
  NOT surfaced; P1-3 C: d1-staging ALSO surfaced (scope preservation);
  P1-1 C: c1 (still-current D1) surfaced.
- Rule 2 'stale-action failure observed in B': B's frozen verifier FAIL on
  P1-2 in >=1 rep (P1-2 is the stale-action case).
- Rule 3 'history-dependent': P1-1 and P1-3 (their deciding information is
  seed-only for at least one scored value); 'improves over A' = C passes
  both reps where A fails both; 'no regression elsewhere' = no case where
  A passed both reps and C did not.
- Rule 4: both comparators reported - C vs B (cost of supersession) and
  C vs A (cost of recall vs baseline) on same case+rep successful pairs.
"""
import json, os, re, sys
from pathlib import Path

# P1B rerun: same frozen decision logic; the evidence dir is overridable so
# this script can evaluate the p1b ledger (EXPERIMENT_P1_PRIVATE convention
# used by run_p1.py). Default remains the original p1 walk.
PRIVATE = Path(os.environ.get(
    "EXPERIMENT_P1_PRIVATE",
    "/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260911-p1"))
RUNS = PRIVATE / "runs"
rows = [json.loads(l) for l in (PRIVATE / "ledger.jsonl").read_text().splitlines() if l.strip()]

print(f"ledger rows: {len(rows)}")
for r in rows:
    print(f"  {r['run']:40s} verifier={r['verifier']:5s} recall={r['recall_calls']}"
          f" nudge={r['nudge']['injected']} vault_iso={r['vault_isolation_ok']}"
          f" wall={r['task']['wall_seconds']}s tok={r['usage']['totalTokens']}")
    if not r["vault_isolation_ok"]:
        print("      VAULT NOTES:", r["vault_isolation_notes"])

if len(rows) < 24:
    print(f"\nINCOMPLETE WALK: {len(rows)}/24 - no decision emitted.")
    sys.exit(0)

def cell(case, arm, rep):
    return next(r for r in rows if r["case"] == case and r["arm"] == arm and r["rep"] == rep)

def keys_surfaced(r):
    txt = (Path(RUNS) / r["run"] / "stdout.txt").read_text(errors="replace")
    return sorted(set(re.findall(r"key=(record-[a-z0-9\-]+)", txt)))

print("\n== retrieval evidence (vault keys surfaced per B/C slot) ==")
for r in rows:
    if r["arm"] in ("B", "C"):
        print(f"  {r['run']}: {keys_surfaced(r)}")

# rule 1
r1_detail, r1 = [], True
for rep in (1, 2):
    c2 = cell("P1-2-quarryline-ci", "C", rep)
    k = set(keys_surfaced(c2))
    ok2 = "record-p2-d2-current" in k and "record-p2-c1" not in k
    r1_detail.append(f"P1-2 C rep{rep}: d2 surfaced={'record-p2-d2-current' in k}, "
                     f"deprecated D1 surfaced={'record-p2-c1' in k} -> {ok2}")
    r1 = r1 and ok2
for rep in (1, 2):
    c3 = cell("P1-3-gullwing-deploy", "C", rep)
    k = set(keys_surfaced(c3))
    ok3 = ("record-p3-d2-current" in k and "record-p3-c1" not in k
           and "record-p3-d1-staging" in k)
    r1_detail.append(f"P1-3 C rep{rep}: d2={'record-p3-d2-current' in k}, "
                     f"deprecated D1={'record-p3-c1' in k}, staging preserved="
                     f"{'record-p3-d1-staging' in k} -> {ok3}")
    r1 = r1 and ok3
for rep in (1, 2):
    c1 = cell("P1-1-tessellate-export", "C", rep)
    k = set(keys_surfaced(c1))
    ok1 = "record-p1-c1" in k
    r1_detail.append(f"P1-1 C rep{rep}: current D1 surfaced={ok1}")
    r1 = r1 and ok1

# rule 2
b_p2 = [cell("P1-2-quarryline-ci", "B", rep)["verifier"] for rep in (1, 2)]
b_exhibits = "fail" in b_p2
c_p2 = [cell("P1-2-quarryline-ci", "C", rep)["verifier"] for rep in (1, 2)]
branch_i = not b_exhibits
r2 = b_exhibits and c_p2 == ["pass", "pass"]

# branch (ii): C suppresses stale (rule 1 retrieval evidence) but fails tasks
c_suppress = r1
c_all_pass = all(cell(c, "C", rep)["verifier"] == "pass"
                 for c in sorted({r["case"] for r in rows}) for rep in (1, 2))
branch_ii = c_suppress and not c_all_pass

# rule 3
hist = ["P1-1-tessellate-export", "P1-3-gullwing-deploy"]
improved = [c for c in hist
            if cell(c, "C", 1)["verifier"] == "pass" and cell(c, "C", 2)["verifier"] == "pass"
            and cell(c, "A", 1)["verifier"] == "fail" and cell(c, "A", 2)["verifier"] == "fail"]
regressions = [c for c in sorted({r["case"] for r in rows})
               if all(cell(c, "A", rep)["verifier"] == "pass" for rep in (1, 2))
               and not all(cell(c, "C", rep)["verifier"] == "pass" for rep in (1, 2))]
r3 = bool(improved) and not regressions

# rule 4 (both comparators; pairs = same case+rep both passed)
def overhead(x, y):
    pairs = [(cell(r["case"], x, r["rep"]), cell(r["case"], y, r["rep"]))
             for r in rows if r["arm"] == x]
    pairs = [(a, b) for a, b in pairs
             if a["verifier"] == "pass" and b["verifier"] == "pass"]
    if len(pairs) < 2:
        return None, f"{x} vs {y}: {len(pairs)} comparable successful pairs - UNRESOLVED"
    wa = sum(p[0]["task"]["wall_seconds"] for p in pairs) / len(pairs)
    wb = sum(p[1]["task"]["wall_seconds"] for p in pairs) / len(pairs)
    ta = sum(p[0]["usage"]["totalTokens"] for p in pairs) / len(pairs)
    tb = sum(p[1]["usage"]["totalTokens"] for p in pairs) / len(pairs)
    ow = (wa - wb) / wb if wb else 0
    ot = (ta - tb) / tb if tb else 0
    ok = ow <= 0.25 and ot <= 0.25
    return ok, (f"{x} vs {y}: {len(pairs)} pairs | wall {wa:.1f}s vs {wb:.1f}s ({ow:+.1%}) "
                f"| tokens {ta:.0f} vs {tb:.0f} ({ot:+.1%}) | "
                f"{'WITHIN' if ok else 'EXCEEDED'}")

r4_cb, txt_cb = overhead("C", "B")
r4_ca, txt_ca = overhead("C", "A")

# branch (c): infrastructure
c_never_fired = [r["run"] for r in rows if r["arm"] in ("B", "C")
                 and not (r["nudge"]["injected"] and r["nudge"].get("resume_reason"))]

print("\n== decision-rule evaluation ==")
for d in r1_detail:
    print(" ", d)
print(f"rule 1 (C retrieves replacement, no superseded-as-current, scope preserved): "
      f"{'MET' if r1 else 'NOT MET'}")
print(f"rule 2 (C prevents stale-action failure observed in B): "
      f"{'MET' if r2 else 'NOT MET'} (B P1-2: {b_p2}; C P1-2: {c_p2})")
print(f"rule 3 (C improves >=1 history case over A both reps, no regression): "
      f"{'MET' if r3 else 'NOT MET'} (improved: {improved or 'none'}; "
      f"regressions: {regressions or 'none'})")
print(f"rule 4 (overhead <=25%): {txt_cb} | {txt_ca}")
print(f"branch-c check (nudge not fired through real path): {len(c_never_fired)}/16 "
      f"{c_never_fired or ''}")
if branch_i:
    print("BRANCH (i): B never exhibited the stale-action failure - study CANNOT "
          "establish prevention (reported as such)")
elif branch_ii:
    print("BRANCH (ii): retrieval success WITHOUT workflow success (C suppresses "
          "stale but fails tasks) - distinct outcome")
elif c_never_fired:
    print("BRANCH (c): inconclusive-never-fired (infrastructure finding)")
elif r1 and r2 and r3 and (r4_cb is not False) and (r4_ca is not False):
    print("VERDICT: (a) PASS - mechanism AND practical")
else:
    print("VERDICT: (b) FAIL")

print("\nfull arm tables:")
for arm in ("A", "B", "C"):
    tab = {c.split("-")[0] + c.split("-")[1]: [cell(c, arm, rep)["verifier"] for rep in (1, 2)]
           for c in sorted({r["case"] for r in rows})}
    print(f"  arm {arm}: {tab}")
