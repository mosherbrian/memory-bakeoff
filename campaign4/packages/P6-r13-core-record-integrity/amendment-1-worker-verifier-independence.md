# P6-r13 amendment 1 — enforce producer/verifier independence at ingress
Tern; 2026-09-22T21:20:05.741343+00:00.
DRAFT, serial amendment. Finding11 in CODE-REVIEW-20260922.md @e48f3bd is a
core-integrity blocker. Original R13 attempt continues unchanged through completion
or its ORIGINAL21:33Z bound; no new requirement inserted into that attempt. Preserve
its exact claim/output/manifest and pin BEFORE this amendment executes. No overlap.

## Evidence and scope

Reported public trusted-ingress reproduction on P5-r2 80092f92: kiln publishes as
worker, then verify_pass as kiln/verifier yields COMPLETE. lifecycle compares seat
to state.worker_seat which no real transition sets; hand-seeded test misses the
bug. R11 baseline924d21a carries same guard. Corvid independently reproduces on
immutable originals AND captured R13 initial candidate, without manually setting
worker_seat or bypassing ingress. Record source pins and actual ledger actors.

Allow changes within original three local modules lifecycle.py/ingress.py/store.py,
plus tests/docs/manifests. No historical parent edits or host-adapter/core API
bypass. Preserve original A-E checks and HostClock.now. Do not weaken atomic-shape,
UTC-instant, immutable-disposition or rollback fixes to satisfy new identity tests.

## Required behavior

Persist authentic producer identity for the CURRENT published attempt, sourced
from trusted-ingress actor provenance and accepted publish/attempt ledger events,
not an optional caller-supplied worker_seat or manually seeded state. A START event
is authored by duty; its actor/flight owner is not automatically the worker. Do not
record cairn as worker merely because it starts dispatch. Tie identity to actual
artifact-producing action/revision/attempt; reject spoofed author overrides.

Both verify_pass and verify_fail from the same principal that produced the checked
artifact reject before any row/cache/state/atomic disposition mutation. Switching
role label from worker to verifier must not defeat the rule. Authorized distinct
verifier continues to work. Equality is principal identity, not an inference from
seat name, filename, role string or hardcoded kiln/corvid pair. A missing producer
identity must not silently allow verdict; recover it only from authentic prior
ledger events or fail closed with an owned explicit error.

Persist/replay/reopen reconstructs identity without tests seeding worker_seat. Repair
attempts, new revision, and worker change must bind their own actual producer and
not retain stale identity: new producer cannot verify its work; an earlier producer
is not forever forbidden from verifying unrelated later work solely by that history.
Preserve worker identity after its flight is cleared/replaced by verifier flight.
No new general role-policy/multi-project framework in this amendment; that future
work is separate. This fixes the explicit author-is-not-verifier invariant even
within current trusted seat set. Other authorization gaps must be reported, not
silently bundled into an unbounded rewrite.

## Admission and blocking tests

Corvid<=10m independent admission plus executable public-path cases BEFORE amended
worker dispatch. Old-fails/new-passes: actual publish via trusted ingress, same-seat
verify_pass and verify_fail reject; atomic hold/decide on rejected verdict leaves
zero writes; both checks hold after reopen/replay. Distinct legitimate verifier
still reaches its correct state/disposition. Include adversarial claimed worker_seat,
role swap, missing/corrupt producer provenance, repair attempt/new producer, and
wrong revision/action references. No Driver.verify-only test (it hardcodes corvid),
no direct state injection presented as public proof. Internal invariant tests may
supplement but cannot replace this end-to-end ingress evidence.

Worker completes original R13 A-E and these tests, retained core83+59 and composed
R11 gate42 against ACTUAL new local modules; test imports/hash paths recorded.
Corvid independent per-family mutations and full final gate, no skipped failures or
self-hash manifest. Update provenance and claims mechanically. Original initial
attempt result remains as recorded, no retrospective claim it included finding11.

## Serial allocation and release

After initial attempt ends and output/claim/base pin captured: retire its timer,
keep kiln idle, do NOT automatically send old-scope candidate to verification. If
original verification already began before this instruction, let it finish without
interruption, preserve its verdict and then start amendment admission. Never overlap.
Cancel unused original verifier grant if not dispatched; record separately, do not
quietly reuse or reclaim historical ceiling. No unlimited scope/time for old attempt.

New prospective amendment: reader10m separate; ONE kiln<=30m; ONE corvid<=30m.
Original P6 candidate1070worker/795verifier ceiling ->1100/825. Any unused old30m
verifier cancellation reported separately. This is conservative cumulative grants,
not asserted elapsed usage. No automatic repair. Conditional Tern release only after
independent unchanged amendment ACCEPTED, concrete cases and captured initial base
pinned. Cairn host-read deadlines, relative active timers, one execution per step.
At expiry/FAIL/INCOMPLETE preserve and return Tern. No live/preparation release.

## Go conformance handoff

~/projects/loop/conformance is external read-only evidence/tooling, not part of
this worker's write scope or a new runtime dependency. If useful, inspect recorder/
mutations without editing that repo or adopting recorded old Python behavior as an
oracle. At acceptance publish full new source commit and behavior-change list
(#2/#6/#7/#10 and #11; #5 truthful status), so Brian's independently authorized Go
work can re-record and report differences. No claim those new recordings exist until
that work reports them. A Go/Python disagreement is a finding, not either side's
automatic correctness. Live hold and known host-timing findings remain unchanged.
