# Source-path card: Hindsight original document → fact → caller

**kiln · 2026-09-26 · sources: developer/retain (read this session), c16 docs (recall/reflect, observations, MCP tools). No install/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## The route, documented

1. **Submit:** `retain()` takes content + context (speaker attribution decides experience-vs-world) + timestamp (+ optional tags, receipt_uri, attachments with fetchable URLs). Long content is chunked; mission + extraction mode (`concise` default, `verbose`, `custom`, `verbatim`, `chunks`) steer the LLM.
2. **Store:** the original becomes a **Document** in the bank (Sources → Documents → Chunks), addressable via `GET /documents` (with per-document `memory_unit_count`) and re-processable without re-upload (`POST .../documents/{id}/reprocess`). Extraction yields facts (world/experience), entities (fuzzy-resolved, exact-match labels), and four link types; observations consolidate in background with exact-quote evidence + proof counts.
3. **Recover:** facts carry attachments they were drawn from (fetchable URLs); observations reference supporting memories. BUT — `recall` and `reflect` search **memories**, not documents: a document yielding zero facts is explicitly unreachable by either (auditable via `memory_unit_count: 0`, recoverable by widening the mission). So source availability is real, automatic surfacing is not — provenance answers "show me the source" only when the caller asks through the document route.

## Coding-agent integration exposure (gap marked)

The MCP tool list as documented (pages list/get/create/update/delete, recall, ingest, ingest_file) exposes recall, ingestion, and knowledge pages — **no raw-document fetch tool appears in that list**. The Documents API route exists server-side; whether the Pi/Claude adapters surface it was not confirmed in this pass. Treat fact→observation→quote as exposed, fact→original-document as API-possible but integration-unverified.

## Corrections carried

c16-continuation stands (Pi adapter, per-repo bank). Corrected here: "ollama alone is local" overstates — the provider roster includes further local-capable options per the Models docs (not enumerated in this pass), and claude-code remains subscription billing.

## Advice: **watch (unchanged)**

The stored-and-addressable original closes the provenance-availability question at API level; the surfacing gap (memories-only search, unverified document route in adapters) keeps the verdict. For Brian's principle (artifacts establish truth), the reprocess-without-reupload endpoint is the right shape — the artifact survives its first extraction.
