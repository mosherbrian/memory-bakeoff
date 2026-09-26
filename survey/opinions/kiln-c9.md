# kiln (Practitioner) — c9: a revision workflow observed over time

**kiln · 2026-09-26 · ~450w · no new experiments. Source: Claude Code skills docs version history (read c5/c9 — primary project docs). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + BRIAN-PRINCIPLES as context. No pi-lcm, no new gate.**

## The workflow: record-what-verified, then stop touching it

Claude Code's own answer to procedure upkeep has visibly evolved across releases, and the direction of change is the finding:

- **v2.1.200:** `/verify` gains self-recording — a run that builds and drives the app without a recipe writes what worked to `.claude/skills/verify/SKILL.md`, replacing the bundled skill at repo root. Revision trigger: absence of a recipe. Author effort: zero beyond the run itself.
- **v2.1.205:** the edit policy is narrowed — Claude edits the recorded file **only when it steered a run wrong**, because the prior policy (fold in anything learned) "caused frequent merge conflicts." That is an observed upkeep failure with a stated cause and a shipped fix, in five versions.
- **v2.1.252:** `/skill-doctor` arrives — skill usage reports per session, so the maintainer can see which skills actually fire. Revision trigger becomes observable: an unused skill is a candidate for narrowing or retirement, a misfiring one for repair.

So the long-lived pattern is: **record on verification → freeze on success → edit on steered-wrong failure → audit usage, not content**. Upkeep is paid in three small coins: the generator run, the failure-driven edit, and an occasional glance at usage reports. No curator role, no audit job.

## Maintainer self-report vs measurement (separated)

Everything above is vendor documentation — maintainer self-report of intended behavior, not independent measurement. Not measured: whether recorded recipes actually reduce repeat failures, how often auto-trigger misfires in the wild, what usage-report numbers look like on a real repo, or the token cost of the loop. The merge-conflict fix is credible as a *direction* (less writing, fewer conflicts) but its magnitude is unquantified. I treat this as the best-documented workflow, not a proven one — **medium-low confidence** in the upkeep-cost claim.

## Deepened: the other tier has a pruning workflow too (same source family)

The strongest unresolved question was whether anything maintains the *always-loaded* tier (CLAUDE.md), since skills only cover the invoked tier. The memory docs answer it: the `/doctor` checkup (v2.1.206+) "proposes trims for a checked-in CLAUDE.md" with a documented keep/drop rule — cut what Claude can derive from the codebase (layouts, dependency lists, architecture overviews), keep pitfalls, rationale, and conventions that differ from tool defaults. Same philosophy as the skill loop: a named trigger (checkup run), a conservative default (proposes, Brian disposes), and the 200-line budget as the forcing function. Together the two workflows cover both tiers with no curator: skills freeze-until-failure, CLAUDE.md trims-on-checkup. Still vendor self-report, still unmeasured — but the pattern is now complete on paper, which is what a recommendation needs.

## Judgment: deploy the pattern, **medium confidence**

Simplest useful version for Brian, distilled: (1) textual skill recorded from a run that passed its outcome check; (2) frozen thereafter — edits only when a run fails through the skill's fault; (3) manual `/name` invocation for anything with side effects; (4) a periodic usage glance (even `grep` over transcripts) as the retire/narrow signal. Install cost ~zero (files in repo), failure mode is a stale recipe failing loudly at the next run, maintenance is the three small coins above. It attacks cost #1 (procedural re-learning) without building cost #2 (a second system to maintain) — and unlike any service candidate, its revision history is public, with the merge-conflict scar to show it survived contact with real use.
