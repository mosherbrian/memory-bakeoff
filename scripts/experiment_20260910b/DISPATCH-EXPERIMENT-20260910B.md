# DISPATCH — controlled experiment EXPERIMENT-20260910B (adjusted per planner, funded by Brian 2026-09-10)

Supersedes the experiment proposal in the conductor's share-back doc where
they differ. Planner corrections ADOPTED in full; see that doc's correction
block. This file is the pre-registration skeleton: hypotheses, arms, decision
rules, and stopping rules below are FROZEN when committed BEFORE the first
evaluation run. Any deviation = stop and report.

## Roles (authorship separated from execution)

- worker-glm-3 (reviewer): AUTHORS the 4 cases + verifiers, blind to arm
  assignment, hidden requirements NOT in runner-visible prompts. Delivers as
  files; <=45 min.
- worker-glm-2 (implementer): harness prep + freezes the case set via commit
  + runs all slots + reports. Does NOT begin evaluation until the frozen
  cases commit exists.

## Design (frozen)

- **Arms (3):**
  - A — baseline: pi-lcm only (daily configuration);
  - B — + relaxed recall tool, NO nudge;
  - C — + relaxed recall tool + automatic nudge via pi-recall-nudge.
- **Cases (4, fresh, never examined, authored by reviewer):**
  - 2 history-dependent: seeded prior-session history contains a
    decision/constraint REQUIRED to satisfy a hidden requirement; the
    verifier fails without recovering it;
  - 2 controls: (i) solvable entirely from current project information —
    tests unnecessary recall/noise; (ii) an older seeded decision EXPLICITLY
    SUPERSEDED by a current instruction — the current instruction must win;
    taking the stale action = failure (stale-harm probe).
- **Slots: 24** = 4 cases x 2 repetitions x 3 arms. Arm order RANDOMIZED
  within each case/repetition. Independent store + workspace per slot.
- **Model:** qwen3.6-35b-vulkan-nothink (daily default), single model.
- **Trigger authenticity (arm C):** every treatment session must GENUINELY
  resume or fork (real `session_start` reason resume/fork, real extension
  gate path — a fresh launch with a harness-inserted message does NOT test
  deployed behavior). Trace must record per slot whether the nudge fired.
- **Pre-evaluation smoke:** verify the full extension PAIR under intended
  daily-like settings (both extensions via packages in the isolated agent
  dir, pi-lcm ACTIVE so normal writes occur) once, with receipt, before the
  first slot.

## Isolation + verification per slot (planner rule 4 — replaces whole-store checksums)

pi-lcm legitimately writes the running conversation; a whole-store checksum is
neither a reachability check nor an appropriate zero-write assertion during
normal operation. Instead, per slot RECORD AND VERIFY:
1. actual database path opened (runtime-resolved) + effective configuration;
2. seeded records present before the run and unchanged after (content-level
   check of the seeded conversation ids — new rows from the run's own
   conversation are expected and fine);
3. the recall connection is read-only (extension-level property, already
   tested — cite the test, plus the store's non-seed deltas confined to the
   run's own conversation id);
4. reachability receipt: seeded content retrievable through the real path
   during the run (Stage-A pattern).

## Exact trial-success rule (planner rule 5 — replaces any placeholder)

PASS supports CONTINUED PERSONAL USE ONLY, not general adoption:
1. C fixes at least one history-dependent case in BOTH repetitions where A
   fails BOTH repetitions of that case;
2. C causes no regression on the other cases (verifier outcomes vs A);
3. NO stale-history action in the superseded-decision control;
4. overhead within the agreed 25% threshold on comparable successful runs
   (wall + tokens); if cost comparisons are insufficient, mark cost
   UNRESOLVED — do not guess;
5. B is reported fully regardless of outcome.
Failure of any of 1-3 = FAIL. Predeclared branches: (a) PASS, (b) FAIL, (c)
inconclusive-never-fired (nudge failed to fire through the real path — report
as infrastructure finding, not outcome).

## Freezing discipline

Cases, verifiers, this file, the randomization schedule, and the decision
rules are committed BEFORE the first evaluation run; commit hash recorded in
the report. Verifiers assess required BEHAVIOR, not a particular
implementation. Hidden requirements live only in seeded history + verifiers,
never in runner-visible prompts.

## Budget + stop rule (planner-set)

- AGGREGATE agent time <= 3.0 h (case creation + implementation + review +
  repairs + reporting). Suggested split: reviewer authoring <=45 min,
  implementer prep+freeze <=45 min, runs+report+repairs within the remainder.
- Machine ceiling 4 h (24 x 8-min slots = 3.2 h execution; ~0.8 h slack).
- STOP RULE: if preparation cannot fit within budget, STOP BEFORE evaluation
  and report — do NOT expand work automatically.

## Boundaries

- F1/F2/f3 and query-rel records: untouched (a new results doc section for
  EXPERIMENT-20260910B only, append-style).
- pi-project-recall/ and pi-recall-nudge/: no behavior changes; if a defect
  blocks the experiment, stop and report rather than hot-fixing without review.
- No new models, no fourth arm, no real-history arm (parked).
- Personal trial: Brian's own activity, runs alongside — not yours to manage.

## Report

Ledger of all 24 slots (arm, case, rep, nudge-fired y/n, verifier outcome,
invocations, relaxation count, overhead), receipts per the isolation rules,
decision-rule evaluation verbatim, honest labels, time account vs budget.
Commit-push-report-STOP.
