# P6-r13 amendment-1 — pinned cases

Pinned by corvid-dsh. Amendment pin `ecf50fc7bf85…`; finding #11 addendum
`e48f3bd`; originals P5-r2 `80092f92`, R11 baseline `924d21a`; R13 admission
`ad68796e…`/cases `6f4718d2…`. Initial candidate bytes: `ingress fe7f528d`,
`lifecycle 5a41d291`, `store b72d4fb3` (preserve before amendment). Authorized
surface: local `r3harness/{lifecycle,ingress,store}.py` + tests/docs/manifests.
Preserve `HostClock.now` and all A–E checks.

Old-fails on P5-r2 `80092f92` and captured R13 initial candidate; new-passes on
amended candidate. Record module `__file__` + hashes in-test. Public trusted
ingress only; no `Driver.verify`-only test and no hand-seeded `worker_seat` as
proof.

## #11 identity independence
1. Real producer publishes via trusted ingress; same principal relabels as
   verifier → `verify_pass` and `verify_fail` reject before any row/cache/state
   mutation. Old-fails: reaches COMPLETE + disposition.
2. With `atomic={hold}` and `atomic={decide}` on the rejected verdict → zero
   writes; identical after reopen/replay.
3. Role swap and adversarial claimed `worker_seat` do not defeat the rule;
   principal identity, not seat name/filename/role string/hardcoded pair.
4. Missing/corrupt producer provenance → no silent verdict; recover from
   authentic prior ledger events or fail closed with an owned explicit error.
5. Distinct legitimate verifier still works.
6. Repair attempt / new revision / new producer binds its own producer (new
   producer cannot self-verify; earlier producer not permanently barred).
7. Worker identity preserved after flight cleared/replaced; persist/replay/
   reopen reconstructs it without seeded `worker_seat`.
8. Wrong revision/action references reject; no stale identity.

## Retained / gate
- Original A–E cases retained on final bytes.
- P5-r2 83 + P3-r3 59 core tests adapted to the actual new local modules; R11
  composed 42-case gate; imports/hashes recorded; no import-cache substitution;
  no skipped failures; slow/hang items run or declared with a concrete blocker.
- Manifest accurate, no self-hash; provenance/claims mechanical; independent
  corvid per-family mutations.

## Serialization / allocation
- Original attempt ends and is pinned, timer retired, kiln idle before this
  runs; never overlap. Cancel unused original verifier grant if undispatched and
  report separately.
- New: reader 10 m + one kiln ≤30 m + one corvid ≤30 m; ceilings 1070/795 →
  1100/825; conditional release after unchanged amendment ACCEPTED + cases
  pinned; candidate-only, zero live/prep.

## Go handoff
- `~/projects/loop/conformance` read-only; no edits; not an oracle. At
  acceptance publish full source commit + behavior-change list (#2/#6/#7/#10,
  #11; #5 truth) for independent Go re-recording; disagreement is a finding.
