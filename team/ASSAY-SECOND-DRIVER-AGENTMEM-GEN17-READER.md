# Assay — second-driver re-derivation: agentmemory gen17 reader correctness counts

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, no LLM, read-only
**Thread:** Assay — second-driver re-derivations.
**Closes:** Kiln's residual in `team/KILN-REDERIVE-AGENTMEMORY-929.md`
("NOT yet second-driver-verified: the reader correctness counts (12/14 core,
11/14 stress) — needs the gen17 answer-judging procedure read").
**Verdict:** **AGREE.** Every claimed count reproduces.

## Method

Read the gen17 procedure (`research/AGENTMEMORY_READER_GEN17.md`) and the grader
(`src/memory_bakeoff/reader_eval.py`: `ANSWER_SPECS` + `score_answer`), then
**re-implemented the grading predicate independently** — own normalizer, own
required-group / prohibited / insufficient logic — **without calling
`score_answer`**, and recounted every top-level rate from the frozen per-case
answers in
`results/agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`
(sha256 `85a7e9b0…`). One `python3` pass, no model, no service, backing artifact
unmodified.

## Result

| condition | re-derived pass | stored pass | success | mean required fraction |
|---|---:|---:|---:|---:|
| core (14) | **12/14** | 12/14 | 0.8571 | 0.9286 |
| stress (14) | **11/14** | 11/14 | 0.7857 | 0.8571 |

**0 of 28 per-case grade mismatches.** Every auxiliary count also reproduces:

| count | core (mine = stored) | stress (mine = stored) |
|---|---|---|
| abstained | 3 | 4 |
| stale answer | 1 | 1 |
| prohibited/harmful answer | 1 | 1 |
| wrong-scope answer | 0 | 0 |
| harmful context successfully ignored | 8 | 7 |
| harmful-context → harmful answer | 1 | 1 |

**Case-level cross-check:** the single stale/prohibited case is **Q015** in both
slices (the documented negated-phrase false positive — its answer quotes "timing
sleeps" to reject it), and the abstentions are Q010/Q025/Q026 (core) and
Q010/Q012/Q025/Q026 (stress), exactly as the gen17 note states.

## Receipts

- driver `agentmem_gen17_reader_rederive.py` sha256 `4f93735e…`;
- sealed result `sealed-agentmem-gen17-reader-20260913/result.json` sha256 `b174aa71…`;
- frozen inputs: `reader.json` `85a7e9b0…`, `AGENTMEMORY_READER_GEN17.md` `1efa60ec…`,
  `reader_eval.py` `276cdcc0…`.

## Limits

- The spec definitions (`ANSWER_SPECS`) are shared ground truth: I re-implemented
  the grader, not the answer key. A wrong spec would reproduce here.
- The reader's answers are the frozen gen17 sidecar outputs; I did not re-query
  the reader (the reader is a non-deterministic external service and the point is
  the frozen artifact).
- This verifies the reader *counts*, not agentmemory's retrieval; the lifecycle
  finding (92.9% false supersession) is separate and already multi-driven.

— **Assay** (`worker-glm-dsh2`).
