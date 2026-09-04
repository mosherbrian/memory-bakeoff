# MemBukkit intended-model path: reproduced

**Evidence class:** `product_identity_reproduction_no_score`. This generation establishes product
identity. It produces no score, touches no benchmark corpus, and must never be
compared with Round1, longitudinal-v1, MemConflict or any baseline number.

Gen7 could not run MemBukkit's intended models: `MemseekAI/membukkit-biencoder-v1` and
`MemseekAI/membukkit-reranker-v2` both returned 401, the pinned resolver silently
substituted `sentence-transformers/all-mpnet-base-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`, and the harness
failed closed with no scored run. `research/MEMBUKKIT_INTENDED_MODEL_GEN7.md`
records that blocker and is unchanged by this generation.

Both repositories are now publicly readable. The previously blocked path
reproduces on the original pinned source, with no fallback, and repeats
identically from a frozen local snapshot with the network blocked.

## Source identity — the historical commit, not a newer one

| field | value |
| --- | --- |
| checkout HEAD | `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` |
| matches the Gen7 pin | True |
| resolver | `src/membukkit/models/registry.py` |
| package version | 0.1.0 |

The intended-model names still live in that exact file at the lines below, so
the question Gen7 asked is the question this generation answers:

```
23: _HUB_ENCODER_REPO = "MemseekAI/membukkit-biencoder-v1"
24: _HUB_RERANKER_REPO = "MemseekAI/membukkit-reranker-v2"
25: _FALLBACK_ENCODER = "sentence-transformers/all-mpnet-base-v2"
26: _FALLBACK_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"
93: hub = _hub_download(_HUB_ENCODER_REPO)
97: return _FALLBACK_ENCODER
116: hub = _hub_download(_HUB_RERANKER_REPO)
120: return _FALLBACK_RERANKER
```

No newer MemBukkit revision was substituted, and none was needed: the
historical source loads the newly public weights unchanged, so the separate
`current_upstream_compatibility_diagnostic` that Gen40 reserved for a failure
was not run.

## Model identity

### Bi-encoder

| field | value |
| --- | --- |
| repository | `MemseekAI/membukkit-biencoder-v1` |
| revision | `50ab0a1fefa47c44d6d66f530dea2d3ea426f5b3` |
| public without credentials | True (gated: False) |
| library / pipeline | sentence-transformers / sentence-similarity |
| license (model card) | apache-2.0 |
| files pinned | 12 |
| every file reconciles to that revision | True |

### Cross-encoder reranker

| field | value |
| --- | --- |
| repository | `MemseekAI/membukkit-reranker-v2` |
| revision | `0b46ab535caa4044542889dd76a15868799aabbe` |
| public without credentials | True (gated: False) |
| library / pipeline | None / None |
| license (model card) | not stated |
| files pinned | 7 |
| every file reconciles to that revision | True |

Weight-file content identity, independent of any local path:

| role | file | bytes | sha256 |
| --- | --- | --- | --- |
| bi-encoder | model.safetensors | 437967672 | `92deea14f506ebfdc44a726463e93577b6fb36a644c3972dc82d4a60784259f9` |
| reranker | model.safetensors | 90866412 | `038f449571ac2716159f9160da61f3d2fa2651410d6d6b91a462c5a7be0f610e` |

Every file in both snapshots was checked against the published revision: large
files by their LFS sha256, small files by recomputing the git blob object id.
Both snapshots reconcile completely — no mismatched file, no local-only file,
no file in the revision that is missing locally.

## Fallback could not be mistaken for success

The resolver, the hub client and both model constructors were wrapped as
observers. Every wrapper forwards to the original and only records what passed
through it, so embeddings and ranking cannot be affected. A run fails if a
substitute repository is requested, downloaded or loaded, or if either model is
loaded from anywhere but the pinned snapshot directory.

| observation | online | offline |
| --- | --- | --- |
| snapshot already cached before the run | {'encoder': False, 'reranker': False} | {'encoder': True, 'reranker': True} |
| repositories downloaded in this run | 2 | 0 |
| fallback events | 0 | 0 |
| bi-encoder loaded from | pinned snapshot | pinned snapshot |
| reranker loaded from | pinned snapshot | pinned snapshot |
| LLM invocations | 0 | 0 |

The offline phase runs in a fresh process with outbound connections blocked at
the socket layer, so a silent re-download would raise rather than pass.

## Synthetic preflight

The fixture is 60 invented facts about a fictional
preservation society and 8 fixed queries, written before
any model output was observed and unrelated to every corpus in this repository.
Nothing here was tuned: pinned product defaults throughout.

1. **Bi-encoder loads and embeds.** Output shape [4, 768], all
   values finite, rows L2-normalised to 1.0.
2. **Reranker loads and scores.** 4 finite scores for a
   fixed query and document set, ordered [0, 1, 3, 2].
3. **End-to-end.** 60 facts written
   (60 new, backend count
   60), then all
   8 queries searched through both intended models.
4. **Provenance.** Every returned item maps to a synthetic write receipt:
   0 unmapped ids.
5. **Repeat stability.** Returned order identical on repeat:
   True; selected set identical:
   True. Order stability and score
   identity are reported separately, as Gen38 required.
6. **Unrelated queries.** The two off-topic queries return a full
   10 hits each, like every other query. The product applies no
   relevance floor on this surface. No pass threshold was invented after seeing
   the outputs; this is recorded as behaviour, not as a failure.
7. **Offline repeat.** 8 of
   8 queries return an identical ordered id list, probe
   values are identical (True), and no download
   occurred.

## What the pipeline actually does

Measured on this path, at pinned defaults, with source read alongside:

- **Writes** are embedded by the intended bi-encoder as they enter the bank.
- **Queries** are embedded by the same bi-encoder; there is no separate query model.
- **Routing** partitions the bank into `24` topic buckets and
  opens only a scan budget of them — measured at 18 to 20 facts scanned of 60,
  a scan fraction of 0.30 to 0.33.
- **The reranker acts after candidate generation**, scoring every candidate in
  the opened region, never the whole bank.
- **Candidate pool** is `candidate_pool=50`,
  `rerank_cap=50`; `top_k=10` leaves the stage.
- **Fusion** is `select="hybrid"`: reciprocal-rank fusion over the
  cross-encoder rank and the cosine rank with `k_rrf=60`. Cosine and
  cross-encoder scores are therefore **not** directly comparable — only their
  ranks are combined. The optional lexical lane is off by default.
- **Presentation is temporal, not by score.** Selection is by relevance;
  the returned list is then ordered by date, so returned order is a
  presentation property.
- **Store** is the in-memory backend, so this generation writes no product database.
- **Provenance** is exact: each hit carries a `source_id` derived from the
  caller's id seed and a `ref` of the form `mem:<first 12 chars>`.

### Lifecycle on this path

Offering the identical 60 facts a second time wrote
0 new rows — the id seed dedupes. Offering one
dated fact that contradicts a stored one appended it as row
61 and left **both** facts `current`
(0 superseded hits, statuses seen:
current). So the direct fact-ingest path is
append-and-dedupe only: it performs no supersession. MemBukkit's supersession
machinery sits on the LLM distiller path, which this generation deliberately
did not exercise. That is a measured property of this path, not a defect, and
not a comparison with any other engine.

### One thing worth knowing before any future run

`ModelConfig.device` reaches the reranker but not the bi-encoder: the encoder
wrapper passes only a path to `SentenceTransformer`, which then picks its own
device. Measured here as encoder on `mps:0` and reranker on
`cpu` in the same process, from one `device="cpu"` request.
Recorded rather than overridden.

## Artifacts

| file | contents |
| --- | --- |
| `results/membukkit_gen40_intended_model/model_pins.json` | both repositories, revisions and per-file identity |
| `results/membukkit_gen40_intended_model/online.json` | acquisition + preflight leaf, digest `a26801ec5c6134bc` |
| `results/membukkit_gen40_intended_model/offline.json` | frozen-snapshot repeat, digest `4c2a41846208a75d` |
| `results/membukkit_gen40_intended_model/comparison.json` | online vs offline reconciliation |

The two digests differ only in the fields
`load_trace`, `phase`, `snapshot_cached_before_run` —
everything else the two phases recorded is equal. Wall-clock and download
timing are excluded from both.

A second complete run into a scratch directory rebuilt the offline digest
byte-identically. The online digest is deliberately not stable across cache
states: the committed leaf was produced with the model cache deleted first, so
it records the acquisition, and a warm repeat differs in exactly
`load_trace` and `snapshot_cached_before_run` and nothing else. Every measured
quantity — probe values, selections, order, provenance, lifecycle — is
identical in both.

Contract module `src/memory_bakeoff/membukkit_gen40.py`, sha256
`f24418c6dd3cbe2a1204b3209560202763beb2982cbdd8864b7a58f286c73faa`. Pinned upstream `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`.

## What this does and does not settle

Settled: the intended MemBukkit stack exists publicly, is pinnable, loads on the
original pinned source with no substitution, and runs end to end with exact
provenance and a reproducible offline repeat. The asterisk MemBukkit has carried
since Gen7 is retired.

Not settled: anything about quality. No score was produced, and the fixture was
built to exercise the path, not to measure it. Whether the intended-model path
should now re-enter a frozen benchmark lane is a Gen41 decision.
