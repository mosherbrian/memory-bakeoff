# P6-r8: diagnose and repair the full-sequence race

Tern: preserve cc8cc2b95e77ea7cf8230d047d0599c36374e44b and independent verdict
35d3fe4d17b4eae9973490e783dddab984b3444d0da0d0fd7ff92efb3d6b0fe0.
Overall FAIL stands. Targeted queued correction, manifest integrity and D1-D4
no-simulated composition independently PASS; do not reopen or rewrite them without
causal evidence. One of three observed full runs failed, isolated reruns passed;
this is a reproduced flake, not a statistically established population failure rate.

Completion claim's residual_faults:[] contradicts its own disclosed timing flakes.
Preserve original claim; next claim must enumerate every known unresolved failure,
even if the final run is green. No inference that last-green erases earlier failures.

## Prospective scope and allocation

ONE <=40m kiln diagnosis+repair; ONE <=25m independent corvid verification.
P6 ceilings705worker/475verifier ->745worker/500verifier. Previous allocations spent;
no automatic further repair. Held witness10/fixture15 and spent prep30 unchanged.
ActionP6r8-repair-3, new execution, linked prior recovery2; no reset/relabel of spent
work. Cairn pins this authorization before single dispatch with host start/deadline,
absolute paths, no overlap and relative one-shot timer. Preserve compact logs in files.
After bound completion corvid <=25m, candidate-review-repair-3.md. Expiry/INCOMPLETE
or FAIL returns Tern; neither launch nor preparation nor live release follows PASS.

Reproduce exact full sequence error: expect_open path sees latency but no worker
success rows and returns INCOMPLETE. Establish the causal ordering across worker
claim/artifact publication, runtime end, observer attach/drain, fault application,
verifier receipt and deadline/reattach. Trace monotonic/UTC source and action/execution
identity without replacing trustworthy clocks with seat-generated times. Identify
whether production sequencing or test scheduling causes it before changing code.
Use controlled scheduling/barriers at existing external boundaries to force the
bad ordering. Retain a deterministic old-fails/new-passes regression plus the full
exact CLI sequence. Unknown cause remains INCOMPLETE, never guessed cache poisoning.

Permitted changes only those needed for the demonstrated race and honest evidence.
No arbitrary sleeps, blanket timeout inflation, retry-until-green, ignored failing
assertion, reduced case set, forged success row, swallowed exception, relaxed timing
bounds or removal of applied-fault/receipt checks. A test scheduling fix is legitimate
only if its synchronization models the actual host precondition; do not manufacture
an ordering real execution does not guarantee. Preserve production failure semantics:
missing worker success must still be INCOMPLETE, not accept-open.

Corvid independently challenge the diagnosed ordering, including delayed producer
and early/late observer within valid grant, expired grant, and same execution reattach
without resend. Run full suite and exact no-simulated sequence; retain all trial results.
After causal regression passes, use a small bounded repeat (at least three whole-suite
runs inside grant, stopping on first failure) to challenge order/load sensitivity.
This is a regression screen, not statistical proof of universal reliability. Report
how much timing variation actually covered. No hidden retries and no last-green claim.
If this cannot complete in the grant, return the demonstrated progress/residuals.

Manifest refreshed mechanically after final changes, transitive executable hashes,
no self-hash. Correct contract pin8ceb879/hash1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343.
Preserve original incomplete/FAIL/PASS history. New findings not addressed are residuals.
No frozen parent/core edits beyond existing copied R3 exception without a separate
reproducer/decision. Retain stdlib boundary, role/profile authority, code signatures,
notification-primary behavior, case isolation, causal evidence, actual ack semantics,
no duplicate dispatch and archive/rollback. Candidate effects only private tmp with
external host/model boundaries intercepted; no actual fixture actions, services,
credentials, production ledger, shared wrappers, research/shadow or retirement.

Continuation assessment: concrete independent D1-D4 and integrity progress narrows
this to an observed ordering failure; one targeted allocation is warranted under
Brian's continuation instruction. Repeated green reruns with unexplained red ones
would not demonstrate convergence. No broader machinery features authorized.
