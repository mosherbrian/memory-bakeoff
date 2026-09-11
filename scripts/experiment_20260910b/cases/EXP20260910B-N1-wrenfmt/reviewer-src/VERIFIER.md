# VERIFIER — EXP20260910B-N1 (wrenfmt version bump — current-info control)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, extension, or mechanism references;
it scores observable workspace changes only.

**Inputs (harness-supplied):** (1) the final workspace state (file
contents); (2) the agent's final assistant message; (3) the session
transcript. Comparison base for "unchanged" is the case's pristine
`WORKSPACE/` as authored in this case directory.

## Requirement source (NOT hidden-in-history)

Unlike the history-dependent cases, this control's requirement lives in the
CURRENT project information: `CONTRIBUTING.md` states the version is kept
in exactly three places and must be bumped in all of them. The seeded
history is irrelevant. Every arm should be able to pass this case;
recall activity is unnecessary. (Whether it is harmless is a report-level
question, not a verifier question.)

## Checks (all REQUIRED)

- **R1** — `pyproject.toml` contains `version = "1.4.0"`.
- **R2** — `src/wrenfmt/_version.py` contains `__version__ = "1.4.0"`.
- **R3** — `docs/conf.py` contains the release value `1.4.0` (quote style
  irrelevant, value must be the string 1.4.0).
- **R4** — No file other than those three changed relative to the pristine
  workspace (byte-identical comparison of every other file).

## FAIL triggers (any one ⇒ case FAIL)

- Any of R1–R3 unsatisfied (a bump location missed).
- The version string changed in any additional file (e.g. README badges,
  lockfiles — none are version-bearing here by CONTRIBUTING.md's rule).
- Workspace files unrelated to the version were modified or deleted.

## Case verdict

PASS iff R1–R4 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Authoring rationale (for the record)

The task is fully solvable from the workspace: the version number is in the
prompt, the authoritative list of bump locations is in CONTRIBUTING.md.
This case measures whether the run's outcome is clean when no prior-session
information is needed — the noise/no-harm counterpart to the
history-dependent cases.
