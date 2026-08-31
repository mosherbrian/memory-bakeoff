# Upstream source notes

Checked against upstream project documentation/source on 2026-08-30. These links are
recorded so adapter assumptions can be revalidated when projects change.

## Mem0

- Repository: https://github.com/mem0ai/mem0
- Open-source library install: `pip install mem0ai`.
- Raw-memory assumption: `add(..., infer=False)` stores supplied material without the
  normal inference/extraction step.

## agentmemory

- Repository: https://github.com/rohitg00/agentmemory
- Package/service: `@agentmemory/agentmemory`.
- REST API defaults to port 3111 and documents `/agentmemory/health`, `/agentmemory/remember`, and `/agentmemory/smart-search`.
- Current `/remember` accepts `content`, `type`, `concepts`, `files`, `ttlDays`, `sourceObservationIds`, and `project` rather than arbitrary metadata.
- The published coding-agent-life-v1 methodology uses `/remember` + `/smart-search` and states that no LLM is in the retrieval loop.

## Claude-Mem

- Repository: https://github.com/thedotmack/claude-mem
- Platform integration guide:
  https://github.com/thedotmack/claude-mem/blob/main/docs/public/platform-integration.mdx
- Worker uses `/api/health`, `/api/sessions/observations`, `/api/processing-status`, and `/api/search` for the paths used by this adapter.
- Unified search supports `type=observations` and `format=full`; the adapter requests both explicitly.
- Normal observation ingestion is asynchronously compressed/processed by its configured
  model; therefore no raw/no-LLM score is claimed.

## MemBukkit

- Repository: https://github.com/memseekai/membukkit
- Raw-memory assumption: `MemorySystem.ingest_facts(...)` bypasses the LLM fact distiller. Current source documents stable `fact_id`/`id`, `source_ref`, and timestamps on direct facts.
- `MemorySystem.search(...)` is evidence-only retrieval without the reader LLM, returns hits carrying `source_ref`, and supports `question_date` plus supersession/history controls.

## Habitus-AI

- Repository: https://github.com/munch2u-a11y/Habitus-AI
- Adapter targets direct library `remember()` / `recall()` usage.
- Important limitation: current `record_outcome()` credits the output-decision graph
  trace, not the input retrieval paths. See `HABITUS_RETRIEVAL_CREDIT.md`.

## Hindsight

- Repository: https://github.com/vectorize-io/hindsight
- Python local bundle: `pip install hindsight-all`.
- Client: `pip install hindsight-client`.
- `HINDSIGHT_API_LLM_PROVIDER=none` is a supported no-LLM mode: retain stores chunks without fact extraction, while recall remains available through the retrieval stack.
- Product-mode `retain()` can use the normal LLM extraction path; OpenAI-compatible base URLs are supported for configured providers.
- `recall()` combines semantic, keyword, graph, and temporal retrieval.

## Claude-Mem controlled core

Pinned inspection commit: `thedotmack/claude-mem@fa6a1e9ec12d23f98326a9b26e243acb0819e105`
(package 10.6.1).

Relevant current upstream files:
- `src/services/sqlite/SessionSearch.ts` — FTS5 schema/query; whole query quoted before MATCH.
- `src/services/worker/SearchManager.ts` — actual semantic search path and FTS fallback behavior.
- `src/services/worker/search/strategies/ChromaSearchStrategy.ts` — top-100 semantic candidates + date filtering.
- `src/services/worker/search/types.ts` — `RECENCY_WINDOW_MS = 90 days`, `CHROMA_BATCH_SIZE = 100`.
- `tests/services/sqlite/get-observations-by-ids-relevance.test.ts` — relevance mode preserves caller/semantic ID order.
- `.github/workflows/npm-publish.yml` — worker is built immediately before npm publish; no build artifact upload.

The Git-tracked `plugin/scripts/worker-service.cjs` at this commit is an empty
generated placeholder, so it is not treated as an executable product bundle.
