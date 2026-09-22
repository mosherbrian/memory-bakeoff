# P6-r6 successful-output correction — Tern

Preparation2 FAILED after an actual side effect. Source bba4935 plus live evidence
is preserved. Read live-preparation-2/director-reconciliation.json and stop-receipt.json.
New worker0e734b30-1790050074 was created at the unique signed path with real socket,
then Tern stopped it. Registry entry retained for evidence; main four untouched.
Prior report '4 unchanged/nothing to stop' was wrong: saved post-registry lists5.
Tool journal completed-count is NOT an effects inventory.

Cause: agent-deck CLIOutput.Success checks quietMode BEFORE jsonMode. Passing
-json AND -q suppresses successful output. Launch exits0 with empty stdout; tool
loads {} then raises E_LAUNCH_NO_ID after creation. Prior negative NOT_FOUND probe
was misleading because CLIOutput.Error emits JSON even when quiet. Source at
/home/bmosher/src/agent-deck/cmd/agent-deck/cli_utils.go Success/Error and
launch_cmd.go output block establishes this distinction. No binary upgrade/edit.

Explicit prospective worker<=20m + independent corvid<=15m correction allocation.
Cumulative worker/verifier415/315 (395/300+20/15). Prior grants spent, not reset.
Preparation ceilings20m spent across two failed attempts; no new live preparation
or retry authorized. Held live witness15/fixture15 untouched. No automatic repair.

Fix only successful machine-readable launch output and durable partial-effect
reconciliation: remove quiet suppression while retaining JSON, strict returned
session_id/id correlation with registry/profile/lane/path. Persist raw stdout,
stderr, return code and prelaunch intent BEFORE validation discards any response.
An empty/malformed success, timeout or transport error must be reported as
ambiguous EFFECT, never zero created; retain evidence and require reconciliation,
no blind launch retry. Record each known returned ID before next side; retain
partially created ownership even if downstream socket validation fails. Do not
infer exact identity from title alone. Preserve parser-safe --idle-timeout=25m.

Regression must test SUCCESS JSON and error JSON separately using the actual
installed CLI behavior or inspected matching CLIOutput semantics, not a runner
that always returns the desired shape. Include quiet+json oldfailure, corrected
success id, empty rc0, malformed response, second-side failure and postcreate
binding failure. Corvid independently checks the distinction and orphan evidence.
No new live launches under repair/check; injected effects/private tmp only. Keep
prior candidate-review-repair.md, write candidate-review-repair-2.md; bind full
manifest and proposed preparation argv. No accepted core or shared-wrapper changes.
Stage C placeholders/full recovery gating remain separately blocked, not repaired
by this change. No re-use/restart/removal of stopped fixture without future release.

Cairn retires old preparation/cleanup timers after reconciling stop-receipt; keeps
failed attempts and correction event. Dispatch P6r6-repair-2 with absolute paths,
host start/deadline, relative timer, no overlap. Workdir:
/home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation
Bound claim hashes then independent<=15m corvid check. Expiry stops/reconciles,
BLOCKED returns Tern; no deadline resets. Next preparation requires new exact-hash
signature and collision-safe owned-resource decision from Tern.
