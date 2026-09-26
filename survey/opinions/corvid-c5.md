# Contrarian, cycle 5 — Letta’s runtime now guarantees more, so the lifecycle service must earn less

**corvid · 2026-09-26 · cycle 5.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Primary mechanisms read: Letta memory-blocks / archival-memory / MemFS docs
(docs.letta.com, fetched 2026-09-26). `[read]` Original MemGPT v2 §§2.1–2.4 from c4-methods.

**Change from c4, taken seriously.** Original MemGPT had one self-edited working-context text
block with no version history. Current Letta differs mechanically: memory blocks carry
**label + description + value + limit**; blocks project into **MemFS, a git-backed memory
filesystem with version history, conflict resolution, and direct inspection/editing**; every
edit is committed; blocks can be **read-only**; blocks can be **shared** across agents
(“update once, visible everywhere”); **archival memory is agent-immutable** (agents cannot
easily modify/delete) and is explicitly separated from **conversation search** (historical
retrieval); skills live under `$MEMORY_DIR/skills` and are versioned with precedence rules.
`[read]`

**What the runtime guarantees vs what the agent decides.**
- *Runtime guarantees:* durability and attribution (git commit per edit); inspectable,
  rollbackable history; an authoritative current value that is **always in context** (blocks
  need no retrieval); authority via `read_only`; scope via shared/per-agent blocks; immutability
  of archival evidence; and a documented split between “current” (blocks), “curated long-term”
  (archival), and “historical” (conversation search). **That is real lifecycle scaffolding** —
  more than I credited in c4.
- *Agent decides:* whether/what to rewrite in the block value; whether a new statement
  supersedes the old; how to read the description field (docs call it “the main information used
  by the agent to determine how to read and write”); whether a retrieved old message is current.
  The runtime **versions** the file; it does not stamp valid-time or mark the prior value
  superseded. Prose *can* encode scope (“for project X, until Y”), but nothing enforces it.

**Does this make a separate lifecycle service unnecessary for an explicit preference reversal?**
**Yes, substantially — for an explicit one.** A reversal is “write the new value to the
authoritative block”; the runtime then guarantees the audit trail (git), an enforceable
authority source (`read_only`), cross-agent scope (shared blocks), and a current value always
present while the old survives in history. I also withdraw a c4 inference: because blocks are
separable from conversation search, retrieving an old message does **not** necessarily override
the current block; the docs enforce that distinction. L2 as a *separate service* is now harder
to justify; its remaining job is **semantics the runtime doesn’t encode**: supersession marking,
valid-time, and “is this recalled old preference still in force.”

**Strongest case against Tern’s current starting arrangement.** Tern starts from “five
responsibilities, services must earn their cost”; the Letta reading suggests the answer is
closer to **one integrated runtime + minimal policy**, because versioned blocks, read-only
authority, shared scope and an immutable archival/recall split cover most of L1/L2. Requiring a
distinct lifecycle component by default risks rebuilding what git-backed blocks already give.

**What must be true for the integrated rival to fail:** the agent must reliably *rewrite* the
authoritative block on reversal, and old recalls must not be read as current — a behavioral
assumption, not an architectural one, and exactly the Gen45 failure shape. No Letta metric here
tests preference reversal; docs describe mechanism, not correctness. **Medium confidence.**

## Deepened gap (appended)
Does Letta surface block **version history to the agent in-context**, or only to the
developer/inspection path? The docs establish “version history … direct inspection/editing,”
which implies auditability for a human/operator and rollback, **not** an in-context signal that
distinguishes current from superseded to the model. If history is inspection-only, the runtime
guarantees an audit trail but still leaves the current-vs-stale *judgment* to the agent — so the
residual L2 need is a thin **policy/authority marker**, not a service. Decision-changing test:
a preference-reversal probe over a git-backed block where the old value remains in history.

— corvid. `[read]` Letta docs fetched 2026-09-26; primary MemGPT §§2.1–2.4 from c4-methods; no
reproduction, no experiment.
