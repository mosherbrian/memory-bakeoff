# Procedure maintenance: the /verify + run-skill-generator pattern

**kiln · 2026-09-26 · ~500w · worked source example only, no blanket winner. Source: current Claude Code skills docs (code.claude.com/docs/en/skills, read this session — Agent Skills open standard). No installs/probes. Roadmaps + BRIAN-PRINCIPLES as context.**

## The example (primary-source, with outcome check and update path)

Three bundled skills cooperate to stop re-learning how to build and check the app: `/run` launches it, `/verify` builds and runs it **against the running app instead of tests/typechecks alone** (the outcome check — "confirm a code change does what it should"), and `/run-skill-generator` records the working recipe (install commands, env vars, launch script) as a per-project skill at `.claude/skills/run-<name>/`. When `/verify` succeeds without a recorded recipe, it writes what worked to `.claude/skills/verify/SKILL.md` so later runs and other agents follow the same steps. The update path is documented and conservative: re-run the generator when the build/launch changes, and Claude edits the recorded file **only when a run steers it wrong** (failed command, missing step) — a change that deliberately avoids per-session diffs and merge conflicts (pre-v2.1.205 folded in every lesson and conflicted).

## What is reused, how staleness is noticed, who pays

- **Reused:** the recorded recipe (commands + env + launch), loaded only when the skill triggers — progressive disclosure keeps it out of context otherwise, with `references/` for detail and `!`-injected live output grounding each run in the current tree.
- **Changed applicability noticed by:** failure. A stale recipe surfaces as a failed run, which triggers the documented edit. There is no background freshness check — staleness detection IS the next run failing.
- **Upkeep paid by:** the person whose run breaks (one edit, reviewed by commit) plus the one-time generator run per project. No audit job, no curator role.

## Three forms compared on this example

1. **Textual procedure** (SKILL.md steps): cheapest to author/review; costs inference at every use and can drift from the tree. Fits stable checklists. Here it is the recipe itself.
2. **Executable helper** (scripts beside the skill, `!`-injected output, `allowed-tools` grants): pays authoring + permission review once, then runs deterministically — the launch script and diff-inlining in the docs' own `summarize-changes` example. Fits machine-checkable steps. Promotion from (1) is earned by repeated unchanged success.
3. **Episode reconstruction** (rebuilding the recipe from past session transcripts): zero authoring, maximum risk — it preserves whatever happened to work once, including workarounds, with no outcome check attached. The docs' pattern exists precisely to avoid this: record what *verified*, not what *happened*.

## Costs the source did not measure

Token cost of loaded skill content across turns (docs warn to keep bodies concise but give no numbers); staleness detection lag (a rarely-run recipe rots silently until needed); skill-trigger reliability (a recipe that never triggers might as well not exist); multi-agent divergence (two agents recording rival `verify` recipes). None are reasons to reject the pattern — they are the upkeep budget to watch.

## Gap deepened: trigger reliability (same source)

The most consequential unmeasured cost turned out to be partially documented after all. Auto-triggering keys on `description` + `when_to_use` (truncated at 1,536 chars in the skill listing); malformed frontmatter fails silently (skill loads with no fields); and the docs' own guidance for side-effecting procedures is `disable-model-invocation: true` — manual `/name` invocation, never auto-trigger. For Brian's recurring procedures that means: the safe default is explicit invocation, and the trigger description is itself a maintenance item (key use case first, under the cap). This strengthens the card's verdict rather than changing it: textual skills with manual invocation have the fewest silent-failure modes of any form compared here.

**Verdict: would deploy this pattern for Brian's recurring procedures (textual first, helper on earned repetition, manual invocation for side effects), medium confidence** — documented update path with failure-driven edits is the lightest maintenance story I have seen in primary docs.
