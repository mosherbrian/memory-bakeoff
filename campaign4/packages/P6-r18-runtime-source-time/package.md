# P6-r18 — explicit runtime source time for real turn ends

Tern author; corvid independent reader/verifier; kiln worker; cairn duty.
DRAFT. Candidate-only, NO shared host runtime/wrapper edits or live launches.
Parent R16 c8e99cf, acceptance82b1418; ../P6-r16-causal-identity/candidate/,
outer3862a0a2e8137ec154542cd6a7558952f5978c4482ecf11979d45a38675d0224.
R17 actual missing-sidecar evidence d0769c2e27b8fc51833a5fafadc62ac940f13436, sibling live-review-failed-1.md;
R17 terminal co-pinned with contract. inputs/ captures installed acp-worker and
both lane wrappers byte-exact with manifest. They are source snapshots, not secrets
or permission to read credential files. Corvid resolves full commit+hash before use.
Recovery4be99bf, clock650830c, identity84f094e, turn883107e, shadow-timef7b0cce,
notification5fefb0f remain governing. Quiet-rest duration blocker stays separate.

## Evidence and decision
R17 real worker/verifier generated runtime ends and claims but no onset sidecars;
actual task texts never requested them. R15 inferred sidecars; that is not reliable
instrumentation. Existing acp-worker emit writes t/item without timestamp and catches
write failures. Do NOT ask a model to type a clock or guess its future runtime item.
Instrument the trusted host runtime's actual turn-end append. Detection time must
never be relabelled source time; no historical backfill or retrospective live PASS.

## Authorized surface and architecture
Copy R16 candidate locally; allow changes to case_entry.py and local r3harness/
harness.py ONLY for consuming the new source receipt/join and exact fixture task
instructions. Accepted core driver/ingress/store/lifecycle/validator/turn_handoff,
host_adapter and existing transport/fault machinery remain byte-frozen. New local
runtime/acp-worker copy from pinned inputs plus small stdlib helper, fixture-only
lane launch wrappers, tests/docs/manifests allowed. Shared ~/.config/agent-deck and
conductor-chat repo MUST NOT be changed. No installs, model calls, real seat/service
operations, credentials or core clock/late-ingress rewrite. Return scope gap first.

Use an explicit opt-in runtime source-evidence interface for future isolated fixture
lanes. Runtime stamps host UTC at actual end append, with bound runtime session/item,
source provenance and honest uncertainty/clock-discontinuity handling. Receipt may
be versioned fields in the same runtime end record or an atomically paired source
record; specify one exact format and failure semantics in interface.md. Avoid an
additional unsynchronized sidecar when the authoritative event can carry its time.
Timestamp comes from trusted runtime, never model text, claim field, detection or
operator guess. Preserve unknown/discontinuity as INCOMPLETE. End-of-turn proves
turn ended, not work success: stalled/cancelled/failed ends cannot certify completed
work without authenticated valid claim and existing policy. No swallowed evidence
failure becomes a PASS; do not kill unrelated model work just because telemetry
failed. Demonstrate source-write/partial-write/crash behavior truthfully.

Consumer binds source record to exact current session/item and action/execution via
existing authenticated runtime/claim/delivery mapping. Unmatched/stale/duplicate/
wrong-execution or conflicting source does not get opportunistically matched.
Existing legacy records lacking reliable source remain explicitly unmeasurable,
not assigned current time. Already verified explicit producer sidecars may remain
supported only with declared source mode/provenance, no silent fallback or different
source selected to get a pass. R16 own-action join and explicit identity hold.
Keep source/detection/recovery clocks and uncertainty distinct; persist evidence so
reopen/replay does not stamp a fresh source time or extend grants.

Task contracts must say exactly who records source time (runtime) and what worker/
verifier must emit (bound claim/artifact/check), with executable helper commands if
needed. No undocumented producer-sidecar task or synthetic stream emitter. Package
includes fixture-lane launch plan using local instrumented runtime with current
model lanes preserved, exact source hashes and explicit opt-in destination/scope.
No proposed fixture may still execute the unchanged shared runtime by accident.
Disabled instrumentation remains backward compatible; future use requires exact
fresh prep/review/signature, not adoption into fleet seats.

## Admission and blocking tests
Corvid<=15m independent admission + concrete checklist BEFORE worker. Reproduce
R17 missing instrumentation on copied evidence and pinned runtime emit. Establish
real emitted runtime schema and local launch closure, not assumptions from fakes.
Decide exact format through worker design within requirements; return unresolved
interface conflict rather than silently writing a new timing policy.

Tests exercise actual candidate runtime emit/write method in isolated tmp streams
with injected clocks/no model calls; consumer must read those SAME emitted bytes
through production CLI composition. No parallel fake emitter fabricating friendly
onsets. No model-authored timestamp. Prove both normal success and genuine verifier
rejection generate usable matched source records without model sidecar help.
Negative matrix: missing receipt; empty/wrong item/session; previous execution;
conflicting duplicate; malformed/partial source; UTC discontinuity; write failure;
stall/cancel end without successful claim; delayed observer; restart. Each source
matches only its own action; unknown timing never passes or gets backdated. At least
one unshared independent source/identity mutation and actual producer-consumer
subprocess test of the shipped hook. Captured clock boundary uncertainty explicit.

Retain full78 composed +83+59 on actual modules; no skip/deletion or historical
source imports. Any assertion requiring legacy source only is reconciled BEFORE
change with corvid and Tern, no blanket weakening. Preserve R13/R14/R16 safeguards,
no duplicates, real rejection, source-vs-detection semantics and causal bounds.
Accurate acyclic manifests/descriptors including runtime/helper/wrappers and
unchanged-core comparison. Deliver candidate/, runtime/, interface.md, changes.md,
fixture-launch-plan.json, logs/commands/rc and NEW claim. Historical R15/R17 bytes
unchanged. Candidate PASS never certifies live timing or runtime adoption.

## Allocation and next boundary
ONE kiln<=45m; ONE corvid<=40m; admission15m separate. Prior cumulative1260/1035
->1305 worker/1075 verifier minutes. No automatic repair. Full suite~11m; honest
INCOMPLETE on unrun/expired, not120s probe substituted. No fixture grant in package.
Cairn releases admission now; conditional worker release only unchanged ACCEPTED
contract+pinned checklist/review+R17 terminal+runtime inputs, no overlapping writer.
Host-read start/deadline and one-shot timer; exact executable completion command in
every prompt/receipt. No inline sender or ledger edits. Failure returns Tern.
After PASS director accepts or opens evidenced correction, then separately allocates
fresh live witness; quiet-rest configurable-window correction still owed, not folded
into this source-time change. No silent idle boundary or new sponsor request.
