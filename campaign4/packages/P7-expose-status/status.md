# P7 status view (derived, read-only)

As-of (host time): 2026-09-23T03:47:22Z. Every fact below is derived from the declared inputs; nothing here is live, scheduled or inferred PASS.

## Connect ruling
Connect is CLOSED as a demonstrated integration stage, NOT accepted for general unattended adoption (director decision CONNECT-FINISH-LINE-20260923.md). R18 is the latest accepted candidate, not a new live PASS. Checks met at stated boundary: 3; partial: 5.

## Eight pre-unattended-use checks
- [partial] Restart cannot duplicate execution (owner: P8 (Tern to allocate))
- [partial] Hung attempt gets enforced owned disposition (owner: P8 (Tern to allocate))
- [met-at-stated-boundary] Worker cannot self-verify (owner: provenance in row)
- [partial] Changed inputs invalidate affected registrations (owner: P8 (Tern to allocate))
- [met-at-stated-boundary] Repair exhaustion stops automatic attempts (owner: provenance in row)
- [partial] Pending judgments visibly block dependents (owner: P8 (Tern to allocate))
- [partial] Evidence recoverable after interruption (owner: P8 (Tern to allocate))
- [met-at-stated-boundary] Routine handoffs don't need Brian (owner: provenance in row)

## Accepted source vs historical witness
- R18: ACCEPTED_SCOPED_CANDIDATE (commit 7857c0ce86fda44f1f245365c47c4e6ba93f5ff2, owner tern)
- R19: TERMINATED (Director engineering boundary: close Connect, move to Expose; not a technical failure; live_executed=False)
- R9 live-review-3 remains the pinned historical positive witness; it is not transferred to later bytes.

## Pending decisions (1 open)
- S13-1: the pre-registration says "the corpus is the records inscribed by that stream", which is ambiguous between pooling the whole stream and building it at ea | owner: tern | raised: 2026-09-20 | affects: S13-1 verdict
  next: owner decision required; dependents blocked (see affected)
- RESOLVED/RETRACTED (not pending): Campaign 4 has been silent for 135 minutes. Cairn did not recover after being wo... -> **RETRACTED 07:38 — FALSE ALARM.** Raised by Claude testing campaign4-watch with a DRY guard that did not apply to rung 

## Active package
P7-expose-status: worker kiln builds this view (cap 100m with admission/verification/repair); no P8/P9 execution authorized here. Next action: verifier review, then director publish decision.

## Costs and limits
Allocations are ceilings, not actual costs; actual worker/verifier minutes spent are unknown in this view. Missing cost/timing data is unknown, never zero.

## Code links
- R18 candidate: campaign4/packages/P6-r18-runtime-source-time/candidate/
- This package: campaign4/packages/P7-expose-status/
- TSV activity (log, not truth): 543 rows, owners {"cairn": 152, "corvid": 228, "kiln": 124, "tern": 39}

## Inputs (pointers with hashes and freshness)
- pending_decisions: campaign4/pending-decisions.md sha256=63e1b056e5b5 observed=2026-09-22T08:17:07Z stale=False
- control_tsv: campaign4/control-events.tsv sha256=c466b1b0c254 observed=2026-09-23T03:43:31Z stale=False
- connect_finish: campaign4/CONNECT-FINISH-LINE-20260923.md sha256=0e92d85cf063 observed=2026-09-23T03:41:11Z stale=False
- r18_acceptance: campaign4/packages/P6-r18-runtime-source-time/acceptance.json sha256=d5c5c5529e81 observed=2026-09-23T03:37:49Z stale=False
- r19_terminal: campaign4/packages/P6-r19-live-runtime-witness/terminal-disposition.json sha256=60241425fdf2 observed=2026-09-23T03:41:11Z stale=False
- charter: campaign4/CHARTER.md sha256=468365c68f66 observed=2026-09-22T13:52:30Z stale=False
- architecture: campaign4/ACCEPTED-ARCHITECTURE.md sha256=cf390ce0d79b observed=2026-09-21T14:45:09Z stale=True
