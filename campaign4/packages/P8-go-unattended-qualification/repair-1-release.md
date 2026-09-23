# P8 single repair release — authority and supervisor liveness

Tern, 2026-09-23. This prospective amendment releases Claude as the sole author
of P8's ONE repair, replacing kiln in the existing 30-minute grant. It implements
Parts A and B of proposal 6f9707f291dac4cdf7d37ca82ee81372ae64593d in agent-loop,
subject to the conditions below. The proposal is preserved as repair-1-proposal.md.
The baseline remains 4a00d675d4384f3bb43d9ab25a291847c7944cb2; live-1 evidence is
preserved at fc54a8e. Its configured-director E_UNTRUSTED_ACTOR is a real failure;
positive closure, timeout and restart/quiet cases were not reached. No retro-PASS.

## Scope and acceptance
A: freeze the core. Persist registry-validated runtime principal/role/session to
core-cast bindings per package, and check them at every core entry including
reopen, timer callback, explicit decide and on-pass close. Rebinding or missing
required binding fails before mutation/effects; never silently backfill historical
packages from current config. Worker/verifier/director sessions stay distinct.
Record actual principals in provenance/status. CLI use remains a trusted-host-user
boundary, not authenticated multiuser authorization. No new allowlist entries.
Preserve the failed live database; new fixtures use new package registrations.

B: implement the proposal's supervised run, intentional-stop marker, control-loop
heartbeat and independent outside liveness check, incident persistence and owned
escalation. No independent heartbeat thread may conceal a stuck Tick. Unknown is
not green. A queued/sent wake is not an acknowledgement. An ack binds incident,
owner, next action and absolute response deadline; it never means recovered.
Recovery requires fresh servicing evidence and reconciled state. Expired ack with
no recovery escalates; acknowledgement must not suppress a fault indefinitely.
Per-action timers remain effective while run is stopped; stop is not cancellation
of obligations already granted. Document this distinction.

Timing correction: 120s stale +60s interval +5s slack exceeds the stated detection
bound. Use a 100s stale threshold, 45s independent interval, AccuracySec<=1s,
RandomizedDelaySec=0 and bounded local read/send calls (combined <=5s per check).
This leaves margin under suspicion detection180s and detection-to-escalation60s;
record actual acknowledged endpoints, not just scheduled sends. The 90s watchdog
remains. Preserve existing explicit-failure30s/total90s requirements where an
explicit failure event is the trigger; a slower sampled health check is only a
suspicion detector. Do not relabel a missed bound as PASS. Host outages are outside
the healthy-host bound and must be explicit. Both checker and service operations
must themselves be bounded. No liveness action redispatches work blindly.

Retain core/host/loop regressions and adjudicated parity exceptions. Add the exact
live-1 failure regression, authority negatives/reopen, liveness state/incident
matrix and stop/rest/no-duplicate cases proposed by Claude. Independent corvid
checks both implementation and these conditions, with unshared negatives. No
Expose work, new dependencies, shared runtime edits or unrelated feature work.

## Allocation and execution
Original grants remain180m, including Claude30m replacing kiln30m and corvid's
postrepair20m. Allocate50m of the previously unallocated60m reserve NOW:
- Cairn fresh preparation10m, including raw identities and cleanup setup.
- Cairn repaired live witness30m, INCLUDING archive and cleanup.
- Corvid additional binding/live evidence review10m.
Total prospective ceilings230m of240m. All prior spent history carries; no grant
is recycled. The final10m remains unallocated, not an automatic extension.

Only the 30m implementation starts on this release. Its delivery receipt records
host UTC start/deadline; time waiting for delivery is not worker execution. Cairn
owns a one-shot deadline wake and no polling. At expiry Claude stops implementation,
files COMPLETE/INCOMPLETE with residuals, and does not extend itself. No second
repair and no P8-r2. Qualification ends NOT READY if remaining blockers cannot be
closed within this scope and cap. The last reserve is not a promise of another fix.

Work in an isolated branch/worktree based on the frozen candidate. Do not replace
main, installed binary, or any live environment. No real seat/service effects in
implementation tests. Candidate build stays private. File repair-1-claim.json in
this package with immutable source commit, full file manifest, binary hash/build
metadata, commands/results, proposal deviations and honest residuals. Preserve all
prior evidence. Every execution receipt embeds the executable completion wake.

On a bound complete claim, cairn may route corvid's existing20m postrepair pass on
those exact bytes, with an absolute deadline and archived evidence. An incomplete
claim returns to Tern; no automatic worker continuation. No live action follows
from a candidate PASS. Fresh binding, exact binary/config/units/commands/cleanup
and Tern signature are required before the newly allocated live work starts.

The later signed live plan will combine the unreached positive-decide, actual
step timeout and restart/no-resend observations with supervisor crash/hang/owned
escalation and intentional-stop/rest checks. Three-minute quiet windows replace
the proposal's ten minutes: capture at least three completed outside-check cycles
in each window, without sending/alarms. Report finite observed silence only. Do
not compress a failed/unfinished live case into PASS to fit a deadline. No main
seat injection, linger/account-wide change, cutover, script retirement or adoption.
