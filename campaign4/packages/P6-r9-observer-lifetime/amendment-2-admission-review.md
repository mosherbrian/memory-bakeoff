# P6-r9 amendment 2 (host timer identity/callback) — independent admission review

- **Reviewer:** corvid (contract reader; independent of author and worker; no
  implementation authorship)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Amendment under review:** `amendment-2-host-timer.md`, sha256
  `592d24c15a42d1328b45abdedd4e3b1e3e718cdc7c8f417570232e5144f8e22a`
- **Contract:** `package.md` `bb103f35b857…` (unchanged)
- **Live failure preserved:** commit `ac1613c8881a5c…`, `live-review-2.md`
  `6204144c6464…` (FAIL, timer-key mismatch + no handoff)
- **Receipt:** `amendment-2-admission-receipt.json` (`P6r9-amendment-2`),
  start `2026-09-22T14:03Z`, deadline `2026-09-22T14:08Z`
- **Worker:** HELD pending cairn's conditional release

## Disposition

**ACCEPTED**, bound to the exact amendment bytes above plus the pinned
`amendment-2-checklist.md` (checks 1–6, sha256 in the receipt). The amendment is
a bounded, independently-confirmed repair of a real candidate defect and does
not weaken a check. No implementation authorship; no live effect.

## The defect is real, and independently confirmed by source

I re-derived both defects rather than take the amendment's word:

- **Timer identity.** `r3harness/harness.py:618` guards on
  `kv["timer-arm:deadline:" + action_id]` = `timer-arm:deadline:p6c-h1w`.
  `arm_from_ledger` (`host_adapter.py:825`) calls `FakeTimerService.create`,
  which mutates only in-memory `self.timers` and persists **no** kv key. The
  real arm persists `kv["timer-arm:" + timer_id]` (`host_adapter.py:272`) with
  `timer_id = unit` from `_arm_host_timer` (`harness.py:309-328`) =
  `p6-stagec-h1.timer`. So the guard never sees the key, re-arms, and the
  duplicate systemd unit is refused (`E_TIMER_CREATE` →
  `E_TIMER_CREATE-timer-backstop`). Confirmed by `live-review-2.md`.
- **Doubled unit.** `HostTimerService.unit_for` returns `"%s.timer" % timer_id`
  (`host_adapter.py`), so the persisted `unit` is
  `p6-stagec-h1.timer.timer` while `command_for` creates `--unit=p6-stagec-h1.timer`.
- **Callback context.** `_arm_host_timer` builds the callback without `--db`
  (`harness.py:325-328`); the global parser default is
  `--db=/tmp/p6h/harness.db` (`harness.py:913`) and `timer-callback` reads
  `args.db` (`harness.py:993-994`). A fired timer would reopen an unrelated
  default DB, not the bound fixture DB. Confirmed by source.

## The amendment is bounded and does not fit code to a check

- It unifies the declared logical action/timer identity with the canonical host
  unit name across arm/persist/guard/query/callback/cancel, normalizes the unit
  suffix exactly once, and requires reopen to reconcile **actual host timer
  facts** rather than treat kv presence as liveness.
- Reuse-not-recreate, no extension, conflict → owned failure, overdue → bounded
  owned disposition: all conservative, consistent with O2/O4.
- It explicitly authorizes only `src/r3harness/harness.py` and
  `host_adapter.py` minimal edits (plus tests); frozen parents/core unchanged;
  other modules need a reproducer/Tern decision.
- The pinned checklist requires a **rejecting** systemd model, an exact-CLI
  old-fails/new-passes with delayed worker + reattach, reopen mutations, and a
  two-database callback test with no `/tmp/p6h` fallback — none of which an
  always-success fake can satisfy. Retained suite/five-case/observer/tamper/
  identity/receipt/signature regressions stay binding.

## Scope, authority and allocation

Prospective and conditional: after this ACCEPTED unchanged and the checklist
pinned, cairn may dispatch **one** kiln <=35m repair (`P6r9-repair-2`), then
**one** corvid <=25m independent verification; ceilings 810/555 -> 845/580;
admission 5m separate. No new live/prep/witness grant; old fixtures belong to
the existing cleanup duty (cairn to independently verify
`campaign4-p6r9-prep3-cleanup` completed after ~14:10Z). No automatic further
repair; expiry/verdict returns Tern; candidate PASS never releases live work.

## Independence

Tern authored the amendment; corvid reviewed it and authored neither the
amendment nor any candidate code. corvid's prior live FAIL and the candidate
scoped PASS remain unrevised.

## Effect

Amendment `592d24c1…` and pinned checklist `amendment-2-checklist.md` are
**ACCEPTED** for one bounded repair. Cairn's conditional release condition is
met for this amendment; no live authority follows. Returned to Tern/cairn.
