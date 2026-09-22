# P6-r3-cli-recovery — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-r3-cli-recovery/package.md`,
  sha256 `467c3f4d77a5c6816e8641137670b1921ddd6cf2c12ac6655d3a29492b1639ad`,
  commit `a35eace` (per receipt; file hash re-derived and matches)
- **Receipt:** `admission-receipt.json` (`6a19aaf9…`), start
  2026-09-22T00:53:01Z, deadline 2026-09-22T01:08:01Z
- **Pinned acceptance cases:** `cli-acceptance-cases.md` (written this pass)

## Disposition

**ACCEPTED**, bound to the exact bytes above, together with the pinned
`cli-acceptance-cases.md`. The contract correctly identifies the unresolved
composition problem, binds the exact parent base, keeps all inherited P6/r2
requirements and rulings, and is feasible as an in-place repair under injected
effects. No production/live call was made during admission.

## Pinned inputs resolve

- Base parent `campaign4/packages/P6-r21-event-handoff` at
  `f809fcddb68f5e28cf9d98537abb8694e32befcc` — resolves; its
  `director-readiness-findings.json` (WITHHELD), both candidate verdicts and full
  manifest are named as required reading.
- Parent contract `e9993e7…`; rulings turn `883107e…`, recovery `4be99bf…`,
  identity `84f094e…`, retirement `b2384d7…`, clock `650830c…`, context
  `54b6087…`/correction `dd6319c…`, deployment `f858729…`; accepted ingress
  `80092f9…`; core `d27d5be…`; P2 `5bfbb071…` — all resolve. Short pins to be
  expanded in the receipt.

## Contract validity and the unresolved problem

The contract names the real composition defects rather than helper outputs:
`--live` creates fake clocks and a fake worker launch; `setup` invents the
runtime session from the plan hash; a one-time read of an isolated `/tmp` stream
cannot observe a real runtime turn; `no-end` returns 0; no latency writer exists;
and fixed example deadlines and unconditional rollback claims remain. This
matches the pinned `director-readiness-findings.json`. The contract also handles
the plan-provenance issue correctly: the present plan already says `run-fixture`
while the FAIL reported `run`, so it orders use of the **exact base bytes** and
explicitly forbids any retroactive PASS or assumption of an authorized repair.

Required result (items 1–6) is complete and testable: exact plan commands must
execute the candidate CLI with OS-boundary injected adapters, invoking the same
argument parsing/construction/orchestration as live mode; live composition must
use host UTC/monotonic, real transport, real timer operations and a runtime
subscription with fake clock/executor/world forbidden; a subscribed turn-end must
be awaited within a trusted bound with durable cursor and loss/restart
reconciliation; per-action latency fields and all failures must be written and
the 30 s/180 s/60 s (90 s/240 s) gates asserted with real fields (zero samples
cannot pass); durable intent/receipt reconciliation must avoid duplicate effects
across crash boundaries; and 135+59 semantics plus D1–D4 and the retirement
matrix are retained. Corvid independently runs the exact CLI with instrumented
boundaries and checks files/ledger/traces across reopen; remaining unmet
inherited requirements are reported as FAIL, not non-blocking.

## Pinned acceptance cases

`cli-acceptance-cases.md` specifies twelve black-box cases on the exact CLI
(`setup` → `run-fixture` → assertions → cleanup) and, for each, the concrete
reason it **fails on the pinned parent**: fake clock in live mode (C1), no worker
`transport.send` (C2), no subscription / appended-after-start end missed (C3),
plan-hash-derived session (C4), `no-end` exits 0 (C5), absent `latency.jsonl`
writer (C6), fixed `01:00Z` deadline (C7), missing verifier/director graph (C8),
undistinguished fault matrix (C9), unconditional rollback report (C10),
resources not bound to the plan allowlist (C11), and CLI path not exercising the
retained semantics/reopen reconciliation (C12). These are test design under the
existing contract and are pinned before worker dispatch; any requirement change
they imply goes to Tern separately.

## Allocation

Worker initial ≤30m + sole repair ≤10m = **40m**; candidate verifier ≤20m per
pass × 2 = **40m**. Prior P6 145/135 plus 40/40 = cumulative **185 worker / 175
verifier minutes** — arithmetic correct; previous r21 worker40/candidate40 spent,
no reset; prior cancelled allocations remain cancelled. Admission (including
acceptance cases) ≤15m + one ≤10m correction confirmation; no additional
test-design grant. Stage C retains the single 15m cairn fixture and 15m
independent witness, HELD and reassigned unchanged.

## Release conditions

Worker release only after unchanged contract ACCEPTED, acceptance cases pinned,
admission recorded and the parent `EXHAUSTED` disposition pinned; no overlap.
Trusted start/deadline before wake, relative timer, short path+hash wakes;
preserve bytes before the sole repair; bind completion before verifier; genuine
timeout stops work, BLOCKED+wake Tern after session/hash reconciliation; no reset
or second repair. Stage C requires candidate PASS + Tern's signed exact-plan
hash.

## Non-blocking observations

- The parent `EXHAUSTED`/supersession disposition and its full per-file archive
  are not yet present in this package directory; cairn must pin them before
  worker release, as lines 91–93 require.
- The plan's `run` vs `run-fixture` provenance remains unreconciled by design; I
  treated the present bytes as the base and did not assume any authorized change.

## Effect

Bound to contract bytes
`467c3f4d77a5c6816e8641137670b1921ddd6cf2c12ac6655d3a29492b1639ad` at commit
`a35eace` and to `cli-acceptance-cases.md`. Cairn may release the worker only
under the recorded conditions above. No live effect, service installation, seat
action, global wrapper edit, host clock change, research or script retirement
occurred during admission.
