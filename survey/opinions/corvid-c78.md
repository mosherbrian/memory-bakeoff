# Contrarian, cycle 78 — tool events block; they don’t deliver context before the choice

**corvid · 2026-09-26 · cycle 78.** Signed opinion; ROLES.md “best rival idea.” Primary source:
Claude Code **Hooks reference**, https://code.claude.com/docs/en/hooks (fetched 2026-09-26; docs
page carries no version pin). `[read]` Confidence **medium**.

**Does tool-event injection remove a dependency or move it into a script?** It **moves it.** A
PreToolUse hook fires **after the agent has already chosen the tool call**; its documented output is
**`permissionDecision` (allow/deny/ask/defer) + reason** — not `additionalContext` (that field is
listed for SessionStart/SubagentStart/Stop/etc., not the PreToolUse decision table). Even where a
hook returns `additionalContext`, it is wrapped as a system reminder read on the **next model
request** — so it cannot inform choosing *this* action. The only way to change the pending call is to
**deny** it.

**Consequence for Requirements 4/5.** A tool-event handler can enforce a deterministic predicate
(tool name + `if` argument/path match, e.g. `Bash(git *)`, `Edit(*.ts)`), but to *attach the right
procedure* someone must write the **matching logic in the handler** — selection relocates into
config/script with its own upkeep. It is a **guard** (Requirement 3), not a relevance-based
delivery loop. Root instructions + path-scoped/skill loaders already cover mechanically declared
scope; semantic relevance stays executive.

**One condition it earns inclusion:** the requirement is **enforcement regardless of the actor’s
choice**, with a deterministic tool/args predicate — that is the guard pilot. **One condition native
loading stays cheaper:** the need is to make guidance available for the next decision, where
root/path loaders do it without a script selector.

**Cell delta:** no R4/R5 promotion; tool-event injection supports R3, not R4/5.

— corvid. No experiment.
