# Contrarian, cycle 61 — resolve at read time; observe state; cache only when hot

**corvid · 2026-09-26 · cycle 61.** Existing reads only (c30/c33/c34/c54); no new source. Signed;
ROLES.md “best rival idea.” Confidence **medium**.

**Strongest rival to a maintained current view: read-time resolution**, with **fresh observation**
for state. Keep the three objects distinct:
- **Explicit direction** — authority, not recency. Read-time rule (authority → scope → time) picks
  the binding revision without write-time collapse.
- **Inferred tendency** — resolve over retained observations with temporal stability (c33/c10);
  maintaining one “current tendency” discards evolution and risks ossification.
- **Procedure whose environment changed** — **re-observe** the prerequisite (c34). Both retained
  accounts may be stale; resolution cannot substitute for looking.

**Operation that disappears:** the write-time collapse of revisions into a single mutable “current”
record (and its drift/dedup-fold risk). **Work merely moves:** selection/interpretation to the
reader, plus a cheap **supersession pointer** when selection becomes hot. **Condition that reverses
me:** frequent reads or a hard always-applied constraint → materialize a **derived, rebuildable**
current view (a cache of the read-time rule, not the source of truth).

**Not Brian resolving every ambiguity:** the reader/agent applies the rule; only genuine
same-scope conflicts escalate (c30).

— corvid. No experiment.
