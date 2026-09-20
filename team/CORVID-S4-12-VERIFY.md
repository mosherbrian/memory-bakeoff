# CORVID-S4-12-VERIFY.md — corvid-dsh verification of QUEUE row S4-12

**Verdict: PASS** — 2026-09-16 13:44 PDT. kiln-flash authored the run, summary,
and check; corvid-dsh verifies (independence holds).

## Declared check

`python3 team/s4-12-crossengine/check_s4_12.py` → `0 findings`, rc 0. The check
is substantive, not a rubber stamp: it re-hashes the frozen corpus v3 and the
pinned trigger `index.ts` on disk against the cited shas, gates every engine
summary on corpus sha + trigger commit + engine pins, compares determinism
re-run tuples for both controlled_core engines, and asserts the control dirs
exist and do not collide with engine dirs.

## Independent recomputation from raw fire logs (not from the summary)

All headline claims reproduced from `results-*/results.jsonl` and
`topics-derivation.jsonl` this pass:

| Claim (summary v1) | Recomputed | Match |
|---|---|---|
| bm25 FBMR_topic 25/30, misses T001/T003/T005/T007/T009 | 25/30, identical miss set (all env_fact) | ✓ |
| controlled_core FBMR 0/30 both engines (honest zero) | 0/30 both | ✓ |
| FalseFire (plain fillers, excl. fresh) 0/60 all arms | raw filler_plain fires 60/60 but every one is `reasons=["fresh"]` at turn 1 → 0/60 as published | ✓ |
| NearMissFire 20/24 bm25; 0/24 controlled | 20/24; 0/24 | ✓ |
| stale/anachronism fillers 0 fires every arm | 0/36 per arm | ✓ |
| F3 entity-echo offtopic 5/30 bm25 (T022–T030 even), 0/30 controlled | 5/30, exactly T022/T024/T026/T028/T030; 0/30 both controlled | ✓ |
| derivation surface non-empty 47/60 bm25; 0/60 controlled | 47/60; 0/60; 0/60 | ✓ |
| determinism spot-checks 9/9 invariant tuples identical, both engines | 9 vs 9, identical, both | ✓ |
| controls separate: never 0/180, always 134/180 | 0/180; 134/180 | ✓ |

## Contract compliance (repo evaluation rules)

- `controlled_core` (claude_mem_fts5_core, pi_lcm_store_reader) kept distinct
  from the `baseline` bm25 context arm throughout; bm25 explicitly not counted
  toward the ≥2. Direct arm cited as S4-10 frozen reference, not a new run.
- Scoring is programmatic from fire logs via the frozen S4-10 harness's
  `metrics()`; no model self-report, no score import.
- Provenance pins recorded and machine-verified: corpus v3 sha, trigger commit
  + index.ts sha, per-engine adapter shas, harness rev.
- Honest zero correctly framed as a stored-surface property, not a product
  verdict; F3 offtopic count explicitly labeled observational (no unilateral
  prereg change); FirePrecision denominator variance disclosed; agentmemory
  probe-not-run disclosed.
- Metered product arm correctly deferred post-reset (PO un-bundle ruling
  honored). $0, all local, deterministic-first.

## Caveats (non-blocking)

- Verification confirms the run matches its own declared protocol and that the
  numbers are real. Whether the retrieval-mediated engine-derived-topics
  protocol is the *right* operationalization of surface-audit implication 3 is
  disclosed by the author (Disclosure 1) as this row's instrument choice; a
  store-dump derivation arm would be a different instrument and is not claimed.
  That instrument choice is Brian's/PO's to ratify, not a correctness defect.

Row S4-12 moves done → **VERIFIED (PASS)**. corvid-dsh, 2026-09-16 13:44 PDT.
