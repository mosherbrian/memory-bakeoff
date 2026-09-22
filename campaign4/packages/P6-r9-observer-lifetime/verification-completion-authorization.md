# P6-r9 verification completion allocation

Tern; 2026-09-22T15:45:00.329537+00:00.

Disposition: repair-3 remains INCOMPLETE, not accepted. Freeze candidate at
f1d7c86f0b38fb653734beb9d906dae44a10a41a.
Manifest 161afac5e212dbc99c77454f4d3cf6fd5ef1768e1c131663e60e7a26c7e78cca.
Preserve candidate-review-repair-3.md and all previous claims/verdicts unchanged.

Authorize ONE independent corvid verification-completion pass <=30 minutes,
no worker allocation and no source/test/manifest changes. New action
P6r9-verify-completion-1. Prior cumulative ceilings 885 worker / 610 verifier
become 885 / 640. Charge prior grant as allocated; this is an explicit additional
prospective grant, not a reset or a claim of unused minutes. No automatic retry.

Reason: targeted failures now have passing evidence; required full retained gate
has not been executed against final bytes. Verification alone is warranted.
The previous verdict records start15:37/deadline15:44 (seven minutes) despite
repair-3 authorization granting thirty. Cairn records that discrepancy separately
with actual dispatch evidence; do not rewrite the verdict or let reconciliation
delay this independent pass. New deadline derives from actual host dispatch time
plus1800s, never a previous worker deadline or obsolete timer.

Run the complete current-package retained gate on frozen bytes, including full
observer7, r3_lifetimes5, case_execution7, reconcile4, host_composition5 and
amendment2_timer3, plus other contract-required retained checks. Recheck manifests
before/after. Independently exercise missing-host-timer/query-failure and callback
intended-state-change/foreign-unchanged/dedup obligations from the admitted
checklist; merely reading worker assertions is insufficient. Preserve stdout,
commands, exit codes and timing in verification-completion evidence files. Full
observer pass must be after final reconcile edits. No repository-wide unrelated
research suite is required: scope is this package's retained gates and its pinned
contract regressions; enumerate exactly what ran and any omissions.

Corvid writes candidate-review-verification-completion.md, distinguishing carried
read-only findings from newly executed results. No PASS if a required gate is
missing, failed or timed out. Stop on a concrete defect and return FAIL with
reproducer; no code fix under this grant. If time expires, return INCOMPLETE with
remaining cases. Candidate verification uses only private fixtures/intercepted
host collaborators, no actual services/timers/seats or live preparation.

Cairn pins this decision, confirms kiln is held/no overlapping execution, dispatches
corvid once with absolute paths and host-read start/deadline, and arms a relative
one-shot verification timer confirmed active. Retire stale verification timers.
Bind new verdict and wake Tern for candidate acceptance and next live decision.
No live run released here; Brian's standing live authority remains in force.
