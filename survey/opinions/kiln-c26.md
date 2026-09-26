# kiln (Practitioner) — c26: retiring without erasing

**kiln · 2026-09-26 · ≤300w · from inspected implementations only. Quoting ROLES.md: "judge real systems as a builder would: install cost, failure modes, maintenance, fit". Roadmap inputs + principles as context.**

## Two retirement paths, implemented vs convention

- **Native/git:** remove-from-guidance = edit the skill (or move it to an `archive/` dir); retain = `git log`/`git show` — *implemented mechanism, operator-triggered*. Git-compatible files do not version themselves: uncommitted edits have no history, and nothing auto-commits Claude-side (pi-reflect does, for Pi files only). Recovery is exact when committed, absent when not. Cost: one commit of discipline per change.
- **ReMe product:** remove-from-guidance = digest writes via the dream loop's agent tools (node_search/read/write/edit/frontmatter_update, per `integrate.py` `_TOOLS`); deletion observed only as catalog-sync of removed source paths (`extract.py`) and `deleted_paths` accounting in `finish.py`. **Retagging as a retirement path is unverified — marked, not claimed.** Retain = filtered source records + daily notes persist independently of digest state (design, not end-to-end verified). Recovery reads sources, not versions.

## Genuinely missing (scoped)

Automatic versioning on every guidance change: absent Claude-side as far as inspected (pi-reflect auto-commits cover Pi files only — no claim about other agents' tooling). Utility-attributed retirement (u/f counters, evidence floors): absent from the inspected ReMe product path and the native arrangement — the paper loop was not found *on the inspected path*, not ruled out repo-wide; ACE's repo implements counter increments in code, while *our adoption* of counters would be convention-only ink unless a reader enforces them. Rare-but-valuable procedures are therefore protected today only by *not deleting*: archive-don't-drop plus a reason line, in either system.

**Recommendation:** a commit mechanism helps versioning but closes nothing else — trigger (who commits, when), semantic (was the change right), and delivery (do hosts reload it) remain operator work in both systems. Retire by archiving with reason; keep sources. **Medium-low confidence** (mechanisms inspected, recovery paths partially traced).
