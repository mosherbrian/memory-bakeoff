# Native versus one service: what stays local, what Zep would add

**kiln · 2026-09-26 · ≤600w · advice only, no installs. Sources: current Zep docs (help.getzep.com/concepts, read this session), Claude Code memory docs (c2), pi-lcm primary notes (c2-cont). Pi loader docs explicitly not re-read (Tern central).**

## Native side (current facilities)

Claude Code: tiered CLAUDE.md + rules + per-repo auto memory (versioned parts versioned, auto parts machine-local). Pi: agent-dir instruction files + pi-lcm SQLite/FTS as tool-callable recall. Local agents: operator-inserted slices. Cost: ~zero install, discipline-only maintenance. What native lacks as a mechanism: (a) **shared cross-host updates** — a correction made on Pi never reaches Claude Code except by hand-copying canonical; (b) **temporal lifecycle with valid-time** — nothing native records *when a fact became invalid*, only that text changed; (c) **governed shared access** — no per-agent scoping beyond file permissions.

## Service candidate: Zep (chosen for the missing mechanism, not a benchmark)

Zep's documented mechanism directly answers (a)+(b): a temporal Context Graph per user/graph addressable by `graph_id`, where new data **invalidates** prior facts by storing the invalidation time on the graph edge (Fact Invalidation), with source episodes retained as provenance and `graph.search` / `thread.get_user_context` as low/high-level retrieval. That is valid-time bookkeeping our native side entirely lacks and pi-lcm's schema (no temporal columns found) does not provide.

- **Update/delivery paths (docs-concrete):** ingest via `graph.add` (business data) and `thread.add_messages` (conversation); every thread message auto-ingests into the user's graph; retrieval returns an assembled Context Block the application places into the model request. Cross-host sharing falls out: any host with an API key reads the same graph.
- **Operational cost:** hosted SaaS (Flex/Flex Plus/Enterprise tiers for observations, debug traces); data leaves Brian's box; SDK dependency + network latency + vendor lock-in + per-use billing. Governance/audit/API logs are built in, which is a plus no native file gives. (Zep's OSS Graphiti library exists as a possible self-host path — **not evaluated this cycle**, named only so it isn't mistaken for the hosted product.)
- **Failure modes to expect:** silent extraction/invalidation errors (the lifecycle risk our bake-off keeps finding: false supersession now with a vendor model behind it), another dependency down, schema drift in custom entity/edge types.

## Advice

- **Native: deploy (keep). High confidence** — covers single-host preferences/procedures at ~zero cost; the c3 canonical-repo + views arrangement stands.
- **Zep hosted: watch. Low confidence** — the invalidation-time + provenance + shared-graph mechanism is the sharpest fit yet for the two genuinely missing mechanisms, but it buys a SaaS dependency for a workload Brian hasn't demonstrated (no multi-host shared-state task yet). Revisit when a named task needs cross-host updates or as-of truth; admit through a lifecycle gate (false-invalidation rate), never on retrieval scores.
- **Skip:** self-hosting Zep/Graphiti as a project — operating a temporal graph store to avoid a SaaS bill inverts the cost argument for one user.

**Net:** native remains the arrangement; Zep is the first service candidate selected for a named missing mechanism rather than a leaderboard number — and the bar for buying it is a demonstrated cross-host or valid-time need.
