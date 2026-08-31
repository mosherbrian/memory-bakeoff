# Memory Engine Bake-off

A reproducible, coding-flavored benchmark for persistent agent memory systems.

> **Start here for the current handoff:** [`STATUS_AND_FINDINGS.md`](STATUS_AND_FINDINGS.md) summarizes the scoreboard, caveats, and emerging conclusions. [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) is the execution plan for the next networked real-engine runs.

Initial field:

- BM25
- sparse TF-IDF cosine baseline
- offline dense LSA baseline
- BM25+dense RRF hybrid baseline
- Mem0
- agentmemory (`rohitg00/agentmemory`)
- Claude-Mem (`thedotmack/claude-mem`)
- MemBukkit (`memseekai/membukkit`)
- Habitus-AI (`munch2u-a11y/Habitus-AI`)
- Hindsight (`vectorize-io/hindsight`)

The benchmark is intentionally split into **raw-memory** and **product** modes. Some
products require an LLM as part of ingestion; pretending otherwise would measure a
made-up implementation rather than the product.

## What it tests

The built-in corpus currently has 50 memories and 26 queries covering:

- exact identifiers and file paths
- semantic paraphrase
- corrections and stale facts
- as-of temporal questions
- multi-hop evidence
- successful vs failed procedures
- repo/speaker-style scope collisions
- protocol details and near-neighbor distractors
- unanswerable/negative queries

Ground truth is explicit and deterministic. Baselines do not get a hidden scope filter; repository scope must be recovered from the query text. For correction/procedure cases the harness
also labels **prohibited** memories (obsolete or verified-failed approaches), so a
retriever cannot score well merely by returning both sides of a conflict.

## Quick start (offline baselines)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

memory-bakeoff run --providers bm25,tfidf_cosine,dense_lsa,hybrid_rrf --mode raw
memory-bakeoff learning-diagnostic
memory-bakeoff manifest --llm-label "none/offline"
pytest
```

The local dense baseline is LSA over TF-IDF. It is deliberately dependency-light and
fully deterministic; it should **not** be confused with a modern pretrained embedding
model. A sentence-transformer baseline should be added on a machine where model
weights are available.


## LLM backends

The LLM boundary is transport-agnostic and OpenAI-shaped. The benchmark can use:

- `fake` — deterministic fixture/echo backend for plumbing and bulk diagnostics
- `chatgpt_sidecar` — file-queue backend answered interactively by ChatGPT through the tool loop
- `openai_compat` — OpenAI or compatible local HTTP servers such as llama.cpp/vLLM/SGLang
- `anthropic` — Anthropic Messages API
- `replay` — offline, fingerprint-validated replay of archived sidecar request/response traces

The intended evaluation ladder is **fake → ChatGPT sidecar → repeated API/local-model runs**.
Sidecar requests are batched before waiting whenever the caller uses `complete_batch()`. An
optional localhost OpenAI-compatible proxy can bridge third-party products to the same queue;
it buffers the complete ChatGPT answer rather than exposing a live token stream. See
`research/CHATGPT_SIDECAR.md`.


## First real reader-impact result

A **56-request** ChatGPT-sidecar run has exercised the end-to-end reader layer:
14 deterministic answer cases × four offline retrievers. ChatGPT was used only to read
the retrieved context; the harness graded answers deterministically. The complete trace
was then replayed offline with request fingerprints verified.

| Provider | Answer pass | Required coverage | Prohibited-answer rate |
|---|---:|---:|---:|
| BM25 | 12/14 (0.857) | 0.857 | 0.000 |
| TF-IDF cosine | 12/14 (0.857) | 0.857 | **0.071** |
| dense LSA | 14/14 (1.000) | 1.000 | 0.000 |
| hybrid RRF | 14/14 (1.000) | 1.000 | 0.000 |

BM25's two misses were omissions: Q012 lacked the complete three-hop credential chain
and Q016 lacked the verified-success NDJSON procedure, so the reader correctly returned
`INSUFFICIENT_MEMORY`. TF-IDF also missed Q016, but its Q008 failure was qualitatively
different: retrieval surfaced the obsolete `deployctl push --region west` memory without
the current correction, and the reader confidently repeated the stale command. Full
request/response artifacts are preserved under `results/sidecar_reader_trace/` (**56
requests / 56 responses**) and reproduce under the `replay` backend. These reader
numbers are still baseline-reader results; third-party engine reader runs remain a
separate phase.

Run the same reader test with another backend using:

```bash
memory-bakeoff reader-eval --providers bm25,tfidf_cosine,dense_lsa,hybrid_rrf --backend openai_compat --model YOUR_MODEL
```

## First real third-party engine: Habitus

The benchmark now vendors the dependency-free **runtime core** from
`munch2u-a11y/Habitus-AI` at commit
`f93b770e4b3c1875151dc13eb90421598c3efa5f`. The nine memory/runtime modules are
verified byte-for-byte by Git blob SHA; see `vendor/habitus/UPSTREAM.md` and
`scripts/verify_habitus_vendor.py`. Only the package initializer is a local shim so
that unrelated UI/audio/Ollama modules do not need to be imported.

Raw retrieval at k=5:

| Provider | Core Hit@5 | Core all-relevant | Stress Hit@5 | Stress all-relevant | Stress prohibited@5 |
|---|---:|---:|---:|---:|---:|
| BM25 | 0.917 | 0.792 | 0.792 | 0.667 | 0.092 |
| TF-IDF cosine | 0.875 | 0.833 | 0.792 | **0.750** | 0.101 |
| dense LSA | **0.958** | **0.958** | 0.583 | 0.542 | 0.050 |
| hybrid RRF | **0.958** | 0.917 | 0.708 | 0.667 | 0.058 |
| **Habitus** | 0.875 | 0.750 | **0.792** | 0.667 | **0.025** |

Two of Habitus's three positive-query misses on the core corpus are the intentionally
historical **as-of** queries. Stock Habitus marks superseded records inactive and does
not expose as-of retrieval. On the 22 positive non-as-of cases its Hit@5 is 0.955
(21/22); its remaining miss is the successful NDJSON-debugging procedure. This
capability limitation remains part of the overall headline score rather than being
silently removed.

Habitus also plateaus at three returned hits on this corpus: k=3/5/8/10 produce the
same core retrieval set and score. That makes its small core context footprint real,
not just harness truncation. The 500-record stress test shows a different tradeoff:
Habitus ties BM25/TF-IDF on Hit@5 while surfacing markedly fewer prohibited stale or
failed memories, but it is much slower in this pure-Python configuration.

Full runs are in `results/core5/`, `results/stress4505/`, and the focused Habitus
folders under `results/`.


## Second real third-party engine: MemBukkit

The sandbox now also vendors the semantics-bearing MemBukkit raw retrieval core from
`memseekai/membukkit` at commit
`f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`. Nine routing/storage/pipeline files
match upstream Git blob SHAs byte-for-byte; see `vendor/membukkit/UPSTREAM.md` and
`scripts/verify_membukkit_vendor.py`. Local shims are limited to packaging, progress,
usage accounting, and no-op telemetry.

Because the sandbox could not download MemBukkit's pretrained encoder/reranker weights,
the completed **controlled-core architecture** arm uses the exact same corpus-fit 32-D LSA
representation as the `dense_lsa` baseline and MemBukkit's upstream bucketed
`MemorySystem` with `select=none`. That isolates its scan-budget organization rather
than pretending a random CI test encoder is a product model.

On the 500-memory stress corpus, MemBukkit preserves the dense-LSA baseline's exact
Hit@5/all-relevant@5 (**0.583 / 0.542**) while opening **32.9% of the bank on average**
(min 30.0%, max 37.8%). Prohibited@5 is 0.042 versus dense-LSA's 0.050. At k=5:

| Provider | Core Hit | Core all-relevant | Stress Hit | Stress all-relevant | Stress prohibited |
|---|---:|---:|---:|---:|---:|
| dense LSA | 0.958 | 0.958 | 0.583 | 0.542 | 0.050 |
| **MemBukkit bucketed/shared-LSA** | **0.958** | **0.958** | **0.583** | **0.542** | **0.042** |

The public `search()` surface chronologically presents the selected evidence, so its
MRR is not directly comparable to retrievers that return relevance order; set-based
Hit/all-relevant metrics are the cleaner raw comparison here.

A separate diagnostic using MemBukkit's own deterministic CI `FakeEncoder`/
`FakeReranker` successfully exercised the production path but is not treated as a
quality score. With shared LSA plus the CI lexical reranker, hybrid RRF *reduced*
stress Hit@5 to 0.458; this demonstrates why product-mode testing with the intended
pretrained reranker remains necessary before judging the shipped hybrid configuration.

The provider names now make this boundary machine-readable: `membukkit_core_lsa` is
the historical shared-LSA/FakeReranker `controlled_core` arm, while `membukkit` requires
a separately installed upstream package and its intended encoder/reranker (`raw_product`
for `ingest_facts`, `product` for normal LLM-backed ingestion). The product adapter
fails closed if it resolves to the vendored controlled-core copy.

## Third real core: agentmemory

The harness now includes a pinned agentmemory retrieval-core arm from
`rohitg00/agentmemory` commit `e04ba88819c365c9acf9d6661ea802143e728bd6`.
Upstream `SearchIndex`, `VectorIndex`, stemmer, and synonym files match Git blob SHAs
byte-for-byte. The controlled arm uses shared LSA vectors and the upstream BM25/vector
RRF formula; graph retrieval and the optional HF reranker are explicitly disabled.

With all 500 stress records retained, agentmemory-core scores **0.583 Hit@5 / 0.500
all-relevant@5 / 0.042 prohibited@5**.

A separate `/remember` lifecycle arm reproduces its Jaccard >0.7 write-time
supersession. That raises stress Hit@5 to **0.792**, but only after collapsing the
store from 500 to **82** live memories: **418/450 (92.9%)** deliberately distinct
near-neighbor stress records are falsely superseded. This is reported as a lifecycle
safety failure, not a retrieval improvement. See `research/AGENTMEMORY_FINDINGS.md`.

## Fourth controlled core: Mem0

The harness also includes a pinned Mem0 search-policy arm from `mem0ai/mem0` commit
`19cb89aff472325c707f64b2f34ae6afdbf7faf7`. The vendored upstream
`mem0/utils/scoring.py` matches Git blob `e85a9cb8e8b263dbab898faa07578044c0a07386`
byte-for-byte. Because the sandbox lacks Mem0's default Qdrant/fastembed stack, this is
not a product run: raw `infer=False` semantics are represented with the same shared
32-D LSA embedding control, while Mem0's current over-fetch/threshold/ranking policy is
executed from the pinned scoring code.

At k=5 it matches dense LSA on positive retrieval: **0.958 / 0.958** core Hit/all-relevant
and **0.583 / 0.542** on the 500-record stress set. Its notable difference is the
semantic threshold: negative-empty-rate is **0.50**, so it abstains on half the negative
cases instead of always filling k with guesses. See `research/MEM0_FINDINGS.md`.

## Probe external providers

```bash
memory-bakeoff probe
```

This reports whether local packages/services are reachable. External adapters fail
closed: an unavailable engine is recorded as unavailable rather than silently replaced
with a simulation.

New result metadata records one of `baseline`, `controlled_core`, `raw_product`, or
`product` while retaining the ingestion mode. Source provenance and publishability are
also explicit. Fuzzy/subtext reconciliation is exploratory only and is excluded from
the authoritative `leaderboard.md`/`leaderboard.csv`. Result directories fail closed
when they already exist; `--allow-overwrite` is reserved for development/debug use.

## Run the whole raw-mode field

```bash
memory-bakeoff run \
  --providers bm25,tfidf_cosine,dense_lsa,hybrid_rrf,mem0,agentmemory,membukkit,habitus,claude_mem,hindsight \
  --mode raw
```

Claude-Mem reports **ineligible** in raw mode because its supported observation path invokes its compression agent. Hindsight is eligible in raw mode when its server is launched with the upstream-supported `HINDSIGHT_API_LLM_PROVIDER=none` configuration (chunk storage + retrieval without fact-extraction LLM calls). Because the server mode is not safely inferable from the client, the harness additionally requires `HINDSIGHT_RAW_LLM_PROVIDER=none` as an explicit run declaration. Run Hindsight again in product mode with its normal LLM pipeline for the separate product comparison. See `RUN_EXTERNAL.md` for setup and reproducibility requirements.

## Metrics

- Hit@5
- Recall@5
- Precision@5
- MRR
- all-relevant@5 (important for multi-hop)
- prohibited@5 (stale/failed evidence contamination; lower is better)
- useful-before-harmful (current/successful evidence ranked before stale/failed)
- negative-empty-rate (reported separately)
- retrieval latency
- exact retrieved context size (characters and words), so larger prompts are not a free win

A separate `scripts/topk_sweep.py` run records retrieval quality against context size across k=1/3/5/8/10. See `results/TOPK_FINDINGS.md`.

## Verified-outcome learning

`toy_adaptive_diagnostic` is a deliberately simple feedback-capable provider used only
to prove the harness can detect learning over repeated verified outcomes. **It is not
Habitus.**

Stock Habitus currently exposes retrieval traces but its public `record_outcome()`
credits output-decision paths, not the retrieval paths that supplied useful memories.
See `research/HABITUS_RETRIEVAL_CREDIT.md` for the small API extension required before
claiming to test Quality-Loop-style retrieval reinforcement.

## Reproducibility principles

1. The harness owns truth and receipts; the model does not grade itself.
2. Same corpus, queries, k, and scoring for every provider.
3. Provider-specific product behavior is preserved rather than faked.
4. Unavailable dependencies/services are reported explicitly.
5. Raw retrieval and end-to-end product tests are separate experiments.
6. Any future LLM-agent phase must pin model, inference settings, harness version,
   context budget, and repeated-run seed/configuration.

## Fifth controlled core: Claude-Mem search policy

Claude-Mem 13.18.0 (commit `fa6a1e9ec12d23f98326a9b26e243acb0819e105`) is
represented by controlled search-policy arms, not a full
product run: `claude_mem_fts5_core`, `claude_mem_chroma_lsa`, and
`claude_mem_chroma_lsa_no_recency`. With the shared LSA representation held constant,
the current Chroma policy scores only **0.208 Hit@5** on both core and stress because its
implicit 90-day window leaves only 9 benchmark memories eligible. Disabling only that
window restores **0.958 core / 0.583 stress Hit@5**, exactly matching dense LSA on recall.
The FTS5 whole-query phrase fallback scores zero on these paraphrased queries. See
`research/CLAUDE_MEM_FINDINGS.md`.

Earlier documentation incorrectly associated that commit with package 10.6.1; npm
10.6.1 records commit `d54e574251d7736cfd6030f8ba86b15fbebd3b50`. Archived
controlled result files remain unchanged.

## Hindsight runtime status

Hindsight is deliberately **not** assigned a pseudo-core score. Its real recall path is a
DB-backed semantic + BM25 + graph + temporal pipeline, so copying the algorithm into a
local Python provider would measure our reimplementation rather than Hindsight.

The main infrastructure blocker has nevertheless been solved: the preserved pg0 0.15.1
Linux binary in `vendor/pg0-bin/` successfully started **PostgreSQL 18.1 + pgvector
0.8.5** in this sandbox and accepted SQL. Hindsight's official `OpenAIEmbeddings`
provider also accepts a custom OpenAI-compatible base URL, so a future controlled run
can use the benchmark's shared LSA representation through a localhost `/v1/embeddings`
endpoint without patching Hindsight.

The remaining blocker is transfer of compiled Python runtime wheels (notably `asyncpg`)
into this network-isolated container. Hindsight's one-day release Actions package
artifact has expired, generic release/PyPI binary downloads cannot cross the current
connector boundary, and this GitHub installation exposes no writable user repo for a
temporary Actions relay. Therefore the current honest status is **database proven,
embedding seam proven, service runtime dependency-blocked, no score yet**. See
`research/HINDSIGHT_FINDINGS.md` and `vendor/pg0-bin/UPSTREAM.md`.
