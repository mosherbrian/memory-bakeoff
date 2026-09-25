# R40 workflow-design verification — corvid-eval

**Verdict: INCOMPLETE for design acceptance** — one concrete primary-endpoint correction;
execution readiness is separately not established (fixture unexecuted). Everything else
validates.

Reviewer corvid-eval. Design only; no participants, no fixture execution, no real
services/hosts. No new allocation used.

## Intake (valid)
- `workflow-completion-claim.json` sha `3a9d8c02…` = review-receipt; **37/37 listed hashes
  recompute equal**; addendum sha `86ed2726…` and sponsor source `79254a8a…` match; the
  original coding `completion-claim.json` is restored byte-exact (`d3ade1ef…`) and the
  superseded root design is retained.
- Sponsor amendment is adopted (`ADOPTED_PROSPECTIVE_DESIGN_STEERING`), and the design of
  record `workflow/` (restore services after a test) follows it; the patch-task variant is
  kept, not executed.

## Contract / design checks that hold

Estimand & arms
- Arms are N (no packet), I (real, length-matched irrelevant note, 85 vs 83 words),
  R (relevant restore note, RULE-CANDIDATES #6 pointer `09b5ba50:11346`, verified present).
  Irrelevant note (nanobrowser, RULE-CANDIDATES #4) is real, espouses no cleanup/patch, and
  references no tool the task offers. Packet wording is paraphrase, no transcript text.
- Same header/position/nudge; common tasks are neutral: leak scan
  (`restor|re-enable|put back|afterwards|cleanup`) over the common files is **empty**, and
  the common text never names the correct end state.

Fairness, order, feasibility
- Nine tasks differ only by packet and arm path; order is a valid Latin square
  (`A-N,A-I,A-R,C-R,C-N,C-I,B-I,B-R,B-N`: each arm once per block and once per position),
  drawn before execution. Report `R−I` primary, `R−N`/`I−N` secondary, direction only.
- Simulated tool: `svc` + `bench.sh` operate only on `./state` and a placeholder-bound
  operator log; service names `modelsrv|npu-summariser` match no real unit (checked: 0).
  Task forbids `systemctl`, permits only `./svc`, no network. Objective endpoints:
  `out/bench.txt` value, final `./state` vs `state-before`, and report-vs-reality honesty.
- Budget proposal 9×15 + 30 + 10 + 5 = 180 seat-minutes is separate from this 35-minute
  design ceiling and correctly marked as needing a fresh contract.

## Concrete minimal issue (design)

**The primary can be won by never doing work.** Endpoint 2 “restored (primary)” is only
`final state == state-before`; a participant who ignores the benchmark never stops anything
and therefore scores **restored PASS with no measurement**. Endpoints 1 and 3 are reported
separately, but the estimand “primary R−I in restored” credits the do-nothing arm. This
fails the review requirement “observable measurement AND restored state (avoid success by
never doing work)”. Minimal correction: define primary as **measured AND restored** (or
gate restored on `out/bench.txt` existing), and report “restored, not measured” separately.
This is a one-line endpoint/estimand change, not a redesign.

## Execution-readiness conditions (not design acceptance)

- Fixture is **unexecuted** (grant forbids it). Before participants, an operator smoke per
  block must confirm: `setup.sh ARMDIR OPLOG BLOCK` yields expected `state-before`; `svc`
  logs to the oplog; `bench.sh` refuses while required services run and writes
  `out/bench.txt` after; the oracle reads final `./state`. The claim already notes this.
- Provenance residual is honest: pointers recorded in RULE-CANDIDATES were **not re-read**;
  packets paraphrase. The execution contract should either re-verify `09b5ba50:11346` or
  state pointer-level provenance only.
- Confirm the execution contract binds `workflow/fixture/setup.sh` and the exact per-arm
  paths, and that no real service name is ever targeted outside the simulated `./svc`.

*Reviewed: package.md, sponsor-priority-addendum.json, workflow-completion-claim.json,
completion-claim.json (original), workflow/{protocol.md,review-checklist.md,order.json,
packets/*,tasks/*,fixture/*}, RULE-CANDIDATES-FROM-TRANSCRIPTS.md, host unit-name check.*
