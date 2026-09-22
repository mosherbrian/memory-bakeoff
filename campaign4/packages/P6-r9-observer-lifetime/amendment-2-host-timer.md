# P6-r9 amendment 2 — reconcile actual host timer identity and callback

Tern; independent corvid admission BEFORE execution. Preserve live failure at
ac1613c8881a5c20049cd7b9b25d4302376b92f1, live-review-2.md and all source/receipts.
Candidate scoped PASS remains; actual positive handoff FAIL, no retroactive success.
Brian's explicit durable live authority (LIVE-AUTHORITY-20260922.md) governs future
releases. This repair is candidate-only; current fixtures belong to cleanup.

## Confirmed defect and directly connected callback defect

Reattach reads timer-arm:deadline:p6c-h1w, but create_host(unit,...) persisted
timer-arm:p6-stagec-h1.timer. Reattach tries duplicate systemd-run. Stored unit has
.timer.timer suffix although actual systemd unit has one .timer. One worker send,
no verifier send; no-end then E_TIMER_CREATE. Independent live review confirms.

Director source inspection: _arm_host_timer callback argv omits --db, but timer-callback
uses args.db default /tmp/p6h/harness.db. An actual timer must reopen THIS bound
fixture database/action, never a default unrelated one. Include every required
execution context and valid CLI ordering, not merely a token naming timer-callback.
The new timer must not silently succeed while enforcing no current work.

## Minimal authorized implementation

Unify declared logical action/timer identity with canonical host unit name across
arm persistence, reattach guard, query, callback and cancellation. No role/id inference
from incidental strings; normalize unit suffix exactly once. Reopen must reconcile
actual host timer facts rather than treating kv presence alone as proof of liveness.
Existing same-action/same-grant timer is reused, not recreated or extended; absent
owned timer can be reconstructed only for remaining original grant. Conflicting
unit/deadline/identity produces owned failure, not hijacking/deleting another unit.
If already overdue, perform bounded owned disposition, not a new full interval.

Fix callback context to exact database/action/identity with actual executable CLI.
Test callback against two independent temp databases: only intended fixture changes;
foreign/default remains untouched. Exact argv parser must run, not imported callback
alone. Callbacks fired early, stale or twice cannot cause premature/duplicate effects.
Keep timers a backstop to notification-driven handoff; no polling or broad redesign.

Explicitly authorize minimal local src/r3harness/harness.py AND host_adapter.py edits
for these defects (expands prior local harness-only allowance). Frozen parents/core
remain unchanged; new copy manifest identifies precise changes. Other module changes
require a concrete reproducer/Tern decision, not blanket authority.

## Acceptance evidence

Corvid pins a short checklist before worker: reproduce stored/queried-key mismatch,
doubled unit and missing-db callback on immutable parent. Tests intercept the OS
boundary with a faithful systemd model: duplicate create MUST reject, queries report
current units, cancel addresses canonical name, and process reopen loses local memory.
An always-success runner cannot certify this defect. Old-fails/new-passes actual CLI
positive sequence with delayed worker and reattach: one timer creation and exactly one
worker/one verifier send. Reopen with valid timer, missing timer, expired grant,
conflicting unit; assert no extension/no duplicate effects. Execute recorded callback
argv with private fixture context and verify real state effects, no /tmp/p6h fallback.

Run retained27-test suite/updated tests, full no-simulated five-case composition and
observer/tamper/identity/receipt/signature regressions. Separate targeted result from
whole-suite result. Mechanically refresh manifest and transitive hashes, no self-hash.
Every known residual stays declared; no retry-until-green or skipped failing gate.
Actual systemd evidence will be collected in a separately signed fresh live run after
candidate verification. Candidate tests themselves mutate no real services/timers.

## Allocation and release

Corvid admission/checklist<=5m separate as before. After unchanged amendment ACCEPTED
and checklist pinned, ONE kiln<=35m, ONE corvid verification<=25m. Prior P6 ceilings
810worker/555verifier ->845worker/580verifier. No automatic further repair. Past
candidate grants consumed; no new preparation/live/witness grant here.
Cairn pins amendment/review/checklist before ONE P6r9-repair-2 dispatch, no overlap,
new execution, absolute cwd/claim/receipt, host start/deadline and relative timer.
Bind outputs before candidate-review-repair-2.md. Expiry/verdict returns Tern.
No fixture reuse/restart under this grant; old live signatures expire unchanged.

Cairn independently verify current campaign4-p6r9-prep3-cleanup completed after~14:10Z
and archive exact-ID stop/remove evidence; don't claim pending cleanup PASS. Director
already confirmed positive timer/service inactive. Cleanup monitoring is existing
live duty, not permission to run another fixture. Research/production state/shared
wrappers/credentials/shadow/retirement untouched; stdlib boundary retained.

Continuation rationale: live delivery works and this failure pinpoints a concrete
persistence-key mismatch that successful fake timer creation concealed. A small
identity+callback repair with a rejecting host model is warranted, not a rewrite.
Fresh live witness remains necessary; candidate success alone cannot prove reliability.
