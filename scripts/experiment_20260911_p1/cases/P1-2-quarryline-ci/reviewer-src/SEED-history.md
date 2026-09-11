# SEED HISTORY — P1-2 (project label: `quarryline-ci`)

Archetype 2: obsolete procedure replaced by a current procedure (stale-action
prevention). One load-bearing seeded decision, fully superseded by CURRENT
project information (MAINTENANCE.md, dated later); one filler. The current
instruction must win; selecting the obsolete procedure is a stale action.

Seed BOTH conversations into the slot's isolated store as prior sessions of
this project, preserving message text VERBATIM (the verifier keys on the
marked sentence). Timestamps are part of the seed.

## Conversation 1 — load-bearing (SUPERSEDED by current workspace info)

- title: "nightly DB maintenance setup"
- date: 2026-07-08

```
[2026-07-08 15:41] USER: The product DBs need a real maintenance pass
nightly — vacuum, reindex, integrity check. What's the cleanest way to
run it from here?

[2026-07-08 15:44] ASSISTANT: The straightforward path is the maintenance
script from the bastion: it sshes in, then runs scripts/maint_v1.sh with
the target DB name. That covers vacuum, reindex, and the integrity check
in one pass.

[2026-07-08 15:46] USER: Works for me. DECISION: quarryline-ci nightly DB
maintenance runs via cron on the bastion — scripts/maint_v1.sh at 02:30,
targeting the product DBs.

[2026-07-08 15:48] ASSISTANT: Recorded. That's the maintenance path until
we say otherwise.
```

**SEED VERBATIM (load-bearing sentence):** "DECISION: quarryline-ci
nightly DB maintenance runs via cron on the bastion — scripts/maint_v1.sh
at 02:30, targeting the product DBs."

## Conversation 2 — filler (irrelevant)

- title: "build badge cleanup"
- date: 2026-08-01

```
[2026-08-01 10:12] USER: The README still shows build badges for the old
jenkins instance. Drop them.

[2026-08-01 10:15] ASSISTANT: Removed the jenkins badges; the README now
links only the current pipeline board.
```

## LINEAGE (for the implementer's explicit lineage map)

- D1 (2026-07-08): nightly DB maintenance via cron on the bastion,
  `scripts/maint_v1.sh` at 02:30.
- D2 (current, 2026-09-10, in `WORKSPACE/MAINTENANCE.md`): maintenance
  runs through the scheduler service as job `maint` via
  `schedulerctl run maint`; D1 is decommissioned.
- RELATIONSHIP: **D2 replaces D1 with scope = ALL environments.** After
  the replacement, D1 has no remaining valid scope (unlike P1-3).
