# corvid-dsh verification receipt — QUEUE row S10-2G

- **Row:** S10-2G — write the check for row S10-2 from row text alone, before
  the artifact exists; `--selftest` mandatory; exit contract per
  `team/tools/check_checker_exit_contracts.py`.
- **Artifact:** `team/S9-RANK-DIAG/check.py` (gate for build row S10-2,
  rank-aware retrieval diagnostics), owned by plumb-fable, batch-dispatched by
  cairn 13:00 PDT, landed 13:07.
- **Verdict: VERIFIED PASS**, 2026-09-18 13:27 PDT (clock read at write).
- **Gate sha256:** `1a5dc4397bf8d354d2d55454de584b80681101507b8dd1d2916b14e716828aa6`
  (read 13:16 pre-verification and re-read 13:27 at receipt time; identical).

## Independence

I am the row's named verifier and did not author the gate. Order held: kiln's
12:59 hold note on S10-2 records `team/S9-RANK-DIAG/` did not exist at
gate-dispatch time; the directory's first content is the 13:07 gate; the build
still has not started (bare gate run at 13:16 found only the gate). The gate
read, per its own header, only the board row and `metrics.py` — which the row
itself names as the prior/source handle — so "from row text alone" is not
violated by that read.

## Behavioral checks (all run live)

1. **Bare pre-build run** (`python3 check.py`): rc 1, findings exactly
   `[MISSING-FILE]` x3 (`rankings.jsonl`, `diag.py`, `report.json`), the line
   `S10-2 gate findings: 3`, no traceback.
2. **`--selftest`:** rc 0 — a conforming build accepted; a receipts-only
   directory, an unreachable `metrics.py` and 15 mutants each rejected by
   exactly their own declared markers (no marker spam, exact-set assertion in
   the selftest itself); no traceback.
3. **Exit contract:** the contract shape (0 clean / 1 with named markers and
   the findings line / `GATE-ERROR` catch-all converting any exception into a
   finding) is implemented and was exercised on the rc-1 and rc-0 paths. The
   contract tool's own covered-set registry does not yet list this gate —
   extending that registry to the S* gates is exactly build row S10-3's
   declared work, so its absence is not a defect of this gate.

## Source read (substance, not file counting)

- SURFACED, not re-derived: the gate recomputes MRR and presence by importing
  the repo's real `memory_bakeoff.metrics.score_case` and requires `diag.py`
  to import it (`METRICS-REDERIVED`), then drives `diag.py` as a subprocess
  with the repo source on PYTHONPATH (`DIAG-BROKEN`).
- Recomputation faithful to the repo: the gate's positional construction
  `QueryCase(case_id, category, "", relevant_ids)` matches the dataclass field
  order; positives-only filtering matches `aggregate`'s semantics;
  `score_case` truncates to k before reciprocal rank, as the gate assumes.
- nDCG extension: recomputed by the one declared binary-gain-log2 definition;
  `report.json` must declare `ndcg_definition` (`NDCG-UNDECLARED`).
- Its own number, never blended: every cell must carry mrr, ndcg, presence
  (`NUMBER-MISSING`); a BLEND scan over cell keys and report top-level keys
  catches folded scores (`BLENDED-SCORE`); reported numbers must equal the
  recomputation (`NUMBERS-DISAGREE`) and the report must be what diag.py
  prints (`DIAG-DISAGREES`).
- Rank-sensitive, by construction: the gate writes its own probe (same
  records, top two swapped — the row's cited claude_mem sel-005 evidence) and
  requires equal presence with lower MRR and nDCG on the swapped arm
  (`DIAG-BLIND-TO-RANK`). A tool reporting presence under another name fails
  here; the selftest contains exactly that mutant.
- Prior cited per the re-measurement rule: `report.json` prior must name
  `metrics.py` AND one of the row's two named earlier reports
  (`PRIOR-NOT-CITED`).
- Enough to read: >=1 adapter, >=5 positive cases per cell (`TOO-FEW-CASES`),
  one row per adapter/condition/case (`RANKING-DUPLICATED`), schema and
  bad-JSON handled (`SCHEMA`, `BAD-JSON`), no LLM/network in build code
  (`LLM-OR-NETWORK`).
- Stated limits are honest and match the row: ranked_ids are what the build
  wrote down; whether a given sprint report actually calls the tool stays
  with the verifier at build review.

## Not-fitted proof (independent of the gate's selftest)

`/tmp/s10-2g-verify/notfitted.py` — my own conforming fixture in a domain the
gate never saw: cache-eviction adapters `lru`/`arc`, conditions
`warm`/`cold`, page-request cases, k=4, one negative per cell, with my own
`diag.py` written from the gate's declared interface docstring (not copied
from its selftest), and `report.json` produced by running MY diag on MY
rankings (the honest "report comes from the tool" construction).

- Conforming fixture: **accepted, rc 0**.
- 20 dirty variants of my own construction: each rejected with rc 1 by
  exactly its named markers. Three are constructions the gate's own selftest
  does not contain: reciprocal-rank mis-scaling (caught by the recomputation
  plus the swap probe), a phantom adapter in the report (caught by
  NUMBERS-DISAGREE + DIAG-DISAGREES), an all-negative board (caught by
  TOO-FEW-CASES + NUMBER-MISSING).
- Result: **NOT-FITTED-PROOF-PASS (21/21 cases: 1 conforming + 20 dirty)**.

## Defects found — all mine, all in my harness, none in the gate

1. First run: five false FAILs because my case() compared the gate's
   sorted marker output against my unsorted expected lists. The gate fired
   the right markers on all five; my comparison was too literal. Fixed mine;
   the corrected harness then passed all 21 cases unchanged in the gate.
2. Two expected-marker sets I first derived were wrong against the gate's
   control flow: the mis-scaled-reciprocal-rank mutant cannot produce
   DIAG-DISAGREES (the gate re-runs the same broken diag, so report and
   output agree — only the swap probe catches it), and the crash mutant
   accumulates four markers before its early return. I corrected my
   expectations from the gate's actual flow, not to fit a green light: the
   corrected sets are what the flow deterministically produces.

## Disposition

S10-2G **done: VERIFIED PASS**. Build row S10-2 is kiln-flash's to start.
At build verification I will additionally check that the declared load
genuinely surfaces the repo's measures into the sprint reporting path (the
gate checks the tool is rank-sensitive, not that a report calls it — the
gate's own stated limit).
