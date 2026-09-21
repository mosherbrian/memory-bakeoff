# P6-live-recovery — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker)
- **Date:** 2026-09-21/22, canonical root `/home/bmosher/memory-bake-off`
- **Contract:** `campaign4/packages/P6-live-recovery/package.md`,
  sha256 `174377f112e460b6cba1132ac2337beff90a99f2cb0d777b4dbaeb9b9d20fde4`,
  commit `91f19cf3cd2579418137381e6f3ddb95d7008d78` (re-derived; working tree
  matches)
- **Receipt:** `admission-receipt.json` (`343b1874…`), start
  2026-09-21T23:47:53Z, deadline 2026-09-22T00:02:53Z

## Disposition

**ACCEPTED**, bound to the exact bytes above. The contract measures the intended
question (host adapters and a bounded live recovery fixture with measured
latency and one effect authority), its inputs and rulings resolve, the staged
gates are explicit and feasible, and the allocation arithmetic is correct. This
is admission of Stage A only; no live action is authorized.

## Pinned inputs resolve

- P5-r2 source at `80092f92c24fb58ad70478faf93e4f39eb184847` — resolves; its
  verification is `ff1f6d89…` as cited.
- Rulings: `RETIREMENT-RULING` `b2384d7…`, `RECOVERY-ACCEPTANCE-RULING`
  `4be99bf…`, `ACTION-IDENTITY-RULING` `84f094e…`, deployment `f858729…`,
  clock decision `650830c…` — all resolve.
- `P2 boundary spec` `5bfbb071…` and `P3-r3 core` `d27d5be…` — resolve.
- Abbreviated pins are to be expanded in the receipt; no moving HEAD.

## Scope and host-interface feasibility

- **Task** (lines 1–6): a narrow host adapter around the accepted P5
  ingress/store — not another platform or polling controller — to test whether
  the controller can recover missed handoffs with measured latency and one
  effect authority using real host interfaces.
- **Host interface is bounded and feasible** (lines 20–24): read-only discovery
  of `~/.config/agent-deck/{wake,campaign4-pause,campaign4-watch,openwork,
  acp-go,acp-go-controller}`, relevant user units and campaign4 ACP event/history
  interfaces, with exact hashes/unit properties captured in `host-inventory.json`
  before implementation relies on them; **do not execute** pause/watch/openwork
  during discovery and do not collect credentials. This is consistent with the
  retirement ruling (wake is an in-scope transport, its global behaviour must not
  be modified; pause stays the emergency actuator).
- **Required implementation** (lines 29–51): trusted source capture of
  completion/failure/dispatch receipts keyed by package/attempt/action/event/
  execution IDs, with host-context clock and attribution (artifact output not
  self-certifying); persisted cursor and restart/lost-wake reconciliation against
  actual session outcomes and bound hashes; a started/queued ack is not
  completion; no blind retry on ambiguous delivery; unavailable observation is
  an owned fault, not idle. Software creates/reconciles/cancels one-shot
  relative timers from remaining authorized ledger duration with stale/early/
  cancelled rejection; every external call bounded; no model polling; host
  subscription or bounded non-model observation permitted with documented
  cadence/failure/resources; explicit dead-turn failures consumed with the
  deadline as fallback, not the completion detector. Declared identity is
  enforced across resume/replacement per the action-identity ruling (late old
  executions cannot finish/interrupt replacements; no suffix inference). Correct
  terminal rest is quiet; missing disposition/malformed state/unrelated seat
  activity cannot hide invalid work; independent health supervision does not
  depend on the process it supervises; notifications/all-seat stop are fake
  targets and existing `campaign4-pause` is unchanged.

## Stages and gates

- **A. Implement** (lines 55–63): listed outputs including `host-inventory.json`,
  `fixture-plan.json`, `retirement-matrix.json`, `rollback.md`; disposable
  `/tmp`, fake adapters and read-only host inspection only; no service
  installation, seat wake/stop, `state.json`, ledger adoption, global wrapper
  changes or host clock changes. Worker proposes exact fixture IDs, seats, units,
  commands and cleanup; the four campaign seats cannot be stopped/repurposed and
  any fixture seats stay in the campaign4 profile with unique `p6-fixture`
  names; no research workload. Feasible and bounded.
- **B. Candidate check** (lines 65–70): corvid verifies pure/injected tests,
  host-interface assumptions, effect allowlist, grants, identity/receipt
  persistence, rollback and fixture feasibility; 83 P5 + 59 core semantics
  preserved; copied store/driver changes allowed for declared identity/adapters
  but any changed accepted semantic is reported before implementing; no live
  effect; bind candidate bytes and fixture plan.
- **C. Live fixture** (lines 72–80): only after candidate PASS **and Tern's
  explicit signed release of that exact fixture-plan hash** (Tern's gate, not
  Brian's); cairn runs one ≤15m fixture while corvid independently witnesses
  within its ≤15m grant; no overlap with implementation; allowlisted solely to
  fixture-owned seats/files/units/ledger; shadow comparison read-only and cannot
  wake/stop; no fleet-wide cutover or script disablement. This matches the
  recovery/retirement rulings.

## Completion check

Items 1–6 (lines 82–119) are complete and testable: the injected
event/transport/timer failure matrix (lost completion wake, explicit failed
turn, queued wake, restart before/after send and ack, stale/duplicate/reordered
events, lost/removed/early timers, startup ambiguity, stale execution
completion, same-action resume, genuine replacement, transaction-boundary
restart) with independently reconciled effects and no duplicate dispatch,
phantom ack or unlimited retry; a real host fixture demonstrating the
worker→verifier→director receipt flow with a deliberately suppressed completion
recovered without a human prompt, plus bounded unavailable-receiver escalation,
with all failures retained; the prospective latency gates exactly as in the
recovery ruling (≤30 s explicit detection, ≤180 s never-started suspicion,
≤60 s detection→recovery-or-acknowledged-escalation, i.e. ≤90 s/≤240 s totals,
recovered and escalated separate, queued wake excluded, model completion not the
endpoint, no outages/clock ambiguity as passing samples, provisional 90 s grace
not assumed); live witness of transport/timer/restart/cleanup with destructive
effects only through fakes and labelled simulations; the retirement matrix with
exact hashes, effect owners, evidence and disable/restore commands plus a
rollback plan that disables candidate effects, reconciles IDs/timers, then
restores one owner; and independent bound-live-evidence verification by corvid,
with acceptance requiring both candidate and live evidence and no retroactive
unit-test adoption claim.

## Allocation

Worker initial ≤45m + sole repair ≤15m = **60 worker**; corvid candidate ≤20m
initial + ≤20m post-repair = 40m plus live witness ≤15m = **55 verifier**;
cairn live fixture ≤15m **separately**. Prior P5 cumulative 95/85 stays
historical; unused P5-r2 repair 10m/post-repair 15m are cancelled at acceptance,
not transferred. Admission ≤15m + one ≤10m confirmation. Arithmetic correct;
effort ceilings distinct from runtime/provider spend.

## Non-blocking observations

- Tern's separate P5-r2 `acceptance.json` is not yet present in the P5-r2 tree;
  cairn must pin it before any Stage A dispatch, as line 130 requires.
- The contract's Stage-A host discovery touches scripts that are themselves
  retirement-matrix subjects; the explicit read-only, no-execute rule is the
  right guard and must be observed (I performed no execution and collected no
  credentials during this review).

## Effect

Bound to contract bytes
`174377f112e460b6cba1132ac2337beff90a99f2cb0d777b4dbaeb9b9d20fde4` at commit
`91f19cf3cd2579418137381e6f3ddb95d7008d78`. Cairn may release **Stage A only**
under the recorded conditional release once admission is recorded and the pinned
P5-r2 acceptance is present; Stage C additionally requires corvid candidate PASS
and Tern's signed exact-fixture-plan release. Changed bytes require independent
confirmation. No live actions, service installation, script retirement or host
clock change now.
