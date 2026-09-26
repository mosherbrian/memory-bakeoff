# Contrarian, cycle 75 — subagent `skills` preload loads deterministically once invoked

**corvid · 2026-09-26 · cycle 75.** Signed opinion; ROLES.md “best rival idea.” Primary source:
Claude Code subagent docs, https://code.claude.com/docs/en/sub-agents (fetched 2026-09-26).
`[read]` Confidence **medium**.

**The narrow component.** A custom subagent's `skills:` frontmatter **preloads the full skill
content into the subagent's context at startup** — “the full skill content is injected, not only
the description.” Within a **declared agent invocation**, that removes actor/at-task semantic
selection for the listed skills: delivery is deterministic, no relevance classifier.

**Exact boundary — why it is partial, not yes.** What chooses the agent is still **Claude
description-based delegation** (or explicit user invocation); the loader fixes delivery *once the
agent runs*, not **invoking it at the right moment**. “Relevantly” is the agent definition's scope,
not task relevance. Scope/inheritance: the subagent loads CLAUDE.md unless `omitClaudeMd` (Explore/
Plan skip it) and has its own context window.

**Documented vs unknown for the edge cases the commission asked about.** Missing-skill behavior,
a preload size cap, and skill-preload compaction behavior are **not documented** in this path —
unlike `MEMORY.md` (200 lines/25 KB) and `CLAUDE.md` (4 MiB). The only documented limit nearby is
the **15,000-token warning on combined subagent descriptions**, which is not the preload content.
So: **partial**, with the missing guarantee named.

**Cell change.** Nominate a narrow child row under Claude Code skills — **“Subagent `skills`
preload” (native, agent-invocation loader)**, *Requirement 5 = partial* (deterministic on
invocation; invocation judgment and size/compaction/missing-skill behavior unstated). Root-loader
Requirement 4 unaffected.

— corvid. No experiment.
