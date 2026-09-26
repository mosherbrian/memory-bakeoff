# System card: Attestor (deterministic bitemporal backend)

**kiln · 2026-09-26 · sources: product docs attestor.dev + inside_attestor page, PyPI `attestor` page, MCP listing (repo cited as github.com/bolnet/attestor, MIT). Docs-level only; no install/probe. Identity note: agent-team memory product — not a security/attestation tool of similar name. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs, principles, COVERAGE as context.**

## Correction/provenance mechanism (as documented)

- **Write-time deterministic supersession:** on every add, same (entity, category, namespace) with different content → old row marked superseded (`valid_until=now`, `superseded_by=<new_id>`), zero LLM in the loop. Conversation ingest uses an LLM extractor plus a four-decision resolver (ADD/UPDATE/INVALIDATE/NOOP), each decision carrying `evidence_episode_id`.
- **Bi-temporal replay:** every memory carries event time (valid_from/valid_until) + transaction time (t_created/t_expired); nothing deleted (except `compact` on archived); entity timeline + point-in-time replay; supersession chain preserved.
- **Provenance:** agent_id, session_id, source_episode_id per memory; namespaces + RBAC + tenant isolation; CLI inspect/export for audit.
- **Retrieval:** six-step deterministic pipeline (~200 flat tokens/call claimed); timeline/chronology queries.

## Host integration required

Python library, Starlette REST, or MCP server (memory_add/get/recall/search/forget/timeline + resources/prompts + SKILL.md); CLI (doctor/add/recall/timeline/compact/update/forget/inspect/api/serve); backends postgres+neo4j / arangodb / cloud; embeddings provider auto-detect. Install cost: services to operate (or cloud account), schema/config ownership, embedding provider. Not a drop-in file.

## Correction carried (c66 response): forget/retention deletion exists in current docs (`memory_forget`, `compact`, retention controls) — my card's "nothing deleted" describes the audit-trail default, not the absence of deletion paths. And the uniqueness/oversized verdict is softened: deterministic supersession + replay is *uncommon* on the inspected roster, not proven unique; team-scoped packaging may still fit a solo user who wants exactly those semantics — oversized is a cost judgment, not an established mismatch.

Distinct vs roster: deterministic no-LLM supersession + bitemporal replay + evidence-linked chain is genuinely unduplicated (MemStrata nearest on determinism, single-host; Hindsight on observations, SaaS-shaped). But the packaging (multi-agent RBAC/compliance/tenant isolation, Postgres+Neo4j) targets agent teams and regulated chat, not one user with three hosts. The useful operation for Brian — deterministic supersede-with-evidence plus replay — rides inside team-ops machinery he would operate alone. Token-budget marketing (21×, 100% recall) not imported. **Watch; coverage: resolved-mechanism-relevant.**
