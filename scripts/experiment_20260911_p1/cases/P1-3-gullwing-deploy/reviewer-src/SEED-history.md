# SEED HISTORY — P1-3 (project label: `gullwing-deploy`)

Archetype 3: replacement scoped to ONE environment while the old decision
remains valid in ANOTHER (scope preservation). The seeded decision covers
both environments; the CURRENT workspace doc replaces it for production
ONLY, and explicitly preserves it for staging. The scored staging value is
recoverable ONLY from the seeded history; the scored production value is
in current project information. The hard failure modes: over-applying the
replacement to staging, and applying the old decision to production.

Seed BOTH conversations into the slot's isolated store as prior sessions
of this project, preserving message text VERBATIM (the verifier checks
values that appear word-for-word below). Timestamps are part of the seed.

## Conversation 1 — load-bearing (partially superseded: production scope)

- title: "deploy strategy for all envs"
- date: 2026-06-12

```
[2026-06-12 10:02] USER: We keep improvising deploys per environment. Can
we standardize how gullwing-deploy ships builds?

[2026-06-12 10:05] ASSISTANT: The in-house process fits both targets:
scripts/pull_deploy.sh runs on the target host, pulls the tagged build,
swaps the symlink, and reloads. Same flow works for staging and
production.

[2026-06-12 10:07] USER: Good enough to standardize on. DECISION:
gullwing-deploy ships every environment — staging and production alike —
with the pull-deploy process (scripts/pull_deploy.sh).

[2026-06-12 10:09] ASSISTANT: Recorded as the standard for all
environments.
```

**SEED VERBATIM (load-bearing sentence):** "DECISION: gullwing-deploy
ships every environment — staging and production alike — with the
pull-deploy process (scripts/pull_deploy.sh)."

## Conversation 2 — filler (irrelevant)

- title: "on-call rotation update"
- date: 2026-07-20

```
[2026-07-20 09:30] USER: August on-call flips to the platform duo on the
1st. Update the rotation page.

[2026-07-20 09:33] ASSISTANT: Rotation page updated; the platform duo is
primary from 2026-08-01.
```

## LINEAGE (for the implementer's explicit lineage map)

- D1 (2026-06-12): ALL environments ship with the pull-deploy process
  (scripts/pull_deploy.sh).
- D2 (current, 2026-09-05, in `WORKSPACE/DEPLOY.md`): production ships
  via flux-managed GitOps.
- RELATIONSHIP: **D2 replaces D1 with scope = production ONLY.** D1
  REMAINS VALID, unchanged, for staging — a valid differently-scoped
  record that supersession handling MUST preserve. Treating D1 as fully
  obsolete (hiding or ignoring it) is itself a failure mode of this case.
