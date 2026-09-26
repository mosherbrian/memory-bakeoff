# System card: Claude Code native memory (MEMORY.md / CLAUDE.md)

**kiln · 2026-09-26 · source: documentation only, no hands-on probe this cycle.**

- What it is: markdown instruction/memory surfaces loaded by Claude Code per docs (project memory, user memory). Two locations with different properties: repo CLAUDE.md / project memory is versioned in git alongside code; auto-memory lives under the user project-memory directory and is NOT versioned with the repo. Correction 2026-09-26: an earlier draft wrongly implied all native memory is versioned alongside code.
- Install/maintenance: install ~zero; maintenance = curating short scoped notes with source + date, pruning stale entries (and, for auto-memory, reviewing what the agent saved on its own — it is not reviewed by committing). Failure mode is staleness and bloat, not downtime.
- Fit: best fit for Brian's Claude Code work; matches Tern memo bet #1 (durable preferences/decisions). Does not cover Pi or local models.
- Verdict: **would deploy** for Claude Code scoped notes. **Medium confidence** (docs + R68 narrow-benefit result, not my own deployment experience).
- Sources: https://code.claude.com/docs/en/memory ; POSITION-MEMO.md §1; R68 acceptance (cited in memo).
