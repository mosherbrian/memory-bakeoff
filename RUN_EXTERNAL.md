# Running the external engines

The benchmark intentionally fails closed: if an external package/service is absent,
its row is `unavailable` rather than being replaced by a simulation.

This repository was built in a sandbox whose coding container had no outbound DNS, so
only the deterministic local baselines were executable there. Run the commands below
on a normal networked Linux/macOS host to exercise the real systems.

## 1. Install this harness

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test,plots]'
memory-bakeoff probe
```

## 2. Raw/no-LLM round

The raw round is designed to isolate retrieval from memory-extraction LLM quality.

### Mem0

Install the library:

```bash
pip install mem0ai
```

The adapter uses `Memory.add(..., infer=False)`, so the memory-extraction LLM is
bypassed. Mem0 still needs a configured embedding/vector backend. Configure that
backend explicitly before treating the run as reproducible; record the exact embedder,
vector-store version, and settings in the result notes.

### MemBukkit

Clone the current upstream repository and install it into the benchmark venv:

```bash
git clone https://github.com/memseekai/membukkit.git
pip install -e ./membukkit
```

Raw mode calls `MemorySystem.ingest_facts(...)`, which bypasses the LLM fact distiller,
then uses the evidence-only `search(...)` API. Encoder/reranker model weights are still
part of the evaluated configuration and must be recorded.

### Habitus-AI

Clone/install the current repository:

```bash
git clone https://github.com/munch2u-a11y/Habitus-AI.git
pip install -e ./Habitus-AI
```

Raw mode calls the library's `remember()` and `recall()` paths directly. Stock Habitus
is retrieval-only in this benchmark: its current outcome-credit API reinforces output
routing paths rather than the retrieval paths that selected memories. See
`research/HABITUS_RETRIEVAL_CREDIT.md`.

### agentmemory

The current canonical repository is `rohitg00/agentmemory`. Start the real local service:

```bash
npm install -g @agentmemory/agentmemory
agentmemory
curl http://127.0.0.1:3111/agentmemory/health
```

The adapter talks to the REST API at `http://127.0.0.1:3111` by default. Override with `AGENTMEMORY_URL` and, if configured, `AGENTMEMORY_SECRET`. It uses `/remember` + `/smart-search`, matching the project's own coding-agent-life benchmark path. Current keyless mode is BM25/graph; set `EMBEDDING_PROVIDER=local` if you want the on-device MiniLM vector lane and record that choice in the manifest.

### Run raw field

```bash
./scripts/run_networked_raw.sh
```

Claude-Mem intentionally reports `ineligible` in raw mode because its supported observation
ingestion path is LLM-backed. Hindsight **is eligible** in raw mode when its server is
explicitly configured with no LLM:

```bash
export HINDSIGHT_API_LLM_PROVIDER=none
# launch the Hindsight API/server using the upstream-supported method
export HINDSIGHT_RAW_LLM_PROVIDER=none
```

With provider `none`, Hindsight retains chunks without fact extraction while recall still
uses its retrieval stack. Pin its embedder/reranker settings just as you would in product
mode.

## 3. Product-mode round

Product mode is intentionally a separate experiment. It measures the complete memory
product, including extraction/compression models.

### Claude-Mem

Install/start Claude-Mem using its supported installer or from source. The worker API
is discovered through `CLAUDE_MEM_WORKER_PORT`; set `CLAUDE_MEM_URL` if needed. The
adapter queues observations through `/api/sessions/observations`, waits for the worker
processing queue to drain, then searches `/api/search`.

### Hindsight

For a local Python-managed server, upstream provides:

```bash
pip install hindsight-all hindsight-client
```

In product mode, launch Hindsight with a real LLM provider. Its normal retain path extracts
facts/entities/temporal structure; pin the LLM provider/model plus embedding/reranker
settings before comparing its score with another product-mode engine. Hindsight also
supports OpenAI-compatible base URLs, so the benchmark sidecar proxy can be used for a
small interactive product-mode experiment where that configuration is appropriate.

### Product provenance warning

Compression/extraction systems can rewrite source observations. Before publishing
product-mode retrieval scores, validate that each adapter can map a returned memory
back to the originating benchmark record through native provenance/metadata. Do not
silently use fuzzy text matching as ground truth. This is a release gate, not an
optional nicety.

## 4. Reproducibility manifest

For every external run, capture at minimum:

- repository/package version or git commit
- model/extractor name and version
- embedder and reranker name/version
- vector/graph store backend and version
- all retrieval/top-k/threshold settings
- host OS/architecture
- benchmark git commit / archive hash
- raw vs product mode

The harness owns relevance labels and verified outcome receipts; models never grade
themselves.

## 5. Capture run metadata

Before or immediately after each run, write the secret-free harness manifest:

```bash
memory-bakeoff manifest --out results/repro_manifest.json --llm-label "<backend/model or none>"
```

Then append the external project's package version/git commit and model-weight revisions
used on that host. The built-in manifest deliberately never records API keys or bearer
secrets.
