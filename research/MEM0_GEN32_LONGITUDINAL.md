# Mem0 Gen32 — longitudinal-v1 raw-product profile, and the three-engine result

## Status

`complete_raw_product_longitudinal_no_temporal_surface`.

Three fresh repetitions of Mem0 2.0.19 in its exact Round-1 raw identity against
the frozen `longitudinal-v1` ruler: 16 ordinary `Memory.add(..., infer=False)`
calls in canonical order, nine checkpoints, 20 cases through native search. No
reader, no LLM call, no GPU.

Gen32 was posted as a **preregistered test**: do the seven failure classes shared
by Gen29 Perseus and Gen31 Hindsight recur in a third architecture? They do — all
seven, in an engine with no temporal retrieval surface at all.

## Identity

- Upstream `mem0ai/mem0` commit `19cb89aff472325c707f64b2f34ae6afdbf7faf7`,
  package 2.0.19 loaded editable from that checkout.
- `Memory.add(..., infer=False)`: no extraction, update, or supersession
  inference. Mem0 constructs an OpenAI client at init regardless; it carries a
  placeholder key and is never called. The preflight proves that by refusing the
  process a socket during a raw add rather than asserting it.
- Dense: FastEmbed 0.8.0 `thenlper/gte-large`, resolved to
  `qdrant/gte-large-onnx` snapshot `770e825c74a004f165b78793f7c8fc4a95280878`,
  1024-D. Sparse: `Qdrant/bm25` snapshot
  `22b8d2af71a76161e18dd432d2cee0eefa66e412`. ONNX Runtime 1.29.0.
- Embedded qdrant-client 1.19.0, on-disk, fresh path and collection per
  repetition. spaCy absent, so entity boosts stay inactive as in Round 1.
- Constant native scope `user_id=memory-bakeoff`; threshold 0.1; top-k 5.
- Ruler unchanged: fixture `a5c67e7b…`, scorer `1dd831e8…`. Adapter
  `mem0-longitudinal-adapter-v1`, contract
  `f41e15212b435346fb50b7794ead1bd00898a4bf89db433cb89b98891502ac6d`.

## What the raw profile actually offers

Measured on an unrelated synthetic domain before anything was frozen:

- **No temporal retrieval surface exists.** The only time-shaped APIs are
  `update`, `_update_memory` and `history` — mutation and audit, not retrieval.
  `metadata.timestamp` is opaque payload and does not participate in ranking.
- Raw `add` never deduplicates or merges: seven adds produced seven points.
- One `history` row is written per add, giving native ingest lineage that neither
  Perseus nor Hindsight offered.
- Reads are side-effect-free: identical result order and scores on repeat, and
  the point count is unchanged by searching.
- Mem0 **can** filter on metadata such as `scope`. Gen10's scored identity
  filtered on the constant `user_id` alone, so that capability is recorded here
  and deliberately excluded from the scored path — using it would very likely
  suppress `scope_collapse` and answer a different question.

A reproducibility hazard worth recording: FastEmbed 0.8.0 warns that
`thenlper/gte-large` now uses mean pooling rather than CLS embedding. Round 1 ran
this same FastEmbed version, so the identity holds — but it holds *only* at this
pin.

## Results

Three repetitions, identical failure totals — zero variance, provenance exact on
every returned item.

| Failure class | Per repetition | Three repetitions |
|---|---|---|
| `stale_persistence` | 5 | 15 |
| `false_persistence` | 3 | 9 |
| `configuration_collapse` | 2 | 6 |
| `scope_collapse` | 2 | 6 |
| `belief_truth_confusion` | 2 | 6 |
| `unsupported_evidence` | 2 | 6 |
| `failed_procedure_adoption` | 1 | 3 |
| `late_history_corruption` | 1 | 3 |
| `missing_required_truth` | 1 | 3 |

Clean across all 60 case-runs: `future_leakage` 0, `unmapped_provenance` 0,
`false_supersession` 0, `procedure_recommendation_missing` 0.

## The three-engine picture

Capability surfaces only. Not a leaderboard.

| | Perseus Gen29 | Hindsight Gen31 | Mem0 Gen32 |
|---|---|---|---|
| `false_persistence` | 9 | 9 | 9 |
| `configuration_collapse` | 6 | 6 | 6 |
| `failed_procedure_adoption` | 3 | 3 | 3 |
| `late_history_corruption` | 3 | 3 | 3 |
| `unsupported_evidence` | 6 | 6 | 6 |
| `missing_required_truth` | 6 | 3 | 3 |
| `stale_persistence` | 12 | 12 | **15** |
| `correction_failure` | 12 | **0** | **0** |
| `history_erasure` | 9 | **0** | **0** |
| `scope_collapse` | **0** | 6 | 6 |
| `belief_truth_confusion` | **0** | 6 | 6 |

Five classes land at **identical counts** across three products that share no
storage engine, no retrieval algorithm and no time model.

The differences are all explainable by one architectural choice each. Perseus
partitions by workspace, so it never collapses scope, but its write path
collapses application time onto transaction time, so corrected history is
erased. Hindsight and Mem0 keep one namespace and let ranking decide, so both
collapse scope. Mem0's single extra failure is `stale_persistence` on **LQ20**,
an `as_of_event_truth` case that Perseus answered with `valid_at` and Hindsight
with `query_timestamp` — the extra failure is the direct cost of having no
temporal filter at all.

## What this does and does not establish

It is three-engine evidence **consistent with** an append-only-without-retirement
explanation for the seven shared classes. Mem0 reproduces all seven while having
no temporal machinery to blame, which removes the time model as the common cause.

It is **not** proof of causation. The three profiles also share this harness,
this ruler, and a no-retirement constraint that the generations themselves
imposed by forbidding truth-driven lifecycle calls. A genuine test of the
retirement half needs an engine that retires aggressively on its own — which is
what makes agentmemory the informative counterexample, since Round 1 measured it
falsely superseding 418 of 450 stress distractors.

## Round-1 contrast

This identical Mem0 configuration scored stress Hit/all-relevant **0.958/0.917**
in Round 1. Excellent retrieval relevance, and seven longitudinal failure classes
underneath it. That is Round 1's own thesis stated as plainly as the data can
state it: getting a relevant-looking result is the easy part.

## Verification

Full suite: 126 passed, one existing warning, with `node` on `PATH`. Focused
tests cover ruler and adapter hashes, the Gen10 four-field metadata envelope, the
refusal to hand Mem0 `configuration` as a routing key, the constant-`user_id`
scored filter, the single available native operation, published identity with no
LLM calls, that the hypothesis reporting states its own limits, and that point
counts never shrink and absence is never called deletion.

Reproduce with `scripts/run_mem0_gen32_longitudinal.py` then
`scripts/summarise_gen32.py`; the API audit is `scripts/preflight_mem0_gen32.py`.
