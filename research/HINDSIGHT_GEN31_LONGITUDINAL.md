# Hindsight Gen31 — longitudinal-v1 raw-product profile

## Status

`complete_raw_product_longitudinal_mention_time_axis_only`.

Three fresh repetitions of Hindsight v0.9.2 in its exact Round-1 raw/no-LLM
learned-reranker identity against the frozen `longitudinal-v1` ruler: 16 ordinary
`retain` calls in canonical order, nine checkpoints captured before their
queries, 20 cases through native recall. No reader, no LLM, no GPU.

## Identity

- Hindsight 0.9.2 (`hindsight-all`, `hindsight-api-slim`, `hindsight-client`,
  `hindsight-embed`), source commit `ebad478240d3171bb88201ececda5e8d9883d22d`.
- `HINDSIGHT_API_LLM_PROVIDER=none`, with the harness's own explicit
  `HINDSIGHT_RAW_LLM_PROVIDER=none` declaration — the provider refuses to infer
  the server's LLM mode.
- ONNX `intfloat/multilingual-e5-small`, snapshot
  `614241f622f53c4eeff9890bdc4f31cfecc418b3`, 384 dimensions, mean pooling,
  normalized, E5 query/passage prefixes.
- Local CPU `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Homebrew PostgreSQL 17.11 + pgvector 0.8.6, fresh database and fresh bank per
  repetition. Top-k 5, `nofile` 8192.
- Ruler unchanged: fixture `a5c67e7b…`, scorer `1dd831e8…`.
- Adapter `hindsight-longitudinal-adapter-v1`, contract
  `c9025733aa894fa5abac43632e9dc916c37e526065d089a882257427c14d60ff`, frozen
  before the first scored query.

Everything the Round-1 profile needs was still present on the machine, including
the pinned E5 snapshot. Nothing was upgraded or substituted.

## The temporal axis this profile actually has

Hindsight distinguishes **`mentioned_at`** — when a fact was stated — from an
**`occurred_start`/`occurred_end`** application-time range. Only the first is
reachable here.

Raw `retain` accepts one per-item `timestamp`, which becomes `mentioned_at` and
is preserved exactly. `occurred_*` is written in only three places, all excluded
from this profile:

- LLM fact extraction — `engine/reflect/prompts.py` teaches the model to emit
  `occurred_start` alongside `mentioned_at`, and Gen31 is the no-LLM profile;
- the transfer importer, which by its own docstring replays "exactly the steps
  retain runs **after** LLM extraction" from an archive of already-extracted
  facts;
- `PATCH /v1/default/banks/{bank}/memories/{id}`, the curate endpoint, whose
  request model also carries `state: "invalidated"` and supersession reasons —
  using it would be exactly the truth-driven lifecycle help the generation
  forbids.

So the honest Gen31 axis is mention time alone. That is a capability boundary of
the raw profile, not a setup failure, and not the same shape as Perseus Gen30,
where the axis existed and was destroyed by the activation step.

One consequence is favourable: because `retain` takes an explicit timestamp, the
store's timeline **is** the fixture's calendar timeline. Gen29 needed a mapping
from fixture instants onto observed write instants; Gen31 needs none.

## Read side effects: measured, then not relied upon

Repeating an identical recall returned the identical document order, and every
table count and content digest across `documents`, `memory_units`, `chunks` and
`memory_links` was byte-identical before and after a batch of reads. The only
movement was in the fused `final` score, at most `8.45e-09`, while the reranker,
semantic and keyword components were exactly equal — floating-point noise in
fusion, not feedback or access bookkeeping.

An earlier version of this check reported reads as non-identical. That was wrong:
it compared whole score payloads, and 1e-9 jitter made two identical rankings
look different. Scored queries therefore ran against the live checkpoint store,
with the measurement above as the evidence rather than an assumption.

## Results

Three repetitions, identical failure totals — zero variance.

| Failure class | Per repetition | Three repetitions |
|---|---|---|
| `stale_persistence` | 4 | 12 |
| `false_persistence` | 3 | 9 |
| `configuration_collapse` | 2 | 6 |
| `scope_collapse` | 2 | 6 |
| `belief_truth_confusion` | 2 | 6 |
| `unsupported_evidence` | 2 | 6 |
| `failed_procedure_adoption` | 1 | 3 |
| `late_history_corruption` | 1 | 3 |
| `missing_required_truth` | 1 | 3 |

Clean across all 60 case-runs: **`future_leakage` 0**, **`unmapped_provenance`
0**, **`false_supersession` 0**, **`procedure_recommendation_missing` 0**,
**`correction_failure` 0**, **`history_erasure` 0**.

Provenance was exact for every returned item in every case. Ingest produced one
document, one memory unit and one chunk per observation — no splitting at this
size — and each hit carried the `document_id` and `record_id` marker that
identify its canonical observation. In raw mode the graph arm is link-based
rather than entity-based: 36 memory links and zero entities.

## Paired contrast with Perseus Gen29

Capability surfaces only. These are different products answering the same ruler;
this is not a numeric leaderboard.

| | Perseus Gen29 | Hindsight Gen31 |
|---|---|---|
| `correction_failure` | 12 | **0** |
| `history_erasure` | 9 | **0** |
| `scope_collapse` | **0** | 6 |
| `belief_truth_confusion` | **0** | 6 |
| `stale_persistence` | 12 | 12 |
| `configuration_collapse` | 6 | 6 |
| `late_history_corruption` | 3 | 3 |
| `failed_procedure_adoption` | 3 | 3 |
| `future_leakage` | 0 | 0 |
| `unmapped_provenance` | 0 | 0 |

**Hindsight repairs exactly what Perseus's collapsed time axis broke.** A
vantage-point query reaches the earlier state, so corrected history is no longer
erased.

**It breaks two things Perseus got right.** Perseus enforced scope with native
workspaces; Hindsight carries scope as ordinary metadata in one shared bank, as
this generation required, and hybrid recall crosses the boundary. And Perseus
could not confuse belief with truth because it had no usable second axis;
Hindsight has one and mixes them.

**Seven classes appear in both.** Stale persistence, configuration collapse,
failed-procedure adoption, late-history corruption, false persistence, missing
required truth and unsupported evidence survive two architectures that share
almost nothing. On this evidence they look like properties of ordinary
append-only ingestion without retirement, rather than of either engine.

## Boundary

`raw_product` retrieval, temporal and lifecycle evidence for one documented
composite: raw no-LLM `retain` plus native hybrid recall with the learned CPU
reranker. Not a full-product Hindsight claim, not a reader result, and not
comparable as a scalar to OM's context-production score.

Databases, service logs and caches stay local and untracked; the committed
evidence is normalized counts, native IDs, traces and hashes.

## Verification

Full suite: 118 passed, one existing warning, with `node` on `PATH`. Focused
tests cover ruler and both adapter hashes, public-only retain payloads with
native provenance, one-bank scope mapping that keeps configurations testable,
routing from public coordinates only, the declared absence of lifecycle and
occurred-range calls, published identity and isolation evidence, the qualitative
paired contrast, checkpoint prefix discipline, and that absence from active state
is never labelled deletion.

Reproduce with `scripts/run_hindsight_gen31_longitudinal.sh <rep> <out.json>`
then `scripts/summarise_gen31.py`; the API audit is
`scripts/preflight_hindsight_gen31.sh`.
