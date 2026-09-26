# Reading note c74 — Letta budget enforcement: does an over-budget change ever get rejected?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 74.**
Skeleton first; **requirement 2** (structural budget limits). Question: follow current Letta Code
source from memory constraints to actual **validation/commit/merge/compile** call sites — can an
over-budget change **reach active context**? Check ordinary and background writes, configured
limits, bypass/override, observable failure. Distinguish Git precommit validation from harness
loading; **/doctor warning is not rejection**. Bounded source trace (tree + named call-site files),
no whole-repo audit, no model calls/probe/install. Deliverable: proposed exact rating
(yes/no/partial) for Letta requirement 2 + the exact missing boundary if partial. Source map:
systems/letta-memfs-fit.md.

*(trace + rating appended below)*

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c73.md.