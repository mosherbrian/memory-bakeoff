# P6-r15-live-failure-rest — pinned checklist

Pinned by corvid-dsh at `P6r15-admission-1`. Brief `c6a79a3a3bc4…`; R14 candidate
`02ea693e` / manifest `8584cbed` / review `93127630`; R13 core `5410332`; rulings
`4be99bf`/`84f094e`/`883107e`/`650830c`/`b2384d7`/`afa126f`/`f7b0cce`/`5fefb0f`/
`fc74f65`. Evidence-only; worker 0. Failed-verification first, quiet-rest second.

## Pre-live
- Fresh isolated root/action/executions and a NEW fixture pair per case; one at a
  time.
- Cairn prepares only on a concrete Tern preparation release; binding review
  checks raw launch IDs, profile/lane/workdirs, actual sockets/incarnations,
  canonical corrected schema + derive rc0; no stopped historical fixtures or
  stale signatures; socket-race partial preserved and reconciled, no blind
  relaunch.
- Tern signs exact current plan/config/binding/code manifest and **exact commands
  against the accepted R14 entrypoint** (`case_entry.py 64edb54e…`) with pinned
  R5/R6 dependencies; reinventory host wrapper/runtime. The plan's `P6-r8`
  `host_commands`/`fault_controls.command` strings are descriptive and must not
  be trusted verbatim.
- Explicit: work grants, observation bound, outer `live_stop_utc`, fault
  actor/effect/onset, precise cleanup IDs/units. Arm and verify exact-ID
  automatic cleanup before execution; archive evidence first.

## Failed-verification (case 1)
- Real worker publication + verifier execution joined by exact identity/hash.
- Authentic post-publication mismatch: applied `corrupt-after-worker` with
  before/after hashes (`faults/failed-verification.applied.json`), genuine
  verifier rejection, independent onset (sidecar or `fault_onset.py mark`, finite
  uncertainty); missing/unbounded onset → INCOMPLETE, not PASS.
- NEVER COMPLETE/accepted; owner + bounded next disposition recorded; retained
  artifact/verdict explains result; one worker + one verifier send, no duplicate
  on continuation/restart/deadline callback. Normal slow startup is not induction.

## Quiet-rest (case 2)
- Real completed/disposed execution; terminal + disposition reachable.
- Legitimate rest recognized across a **declared finite** observation interval
  covering the configured observer/reconcile cycle, plus bounded restart
  reconciliation; no new sends, repeated alarm or invented successor.
- Inspect actual ledger, outbox, latency records and effects (not incumbent
  agreement); no synthetic failure rows added. No eternity claim.

## Both / matrix
- Timer callback identities and authoritative deadlines current; grants preserved
  through continuation; stricter outer stop honored; cleanup verified for owned
  fixture seats/units only; per-file evidence binding; actual exit codes.
- Recovery timing explicit onset detect30/recover60/total90, suspicion180/60/240;
  acknowledged progress/escalation is recovery, queued alone is not; source
  uncertainty or unjoined timestamps → INCOMPLETE; work duration separate; no
  manufactured onset.
- Unshared negative: wrong action/execution (`E_ACTION_MISMATCH`/
  `E_EXECUTION_MISMATCH`) and missing onset (`E_NO_ONSET`) reject before a false
  PASS.
- Final matrix distinguishes these two fresh cases from R9's historical positive
  and the still-unexecuted lost-completion/queued cases; no four-case PASS,
  adoption, script retirement or research claim from two cases.

## Bounds
Worker 0; admission corvid15m; two preparations cairn10m each; two binding reviews
corvid5m each; two live operations cairn20m each (if it cannot fit inclusive
cleanup margin, return the exact proposed allocation before execution); two
result reviews corvid15m each; final matrix corvid5m. Candidate ceilings 1200/975
unchanged; no repairs/retries; unused allocation cancelled at terminal; every
dispatch/receipt carries an executable completion notification with exact
profile/session/action/absolute path.
