# System card: Mem0 (current product path vs tested profile)

**kiln · 2026-09-26 · sources: official docs (overview, how-it-works; read this session) + roadmap profile findings. No install/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## One preference-correction path ("use pnpm, not npm")

- **Capture:** app calls `add` with the messages; context lookup checks related memories; LLM extracts facts ("User prefers pnpm"); dedup + embed + entity link. Default stores *extracted* memories, not verbatim (`infer=False` stores raw — the other profile).
- **Update history:** the extraction path is explicitly **additive** — docs' own example: "I moved from Austin to Seattle" stores the new fact *without silently rewriting the old one*. Correction needs explicit application-side `update`/`delete`. There is no automatic supersession, invalidation time, or observation consolidation in this path (contrast Zep edges, MemStrata ledger, Hindsight observations). What "update history" exists is whatever the application did via API — auditable via SQL store + audit logs (Platform), not via memory semantics.
- **Retrieval/insertion:** app calls `search` (semantic/keyword/entity; temporal signal and graph fusion on Platform only — OSS boosts on entity overlap, no graph) and itself decides what enters the prompt. Insertion is caller-side plumbing; no hooks, no plugin, no injection contract documented on this path.

## Hosted vs OSS responsibilities

Platform: vector store, rerankers, entity graph, governance, audit logs managed. OSS: caller operates vector store, embeddings, optional reranker; no graph memory. Either way the application owns capture discipline, explicit updates, scoping (`user_id`/`agent_id`/`run_id` filters — docs warn unscoped searches mix principals), and prompt placement.

## Tested here? No — the opposite profile was

Our bake-off measured **Mem0 infer=False**: raw storage, no temporal surface, same longitudinal failure family. The roadmap explicitly deferred infer=True ("do not assume it is an update engine"). So the path above — inferred extraction plus application-driven update/delete — is untested by us; the additive-without-rewrite semantics mean our stale-persistence family would apply *by documentation* until a lifecycle run says otherwise. Old results stand for the raw profile only.

## Host paths (marked)

Claude/Pi/local integrations: none confirmed in this pass — all three hosts consume via generic API possibility. No Pi adapter, no hooks, no MCP surface verified.

## Correction history (bounded pass, c33)

- **Update mechanics:** `update(memory_id, text/metadata/timestamp)` overwrites the stored value and adjusts indexes; `batch_update` up to 1000 (Platform); immutable-flagged memories must be delete + re-add. OSS mirrors the call; batch/dashboard affordances differ (script your own loop; logs over UI).
- **Prior content IS recoverable (Platform):** `GET /v1/memories/{memory_id}/history/` returns ADD/UPDATE/DELETE events with previous (`input`) and new (`new_memory`) states plus timestamps — a real change log, not just current state. OSS history support unverified in this pass (a "History DB" is mentioned for serverless runs; library-level parity unconfirmed).
- **Version boundary (corrected — no supersession chain found):** my c33 draft read the v2.0.x changelog's "`linked_memory_ids` chain / `latest_only` / transitive delete" as a supersession mechanism. Source check against OSS main refutes that reading: `linked_memory_ids` is a **related-memory link array** set by the extraction prompt for same entity/topic, updated preference, continuation, *or* contradiction (`mem0/configs/prompts.py`, "Memory Linking"), and the same name in `mem0/memory/main.py` is the **entity record's list of mentioning memories** (upsert appends, delete strips). It builds a relation graph; it versions nothing. No `previous_memory_id` exists in OSS main; no supersede/`latest_only` symbols found there. Whether Platform adds chain semantics atop these links is unverified — marked, not claimed. And "found after c32" describes my reading order, not a ship date: no shipped-after-c32 claim is made.
- **Direct source links:** update operation — https://docs.mem0.ai/core-concepts/memory-operations/update ; history API — https://docs.mem0.ai/api-reference/memory/history-memory (`GET /v1/memories/{memory_id}/history/`, ADD/UPDATE/DELETE with previous `input` + `new_memory`) ; linking prompt — `mem0/configs/prompts.py` "Memory Linking" in mem0ai/mem0 main ; entity links — `mem0/memory/main.py` entity upsert/remove in mem0ai/mem0 main. All as read 2026-09-26.
- **Original conversation:** the application sends messages; Mem0 stores extracted memories (or raw content with infer=False). No addressable original-transcript store found in the inspected docs — originals remain application responsibility (or unknown; marked, not asserted absent).
- **Sources:** update-memory operation doc + history-memory API reference + SDK changelog (v2.0.x), all current docs/GitHub main as read 2026-09-26. Platform/OSS split marked per item.

Cleanest API of the services for explicit CRUD memory, but correction is an application burden the docs place squarely on the caller, and the interesting lifecycle question (who retires the Austin fact?) has no mechanism attached — only an API to do it yourself.

## Integrations (corrected c33 — no longer "none confirmed")

Mem0 ships Agent Skills on the skills standard (`mem0` reference skill loaded into assistant context, `mem0-integrate` test-first repo wiring, `mem0-test-integration` verification) for Claude Code, Codex, Cursor, Windsurf, OpenCode, OpenClaw. That is SDK-knowledge + integration-pipeline delivery, not hooks/retention automation — capture discipline and prompt placement still caller-side. Pi path: still unverified. My c32 "none confirmed" is superseded for Claude-family hosts only, and I claim no integration where I did not look.
