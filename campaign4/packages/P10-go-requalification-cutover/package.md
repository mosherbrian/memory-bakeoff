# P10 — Go unattended requalification and bounded cutover
Director Tern; author Claude; independent admission/verifier corvid; fixture and
legacy control owner cairn, becoming duty-only after cutover. Sponsor authority:
campaign4/SPONSOR-REQUALIFICATION-20260923.md co-pinned. Research remains paused.

## Target and pins
ONE newly funded package, not P8-r2 or renewed P9. Qualify one declared supported
agent-deck/systemd host configuration, then cut over the next real work item with
rollback. No universal stall-freedom or cross-host guarantee. Source base agent-loop
c124d82cd26ae4966f3e6a935cb24d971347ec8c; installed binary221bb3aa... verified,
full pins inputs.json. Read P8 qualification-final.md, liveness-blockers-addendum.md,
P9 acceptance.json, architecture sections6/7, recovery ruling4be99bf, retirement
rulingb2384d7, clock650830c, identity84f094e, turn-end883107e. Paths and hashes in
inputs.json resolve from memory-bake-off root. Preserve all historical verdicts.

## Fixed implementation scope
1 Damaged/unreadable incident state cannot abort assessment silently. Produce an
owned UNKNOWN alarm through an independent viable route; preserve original bytes
(or explicit inability-to-read evidence), incident identity/ack/deadline continuity
and notification deduplication. No silent empty-state reset. Exercise malformed,
unreadable, truncated and partially populated state and repeated checker/reopen.
If quarantine is used, it must preserve evidence and not overwrite the only copy.
Failure to preserve/write/notify remains explicit owned failure, not green.
2 Future heartbeat beyond a justified small tolerance is UNKNOWN/alarm; exercise
clock rollback and exact boundary. Negative age never becomes proof of freshness.
3 Bind completed pass to authoritative current process incarnation, preferably
systemd InvocationID plus appropriate process identity. Old/fresh prior-run pass,
PID reuse, missing/unreadable identity and restart before first completed Tick
must not certify current health. Bounded startup grace may avoid false alarms but
must not be called recovered. Heartbeat remains from completed control Tick.

Keep accepted core/host/py and main routing semantics frozen unless a concrete
live integration defect requires Tern's prior scoped amendment inside this SAME
budget. Changes confined to liveness/CLI service integration, tests, units/docs
and necessary fixture/qualification plan. No dependency, framework, compactor,
research, multi-project feature or presentation redesign. Build isolated branch/
worktree; no moving installed/main target during review or fixtures. New binary
and manifests must be immutable before each verification. Preserve P9's labels
until qualification; qualify exact binary shipped, not another build.

## A: admission and preregistration (corvid15m)
Pin adversarial checklist before Claude dispatch: reproduce three P8 failures on
base; same-case expected corrected outcomes; fault injection and true evidence
sources for each live case. Inspect unit/command feasibility read-only. Inventory
actual scripts, hashes, unit names/configs/callers and whether they affect only
campaign4: openwork, campaign4-watch, coax (including units named coax-dry),
shadow-watch and manual dispatch/deadline writers. Names alone are not scope.
Do not run watcher/pause or send tasks. Pin live/cutover checklist; bounded
rejection if scope, identity, allocation or executable path missing.

## B: candidate implementation and independent qualification
Claude60m, corvid30m. Reproduce pre-fix failures, positive and negative incident/
clock/incarnation cases, retained core/host/loop/expose suite +125 conformance and
adjudicated parity. Corvid uses unshared malformed-state/incarnation mutations.
Check actual CLI and systemd unit semantics, not only imported functions. Inspect
no hidden heartbeat goroutine, no false recovered from ack/send, bounded external
calls, notification failure handling and persisted response deadlines. No need to
repeat all mutation sweeps if relevant negatives and regressions establish scope.

Author delivers immutable candidate source/binary/build/manifest, complete test
logs and residuals, executable live plan and executable rollback/cutover plan
with exact command templates. Candidate PASS is not live PASS or cutover release.
ONE corrective attempt30m plus independent20m available only on Tern release for
eligible defects, shared across candidate/live stages (not one per stage). If a
live repair is used, affected cases must rerun within remaining original live
allocation and its signed plan; no free retries or time resets.

## C: fresh isolated live qualification
Cairn prep15m; corvid binding10m; cairn live60m INCLUDING archiving/cleanup; corvid
live-review20m. Tern signs exact binary/config/units/fixture IDs/incarnations,
commands, fault actor/onset, deadlines and automatic exact-ID cleanup before work.
Four distinct fresh worker/verifier/duty/director fixtures, no main-seat faults.
Prep idle only until signed live release. No reused historical sockets/evidence.
Live witness must exercise production Go entrypoints and actual systemd + wake:
- Positive worker->independent verifier->director decide on fresh non-cast principals,
  committed terminal disposition and no duplicate dispatch on restart.
- Kill run during bounded work/receipt handling: real automatic restart without
  blindly re-sending. Capture outgoing identities/counts and evidence reconciliation.
- Hang run: real watchdog termination/restart; additionally establish outside check
  detects a hang when restart cannot restore progress, without an in-loop helper
  fabricating the finding. Test corrected incarnation across restart.
- Restart loop reaches owned escalation; actual duty/director acknowledgements
  bind owner/next action/deadline, not merely delivered or queued wake. Include
  unavailable duty reaching director. Record recovery separately from escalation.
- Intentional stop exits64, no auto restart, stray service start cannot undo marker;
  explicit start resumes. Healthy terminal rest and deliberate stopped state stay
  quiet for >=3min and >=3 completed outside-check cycles each. No perpetual alarms.
- Real granted step timeout interrupts correct fixture once and wakes owner;
  deadline still enforces while run is down/stopped, callback replay no duplicate.
- Corrupt incident and future/prior-incarnation pass cases remain owned/UNKNOWN in
  actual independent checker path. Changes restricted to isolated fixture state.

Use trusted host event/journal timestamps and monotonic intervals, not model time.
Apply recovery ruling: explicit event detection30s, suspicion180s, detection to
recovery or acknowledged owned escalation60s (total90/240). Classify origin before
measurement; do not call a visible explicit failure suspicion after missing bound.
Healthy-host assumption stated; service outage and clocks discontinuous are not
passing samples. No exact source-time instrumentation of ACP needed: distinguish
observable host event from unknown remote onset. Store all failures/censored cases.
No five-case P6 proof apparatus or substitutes for actual executable paths.
If any required live gate lacks evidence, outcome NOT READY and NO CUTOVER.

## D: success step — bounded production cutover and first real package
Requires corvid live PASS + Tern explicit qualification acceptance and exact
cutover signature; sponsor permission already granted. Cairn cutover45m total;
corvid postcutover10m. The45m includes switch, first real worker20m/verifier10m
operation and rollback time; these are nested ceilings, not extra allocations.
Before switch capture hashes, unit enabled/active/config state, previous binary,
registry bindings, ledger/claims and exact restoration commands. Drain any old
in-flight work; never import edited historical TSV as current execution authority.
Use a NEW production campaign4 ledger/config and validated actual role bindings.
Keep portable binaries/versioned configs; installing the qualified candidate and
its exact units is authorized only by the signed cutover step.

Sequence: stop/disable the inventoried campaign4 old effect sources (openwork,
campaign4-watch, coax, shadow-watch; retire Cairn's manual-controller dispatch and
deadline/ledger-writing role). Verify no scheduled/active old effect source remains.
Then enable candidate run and independent health-check timer, verify servicing,
stop policy and duty route. No indefinite dual owners. If a named timer is shared
with another project, isolate campaign4's caller/config without disrupting that
project; return concrete overlap to Tern before switch. No script file deletion.
Keep wake transport, lane wrappers and campaign4-pause hard-stop actuator.
Cairn remains exception/duty owner; it may not silently resume manual scheduling.

First real work package within this success step: P10-production-handoff-1. Kiln
writes an operator handoff for the actual deployed loop (source/binary/config/unit
pins, install/run/status/stop/restore commands, effect-ownership/rollback map and
known limits); corvid independently checks those against read-only actual host
facts. Output campaign4/OPERATOR-HANDOFF-20260923.md plus machine manifest and
verification under this package. It is useful deployment documentation, not a
fixture token task or memory research. Authoritative dispatch, turn-end handoff,
claim/artifact verification, deadline and pending director decision MUST run via
agent-loop. Tern records the final disposition via that Go CLI. No manual wake
substitution may count as successful software operation. Predeclare its task and
completion requirements in signed cutover plan; do not let worker choose verifier.

Rollback on cutover failure: archive/reconcile in-flight action identities first,
disable candidate dispatch/health effects and owned deadline callbacks, reconcile
any already delivered worker/verifier execution (no duplicate or lost ownership),
restore previous binary/config as needed, then re-enable exact old timers and
Cairn controller ownership. campaign4-watch was suspended for rest but rearmed
for P10; restore its active campaign ownership on rollback. Stop marker alone is
not timer cancellation. Verify one effect owner after rollback. Never re-enable
old and candidate controllers together. If first real work times out, preserve
its outcome and rollback/owned block; no invented successful cutover.

## Budget, stopping and final evidence
Aggregate explicit ceilings minutes: admission15 + author60 + candidate-review30
+ sole repair30 + recheck20 + prep15 + binding10 + live60 + live-review20 +
cutover45 + postcutover10 =415. Package ceiling420; remaining5 UNALLOCATED.
Every stage gets host-read start/absolute deadline and one-shot duty enforcement.
No automatic extension/revision chain; unfinished required gate -> NOT READY or
CUTOVER_FAILED with rollback/owned-rest disposition, not automatic P10-r2. Actual
elapsed/work vs allocations separate. Prior P8/P9 spent histories remain intact.
Cutover grants cannot be spent before qualification. Any timeout/failure returns
to Tern for the one permitted repair or terminal disposition, within this budget.
Director decides ordinary boundaries; only charter hard stops require Brian.

Final report maps eight architecture checks plus supervisor liveness to exact
unit/CLI/live/production evidence, pins binary/config/adapter, counts all outcomes,
reports actual limits and retired/restored unit receipts. Cutover PASS requires
first real package and postcutover review, not merely a service marked active.
No scripted research launch follows. Research remains paused pending a separate
post-finish director package. No global provider/model or account linger changes.

## Current release
Admission ONLY. Cairn dispatches fresh corvid15m after rest explicitly ended and
campaign4 watchdog active. Pins/checklist precede author. Accepted admission
returns to Tern for notify-claude implementation release; no implicit live or
cutover. Full executable completion wake with profile/exact seat/qid/absolute
receipt in every dispatch. Compact append-only records; commit/push boundaries.
