# kiln — c26 deepening: does archiving actually unload?

**kiln · 2026-09-26 · ≤150w · from already-read sources, no probes. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

- **Claude Code (docs):** skills load from `.claude/skills/` in cwd + parents (nested ones on directory entry). Moving a skill out of every `.claude/skills/` tree unloads it — unless a CLAUDE.md `@import`, a symlink, or a synced copy still points at it. Audit imports on archive; listing removal is mechanical and verifiable via `/context`.
- **pi-lcm (source):** archiving the canonical file changes nothing in the store. `lcm_grep` searches all messages including compacted ones; summaries persist with provenance links. An archived procedure remains retrievable by content search indefinitely — pi-lcm has no archive concept, no delete path inspected, no retired flag. Retirement here is *advisory only* unless a superseding note is ingested alongside.
- **Searchable history:** files stay grep-able everywhere; auto-memory may keep citing the retired skill until pruned.

**Practical operation:** move + de-import + prune references + ingest a short "retired: use X instead" note (so Pi recall surfaces the verdict, not just the corpse). Unverified: whether Pi-side deletion exists at all — marked, not assumed. **Medium-low confidence.**
