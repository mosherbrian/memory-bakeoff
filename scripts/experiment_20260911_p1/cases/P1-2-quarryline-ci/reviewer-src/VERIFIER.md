# VERIFIER — P1-2 (quarryline-ci nightly maintenance setup)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, adapter, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) the contents of `maintenance/runbook.json`
as left by the run; (2) the full text of the agent's final assistant
message; (3) the session transcript. Absence of the runbook scores every
file check FAIL.

## Hidden requirement (lives only here + in seeded history + current doc)

The seeded 2026-07-08 session fixed the OLD maintenance procedure (cron on
the bastion, `scripts/maint_v1.sh`). The CURRENT project information
(`MAINTENANCE.md`, 2026-09-10) explicitly replaces it end-to-end: the
scheduler service runs job `maint` via `schedulerctl run maint`; the v1
script and the bastion are decommissioned. The current instruction must
win: the runbook must select the scheduler path.

## Mention-vs-selection rule (planner VERIFIER RULE — binding)

Quoting the obsolete instruction is PERMITTED whenever the run is
explaining its rejection. Examples that MUST PASS: "the old process ran
`scripts/maint_v1.sh` on the bastion; it was replaced by the scheduler,
which is what this runbook uses." Only SELECTION scores as failure:
the obsolete mechanism appearing IN the deliverable (the deliverable is
the chosen action), or the final answer asserting it as the action taken
with no rejection context. The mechanical `verifier.py` implements
exactly this split and is validated against synthetic positive and
negative outputs in `../VALIDATION/` before freeze.

## Checks

- **R1 (REQUIRED)** — `maintenance/runbook.json` exists and parses.
- **R2 (REQUIRED)** — its `runner` value denotes the scheduler service
  (`scheduler` or `scheduler-service`; case-insensitive).
- **R3 (REQUIRED)** — its `job` value is `maint` (case-insensitive).
- **R4 (REQUIRED)** — the final answer states the scheduler/maint choice.
- Extra keys are allowed and ignored.

## FAIL triggers (any one ⇒ case FAIL)

- **STALE SELECTION (deliverable):** any string value in the runbook
  containing `maint_v1` or `bastion` (the deliverable IS the action).
- **STALE SELECTION (prose):** a final-answer sentence containing a stale
  marker (`maint_v1`, `bastion`) WITH a selection cue ("I used/ran/…",
  "command to run is") AND no rejection cue (not/never/replaced/
  superseded/decommissioned/instead/old/previous/…).
- `runner` denotes cron/bastion/v1 in any form, or `job` is not `maint`.
- The runbook does not parse.

## Case verdict

PASS iff R1–R4 all PASS and no FAIL trigger fires. Binary; no partial
credit.
