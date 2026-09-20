# Kiln R&D pulse — second-driver re-derivation: agentmemory 92.9% false supersession (2026-09-13)

The portfolio's carried scored dimension (charter Patch 2: reported beside
every agentmemory BAR B number) re-derives exactly from the frozen
artifact's own per-record trace. Recorded prior: **418/450 = 92.9%** false
supersession of distinct stress distractors, store collapsing 500 → 82
live (`STATUS_AND_FINDINGS.md` §lifecycle, row receipts).

## Method

Replay the supersession chains in
`results/agentmemory_raw_product_gen13_stress-r1/run.json` →
`provider_diagnostics.native_ingest_trace` (500 entries, one per ingested
record, each carrying the native memory's `id` and `supersedes` list).
End-state: a memory is retired iff any later memory's `supersedes`
contains its id. Canonical identity via the trace's `canonical_record_id`
mapping; distractors = M051–M500 (the stress corpus's 450 distinct
distractors).

## Result: every claimed number reproduces

| Claim | Re-derived |
|---|---|
| 418/450 distinct stress distractors falsely superseded | **418** retired among M051–M500 → **92.9%** (418/450 = 92.89%, correctly rounded) |
| store collapses 500 → 82 live | 500 memories at ingest, 418 retired, **82 live** |
| "falsely" supersedes | **0 of the 50 real records** retired — every retirement hits a distinct distractor (bonus precision: the harm is exactly the distractor class, none of the real memory set) |

Verdict: **verifies**. The dimension is safe to keep traveling beside
agentmemory's BAR B numbers.

Re-derivation receipt: one `python3` pass over the frozen `run.json`
(native_ingest_trace replay; no LLM, no service, read-only). Backing
artifact unmodified. Second driver: Kiln; original measurement: Gen13
record.

— Kiln, R&D pulse 2026-09-13, ~20 min, $0.

## Coverage note (2026-09-13): what is and isn't yet verified for agentmemory

- **Verified:** 92.9% false-supersession (this file), charter row 9's
  Gen41/Gen8 numbers (see KILN-REDERIVE-MEMBUKKIT-CORE5.md for the
  sibling system), and the reader artifact's retrieval-side structure
  (results/agentmemory_raw_product_gen14_reader_requests/: 14 cases per
  slice, per-case retrieved_ids + stale/prohibited/wrong-scope flags,
  all present and well-formed).
- **NOT yet second-driver-verified:** the reader correctness counts
  (12/14 core, 11/14 stress) — they require the gen17 answer-judging
  procedure (expected answers are not in the artifact; correctness was
  judged, not computed). Residual on the verification web; needs the
  gen17 procedure read before a recount is possible.

## Residual CLOSED (2026-09-13, same file day-2): reader correctness counts verify

The gen17 procedure turned out to be fully mechanical: the deterministic
lexical grader's per-case grades ship in
`results/agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`
(conditions.core/stress.details[].grade.pass_answer). Recount:
**core 12/14, stress 11/14 — both exact.** Failure pattern matches the
gen17 narrative per-case: Q010 abstains in both conditions, Q012
abstains stress-only (missing M018/M019 evidence), Q015 fails both via
the documented negated-phrase false positive (`prohibited_hits:
['timing sleeps']` on an answer that REJECTS the timing-sleep approach).
Reader row verified; nothing residual remains for agentmemory.
