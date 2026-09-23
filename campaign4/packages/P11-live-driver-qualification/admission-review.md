# P11-live-driver-qualification — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P11-admission-1`, start `14:54:54Z`, deadline `15:09:54Z`
- **Brief:** `package.md` sha256
  `61ae7ed6bbdee2e95fbbe89888588561385de90585bbe98baae47a3680e68134`
  (contract `6f780b3`); `inputs.json`; `sponsor-authorization.json`;
  `admission-receipt.json`.
- **Scope:** read-only admission + preregistered checklist. No source/live changes.

## Verdict

**BOUNDED REJECTION — budget arithmetic does not reconcile.** Pins, scope and the
F1/F2/F3 mandate are sound and the preregistered checklist is filed, but the
itemized allocation sums to **310 m**, not the claimed/sponsor **410 m**: a **100 m
gap** in a contract that states "No hidden/unallocated reserve". This is an
allocation defect, not a scope objection; correct the itemization (or restate the
per-stage ceilings) before author release. Everything else below is acceptable.

## Pin / input verification (all OK)

- `inputs.json.paths_sha256`: **17/17 recomputed equal**, including the P10
  `package.md 9a8b6b66…`, `terminal-disposition.json 5b4b33dc…`,
  `author-plan-recheck-findings.md cb87379a…`, the four plans/scripts and six task
  texts.
- Candidate source `1341f0469fba…` and binary `c1c49a29…` unchanged; parent commits
  `de4d6e2` (P10 close), `8aed6d7` (F1/F2/F3 findings), `d1b9f7c` (plan repair) and
  contract `6f780b3` resolve. Sponsor authorization present (`410`, "I authorize a
  new round", research paused); P10 terminal preserved EXHAUSTED/NOT_READY; prior
  legitimate rest with watcher inactive (rearm before work).

## Budget finding (blocking)

Package states: `admission15 + author45 + review25 + sole correction30 + recheck20
+ prep15 + binding10 + live75 + live-review20 + cutover45 + postcutover10 = 410m`.
Arithmetic: 15+45+25+30+20+15+10+75+20+45+10 = **310**. Sponsor
`director_allocation_minutes = 410`. So 100 m is either omitted from the
itemization or a stage is understated, contradicting "No hidden/unallocated
reserve". **Smallest correction:** reconcile the itemization with the sponsor's
410 (state the exact per-stage ceilings and the total; if a stage legitimately
needs the missing 100 m, name it). P10 had the same pattern (415 claimed vs 315
itemized) — do not repeat it silently.

## Scope assessment (acceptable)

- Only F1/F2/F3 are correctable, in **package-local copies** of the P10 plans/
  tests/evidence; historical P10 files untouched; Go/core/host, installed binary,
  main, routing, dependencies and research frozen. Mechanical P11 renaming allowed
  but must be listed in the diff; new defects outside the three require a scoped
  director decision. P10 section C live matrix and section D cutover are inherited
  with the P10 recovery bounds (30/180 + 60, totals 90/240). PASS-only cutover.
- F1/F2/F3 are pinned to concrete, non-DRY behavioral checks (checklist filed);
  DRY=1 command printing explicitly cannot establish any behavioral PASS.

## Acceptance checklist (preregistered)

Filed as `acceptance-checklist.md` (F1/F2/F3 concrete checks, old-fails on pinned
P10, corrected real shell/process + Go-sequence offline checks, one unshared
negative per family, unchanged-Go recheck, and the adverse-outcome rules). It must
be pinned before author dispatch.

## Effect

One bounded verdict: **BOUNDED REJECTION** — reconcile the 310-vs-410 allocation
gap (or restate exact ceilings) and keep the unchanged pinned contract; then the
author may be conditionally released on an ACCEPTED unchanged contract with the
checklist pinned. No source/live/cutover change made. Returned to Tern.
