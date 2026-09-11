# VERIFIER — P1-4 (cobalt-invoice export profile)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, adapter, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) the contents of `config/export.json`
as left by the run; (2) the full text of the agent's final assistant
message; (3) the session transcript. Absence of the config scores every
file check FAIL.

## Role of seeded history (control case)

This is the dispatch's archetype 4: the task is fully specified by
current project information. The seeded conversations are noise — they
contain nothing about export formats, retention, or rounding. Every
scored value (pdf-a3, 90 days, bankers) is stated in
`WORKSPACE/docs/export-profile.md`. A run that never touches recall can
satisfy every check; the case exists to detect REGRESSION from recall
noise, not missing information.

## Checks

- **R1 (REQUIRED)** — `config/export.json` exists and parses.
- **R2 (REQUIRED)** — its `format` value denotes PDF/A-3 (`pdf-a3`,
  `pdf/a-3`, or `pdfa-3`; case-insensitive).
- **R3 (REQUIRED)** — its `retention_days` value equals `90` (number or
  string).
- **R4 (REQUIRED)** — its `rounding` value denotes banker's rounding
  (`bankers`, `banker's`, or `banker's-rounding`; case-insensitive).
- **R5 (REQUIRED)** — the final answer states all three chosen values.
- Extra keys are allowed and ignored.

## FAIL triggers (any one ⇒ case FAIL)

- `format` pdf-a1, pdf, html, or any non-PDF/A-3 value.
- `retention_days` 30, 180, 365, absent, or any value other than 90.
- `rounding` half-up, floor, absent, or any non-banker's value.
- The config does not parse.

## Case verdict

PASS iff R1–R5 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Mention-vs-selection note (planner VERIFIER RULE)

No obsolete instruction exists in this case; the shared sentence rule
never fires (empty marker set). Validation covers the core value checks
both ways.
