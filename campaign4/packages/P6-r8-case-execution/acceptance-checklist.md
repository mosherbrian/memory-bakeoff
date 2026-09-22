# P6-r8-case-execution — adversarial acceptance checklist (pinned pre-worker)

- **Author:** corvid (independent reader; pinned BEFORE worker dispatch)
- **Date:** 2026-09-22; bound to contract `package.md` sha256
  `1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343` @
  `17cd6bfbb5f259dac8845046aa2f7c646cce0713`
- **Parent (immutable):** P6-r7 `17cd6bf…`; entry `46681fbb82cb…`; plan
  `cc5993ab…`; readiness `12d5ce7f…`; repair PASS `677dbeac…`
- **Rule:** every check blocking. No edits to frozen parent/core. Candidate work
  is private tmp + injected effects only; no live seat/send/restart/service/
  timer/credential/production-ledger effect. Missing/failed intervention is
  INCOMPLETE/FAIL, never a passing fault case.

## R1 — executable fault protocol

- **R1.1 per case:** all five cases (positive handoff, lost completion, failed
  verification, queued/ambiguous transport + restart, quiet rest) have explicit
  **exact host commands, responsible actor, preconditions, controlled
  intervention, independent onset capture, expected evidence and cleanup** — in
  the signed plan or an implemented fixture control. Passing `--case` alone, or
  relying on test-only `hold`/`tamper`/`queued-first`, does **not** count.
- **R1.2 no substitution:** real model seats perform worker/verifier work;
  fixture controls never substitute synthetic producers, and never fabricate
  runtime events, transport acks or verification outcomes. A controlled
  transport fault is labelled **induced** and preserves the true underlying
  receipt/uncertainty.
- **R1.3 causal order:** end-to-end proof that the fault was actually applied →
  onset recorded independently → observer detected → recovery/owned escalation
  acknowledged. Onset is never guessed from candidate detection; finite
  uncertainty is conservative.
- **R1.4 isolation:** fault controls touch only the future isolated fixture,
  never production seats or shared transports.
- **Unshared mutation:** **absent fault/onset** — a case with the intervention
  missing or onset missing must be INCOMPLETE/FAIL, not pass.

## R2 — case isolation plus real sequence

- **R2.1 identities:** declared distinct case/action/execution identities and
  case-scoped db, claims, artifacts, receipts, manifest, onset, latency, witness
  and timer units derived from the signed plan/config (immutable per-case
  subroots under one suite root allowed).
- **R2.2 no invented runtime files:** runtime streams/sockets stay the actual
  launch-bound paths; never invent case-specific runtime files, truncate real
  streams, or infer identity from suffixes.
- **R2.3 reuse safety:** live seats reused only after preceding execution is
  reconciled, with new execution correlation.
- **R2.4 replay vs execution:** replay/restart inside one case keeps the same
  identity and causes **no fresh send**; a different case **actually executes**.
- **R2.5 aggregate:** all five cases execute **once** on one suite root via the
  exact five-command sequence, preserving earlier evidence byte-exact; matching
  per-case evidence with no cross-case authority; rollback accounts for every
  case's effects. Not five independent test environments.
- **Unshared mutation:** **case identity/evidence cross-contamination** — if case
  B's receipt/witness/latency is B's own (not A's or shared), and replay causes no
  second send, the check passes; contamination or fresh replay sends fail.

## R3 — budgets and observer lifetime

- **R3.1 deadlines:** trusted worker/verifier deadlines derive from actual signed
  grants (900/600); **no 8-second timeout consumes a 900/600-second grant**.
- **R3.2 observer:** either a bounded notification-backed observer lasts through
  authorized work/handoff, or an explicit **reattach** path consumes late
  completion under the same action/execution **without a second send**; all
  waits/restart recovery owned and bounded; no polling or silent deadline
  extension.
- **R3.3 separation:** normal model work is separate from 30/60/90 and
  180/60/240 recovery latency.
- **R3.4 proof:** completion **after the former 8-second cutoff but before the
  real grant** is handled once; real grant expiry escalates boundedly.
- **R3.5 production path:** tests may control clock/external boundaries but must
  exercise the **production** deadline calculation and the actual CLI
  reattach/notification path — not a separate miniature implementation. A local
  copied, manifest-bound harness revision is allowed **for R3 only**, with the
  pinned parent retained/compared; no frozen parent/core edits.
- **Unshared mutation:** **premature/late deadline or restart** — delivery before
  the old 8 s cutoff, after it but within grant (once), and at real expiry
  (bounded escalation) must each behave correctly.

## Retained from P6-r7

- H1 actual host branch (no synthetic producer, owned missing-host failure);
  H2 live gate against current registry + real sockets/incarnations + fail-closed
  code/candidate hash binding; H3 exact (action, execution, case) join, ack
  semantics, bounded uncertainty; H4 exact subprocess CLI, artifacts **and**
  outcomes, five cases (not three), archive-before-disable.
- Parent 11 tests retained; fail-closed hash negatives, one-send and ack
  semantics, real registry/socket binding, timing joins, archive-before-disable
  must still pass. Changed paths run their regressions; unchanged components
  reused unchanged.
- Import boundary: stdlib + owned modules only; no dependency, duplicate-method
  or fallback bypass. No wrapper/script retirement.

## Allocation / boundary

Worker initial ≤40m; candidate verification ≤25m; ceilings 525/400 →
**565/425**. Admission/checklist ≤15m (separate). Live witness 10m and cairn
fixture 15m HELD; preparation 30m spent, no renewal. No research/shadow.
Candidate PASS certifies **injected execution only**; fresh binding and an exact
signed live plan remain separate gates. These checks cannot add scope without a
Tern amendment.
