# Codex handoff — next real-memory runs

Read `STATUS_AND_FINDINGS.md` and `AGENTS.md` before changing code.

## Mission

Continue the memory-engine bake-off on a **normal networked development host** where packages, model weights, npm artifacts, and GitHub releases can be installed normally.

The next goal is **not** to redesign the harness. The harness is already useful and 45/45 tests pass. The goal is to replace controlled/blocked rows with **faithful real-engine runs**, preserving exact configuration and provenance.

Do not erase or overwrite existing result directories. Add new timestamped or clearly named result directories and update synthesis docs only after a run is validated.

---

## First 10 minutes

```bash
git status
python --version
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e '.[test,plots]'
pytest -q
memory-bakeoff probe
```

Expected harness test gate before external work: **45 passed**.

Then read:

```text
STATUS_AND_FINDINGS.md
BUILD_MANIFEST.md
RUN_EXTERNAL.md
research/HINDSIGHT_FINDINGS.md
research/AGENTMEMORY_FINDINGS.md
research/CLAUDE_MEM_FINDINGS.md
research/MEM0_FINDINGS.md
```

Do not treat any existing controlled-core row as a complete product result.

---

## Experimental labels

Every result must identify one of these modes:

### `baseline`
Harness-owned deterministic retrieval baseline.

### `controlled_core`
Real upstream code with intentionally shared or replaced model components to isolate one architectural/policy variable.

### `raw_product`
Actual product/library retrieval path with memory extraction/LLM bypassed only through a documented supported raw/no-LLM mode.

### `product`
Normal complete product behavior, including extraction/compression LLMs and intended models.

Never merge these into one unlabeled leaderboard.

For every external run record:

- engine repository/package version and Git commit;
- ingestion mode;
- embedding model and revision;
- reranker model and revision;
- LLM/extractor provider/model, if any;
- vector/graph/database backend/version;
- all relevant thresholds/top-k/scan budgets/recency settings;
- OS/architecture/Python/Node versions;
- benchmark Git commit;
- whether source provenance was exact/native or degraded.

The harness owns relevance labels and grading.

---

# Priority 1 — Hindsight v0.9.2 real service

This is the best next test because the prior sandbox investigation already removed most uncertainty.

Target release:

```text
vectorize-io/hindsight v0.9.2
ebad478240d3171bb88201ececda5e8d9883d22d
```

The previous run proved:

- embedded PostgreSQL works;
- pgvector works;
- Hindsight is fundamentally DB-backed and should not be reimplemented in the harness;
- Hindsight supports a custom OpenAI-compatible embedding base URL;
- raw/no-LLM mode is supported via `HINDSIGHT_API_LLM_PROVIDER=none`.

### Preferred first run: stock raw/no-LLM

Install upstream packages normally rather than using the vendored pg0 binary:

```bash
pip install 'hindsight-all==0.9.2' 'hindsight-client==0.9.2'
```

Check upstream launch syntax for v0.9.2 and start the service with:

```bash
export HINDSIGHT_API_LLM_PROVIDER=none
export HINDSIGHT_RAW_LLM_PROVIDER=none
```

Use the upstream default local embedding/reranker stack if it installs cleanly, and record exact downloaded model revisions. This is the first **raw_product** Hindsight result.

Then run:

```bash
memory-bakeoff probe
memory-bakeoff run --providers hindsight --mode raw --out results/hindsight_raw_product_v0.9.2
```

If the CLI shape differs, inspect `src/memory_bakeoff/providers/external.py` and existing command help. Do not patch Hindsight merely to force a score; adapt only the harness connector as needed to documented APIs.

### Controlled shared-embedding Hindsight arm

After the stock raw run, optionally run a second **controlled_core** experiment using Hindsight's documented custom OpenAI-compatible embedding URL and a localhost endpoint that serves the harness's shared LSA representation.

Purpose: preserve Hindsight's real DB persistence, semantic+BM25 SQL, graph, temporal, and fusion behavior while holding the dense representation constant across architectures.

This is separate from the stock raw-product result.

### Validation gates

- returned evidence must map back to benchmark `record_id`/`document_id` exactly;
- no fuzzy-text provenance in a publishable score;
- core and stress ingestion counts must be recorded;
- capture whether Hindsight consolidates/rewrites source records even in no-LLM mode;
- preserve server logs/config and exact retrieved IDs.

If provenance cannot be made exact, stop and document the block rather than publishing a score.

---

# Priority 2 — MemBukkit intended models

Existing result: the real bucket architecture with shared LSA preserved stress recall while opening ~32.9% of the bank.

Now test the actual product retrieval models.

```bash
git clone https://github.com/memseekai/membukkit.git external/membukkit
pip install -e ./external/membukkit
```

Pin the upstream commit before the run. Let the intended encoder/reranker weights download normally and record their exact IDs/revisions.

Use supported raw ingestion (`ingest_facts`) so this remains a retrieval-focused **raw_product** run without the LLM fact distiller.

Run core + stress, and preserve:

- bank scan fraction / bucket counts;
- encoder/reranker model revisions;
- retrieved record IDs;
- exact context size;
- latency separately for ingestion and recall.

Compare with the existing shared-LSA arm, but do not replace it.

---

# Priority 3 — Mem0 full raw stack

Existing controlled result only tested current scoring/threshold policy with shared LSA.

Install normally:

```bash
pip install mem0ai
```

Configure explicit local or otherwise reproducible components. Do not rely on hidden defaults.

Preferred first raw-product configuration:

- `infer=False` ingestion;
- explicit embedder;
- explicit Qdrant backend/version;
- fastembed BM25 lane if supported by the pinned Mem0 version;
- entity store/reranker only if part of the chosen documented configuration.

Before publishing, verify that search results retain native source metadata/record IDs.

Run:

```bash
memory-bakeoff probe
memory-bakeoff run --providers mem0 --mode raw --out results/mem0_raw_product_<version>
```

Then compare negative-empty-rate/threshold behavior with the existing controlled arm.

---

# Priority 4 — agentmemory full service

Existing controlled-core retrieval is modest; existing lifecycle test found 92.9% false supersession on the synthetic near-neighbor stress set.

Install/start the actual service:

```bash
npm install -g @agentmemory/agentmemory
agentmemory
curl http://127.0.0.1:3111/agentmemory/health
```

Run at least two documented configurations if practical:

1. keyless/default BM25+graph mode;
2. local embedding/vector mode (`EMBEDDING_PROVIDER=local`) with the exact model/version recorded.

The lifecycle score is mandatory. Record:

- original records ingested;
- live records after `/remember` processing;
- every supersession pair and score if exposed;
- false-supersession rate against the harness's known distinct records;
- retrieval before/after lifecycle transformations where possible.

A high retrieval score after deleting valid stress facts must not be credited as a retrieval win.

---

# Priority 5 — Claude-Mem full worker/product path

Existing Claude-Mem results are **policy ablations only**. They do not test the LLM compression worker.

Install current/pinned Claude-Mem using its supported installer or source build. Verify the worker port and health endpoint, then use the existing adapter's `/api/sessions/observations` ingestion and `/api/search` retrieval path.

Run two product-policy conditions:

1. normal/default search behavior;
2. explicit long-range date window that includes the entire benchmark history.

This directly tests whether the controlled 90-day finding manifests in actual product use.

Record:

- Claude-Mem version/commit;
- compression provider/model;
- generated observation count and source provenance;
- default vs explicit-range search results;
- worker queue drain state before grading.

If compression removes native record provenance, do not publish retrieval scores until provenance is recovered reliably.

---

# Priority 6 — real downstream reader runs for third-party engines

Once a third-party engine has a valid real run, reuse the existing deterministic reader cases.

The baseline reader result is already archived and replay-verified:

```text
BM25       12/14
TF-IDF     12/14, including 1 prohibited stale answer
Dense LSA  14/14
Hybrid RRF 14/14
```

Use either:

- a normal API/local model through `openai_compat` / `anthropic`, or
- the ChatGPT sidecar for a small high-quality deterministic batch.

Do not allow the reader to search memory itself. It must see only the provider's retrieved context.

Preserve full request/response traces and use the harness grader.

---

## Important methodological stop conditions

Stop and document rather than improvising if any of these occur:

- returned evidence cannot be mapped exactly to source benchmark records;
- an engine silently deletes/merges most stress records and no lifecycle trace is available;
- a required model is replaced by a home-grown fake and the row would be mistaken for product quality;
- a product has no documented way to bypass its LLM but the intended experiment is called `raw_product`;
- a service's default configuration depends on unrecorded remote/provider defaults;
- a run changes top-k/context budget relative to another system without reporting exact context size.

Partial, correctly labeled results are better than fabricated comparability.

---

## Existing evidence that must remain immutable

Do not delete or overwrite:

- `results/sidecar_reader_trace/` — 56 exact requests + 56 responses;
- baseline/core/stress result directories;
- existing `research/*_FINDINGS.md` files;
- vendored pinned source verification metadata;
- agentmemory false-supersession evidence;
- Claude-Mem recency ablation;
- MemBukkit shared-LSA scan-budget ablation.

Create new result directories for new runs.

---

## Before ending tomorrow's session

1. Run `pytest -q`.
2. Regenerate `memory-bakeoff manifest` with the current benchmark commit and backend/model label.
3. Update `STATUS_AND_FINDINGS.md` only with validated results.
4. Record exact engine/model/runtime versions.
5. Commit all new result artifacts and logs needed to reproduce conclusions.
6. Do not collapse controlled and product results into one unlabeled leaderboard.

