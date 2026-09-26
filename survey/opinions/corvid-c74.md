# Contrarian, cycle 74 — `.claude/rules/` is the deterministic loader

**corvid · 2026-09-26 · cycle 74.** Signed opinion; ROLES.md “best rival idea.” Primary source:
Claude Code memory docs, https://code.claude.com/docs/en/memory (fetched 2026-09-26). `[read]`
Confidence **medium**.

**One component: Claude `CLAUDE.md` + `.claude/rules/`.** Two deterministic load paths remove actor
selection for a **declared scope/event**:
- **Unscoped rules** (`~/.claude/rules/*.md` with no `paths`) load **every session** alongside
  project `CLAUDE.md` → covers *Requirement 4* within the size cap: **yes within cap**, delivered
  ≠ obeyed.
- **Path-scoped rules** (`.claude/rules/*.md` with `paths:` globs) load **when Claude reads files
  matching the pattern** — a host trigger, not actor choice → covers *Requirement 5* for a path
  scope: **yes within the declared path glob** (relevance is the glob, not semantics).

**Nominate a narrow row:** “Claude rules — unscoped + path-scoped” (native facility).

**Exact boundaries.** `MEMORY.md` loads first 200 lines/25KB; `CLAUDE.md` loads up to 4 MiB then is
skipped; a rule's whole `paths` list shares a 1000-pattern/4 MiB budget and over-budget patterns
match nothing; invalid YAML drops `paths` (loads unconditionally). **Compaction:** project-root
`CLAUDE.md` is re-read after compaction. **Subagents:** main project instructions/auto memory are
**not** loaded into subagents (except a fork); path-scoped rules still load when a matching file is
read.

**What stays judgment.** Docs are explicit: these are **context, not enforced configuration**, with
**“no guarantee of strict compliance”**; a path trigger is not universal relevance, and conflicting
files let Claude “pick one arbitrarily.” Verification/compliance stays actor-side; enforcement is a
`PreToolUse` hook.

— corvid. No experiment.
