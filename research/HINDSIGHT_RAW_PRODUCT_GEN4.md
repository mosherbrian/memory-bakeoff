# Hindsight raw-product retrieval benchmark (generation 4, invalidated)

> **Status: invalidated.** A later service-isolation audit found that all
> generation-4 repetitions attached to a stale generation-3 process on port
> 8891. The configured ONNX model path also named a snapshot directory rather
> than the required `onnx/model.onnx` file, so the intended fresh services would
> have failed to start. Consequently, none of the scores or aggregates below
> are publishable product evidence. They are retained only as historical
> diagnostics; see `research/HINDSIGHT_GEN4_INVALIDATION.md` and the corrected
> generation-5 result directories.

## Scope and classification

This is the first authoritative Hindsight result in this repository for the
specific configuration below. Its experiment class is **`raw_product`**: it ran
the real upstream service and retention/retrieval path, but used raw no-LLM
ingestion. It is not a score for Hindsight's default or full LLM-backed product
architecture.

No reader evaluation, LLM extraction, learned reranker, SentenceTransformers
embedding configuration, other product work, or Claude Code transcript corpus
access occurred in this generation.

## Exact evaluated system

- Service/packages: `hindsight-api-slim==0.9.2`, `hindsight-client==0.9.2`, and
  `hindsight-embed==0.9.2`.
- Database: `pg0-embedded==0.15.1` with `asyncpg==0.31.0`; every repetition used
  a distinct `pg0://memory-bakeoff-gen4-*` database namespace and distinct bank.
- Raw retain: `HINDSIGHT_API_LLM_PROVIDER=none` plus the harness's explicit
  `HINDSIGHT_RAW_LLM_PROVIDER=none` declaration. No LLM was configured.
- Embeddings: Hindsight ONNX provider with
  `intfloat/multilingual-e5-small` snapshot
  `614241f622f53c4eeff9890bdc4f31cfecc418b3`; 384 dimensions, mean pooling,
  normalized output, 512-token limit, `query: ` and `passage: ` prefixes.
  `onnxruntime==1.29.0`, `transformers==5.15.1`, and `tokenizers==0.22.2`.
- Reranker: Hindsight `rrf` passthrough; no learned cross-encoder was active.
- Host: Apple M1/macOS, arm64, Python 3.13. Exact non-secret fingerprints and
  package versions are in each repetition's `hindsight_runtime.json` and
  `run.json`.

The service directly showed semantic and keyword score components in this raw
configuration. Hindsight source configuration also exposes graph and temporal
strategies, but raw no-LLM retain produced no extracted source facts in the
generation-3 smoke. These results therefore make no graph or temporal
contribution claim.

## Repetitions and publication gate

Each post-fix repetition was fresh: service startup/readiness, unique pg0
namespace and bank, ingestion, retrieval, clean service shutdown. All six were
`status=ok`, `experiment_class=raw_product`, and `publishability=publishable`.
Their provenance reports used only `native` canonical record IDs.

| Corpus | Fresh authoritative repetitions | Records | Held-out queries | Result directories |
|---|---:|---:|---:|---|
| Core | 3 | 50 | 26 | `hindsight_gen4_core_r2`, `r3`, `r4` |
| Stress | 3 | 500 | 26 | `hindsight_gen4_stress_r1`, `r2`, `r3` |

The preserved `results/hindsight_gen4_core_r1/` attempt is excluded from these
aggregates. It surfaced a client-session cleanup defect before scoring completed
without warnings. `INVALIDATED.md` in that directory explains the issue. The
small fix closes providers in the runner's `finally` path and has regression
coverage; every authoritative repetition was created in a new directory after
the fix.

## Aggregate retrieval results at top-k = 5

Values are arithmetic means across the three independent runs; brackets are the
observed minimum--maximum across repetitions.

| Metric | Core (50 memories) | Stress (500 memories) |
|---|---:|---:|
| Hit@5 | 0.875 [0.833--0.917] | 0.181 [0.167--0.208] |
| Recall@5 | 0.854 [0.812--0.896] | 0.181 [0.167--0.208] |
| Precision@5 | 0.208 [0.200--0.217] | 0.036 [0.033--0.042] |
| MRR | 0.573 [0.556--0.588] | 0.103 [0.094--0.111] |
| All-relevant@5 | 0.833 [0.792--0.875] | 0.181 [0.167--0.208] |
| Prohibited@5 | 0.128 [0.125--0.133] | 0.022 [0.017--0.025] |
| Harmful-presence rate | 0.597 [0.583--0.625] | 0.111 [0.083--0.125] |
| Mean prohibited count | 0.639 [0.625--0.667] | 0.111 [0.083--0.125] |
| Useful-before-harmful | 0.917 [0.875--0.938] | 0.589 [0.500--0.667] |
| Negative-empty rate | 0.000 [0.000--0.000] | 0.000 [0.000--0.000] |
| Returned context chars | 417.1 [412.2--421.2] | 585.2 [584.7--585.9] |
| Returned context words | 61.3 [60.4--61.9] | 82.8 [82.4--83.2] |
| Retrieval latency (ms) | 33.9 [33.0--34.6] | 56.6 [49.2--68.7] |

Per-query returned IDs, prohibited counts, context size, and latency are in the
six `detail.csv` files; each `run.json` preserves the full provenance report and
execution-environment fingerprint.

## Class-labeled comparison only

The comparison below is intentionally not a single unlabeled leaderboard. The
historical baseline and controlled-core values are prior one-run artifacts, not
additional repetitions of the Gen4 configuration.

| System/result | Experiment class | Core Hit@5 | Stress Hit@5 | Notes |
|---|---|---:|---:|---|
| Hindsight ONNX+RRF raw retain (this report) | `raw_product` | 0.875 mean | 0.181 mean | Three fresh repetitions per corpus; no LLM extraction or learned reranker. |
| Dense LSA baseline | `baseline` | 0.958 | 0.583 | Historical deterministic baseline. |
| MemBukkit shared-LSA arm | `controlled_core` | 0.958 | 0.458 | Historical controlled routing/core result, not the upstream intended-model product. |

The stress result shows this exact raw ONNX+RRF configuration loses substantial
retrieval recall under the deterministic near-neighbor distractors. Its lower
prohibited rate is reported separately and is not treated as compensating for
the retrieval loss or as evidence of lifecycle behavior.

## Verification

The cleanup fix and benchmark metadata launcher were checked with the full suite:
`55 passed`, plus one existing Python 3.13 `importlib.metadata` deprecation
warning. No archived result directory was overwritten.
