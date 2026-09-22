# P6-r9-observer-lifetime — live review 2 (independent)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-livereview-2`, start `2026-09-22T13:59Z`, deadline
  `2026-09-22T14:09Z`
- **Grant:** reassigned never-dispatched r9p1 task/review; `corvid <=10m`
- **Evidence:** `live-positive-2/` (incl. `director-observation/receipt.json`),
  `live-positive-release-2.json`, `live-positive-2-receipt.json`,
  `live-execution-2/`, `/tmp/p6r9-live-positive-2/`
- **Scope:** read-only review of actual identity, deliveries, handoff, claim,
  verdict, no-duplicate-send, timing and cleanup. No retry, no send, no
  mutation.

## Verdict

**FAIL.** The run is an honest owned failure (rc3 `E_CASE_FAIL`, no fabricated
success), but the required positive worker→verifier handoff did **not** occur:
the reattach path attempted to re-create an already-armed host timer and was
refused (`E_TIMER_CREATE-timer-backstop`), so the verifier was never dispatched
and never observed. The cause is reproducible in the candidate, not an external
outage: the reattach guard reads a kv key that `create_host` never writes.

## Confirmed

- **Gate/identity:** `gate.out` `{"gate":"PASS","registry_source":"live-agent-deck",
  worker":"2382c1d3-1790085057","verifier":"b1c91738-1790085057"}`; arm rc0.
  All delivered messages route to the two signed r9p3 seats (`deliveries.jsonl`,
  `outbox/send-000.json`, `manifest.json` routes). Exactly **one** worker
  dispatch (`msg-p6c-h1w-1`, state `sent`); **zero** verifier sends.
- **Worker result real:** claim `ex-b17505a8cea0` `outcome: completed`,
  `out.bin` sha256 `c16a40a4…b39a`; producer onset `13:58:03Z`
  (`provenance: fixture-producer-seat`, uncertainty 1s). No duplicate/fresh
  identity, no forged clock.
- **Honest failure preserved:** `run.out` rc3
  `E_CASE_FAIL` `"positive reattach did not commit under valid grant"`;
  `latency.jsonl` is an explicit zero-signal `no-end-failure` sample
  (`committed_at/detected_at/dispatch_at: null`), not a success.

## Root cause — timer-key mismatch (confirmed independently)

- The reattach guard at `r3harness/harness.py:618` tests
  `kv["timer-arm:deadline:" + action_id]` = `timer-arm:deadline:p6c-h1w`.
- `arm_from_ledger` (`host_adapter.py:825`) calls `FakeTimerService.create`,
  which only mutates in-memory `self.timers` and **persists no kv key**.
- The real host arm (`host_adapter.py:272`) persists
  `kv["timer-arm:" + timer_id]`, and `_arm_host_timer`
  (`harness.py:309-328`) passes `timer_id = unit = "p6-stagec-h1.timer"`.
  So the stored key is `timer-arm:p6-stagec-h1.timer`
  (director-observed; its `unit` field is the doubled
  `p6-stagec-h1.timer.timer` from `unit_for`).
- The guard therefore always sees `None`, re-runs `_arm_host_timer`, and on
  reattach the existing systemd unit refuses the duplicate create →
  `OwnedFault E_TIMER_CREATE` → harness returns
  `{"decision":"owned-failure","reason":"E_TIMER_CREATE-timer-backstop",
  "latency_samples":0}`, which `case_entry.py:1157-1161` re-raises as
  `E_CASE_FAIL`. The director's "suspected duplicate-create refusal" is
  confirmed by code and by the stored/queried key shapes; no missing stderr
  needed.

## Not met / open

- **O1 handoff:** verifier never dispatched/observed; positive path not
  demonstrated. Even the reattach, once fixed, must re-observe the late worker
  end and reach the verifier.
- **Timing:** only onset present; dispatch/commit/detect are null, so timing
  acceptance is INCOMPLETE as a separate limitation.
- **Cleanup not yet verifiable:** at review time (14:0xZ) both r9p3 ids are
  still in the registry (`idle`/`waiting`); the automatic
  `campaign4-p6r9-prep3-cleanup.timer` is armed for ~14:10Z and the director
  stopped only `p6-stagec-h1.timer`/service (`list-timers` empty; no transient
  unit). Release condition 6 requires cairn to verify the automatic cleanup
  actually succeeded; until then fixture-removal is unverified.

## Effect

Live attempt `P6r9-live-positive-2` is a **FAIL**: real worker completion but no
verifier handoff, caused by a candidate defect in the reattach timer-backstop
guard (key `timer-arm:deadline:<action>` vs stored
`timer-arm:<timer_unit>`). No retry was taken (correct). Returned to cairn for
the automatic-cleanup check and Tern disposition; a repair of the guard key and
a fresh signed run are required before any positive acceptance.
