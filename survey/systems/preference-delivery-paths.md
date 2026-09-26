# Preference delivery paths: one correction, three hosts

**kiln · 2026-09-26 · ≤500w · advice only, no installs/probes. Sources: current Zep docs (adding-business-data, retrieving-context, concepts — read this session), Claude Code memory docs (c2), pi-lcm primary notes. Pi config docs not re-read (Tern central). Concrete correction traced: "use pnpm, not npm".**

Storage ≠ capture ≠ ingestion ≠ retrieval ≠ application. No host collapses all five; every gap below is a place the correction dies silently.

## Claude Code

- **Capture:** Brian says "remember pnpm" → Claude may auto-save, or Brian edits `~/.claude/CLAUDE.md` / `CLAUDE.local.md` directly. **Ingestion:** a file edit is instantly stored; an auto-memory write lands in a topic file behind the MEMORY.md index. **Retrieval:** CLAUDE.md loads every session (always-visible); auto topic files load only if the index (200 lines/25KB cap) still references them. **Application:** arrives as context, not enforcement — obeyed when specific and uncontested, ignored on conflict (resolution is arbitrary). Deps: file checkout, index headroom. **Failure point:** stale auto-entry outlives a reversal; or the entry falls past the index cap and silently stops loading. Native files *can* carry explicit status/validity lines ("superseded 2026-09-26: …") — cheap, no extraction needed.

## Pi

- **Capture/ingestion:** manual — operator writes the canonical preference file; nothing observed auto-extracts. **Storage:** file in/visible to the agent dir; pi-lcm FTS holds session text as recallable archive. **Retrieval/application:** file content enters context per the harness load path (order unverified); pi-lcm hits arrive only via tool call. Deps: checkout/symlink freshness, operator discipline. **Failure point:** view drift — Pi's copy fixed while canonical moved on. Mitigation is the c3 single-writer rule, not machinery.

## Zep

- **Capture/ingestion:** app calls `graph.add` (text/message episode with `created_at`, `source_description`, metadata); writes to one graph complete **sequentially** and ingestion "can take a few minutes" (docs). Extraction builds fact edges; a mis-resolved correction invalidates the wrong fact — vendor-model version of our false-supersession family. **Retrieval:** `thread.get_user_context()` auto-searches (semantic + full-text + graph) using the **four most recent thread messages as the query** — a pnpm correction is returned only if those messages retrieve it; custom templates control format, not relevance. **Application:** the docs are explicit — the Context Block is **untrusted input**, kept out of system/developer channels and passed as user-level data or tool_result. A preference delivered as data can be outvoted by instructions. API access is therefore no guarantee the correction governs behavior. Deps: network, key, ingestion lag, template, app-side prompt placement. **Failure points:** lag (recent correction missing from block), wrong-edge invalidation, data-channel demotion.

## Verdict

For one explicit correction, native files win on every host: instant ingestion, visible storage, explicit validity lines, zero dependencies — **would deploy, medium confidence**. Zep's path is the only one with shared cross-host delivery and valid-time invalidation, but it adds lag, extraction risk, and data-channel status: **watch, low-medium confidence**, earned only by a demonstrated cross-host need. Never claim "API access delivers context" — retrieval returns a string; only placement plus instruction priority decides what the model does.
