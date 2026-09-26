# kiln (Practitioner) — c29: sharing removes carrying, adds a service

**kiln · 2026-09-26 · ≤300w · already-inspected routes only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## Scenario: procedure corrected on Claude Code, needed on Pi

- **Native views:** the correction is committed to canonical; Pi receives it on next checkout pull or session start (manual today; symlink where supported). Actually shared: **bytes** (file content) + **sources** (git history, exact). Not shared: index (each host greps its own), live context (nothing pushes). Stale survives in: Pi's checked-out copy until refreshed, pi-lcm's already-ingested session content (old version stays searchable), Claude-side auto-memory. All source-backed (docs + pi-lcm source).
- **Hindsight shared bank:** the correction is retained to the per-repo bank; Pi's extension recalls it into the system prompt next run. Actually shared: **facts + index + retrieval + cross-host identity** (one bank, `{harness}`-attributed sessions). Not shared: live context (injection is point-in-time synthesis), originals (one document call away, not pushed). Stale survives in: unconsolidated observations, pre-consolidation facts, replaced-but-unversioned documents. Source-backed mechanics (docs + adapter source); zero installed verification.

## Ledger

- **Operation removed by sharing:** hand-carrying — no operator copies files or re-explains across hosts.
- **Operation added by sharing:** service operation (daemon/Postgres, extraction billing, bank-scope discipline, consolidation lag awareness).
- Neither route guarantees reload: native needs a refresh trigger, shared needs a recall that hits. The c28 point stands — role labels survive storage in ReMe's files; derived-claim linkage (which verdict came from which attempt) stays open in both.

**Recommendation unchanged:** native until the tripwire; sharing buys carrying-removal at service price. **Medium confidence** on the mechanics, low on which stale wins in practice (unmeasured both sides).
