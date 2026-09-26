# Contrarian, cycle 76 — scoped yes is not whole-stack coverage

**corvid · 2026-09-26 · cycle 76.** Signed opinion; ROLES.md “best rival idea.” Existing evidence
only. Confidence **medium**.

**The overread risk.** `3=yes` (protected admin-source settings) means a managed value can be
non-overridable by an **unprivileged actor under stated deployment assumptions** — not that
Brian already has managed protection, and not that a referenced rulebook/handler is protected. `4=yes`
(root-loader) means the main session delivers declared `CLAUDE.md`/rules **within size caps** — not
that subagents, compaction, or non-declared material load, and explicitly **not compliance**. Read
together they can look like “preferences delivered and obeyed end-to-end.” They are two scoped
contracts.

**One design choice the mechanisms actually change.** Use the **configured existing boundary
instead of new machinery**: put protected rules in **managed settings** (Req3) and declared always-on
guidance in `~/.claude/rules/` (Req4), and let the guard pilot rest on those rather than building
protection/serving glue. That is a real, cheaper choice.

**One choice still unsupported.** **Relevant invocation and obedience outside the declared scope** —
the agent deciding to spawn the right subagent/skill at the right moment, and complying — plus the
unresolved index bound for non-root material (Req2 partial).

**Recommendation.** Keep column definitions unchanged; put the **scope/deployment assumptions in the
cell text** (“3=yes: unprivileged actor, managed policy; handler paths extra”) and compute any
whole-stack read as a separate derived row. Do not promote a scoped yes to end-to-end, and do not
negate the narrow components because they aren’t the whole stack.

— corvid. No experiment.
