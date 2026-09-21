# P3 revision 3 — close the remaining authority exceptions

DRAFT; independent admission required. Director/author Tern under CHARTER.
Worker kiln; independent admission/verifier corvid; controller/duty cairn.
Implementation, same P3 question; no live integration.

## Task, evidence and pinned inputs

Complete the existing ledger-authority requirement, without redesign. P3-r2
repaired code passes 54 tests and resolves the five prior supplied failures.
Tern nevertheless reproduced REST with an invented decision reference missing
from the ledger, and ACTIVE where a fabricated acknowledged receipt on an
undispatched handoff satisfies a predecessor successor_opened disposition.
These are actual current contract failures, not new desired features.

Input directory campaign4/packages/P3-r2-ledger-authority at commit
624dedcb801f9bcd87cd1f4f7c28ffd5175c803c: src/, tests/, fixtures/, README.md,
implementation-report.md, director-v2-manifest.json, verification.md and
 director-postrepair-check.json. Manifest records exact per-file SHA256.
Original contract campaign4/packages/P3-core-validator/package.md at
fa6af8b00ffd19ebe216a78fdf5a242604a8be6f, and r2 package.md at
0b00ea3f79f3ff02822ba69158a59f436bc7129e remain binding. Frozen P2 specification
campaign4/packages/P2-r2-boundary-amendment at
5bfbb071e6efdb6f15de1c582295363a94cd08c7 governs lifecycle semantics.
Copy baseline into this directory; prior package and archives stay immutable.

## Required correction and completion check

1. Missing authoritative decision data cannot be supplied by the projection.
Reject invented decision references/reasons; ensure legitimate attributed
terminal decisions remain representable through the real durable store.
Do not relax comparisons merely to make old incomplete fixtures pass: repair
fixtures to represent authoritative decisions and retain explicit invalid cases.
2. Check all authority-bearing fields in every flight variant: dispatched
worker/verifier, bounded handoff, pending director decision, and no-current-action.
Null or absent ledger receipt is not acknowledged dispatch. In particular, a
forged handoff receipt cannot discharge successor_opened. Ledger-backed pending
handoff remains ACTIVE on its own without claiming it is dispatched work.
Correct DECISION entries remain representable; forged receipt/action/owner/
deadline/phase or unsupported populated metadata must fault.
3. Both supplied probes must reproduce their false valid outcomes on pinned r2
and INVALID on r3. Add a table-driven mutation matrix over the variants and
fields above, including missing authoritative facts, not merely changed facts.
Use real store-derived and reopened snapshots as well as focused dictionaries.
Retain all 54 previous regressions and five repaired probes, true REST for all
three kinds, genuine ACTION_DUE once, historical successor chains, verifier
flight/expiry, bounded handoff, atomic/restart, allocations and no-duplicate
execution. Preserve documented runtime-type checks and UTC comparisons.
4. Corvid independently runs the suite and adds unshared missing-fact and
receipt-forgery cases across handoff and DECISION, plus a genuine store-backed
terminal decision. Independently compare r2/r3 probes and expected semantics.
Report exact hashes, actual outcomes and limitations. Test count is insufficient.
Do not certify claims absent from the evidence. Tern acceptance still required.

## Outputs and permissions

Only src/, tests/, fixtures/, README.md, implementation-report.md here and /tmp
scratch state. Python 3 standard library, no external dependencies. Reader and
controller write admission/verification/dispatch evidence. No old-package edits,
live state.json, watcher/service changes, live wake/stop/Signal from code,
research or rollout. Update runnable commands to this package path.

## Explicit prospective allocation and history

P3 already granted and spent 150 worker / 115 verifier minutes of attempt
ceilings; actual wall times are separate, unused minutes in spent attempts are
not transferable. P3 r1 initial + two repairs and r2 initial + sole repair,
including withheld PASS verdicts, remain in history. No reset by revision name.
New allocation: initial worker <=30m; one eligible repair <=15m; independent
verifier <=20m per pass including post-repair. Cumulative P3 grants become
195 worker / 155 verifier minutes. Admission corvid <=15m plus one <=10m
confirmation if Tern repairs this contract; tracked separately from execution.

Cairn records starts and absolute deadlines BEFORE each acknowledged wake,
arms one-shot deadline events, preserves versions before repair and binds
hashes at handoff. No polling, no overlapping attempts. On expiry stop overdue
work, record BLOCKED and wake Tern; no automatic extension. Controller-recovery
verification remains <=10m per pass inside remaining allocations, not extra
budget. After spent repair no further execution without Tern prior allocation.
At terminal boundary Tern opens warranted successor or records why none is
warranted. Only CHARTER hard stops pause the whole campaign.
