# Where the harness code is

Director-maintained map, 2026-09-22. Acceptance is scoped evidence, not deployment.
There is no adopted production harness yet. Package number alone never selects code.

Further live releases are held for the [ten-finding review disposition](CODE-REVIEW-DISPOSITION-20260922.md): durable-record and host-timing concerns require regression proof and correction. Prior acceptance is scoped, not a clean bill of health.

| Start here | What it is | Accepted version / limit |
|---|---|---|
| [P5-r2 core](packages/P5-r2-atomic-authority/src/) | Lifecycle, validator, SQLite store, driver, trusted ingress, supervisor/status; stdlib-only baseline | `80092f92c24fb58ad70478faf93e4f39eb184847`; [acceptance](packages/P5-r2-atomic-authority/acceptance.json). Internal fake/store helpers are not public ingress. |
| [P6-r9 case entry](packages/P6-r9-observer-lifetime/src/case_entry.py) | Previous accepted candidate's case CLI | Source `f1d7c86f0b38fb653734beb9d906dae44a10a41a`; 34-test gate and one real positive handoff accepted. Fault/rest limitations below. |
| [P6-r9 runtime](packages/P6-r9-observer-lifetime/src/r3harness/) | Actual local harness, host adapter, observer and copied core used by those cases | Same source pin; [composition manifest](packages/P6-r9-observer-lifetime/composition-manifest.json) binds the executable files. Do not replace this directory with P5-r2 by assumption. |
| [P6-r9 fixture support](packages/P6-r9-observer-lifetime/src/) | Fault controls, delivery wrapper, source-time tools; `seat_emulator.py` is test-only | Same manifest. Presence of test helpers is not permission to substitute them into live evidence. |
| [P6-r11 candidate source](packages/P6-r11-case-observer-continuation/candidate/src/) | Earlier accepted candidate: failed/quiet continuation, authenticated rejection, routing-error propagation | Source `924d21ab0884946393d614c015c9b70fc669f260`; [acceptance](packages/P6-r11-case-observer-continuation/acceptance.json), 42-test gate. Injected only; supersedes R9 for candidate development, not its historical live witness. |

Latest accepted candidate: [R13 source](packages/P6-r13-core-record-integrity/candidate/src/) at `5410332b1d614823ca29d343b051ab471c4bacb3`, [acceptance](packages/P6-r13-core-record-integrity/acceptance.json). Record-integrity and producer/verifier repairs; 59 composed +83+59 retained tests. Injected only. R14 host-timing candidate is now accepted as described below; historical live evidence is unchanged. Finding5 was not reproduced on the tested public path.

The executable surface is not yet standalone. `case_entry.py` directly references
[P6-r5 source](packages/P6-r5-launch-binding/src/) and
[P6-r6 source](packages/P6-r6-live-preparation/src/); preparation and cleanup also
use P6-r6 tools. Those are pinned runtime dependencies, not disposable history.
Start at `case_entry.py`, then its local `r3harness/harness.py` and host adapter;
use the signed plan/manifest to resolve the exact transitive surface. No live
command is provided here: expired fixture signatures must never be reused.

Evidence to read: [candidate acceptance](packages/P6-r9-observer-lifetime/candidate-acceptance-repair-3.json),
[positive live acceptance](packages/P6-r9-observer-lifetime/live-positive-acceptance.json),
and [R10 incomplete matrix](packages/P6-r10-live-recovery-matrix/terminal-disposition.json).
Positive handoff worked live on R9. R11 fixes failed/quiet continuation and authenticated rejection in injected tests; no R11 live witness yet. Lost-completion and queued/ambiguous controls remain missing. [R12](packages/P6-r12-reviewed-regressions/package.md) reproduces the ten code-review findings while live releases stay held. No four-case recovery, shadow or adoption PASS.

Other package directories are work/provenance records, not alternative recommended
installations. Historical bytes can still be dependencies of a later accepted
surface. Missing verdict means unaccepted/unknown, never implicit promotion.
Do not edit/delete frozen packages to clean up navigation.

[Source-repository decision](SOURCE-REPOSITORY-RULING-20260922.md): extract a small
normal source tree after current P6 live-path work, preserving every existing pin.
Tern updates this map at source acceptance/promotion boundaries; ordinary receipts
and dispatches do not require updates. This file is navigation, not execution authority.

Latest accepted composed surface: [R14 candidate](packages/P6-r14-host-timing/candidate/src/) at `02ea693e48cce93deace64e7e1e545f831506d8d`, [acceptance](packages/P6-r14-host-timing/acceptance.json). Timer authority, separate verifier grants, owned observation continuation and honest metrics; 70+83+59 injected tests. R13 core unchanged. R15 is the pending fresh live failure/rest witness, not deployment. Lost-completion proof and queued/ambiguous controls still unresolved.

R15 live failure case demonstrated genuine rejection/no-COMPLETE/1+1 sends, but causal timing was INCOMPLETE: onset selected by filename order. [R15 disposition](packages/P6-r15-live-failure-rest/terminal-disposition.json) preserves it; R16 is the pending narrow identity-join correction. R14 remains accepted injected candidate, not live recovery acceptance.

Latest accepted composed candidate: [R16](packages/P6-r16-causal-identity/candidate/src/) at `c8e99cf966b3f10ea5a5c22704ba8af087038246`, [acceptance](packages/P6-r16-causal-identity/acceptance.json). Causal evidence joins by bound item/action; explicit sidecar item required; 78+83+59 injected tests, all other production Python unchanged from R14. R17 is fresh live witness work, not adoption.

R17 live failure again proved authenticated rejection but remained INCOMPLETE: required onset sidecars were absent and never specified in task text. R18 is pending explicit runtime source-time instrumentation, isolated from shared fleet runtime. R16 remains the accepted candidate; no timing/adoption PASS.
