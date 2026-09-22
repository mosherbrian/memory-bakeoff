# P6-r6 explicit launch-tool repair allocation — Tern

P6r6-prepare-1 FAILED. Preserve live-preparation stdout/stderr/registry and
preparation-failure-record.json; candidate source pinned at6bbdd1e. No new
sessions are recorded, nothing to stop. Old preparation release c1d2e0c may
NOT be retried. Retire its preparation/cleanup timers after registry reconciliation.

Authorize one prospective <=20m kiln repair and <=15m corvid independent check.
No automatic further repair. Cumulative P6 worker/verifier ceilings395/300
(prior375/285 +20/15). Original author30 and candidate20 grants spent.
Original cairn preparation10 attempt ended FAILED; no fresh preparation grant
is made here. Live witness15 and cairn fixture15 remain HELD; no binding witness
ran on this failed preparation. Actual elapsed use differs from ceilings.

Scope: make the actual installed agent-deck launch invocation parse exactly as
intended, idle with no initial task. Tool currently sends separate tokens
-idle-timeout 25m -json; installed CLI reports invalid idle-timeout '-json'.
Read installed CLI help and local parser source at
/home/bmosher/src/agent-deck/cmd/agent-deck/launch_cmd.go and its argument
normalization; do not infer shell quoting is the explanation (subprocess uses
argv). Prefer parser-safe value binding such as --idle-timeout=25m if verified.
Test all relevant value flags, path placement, JSON response shape and exact
returned identity; no silent title-only fallback when response is ambiguous.
No agent-deck upgrade or shared binary/source edits. Fix package tool only.

Regression must exercise production launch_idle through the actual argument
normalization semantics, not just assert an invented runner says success. Capture
exact expected argv and response, no -message. Use injected subprocess effects
and a read-only/parser-only reproduction; do NOT create real seats to test this
repair. If installed parser cannot be exercised without effects, document that
limit and reproduce from inspected matching source; don't claim a live test.
Verify partial creation is recorded and can be reconciled if second launch fails,
without retrying the first launch; preserve existing identity/socket/cleanup gates.
Code/plan hashes change => invalidate old signature. Output corrected full manifest
and exact proposed PREPARATION argv; candidate-review-repair.md binds both. Keep
old candidate-review.md. Run meaningful tool regressions, no parent core rewrite.

Stage C remains independently blocked by director-candidate-record.json (phase4
placeholders and no complete recovery/total enforcement). This small repair does
not resolve those or authorize tasks. Do not start fixing unrelated code under
this grant. Tern decides next preparation and Stage C work after the verdict.

Cairn dispatches P6r6-repair-1 after no-overlap check, host-stamps receipt/start/
deadline and absolute claim path, relative timer before one wake. All pointers
absolute; canonical workdir:
/home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation
Kiln reads contract/checklist, this decision, failure record and new receipt.
Actually wake cairn with bound completion. Expiry stops/reconciles then BLOCKED.
Corvid independently reproduces original parser failure and checks corrected
argv semantics; no real seat/service action under either grant. Return Tern.
