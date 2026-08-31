# Provider notes and fairness rules

## Two benchmark modes

### Raw mode
Tests memory retrieval with LLM extraction disabled where the product has a supported
path for doing so. This isolates storage/retrieval from summarizer quality.

- BM25: native.
- dense_lsa: native deterministic offline baseline.
- hybrid_rrf: native BM25 + dense baseline.
- Mem0: `add(..., infer=False)`.
- MemBukkit: `ingest_facts(...)` bypasses the LLM distiller.
- agentmemory: `/remember` + `/smart-search`; current keyless mode is BM25/graph without an LLM, with local embeddings an explicit opt-in.
- Habitus: direct `remember()` / `recall()`.
- Claude-Mem: **not eligible**; normal observation processing is LLM-backed.
- Hindsight: eligible when the server is launched with `HINDSIGHT_API_LLM_PROVIDER=none`; retain falls back to chunk storage while recall remains available. Raw runs also require the local declaration `HINDSIGHT_RAW_LLM_PROVIDER=none` so the harness never silently assumes the server mode.

### Product mode
Uses each project's intended ingestion/extraction path. This is the correct mode for
end-to-end product comparisons, but requires model/API configuration for systems such
as Claude-Mem and Hindsight.

## Critical identity disambiguation

- `agentmemory` means `rohitg00/agentmemory` (the current TypeScript coding-agent
  memory service), **not** the unrelated older PyPI package of the same name.
- `Claude-Mem` means `thedotmack/claude-mem` (Bun/TypeScript worker + Claude Agent SDK),
  **not** older similarly named Python packages.

## Scope and temporal filtering

The local baselines do **not** use hidden scope metadata to pre-filter candidates; scope
must be resolved from the query text. For explicit as-of cases, the harness supplies
the structured cutoff to providers that expose an as-of API, while the question also
contains the date in text. Report native temporal/scope filtering as a capability, and
do not silently give one engine metadata filtering that another must infer.

## Negative questions

Many retrieval systems always return top-k results. Negative/unanswerable behavior is
therefore reported separately (`negative_empty_rate`) and does not dominate the main
retrieval score.

## Result ownership

The harness owns relevance labels, prohibited/stale labels, receipts, and metrics.
Model self-assessment never changes ground truth.


## Product-mode provenance release gate

LLM-backed extractors may rewrite observations. A product-mode provider is not eligible
for publishable ID-based scoring until returned memories can be mapped to originating
benchmark records through native provenance/metadata (or an explicitly documented,
provider-neutral source-tag protocol). Fuzzy text matching is useful for diagnostics but
is not accepted as ground truth.

## Adapter provenance details

### agentmemory
Current `/agentmemory/remember` does not accept arbitrary metadata. The adapter stores
the harness record ID in the memory `type` field as `memory-bakeoff:M###`. Queries never
contain this marker. `/smart-search` may return compact rows, so after agentmemory has
selected and ranked a stable ID the harness reconstructs the canonical original text
for the reader. This preserves the engine's ranking while avoiding fuzzy text matching.
The project's own published coding-agent-life benchmark also uses `/remember` followed
by `/smart-search` with no LLM in the retrieval loop.

### Hindsight
The current Python client accepts a Python `datetime` for `retain(timestamp=...)`; the
adapter passes the original timestamp object and reads `RecallResponse.results` first.
`document_id`/metadata are used for provenance when the client returns them.

### Claude-Mem
Search explicitly requests `type=observations&format=full`. Normal observation ingestion
remains product-mode-only because the supported worker path asynchronously compresses
observations with its configured model. Product-mode ID scoring remains gated on native
source provenance surviving that rewrite.

### MemBukkit
`MemorySystem.ingest_facts(...)` is a documented direct/no-distiller path. The adapter
sets `source_ref` to the harness record ID and uses evidence-only `MemorySystem.search`,
which exposes `source_ref` on each hit and supports as-of filtering/history controls.
