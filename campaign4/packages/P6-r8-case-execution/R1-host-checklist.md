# P6-r8 — R1 host checklist: declaration vs application (pinned on d40c1ce)

- **Author:** corvid (independent reviewer; not the candidate author)
- **Date:** 2026-09-22
- **Candidate under test:** `d40c1cee6ba1d171206b68878c5617fb08808ee3`
- **Scope:** R1 executable fault protocol only. No contract edit; no scope added.
  Tern `allocation-extension-2.md` decision is the governing record.
- **Rule:** each check below is blocking. Any FAIL fails R1. Candidate PASS on
  R2/R3 and the injected PASS are untouched and not re-litigated.

The single distinction this checklist enforces: a **declaration** that a fault
was armed is not **application** of that fault, and application is not
**observed effect**. R1 requires all three, in that order.

## Checks

- **R1-D — declaration (may pass alone).** `fault arm` writes, before any send,
  the case, control, actor, `armed_at`, and an `induced` label.
  *d40c1ce:* PASS. `fault_arm` writes `faults/<case>.json`
  (`src/case_entry.py:717-725`). This is the only thing `fault arm` does.

- **R1-A — application by a host consumer (BLOCKING).** An executing consumer on
  the real host path must *apply* the declared control to the isolated fixture
  during real seat operation; the declaration must be the input to a behavior
  change, not a label read after the fact.
  *d40c1ce:* **FAIL.** `run_case` loads the record only to require its presence
  and to compare `armed_at <= onset_at` (`src/case_entry.py:855-867`,
  `_check_causal` at `:785-826`). No branch anywhere reads
  `intervention["control"]` to change fixture behavior; grep of
  `hold-verifier-texts`/`corrupt-after-worker`/`transport-queued-first` finds
  them only in the `FAULT_CONTROLS` tuple and the plan. The record is inert.

- **R1-B — live path honors the fault (BLOCKING).** Live commands must consume
  the intervention; `FAULT_ROOT`/`FAULT_CASE` may not be the only channel and
  live commands must not ignore them.
  *d40c1ce:* **FAIL.** Live branch sets only `MSGDIR`/`FAULT_ROOT` and never
  forwards `FAULT_CASE` (`src/case_entry.py:891-893`; `FAULT_CASE` is forwarded
  only in the `simulated` branch at `:884-889`). `README.md` states verbatim:
  "live commands ignore both variables." The consumer exists only in test
  executables, which are outside the production path.

- **R1-C — the plan must be executable (BLOCKING).** Every case in the proposed
  live plan names an exact executable host step with a real, non-empty argv.
  *d40c1ce:* **FAIL.** Phases `3/6/9/12/15` (`stagec-plan.json`) name
  `src/seat_emulator.py worker+verifier emulators (exact argv in operator
  brief; external step, concurrent with run-case)`. This is a pseudocommand:
  the argv is deferred to an "operator brief" that does not exist, and the
  emulator is not invoked by `run-case`. It also stands in for the real model
  seats R1 requires, and its hold path cannot fire: `seat_emulator.emulate`
  tests `control == "hold-" + role` (= `hold-verifier`) against the declared
  `hold-verifier-texts`, so the lost-completion control never applies even
  externally.

- **R1-E — applied receipt / observed effect (BLOCKING).** The controller must
  emit a receipt of what it actually applied, with exact case/action/execution,
  independent host time, and real before/after or transport evidence — not
  merely `armed:true`/`induced:true`.
  *d40c1ce:* **FAIL.** The receipt records `intervention` and `induced` copied
  from the declaration (`src/case_entry.py:1082-1083`); there is no application
  record and no before/after artifact. `induced` is derived purely from
  `control != "none-declared"` (`:719`), i.e. from the declaration itself.

- **R1-F — disabled-consumer falsification (BLOCKING).** Removing the applying
  consumer while leaving a valid armed record must make the case fail
  (fail-closed).
  *d40c1ce:* **FAIL / not testable.** There is no production consumer to
  disable. Removing the external test emulator leaves the armed record in place
  and `run-case` still accepts on declaration + causal order, so the case does
  not fail closed on absent application.

## Verdict

**FAIL on R1 for `d40c1ce`.** R1-D (declaration) is met. R1-A, R1-B, R1-C,
R1-E and R1-F are unmet: the fault is declared but never applied by any
executing production consumer, no applied receipt/observed effect exists, and
the live plan's "seat" step is a nonexistent-pseudocommand emulator rather than
real seat operation. This is the rejected R1 defect repeated, not a new
requirement. Withhold acceptance/preparation/Stage C; no contract edit proposed.
