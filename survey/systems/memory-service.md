# System card: hosted memory service (e.g. Zep-style temporal/graph layer)

**kiln · 2026-09-26 · source: documentation/paper only, no hands-on probe this cycle.**

- What it is: external service holding memory with search, temporal structure, lifecycle APIs; clients on Claude Code / Pi / local models call it over network.
- Install/maintenance: obligations depend on hosting. Self-hosted = user runs the server + SDK + auth + backup, owns schema upgrades, embedding-model pins, monitoring. Hosted (vendor-managed) = no user-managed server/backups; obligations shift to subscription cost, data leaving the box, vendor lock-in, and API/lifecycle tuning. Correction 2026-09-26: an earlier draft wrongly implied all services require user-managed servers/backups. Common failure modes either way: extra latency, another dependency down, silent update/supersede errors (our bake-off flagged false-supersede risk in lifecycle arms — see memo's "admission, revision, forgetting" frontier). Our controlled comparisons do not rank full products.
- Fit: only justified for a named workload needing shared access across agents or temporal queries; overkill for single-user scoped notes.
- Verdict: **would watch**, deploy only behind a demonstrated paraphrase/temporal/shared-access miss. **Low confidence** in any product choice (agreeing with Tern memo §3).
- Sources: https://arxiv.org/abs/2501.13956 (Zep, via memo); POSITION-MEMO.md §§3,7.
