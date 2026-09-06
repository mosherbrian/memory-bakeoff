# The rivals harness

`~/rivals/review-generation` is the blind two-reviewer gate this project runs
before every handoff. It lived only on Brian's laptop until Gen120, which meant
the two fixes made to it that day - per-reviewer worktree isolation, and honouring
the reviewers' own severity - existed nowhere else and would have died with the
box.

These are versioned copies. `~/rivals/` remains the live path the doorbell and the
checklist reference; treat this directory as the backup of record and copy changes
both ways deliberately, because two files that can drift will.

**What it does.** GLM 5.3 and 5.3-flash review the repository independently and
blind to each other, using Pi so they read the source themselves rather than a
summary the implementer chose to write. The implementer is the weakest reviewer of
its own work and the author of the handoff the others read.

**Two properties worth preserving if this is ever rewritten:**

1. **Each reviewer gets its own git worktree.** They used to share one checkout,
   and this project's witness tests deliberately mutate a frozen file and restore
   it. Reviewer A's test run made reviewer B see a tampered tree, and B correctly
   reported a defect it could not attribute. Reviewers sharing mutable state are
   not independent - they are each other's confounder.
2. **The verdict is read, never inferred.** An early version regexed the opening
   prose for phrases like "is sound" and read two agreeing reviews as a
   disagreement. If the token is absent that is UNDECLARED, and UNDECLARED
   escalates; it is not licence to guess.
