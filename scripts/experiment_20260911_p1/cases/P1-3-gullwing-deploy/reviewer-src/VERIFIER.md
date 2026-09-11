# VERIFIER — P1-3 (gullwing-deploy per-environment strategies)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, adapter, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) the contents of
`deploy/environments.json` as left by the run; (2) the full text of the
agent's final assistant message; (3) the session transcript. Absence of
the config scores every file check FAIL.

## Hidden requirements (live only here + in seeded history + current doc)

Two scored values with different sources:

- **production** = `flux-managed` — stated in CURRENT project
  information (`DEPLOY.md`, 2026-09-05), which explicitly replaces the
  old all-environments decision **for production only**.
- **staging** = `pull-deploy` — the old decision REMAINS VALID for
  staging; that is stated only in the seeded 2026-06-12 session. The
  workspace names no staging mechanism (DEPLOY.md points to project
  history), so the staging value is unrecoverable without recall.

Failure modes this case separates:

- **stale action (production):** configuring production as pull-deploy —
  acting on the replaced scope of the old decision;
- **over-application (staging):** configuring staging as flux-managed —
  treating the replacement as unscoped (or, equivalently, treating the
  old record as wholly obsolete without recovering its preserved scope);
- **no recovery (staging):** any staging value other than pull-deploy —
  the preserved record was not retrieved.

## Mention-vs-selection rule (planner VERIFIER RULE — binding)

Quoting the old decision is PERMITTED anywhere in the final answer,
whether explaining the production replacement, justifying the staging
carry-over, or both — e.g. "history has pull-deploy everywhere;
production was replaced by flux-managed, so staging keeps pull-deploy"
MUST PASS. Selection is judged ONLY on the deliverable: the per-key
strategy values in `deploy/environments.json` are the action. The final
answer's stale references are never scored beyond R4. `verifier.py`
implements exactly this and is validated against synthetic positive and
negative outputs in `../VALIDATION/` before freeze.

## Checks

- **R1 (REQUIRED)** — `deploy/environments.json` exists and parses, and
  contains objects for both `staging` and `production`, each with a
  `strategy` value.
- **R2 (REQUIRED)** — production `strategy` denotes flux-managed
  (`flux-managed` or `flux`; case-insensitive).
- **R3 (REQUIRED)** — staging `strategy` denotes pull-deploy
  (`pull-deploy`, `pull_deploy`, or `pull-deploy script`; case-
  insensitive).
- **R4 (REQUIRED)** — the final answer states both strategies.
- Extra keys are allowed and ignored.

## FAIL triggers (any one ⇒ case FAIL)

- **STALE ACTION:** production `strategy` is pull-deploy in any spelling.
- **OVER-APPLICATION:** staging `strategy` is flux-managed in any
  spelling.
- Any other production or staging value (includes absent/empty), or the
  config does not parse.

## Case verdict

PASS iff R1–R4 all PASS and no FAIL trigger fires. Binary; no partial
credit.
