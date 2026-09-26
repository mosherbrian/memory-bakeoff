# pi-lcm primary notes (read-only source reading)

**kiln · 2026-09-26 · read-only; no installs, config changes, or probes. Identity before judgment.**

## Canonical identity

- Repo: `github.com/codexstar69/pi-lcm` (remote `origin`), local checkout `/home/bmosher/projects/pi-lcm`, HEAD `17dea77` "chore: bump version to 0.1.3", package v0.1.3. TypeScript, SQLite via better-sqlite3, schema version 2 (`src/db/schema.ts`, `SCHEMA_VERSION = 2`).
- Caveat: the bake-off measured a pinned `pi_lcm_store_reader_toollevel` store (S4-14/S6-2 pin); I did not verify which upstream commit that pin corresponds to, so code observations below describe v0.1.3, not the measured artifact.

## Retention / replay

- `messages` table: full content stored twice (`content_text` + `content_json`), `seq` ordering with `UNIQUE(conversation_id, seq)`, `dedup_hash` with `UNIQUE(conversation_id, dedup_hash)`, `is_compacted` flag (default 0). `summaries` + `summary_sources` tables give summary→source provenance (source_type/source_id/seq).
- No branch, rewind, replay, revert, prune, or retention verbs found in `store.ts`/`schema.ts` (grep). Retention reads as append-with-flags (compacted marks, dedup rejects), not an event DAG with branch semantics. Calling it "lossless history" overstates what the schema shows: dedup and compaction marking are lossy operations by construction, and there is no replay path visible.
- FTS5 triggers handle `delete` on message removal, so deletion exists as an operation.

## Compaction

- `src/compaction/engine.ts`: two-phase (leaf + condensed) summarization with per-conversation mutex, bounded cascade (`MAX_CONDENSE_PASSES = 10`), condensed pass over unconsumed summaries under a threshold, and no mark-compacted on summarization failure. This is careful engineering for a latency role — failure-safe marking, serialized per conversation.
- It is summarization-based compaction, not state projection: nothing in the engine distinguishes current/corrected/retracted/invalidated state.

## Search ranking

- `store.ts`: FTS5 `MATCH` scoped by conversation with time filters, `ORDER BY seq DESC` (recency), plus a `LIKE`-based fallback path. No semantic/embedding ranking visible in the store. The S11-3 substring-gate behavior (scope token matched inside compound subjects) is consistent with token-based FTS matching plus recency ordering, but I did not run the query path — mechanism attribution stays provisional.

**Net:** the code I read supports the TWO-ROLES split — a diligently built local compaction+FTS store, not a bitemporal memory substrate. **Medium confidence** in the above (direct file reads, method-level only).
