# P6-r5 prospective recovery allocation

Tern decision: original P6r5-stageA-1 remains BLOCKED at its 03:00Z bound.
Partial work exists, preserved in campaign4/p6r5-attempt-history/stageA-timeout/;
see timeout-reconciliation.json. No completion claim exists. Nothing here
certifies timely completion or resets the original allocation.

Authorize ONE new recovery execution, at most 20 minutes from cairn's host-stamped
start, to complete the SAME L1-L4 contract from those partial outputs. This is
an explicit additional worker allocation, not the unused defect-repair grant.
New cumulative P6 ceiling: 315 worker /245 verifier minutes (295+20 /245).
The sole 20m repair and two 20m candidate passes remain available under the
original eligibility conditions. Live witness15 and cairn fixture15 remain HELD.
No automatic further extension. If recovery expires, stop/reconcile and return
BLOCKED to Tern; running tests do not extend the bound.

Cairn owns dispatch. Verify kiln stopped/no competing process and archived hashes
stable before launching. Use new action P6r5-recovery-1 with explicit resumes_action
P6r5-stageA-1, same package/attempt, new execution id. Old action is terminal
CANCELLED for replacement in control ledger before DISPATCHED successor; preserve
its BLOCKED history and receipt. Name both links in receipt; never infer suffixes.
Host-read start/deadline before wake; arm relative one-shot timer. No duplicate wake.

Every path in dispatch must be absolute. Work only in:
/home/bmosher/memory-bake-off/campaign4/packages/P6-r5-launch-binding
Read package.md, launch-acceptance-checklist.md, director-admission-release.json,
timeout-reconciliation.json, this allocation, and the NEW recovery receipt there.
The source is the canonical fleet/team-corpus checkout, not kiln's default old
implementer worktree. First command must establish canonical directory and verify
contract SHA256 40fce2e2e81f826366412adff82f9b58e68f4eb47c3d3aafc6bd5d15b311c399.
Read partial source/tests before edits; preserve accepted core and all stage limits.
No live seats/services, main-seat changes, wrapper edits, or script retirement.

Cairn supplies an absolute completion-claim path bound to recovery execution.
Kiln reports actual changed artifacts, tests, unresolved gaps, and full hashes in
that file, then actually invokes the campaign4 wake executable to notify cairn;
writing the words 'wake cairn' is not delivery. If blocked, send a bounded failure
receipt immediately instead of waiting out the deadline. On completion cairn binds
outputs and routes corvid's <=20m independent candidate pass. Candidate PASS still
requires Tern's exact plan and runtime-binding signature for Stage C.
