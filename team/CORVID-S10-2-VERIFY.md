# CORVID-S10-2-VERIFY — build verification of row S10-2

corvid-dsh, 2026-09-18 14:4x PDT. Verdict: **VERIFIED PASS** (with two stated
limits, §7–8). Row S10-2 ("Rank-aware retrieval diagnostics: surface the
rank-sensitive measures … into the sprint reporting path"), owner kiln-flash,
artifact `team/S9-RANK-DIAG/`. Gate S10-2G was verified by this seat 13:27 PDT
(`team/CORVID-S10-2G-VERIFY.md`); the gate is unchanged.

## 1. Gate

- `check.py` sha256 `1a5dc4397bf8d354d2d55454de584b80681101507b8dd1d2916b14e716828aa6`
  — identical to my 13:27 gate verification. Kiln's done stamp quotes the same
  value (re-computed at its close).
- Declared check re-run by me: rc 0, "S10-2 gate: clean (3 adapters, 6 cells;
  MRR and presence by metrics.score_case, nDCG recomputed; diag.py driven and
  rank-sensitive)".
- Mandatory `--selftest`: rc 0, PASS — conforming build accepted; receipts-only
  directory rejected; unreachable metrics.py rejected; 15 mutants each rejected
  by exactly their own markers; the swap probe moves MRR and nDCG and leaves
  presence; no traceback.

## 2. The build (all sha256 at 14:40 PDT)

| file | sha256 (16) | bytes |
|---|---|---|
| rankings.jsonl | `0076d264d9b3b7f0` | 30 rows |
| report.json | `248a8cb6bf238e01` | the tool's own output |
| diag.py | `196217842a242712` | reporting-path tool |
| make_rankings.py | `bb361626a0ab032f` | capture runner |
| design.md | `b6fe00a4cab46b90` | fixed before capture |

## 3. Independent recompute (numpy-free, my own code)

- All 12 cells (3 adapters × 2 conditions × {mrr, ndcg, presence}) recomputed
  from `rankings.jsonl` with my own harness calling the real
  `memory_bakeoff.metrics.score_case` plus my own binary-gain-log2 nDCG:
  **every value matches report.json to <1e-9.**
- `diag.py rankings.jsonl --k 5` executed by me in a clean env
  (PATH=/usr/bin + repo src on PYTHONPATH): rc 0, exactly one line of JSON,
  parsed content **equal to report.json's `per_adapter`** — report.json is the
  tool's own output, not hand-written numbers.

## 4. Capture integrity (checks the gate does not make)

- `relevant_ids` on all 30 rows == the S6-2 manifest's pre-run `helpful` map
  (`team/S6-SELECTIVITY/manifest.json`), verified by me directly.
- Every `ranked_ids` entry matches the store-id grammar
  (`<case>-r[1-4]` base, `<case>-tool-[00-09]` pressure); no duplicates; every
  list length within its adapter's declared top_k (bm25 1, pi_lcm 5,
  claude_mem 3).
- Consistency with verified priors, all four directions:
  - presence cells (bm25 1.0/1.0, pi_lcm 0.2/0.2, claude_mem 1.0/1.0) equal
    S8-DOOR's verified rung-1 presence cells;
  - the cited rank-move prior REPRODUCES: claude_mem sel-005 normal
    `[r1, r2, r4]` → pressure `[r2, r1, r4]` — the exact top-two swap my
    `CORVID-S8-7-VERIFY.md` recorded with presence and bytes unchanged;
  - claude_mem pressure sel-003 carries `sel-003-tool-01` in top-3 — a tool
    chunk genuinely entered a pressure-time ranking, so the regenerated load
    was really in the store;
  - kiln's byte-total claim holds: my receipt line 33 records
    "21,069–21,362 bytes (≥ the declared 20,000)" and S8-DOOR
    `results.jsonl` competing_bytes are exactly min 21069 / max 21362.
- Prior citations checked in the cited files: `RESEARCH-Q1.2-ISOLATION-RESULT.md`
  line 62 (k=5 metrics with MRR among the five), `COLDREAD-20260912-scoreboard.md`
  line 77 (R@20/MRR); nDCG absent from both, so the extension claim is true.
  S6-2 corpus pin `5a8668f7…` re-hashed by me — matches design.md.

## 5. The delegated call, made explicitly (reporting-path reach)

Kiln's claim handed me "sprint report actually calls diag.py" as my named
check; the verified gate's own limit defers the same question here. My call,
with the state as of 14:40 PDT:

- **Satisfied now:** the measures are surfaced as their own numbers —
  `python3 diag.py RANKINGS --k 5` works from a clean environment (I ran it),
  returns one parseable JSON line, and `report.json` renders
  {mrr, ndcg, presence} side by side per adapter/condition, matching the
  outline's "alongside evidence presence", never blended (no composite exists
  anywhere in the artifact — read, not assumed). The invocation is copyable
  from exactly two documented places (design.md's tool section, report.json's
  provenance). The outline's second Done-when clause — automatic examples
  showing order change moves the measures while presence stays — is
  demonstrated by the gate's swap probe and re-confirmed in today's selftest.
- **Pending, and stated so it cannot pass silently:** no sprint-close report
  embeds these cells yet — sprint 10 has not closed, and `SPRINT-9-DEMO.md`
  predates the tool, so nothing existing is defective by omission. The
  consumption obligation lands at sprint-10 close: the demo must call
  `diag.py` (or embed its cells). **If the sprint-10 demo ships without the
  ranking measures, this row's reporting-path reach fails retroactively** and
  should be reopened on that evidence.

## 6. What the capture means (substance, not file-counting)

The rankings re-derive a fact the delivery plane could only hint at:
under rung-1 pressure, presence is flat everywhere (1.00/1.00, 0.20/0.20,
1.00/1.00 — the door's result, reproduced from ids) while order MOVES
(sel-005's swap lifts claude_mem MRR 0.8 → 0.9 with presence pinned; a tool
chunk takes sel-003's #3). The synthetic claude_mem example in the row text is
now a measured one, with the two numbers separated exactly as the row demands.

## 7. Limits (stated on purpose)

- **Adapter stack not re-executed in this lane.** numpy is absent here
  (verified: `import numpy` → ModuleNotFoundError), same limit as my S10-1
  verification. I did not re-run the three adapters; I verified the capture's
  consistency with every pinned prior instead (§4). The capture ran on kiln's
  host through the imported rung-1 machinery, sha-bound by the gate's checks.
- `ranked_ids` are what the adapters returned at their declared top_k —
  the gate cannot see the adapters rank; neither can I re-derive them without
  the stack. The four prior-consistency checks in §4 are the compensation.

## 8. Owned defects (mine, not the build's)

- My first recompute harness parsed ids with `rsplit("-", 1)`, which mangles
  `sel-003-tool-01` into case `sel-003-tool` and raised a false failure on
  exactly the row that proves the load was real. Fixed by matching the id
  grammar explicitly (§4); the build was right, my parser was wrong.
- My first grep for the byte totals in my own S8-7 receipt used a bare
  `21[0-9]{4}` pattern and missed the figures because my receipt writes them
  as "21,069–21,362" (comma + en-dash). I nearly logged a false provenance
  defect against kiln's stamp; the figures were there all along.

## 9. Disposition

VERIFIED PASS. The row is honestly done: the gate is the verified gate, the
capture re-derives the priors it cites, the tool surfaces the measures as
separate numbers with a working documented invocation, and report.json is the
tool's own output, independently recomputed by this seat to <1e-9. Limits §7
and the sprint-close consumption obligation §5 are part of this verdict.
