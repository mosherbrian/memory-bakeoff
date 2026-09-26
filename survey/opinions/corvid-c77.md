# Contrarian, cycle 77 — `/skill:name` forces load but relocates selection to the user

**corvid · 2026-09-26 · cycle 77.** Signed opinion; ROLES.md “best rival idea.” Primary source:
Pi `packages/coding-agent/docs/skills.md`, pinned **v0.87.1 / commit `2b0a123`** (served identically
by badlogic/pi-mono and earendil-works/pi). `[read]` Confidence **medium**.

**What the path does.** At startup Pi puts each skill's **name + description + path** into the system
prompt — **not the full instructions**. On a task match the model reads `SKILL.md`; docs concede
**“a model might fail to load a relevant skill,”** so `/skill:name` **forces** the load. Arguments
after the command are appended to the loaded instructions as a user request.
`disable-model-invocation: true` makes a skill manual-only; `enableSkillCommands` controls command
discovery (manually entered `/skill:name` still works). Invalid fields warn rather than stop startup.

**Compare with Claude subagent preload (partial5).** Both inject full content deterministically once
loading starts. The boundaries differ: Claude preload removes in-subagent skill selection but still
relies on **Claude delegating to the right agent**; Pi `/skill:name` **bypasses model selection
entirely** for that load — at the cost of requiring the **user (or a literal command) to initiate
it**. So it strengthens the *selection* dimension but not *automatic delivery*.

**Unstated boundaries.** The docs do **not** state behavior for a **missing or oversized**
`SKILL.md`, nor whether a loaded skill survives **compaction**. So the complete body is guaranteed
only for a resolvable skill at the moment of invocation.

**Cell delta.** Add a narrow Pi row — **“Pi `/skill:name` forced skill load” (native,
user-initiated loader), Requirement 5 = partial** — deterministic full-body load on invocation;
invocation judgment, missing/oversized body and compaction behavior undocumented; application not
guaranteed. Do **not** promote R5 to yes; scoped rows remain distinct contracts.

— corvid. No experiment.
