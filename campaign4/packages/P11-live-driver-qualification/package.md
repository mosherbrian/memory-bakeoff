# P11 — corrected live driver, qualification and cutover
Director Tern; author Claude; independent admission/verifier corvid; fixture/controller cairn.
Brian explicitly authorized a new round after P10 terminal. Research remains paused.
This is new prospective allocation, not reopening P10 or erasing its failed evidence.

## Frozen inputs and scope
See inputs.json for immutable commits and full hashes. Go source remains
1341f0469fba84787112a705b0d107e096644085; shipping candidate binary remains
c1c49a293ed9434c1f6e1f539fd5d9ebf89a0fab220580cf69ddd821547afac8.
Only correct P10 author-plan-recheck-findings F1/F2/F3 in package-local copies of
plans, their tests and evidence. Do not edit historical P10 files. No Go/core/host,
installed binary, main, routing feature, dependency or research changes. Mechanical
package/path/action renaming to P11 is allowed and must be listed in the diff.
Retain P10 cutover/task mechanisms; new defects outside these three require a
scoped director decision before edits, never silent expansion.

F1: captured command stdout is data only. Actual non-DRY helpers must parse valid
rest/ok/starting/unknown fixtures; malformed/missing data remains explicit failure.
A failed required wait/assertion must yield FAIL or INCOMPLETE, never disappear
behind final rc0. Preserve diagnostics. Distinguish construction rehearsal from
executable behavioral checks; inspect every results row, not just process exit.
F2: wall expiry must stop the original driver AND its effect-capable children
before cleanup, with an explicit WALLSTOP/INCOMPLETE record and idempotent cleanup.
Use a validated process identity/group or owned service scope, not an unvalidated
PID file vulnerable to reuse. No effects after bound or cleanup; arm and verify
the deadline before tasks; inability to arm is failure before effects. Offline
subprocess witness must trigger expiry during a blocked operation and prove no
later dispatch/drop-in/command sentinel, child termination and one cleanup.
F3: L2 must reach a supported, evidenced settled state and its timer/effects must
be reconciled before later cases. Do not invent a decide command valid only in
another phase. Prove settlement against the frozen Go CLI with injected transport;
then run the relevant sequential case chain, showing no L2 cancel/wake in L6 and
rest only with no open work. Preserve the original restart/no-resend assertion.
No lost case, weaker timing gate, swallowed failure or forged PASS to fit scope.

## Admission and independent executable review
Corvid15m: preregister F1/F2/F3 concrete checks before author starts; assess this
contract, scope and allocation independently. ACCEPTED or bounded REJECTION.
Claude45m initial; corvid25m candidate review. Author emits source diff, plan hashes,
claim with residuals, executable regression logs and command/results coverage.
Corvid reproduces old failures on pinned P10, exercises corrected real shell
helpers/processes and Go sequence offline, adds one unshared negative per family.
DRY=1 command printing cannot establish any F1/F2/F3 behavioral PASS. Check all
required outcomes and adverse command failures. Recheck unchanged Go source/binary.
ONE optional correction30m + independent20m shared across the package, only by
explicit Tern release; not automatic. No second correction or automatic successor.

## Live qualification (separate signed release)
Incorporate P10 package.md section C's full case matrix and recovery bounds unchanged,
except this package allocates 75m live INCLUDING archive and exact-ID cleanup.
Cairn idle prep15m, corvid binding10m. Fresh four distinct worker/verifier/duty/director
fixtures with authoritative runtime/incarnation/socket binding; main seats excluded.
Tern signs materialized plan/config/units/binary/IDs, fault onset/actor, start and
absolute deadline, automatic cleanup. No author/live overlap or live dispatch before
candidate PASS and signature. Host-read clock and relative one-shot timer required.
Cases: positive independent handoff+director decide; crash restart without resend;
watchdog hang recovery and outside detection; restart-loop acknowledged escalation
including unavailable duty; >=3min/>=3 checks quiet rest and deliberate stop;
real step timeout while run stopped, one interrupt/wake and replay deduplication;
malformed incident, future heartbeat and prior incarnation/controlled startup.
P10 recovery bounds remain explicit30s/suspicion180s + acknowledged ownership or
recovery60s (totals90/240). Wake delivery alone is not acknowledgement. No case
reclassified after a failed bound. All failed/censored cases retained.
Corvid live-review20m. Missing required live evidence => NOT READY, no cutover.

## PASS-only success step
Incorporate P10 package.md section D in full: cairn45m cutover INCLUDING first real
worker20m/verifier10m operation and rollback; corvid postcutover10m. Tern acceptance
of independent live PASS + exact cutover signature required. Fresh production
ledger, exact source/binary/config/role/session bindings; never import TSV as truth.
Inventory actual callers and prior unit state; drain old effects and callbacks.
Retire campaign4 openwork, campaign4-watch, coax (coax-dry caller), shadow-watch
and Cairn's manual controller role in the bounded switch, no indefinite dual owners.
Cairn remains duty; wake/lanes/pause stay. Keep other projects untouched.
First real package P11-production-handoff-1 produces OPERATOR-HANDOFF-20260923.md
and bound deployment manifest/verdict. All dispatch/handoff/deadlines/decision via
Go. Pin concrete tasks before signature; no manual substitute counts as success.
Rollback archives and reconciles in-flight identities, disables candidate effects
and timers, restores old binary/config/timers/controller, and verifies one owner.
Do not re-enable old owners while candidate can send. Preserve history and report
all architecture checks, liveness, retirement receipts and remaining limitations.

## Budget and terminal behavior
Prospective minutes: admission15 + author45 + review25 + sole correction30 +
recheck20 + prep15 + binding10 + live75 + live-review20 + cutover45 + postcutover10
=410m total ceiling. No hidden/unallocated reserve. Each grant separately started
from host UTC with absolute deadline and relative one-shot enforcement. No reuse
of P10 cancelled/spent grants (P10 allocated415/ceiling420 remains historical).
Actual elapsed is reported separately; unused time is not automatically a fresh
attempt. Timeout/incomplete returns to Tern; no automatic reset, extension or
package revision. On terminal failure declare NOT READY/owned rest and successor
decision; on PASS complete bounded cutover before claiming replacement. No research
release or script retirement merely from candidate PASS.

## Release
Admission first, watcher active and prior rest explicitly ended. Author is
conditionally authorized only after ACCEPTED on this unchanged pinned contract,
checklist pinned and no overlap: Cairn records host start+45m deadline, arms the
one-shot, and sends exact release to Claude using notify-claude tern. If admission
changes requirements return to Tern, do not dispatch. Author completion claim must
be immutable at this package/completion-claim.json. Completion notification in every
dispatch uses full executable/profile/exact cairn ID, absolute claim path and qid.
Cairn routes COMPLETE to fresh corvid25m; PASS returns to Tern for live signature.
No further Brian permission needed within this contract.
