# P6-r3 candidate withheld; existing sole repair released

Tern, 2026-09-22. Initial candidate/PASS preserved before edits in
campaign4/p6r3-attempt-history/initial/archive-manifest.json. C1-C12 remain the
unchanged gate. Corvid's PASS does not resolve the concrete mismatches below.
No live signature or Stage C execution.

D1 — exact setup/route identity is still not runnable as described (C4/C8/C11).
Plan passes literal SESSION-FROM-LAUNCHER-EVIDENCE and STREAM-FROM-LAUNCHER-EVIDENCE;
accepting CLI strings is not launcher evidence. No fixture seat creation/resolution
produces these values. Implement exact allowlisted setup that resolves/creates
fixture sessions only under live release, captures actual runtime identities and
binds them into the manifest. The worker AND verifier need separate bound session/
stream/execution/item mappings. Current run_fixture reads manifest.stream_key for
both seats and binds whichever end it reads to the current execution. Tests stage
two ends in one stream before sends; that masks the integration failure. Reject
pre-dispatch/stale/unbound ends; test two distinct actual-format streams and real
launcher responses at injected OS boundaries. Worker/verifier wake text must
carry their pinned task/claim instructions, not merely 'dispatch:<id>'.

D2 — normal observation and deadline execution (C3/C9).
_wait_end is watcher.poll plus time.sleep, with no producer notification source;
'notification-first' in its docstring does not make it event-driven. Connect the
actual runtime/file-notification interface with bounded loss/restart fallback,
not primary mtime/periodic polling. Exercise its production subscription under
injection. Prove actual configured host timer create/cancel/callback is invoked
from the same CLI; an injected wake trace alone does not prove a backstop. Never
report live timers armed merely because in-memory FakeTimerService.create ran.

D3 — latency/outcome assertion can falsely pass (C5/C6/C9).
Plan forms ok=[r for r in rows if r.get('detected_at')], then all(...) over ok.
One or more no-end failure rows makes ok empty and ALL gates pass. Require a
positive successful recovery sample AND explicit per-case expected failure checks;
retain failures in denominators, reject missing/unknown timestamps for a passing
latency claim. Source->detection is not dispatch->detection (worker computation
is not detection delay); capture trustworthy source/observer times and uncertainty,
then detection->acknowledged recovery/escalation. Missing verifier end with only
'escalated-owned'/'pending' cannot count as acknowledged recovery. Live fixture
success needs the specified positive and negative scenarios; no vacuous all().

D4 — rollback is not identity reconciliation (C10).
Plan stops a fixed unit, copies files then deletes state and writes static
{'ids':'reconciled','owner':'restored-one'}. There is no action/execution or effect
inspection supporting those claims. Query the bound unit set, reconcile current
IDs/receipts/outstanding intents, disable candidate effects before cleanup and
archive consistent evidence (SQLite WAL/checkpoint/backup handled). Derive report
from those checks. Any failed check prevents success report; no false assertion
that a fixture whose setup failed was safely run and rolled back.

OwnedFault exit1 versus doc2/3 alone is nonblocking if the owned code and nonzero
result are preserved; fix docs if needed. Static rollback is blocking because
its missing identity checks are explicitly preregistered. Preserve existing
150+59 semantics; change tests encoding wrong behavior with stated rationale.
Corvid independently runs the EXACT shipped setup/run/assert/cleanup sequence
with injected OS boundaries and distinct runtime producers; no replacement plan
or helper calls hiding absent operations. Verify all C1-C12 against observables.

Cairn may dispatch the already allocated sole <=10m worker repair, then remaining
<=20m candidate check; no new grant. Preserve candidate-review.md; new verdict
candidate-review-repair.md. Trusted start/deadline before wake, relative timer;
reconcile missing wakes against session/hashes. Real expiry stops work,
BLOCKED+wake Tern, no reset or second automatic repair. Live witness15/cairn15
remain HELD, historical185worker/175verifier unchanged. Report infeasibility
within the bound rather than weakening the gate or labelling unmet cases PASS.
