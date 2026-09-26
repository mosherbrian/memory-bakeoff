# Source card: Hindsight host path (what the agent actually receives)

**kiln · 2026-09-26 · sources: API docs (documents, recall) + integration source (`inject.ts`, `knowledge-injection.ts`, Pi adapter, changelog 0.1.x–0.7.x). No install/probe. Quoting ROLES.md: "maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## What the host gets vs what stays in service

- **Host gets rendered strings, not the store.** Auto-injection carries reflect synthesis, page snippets, or raw recall observations as bullet text inside `<hindsight_memory>` tags (system prompt on Pi; `additionalContext` on Claude). Fact IDs, `document_id`/`chunk_id` travel in API recall results, and `include.chunks` / `include.source_facts` can attach raw source text — but the auto-inject formatters consume **rendered strings**; whether the automatic recall call sets those include flags was not confirmed in this pass. Explicit tools (`hindsight_search_knowledge_pages`, `hindsight_read_knowledge_page`, `hindsight_reflect`) give the agent a pull route to depth.
- **Service retains everything else:** documents with `original_text`, chunks, graph links, observations with proof counts, consolidation state, bank config. Reachable via Documents API, not pushed to the host unasked.
- **Anti-feedback-loop is implemented:** transcript readers strip the `<hindsight_memory>` tag so injected synthesis is never re-ingested — a concrete answer to the retain→reflect→retain contamination worry.

## Retain IDs and replacement semantics (the failed-alternative question)

- Transcript retention is **idempotent append** (new turns only, retried on failure, session-tagged) — history accumulates, not replaced.
- Same-`document_id` re-retain **replaces**: old facts deleted, new ones created. Tag changes invalidate derived observations and queue re-consolidation (with co-sourced blast radius documented). No document-version history was found in the API surface (`content_hash` stored, but no prior-version endpoint seen) — so a corrected document destroys its failed alternative in place. Recovery of the superseded version requires retaining under a new ID, a discipline the API permits but nothing enforces. For Brian's "preserve failed alternatives with outcomes," this is the sharpest limit found: the system versions *beliefs* (observations refined, history preserved across evidence) but *replaces* documents.

## Correction and crediting (documented behavior)

Agents must credit used memories (0.7.0, mandatory blockquote); the verified-stale protocol is agent-ingested "Correction: <topic>" docs stating claim/truth/evidence. First-prompt injection can select reflection, pages, or raw recall. Reflect rendering is constrained by prompt (declarative past-tense, verbatim tables) after a real confabulation incident (0.8.6-blog) — evidence the loop is operated, not just shipped.

## Implication

The host-source route is: rendered synthesis by default, explicit pull for depth, document originals one deliberate API call away — good availability, gated surfacing. Failed-alternative recovery is the gap: replacement semantics at the document layer mean the bank remembers conclusions better than the attempts they replaced. Native files (git history) still win on that axis specifically.
