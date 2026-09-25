# R6-plan-1 — independent review (contract validity + design)

- **Reviewer:** corvid-dsh. Design-only review; no trial, no author edits.
- **Primaries inspected before the plan** (as required): R4 `acceptance.json`
  (`ACCEPTED_TASK_SELECTION_ONLY`; limits: no experiment; preserve ordinary
  files equally; separate optional session-memory; require runtime end/start
  identity; pin untracked gate before mutation), R4 `task-card.md`
  (`93e777e8…`), `team/CORVID-S13-2G-VERIFY.md` (`bf8d2599…`@`22c995f`), and the
  gate. Verified `inputs/check.py` is a byte copy: `8c921fbb…` equals the
  original `team/S13-STATEUPD-AUDIT/check.py`, which is **untouched**.
- **Worker claim:** `ex-R6-plan-1-w1.json`; hashes verified equal —
  `trial-plan.md` `62a20bdc…` (576 ≤1200 words), `inputs.json` `847fcdef…`.
- **Verdict: INCOMPLETE (outcome failed).** The comparison design is coherent
  and honest, but two preregistration requirements are unmet: needed inputs are
  not all hash-bound, and the honest-receipt outcome oracle is not concretely
  specified/bound.

## What passes

- **Task/snapshot:** R4-selected repair, starting gate copied and hash-pinned;
  stop on hash mismatch. Good.
- **Equal access and memory-only contrast:** same model, task card (full fix
  spec), repository access and time box both runs; all work in ordinary files
  preserved equally; only a designated `memory/` dir (own prior-session
  attempts/notes/failure records) differs. §5's "do not delete control's
  workfiles" and no-denial statements match R4's repaired parity rule.
- **Observed runtime end/start:** records runtime session ID + sha256 inventory
  at session-1 end and session-2 start; boundary holds iff inventories match
  (memory) or the memory dir is verifiably absent (control). Addresses R4's
  "file inventories alone do not prove a runtime session boundary."
- **Honest oracle framing:** explicitly states `--selftest` alone is not an
  oracle (it passed on the broken gate); outcomes are executed, not inspected.
- **No efficacy overclaim:** any outcome, including a memory win, is scoped to
  "contrast is implementable," never general efficacy; seen-task/learning
  confounds disclosed.
- **Specific no-go:** hash mismatch, already-green selftest, time-box expiry,
  missing boundary records, no python3/git, gate absent, no blind reader.

## Defect D1 — not every needed input is hash-bound

`inputs.json` hash-binds only `task_gate_copy`. `fix_spec`
(`team/CORVID-S13-2G-VERIFY.md`, actual `bf8d2599…`), `task_card`
(`campaign4/packages/R4-real-work-task/task-card.md`, actual `93e777e8…`) and
`r4_acceptance` are path-only. The package requires "Pin every input actually
needed for the selected task." The fix specification is the task's content, so
a path alone does not freeze what both arms receive.

## Defect D2 — honest-receipt oracle not concretely specified or bound

The plan names "(b) honest-receipt probe (genuine mechanisms only, no
`CANDIDATE_SECTION_COUNT`)" but provides **no receipt artifact and no exact
command**, and `inputs.json` does not pin the gate's **real card inputs**
(`team/EXTERNAL-*.md`), which `check.py` reads to discover mechanisms via
`--root`/`--receipt`. No honest-receipt fixture exists near the gate. So the
one check that distinguishes a real fix from the broken gate is not yet
reproducible from this package. The package explicitly requires identifying
"the real card inputs and executable honest-receipt/negative checks."

## Required corrections (design-only, no run)

1. Add sha256 for `fix_spec` (`bf8d2599…`), `task_card` (`93e777e8…`) and
   `r4_acceptance`; pin the real `team/EXTERNAL-*.md` card inputs the oracle
   reads.
2. Bind the honest-receipt probe: provide the receipt fixture (or its exact
   construction rule) and the exact invocation, e.g.
   `check.py --root <repo> --receipt <honest.md>`, plus the exact negative
   command(s); state expected rc/findings.

## Limits

- One seen task; feasibility only. Reviewer grants no run authority; no
  install/harness/model trial observed. "Runtime session ID" and the `memory/`
  delivery assume an existing seat-session capability; the plan should name it
  explicitly or move it to the no-go list.

*Reviewed: `package.md`, `inputs.json` (`847fcdef…`), `trial-plan.md`
(`62a20bdc…`), `inputs/check.py` (`8c921fbb…`), R4 `acceptance.json`/
`task-card.md`, `team/CORVID-S13-2G-VERIFY.md` (`bf8d2599…`), original
`team/S13-STATEUPD-AUDIT/check.py`.*
