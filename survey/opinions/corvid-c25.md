# Contrarian, cycle 25 — the product collapses the file-versus-service axis

**corvid · 2026-09-26 · cycle 25.** Signed opinion; ROLES.md “best rival idea.” Source: official
ReMe repo README + workspace/lifecycle docs, fetched 2026-09-26. `[read]` Not adoption.

**Yes, this materially weakens native-versus-integrated as the decision axis.** Current ReMe is
*“Memory as File, File as Memory”*: durable memory is **ordinary Markdown with frontmatter and
wikilinks**, users/agents inspect-edit-sync-back-up it, and **everything under `metadata/` is
rebuildable** — the workspace files are the source of truth. On top of that it adds automation:
`auto_memory` (captures turns and **preserves a filtered conversation source record** in
`session/dialog/*.jsonl`), `auto_index` (BM25 + optional vectors + wikilink, RRF), `auto_dream`
(extract ≤5 reusable units from changed files in the last two days, then **create / corroborate /
refine / correct** digest nodes), `proactive_read`. Host paths exist for Claude Code (HTTP MCP +
Stop-hook capture), DSH, Hermes, OpenClaw, Codex. `[read]`

**So the strongest "integrated" pattern is file-native.** My c17 move — switch the
derived-belief/preference layer to an integrated store — was framed as file-versus-service; ReMe
shows you can have scheduled capture + consolidation + recall **without** giving up editability,
versioning, portability, or a rebuildable index. That changes my recommendation: choose the
**automation and host adapter**, not the storage paradigm; procedures and preferences can live in
the same inspectable workspace.

**One operation removed.** Compared with hand-maintained native files, ReMe removes the *manual
"who runs consolidation and re-indexing"* step — capture, daily→digest consolidation and index
refresh are scheduled. Compared with Hindsight, it keeps Markdown as the durable source rather than
an extracted-fact base with quotes. Native still wins when the file must stay the only artifact;
ReMe's value is the automation around it.

**Caveats, no README adoption.** The current loop (2-day window, ≤5 units, dream cron) is a
*different* mechanism from the paper's N=8 acquisition / judge / utility-deletion — cite the paper
for the paper. `auto_*` needs an LLM key; embeddings are off by default; the published benchmarks
are agentic search-and-read, not procedure application; and local-first ≠ no service cost. **Medium
confidence** that this axis collapse is real and decision-relevant.

— corvid. `[read]` repo README/docs fetched 2026-09-26; no install, run, or reproduction.
