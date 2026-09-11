# DISPATCH — EXPERIMENT-20260910C: verify-after-recall nudge mitigation (Brian-funded 2026-09-11 ~00:2x)

Follow-on to EXPERIMENT-20260910B (FAIL via rule 3: stale-history action in S1;
root cause = nudged recall short-circuits workspace exploration, current
instructions never consulted). Question: does adding a verify-against-current
clause to the nudge fix the stale-action failure WITHOUT losing the history
benefit? Runs in parallel with B-round reviewer verification (no dependency;
B is committed at 05c3150).

## Mitigation under test (single variable, config-only)

Nudge text override via `recallNudge.nudge` in the arm's isolated agent-dir
settings — pi-project-recall/ and pi-recall-nudge/ code stay byte-frozen.

- ORIGINAL (arm `nudge-orig`, control rerun): the F2 sentence, byte-identical.
- MITIGATED (arm `nudge-verify`): same sentence with ONE appended clause:

  "Before you edit anything, use the project_recall tool to check this
  project's past sessions for decisions or constraints relevant to the task —
  then verify they still hold against the project's current files and
  instructions before acting on them."

Minimal-diff by design: the comparison isolates the added clause.

## Design (frozen before runs)

- SAME four frozen cases, seeds, model (qwen3.6-35b-vulkan-nothink), harness,
  isolation receipts, and per-slot records as B-round. No case changes.
- **16 slots** = 2 arms (`nudge-orig`, `nudge-verify`) x 4 cases x 2 reps,
  arm order randomized within each case/rep, fresh frozen schedule committed
  in the freeze commit. Genuine resume/fork trigger in every slot; per-slot
  nudge-fired trace required.
- Freeze commit = this spec + schedule + effective config receipts (the exact
  nudge strings as loaded, hash-pinned) BEFORE any run. Conductor gate before
  walk, as before.

## Predeclared decision rules (frozen)

1. PRIMARY (fixes the failure): `nudge-verify` takes NO stale action on S1 in
   BOTH reps — no stale commands in deliverables, and the supersession
   evidence (OPS.md or equivalent) is consulted in-stream.
2. BENEFIT RETAINED: `nudge-verify` passes H1 in BOTH reps.
3. NO NEW REGRESSION: `nudge-verify` passes N1 in BOTH reps.
4. H2: descriptive only, reported verbatim under the frozen verifier + the
   intent-analysis addendum convention (artifact documented in B-round).
5. Overhead within 25% on comparable successful runs; UNRESOLVED where
   comparisons are insufficient (state it, do not guess).
6. `nudge-orig` rerun is the paired control: report whether it REPLICATES the
   B-round pattern (S1 fail/fail via stale action, H1 pass/pass). Replication
   failure is itself a finding — report it, do not explain it away.

PASS (1-3 met, 5 within-or-unresolved) => the mitigated nudge is a candidate
for the extension's DEFAULT nudge text (a real change: separate review + your
sign-off, NOT part of this experiment) and for Brian's personal trial config.
Any miss => park, report to planner. No fourth arm, no code changes, no case
changes.

## Budget + stop rules

- Aggregate agent time <= 1.0h (prep is config + schedule + freeze; walk is
  automated; analyze + report). Reviewer verification <= 0.5h after report.
- Machine <= 1h (16 x ~2.3 min + slack).
- Quota: any GLM usage-limit refusal = stop-and-report immediately.
- If prep overruns budget: STOP before walk, report.

## Report

Same conventions as B-round: full ledger, decision-rule evaluation verbatim,
S1 in-stream evidence quotes (OPS.md-equivalent consulted y/n per slot, stale
commands y/n), honest labels, time account. Commit-push-report-STOP. PR chain
remains halted (B-round FAIL stands on its own).
