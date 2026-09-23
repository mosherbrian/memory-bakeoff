# P12-closure-1 — independent closure review (corvid)

- **Action:** `P12-closurereview-1`, start `17:36:32Z`, deadline `18:01:32Z`.
- **Claim:** `closure-1-claim.json` on amendment `3caa0d1` + ruling `d0670c8`;
  candidate `669648cb` / binary `3916950a`.
- **Verdict: PASS.** The three previously-unsupported obligations are now
  implemented, bounded and independently reproduced. Carried live assumptions are
  listed below.

## Pins / integrity

- **26/26** claim hashes match (11 plans + 12 evidence + 3 decision); decision
  files `closure-allocation-1.json cbfdb09b…`, `closure-1-receipt.json
  e3bc2db…`, `closure-early-callback-correction.json 5348a3f1…`.
- Source `669648cb66b771a147a6ce8197e6654461abe7fc`; `git diff cbfe3d9..669648c`
  **empty** for `internal/core`, `internal/py`, `conformance/cases` (frozen).
  Changed set is bounded: loop/shutdown/timeout/timer tests + `mutate_go.py`.
- Release binary `/home/bmosher/projects/agent-loop-releases/agent-loop-669648cb66b7/bin/agent-loop`
  = `3916950a…`, matching the claim; the reviewed plan repair `9a2a1795` is
  unchanged.

## Independent reproduction (my runs, real CLI + shipped binary)

- **Never-acked escalation (real time, no FakeClock):** settled a timeout with no
  ack, then ran `run --every 1s` for 128 s. Duty escalation at **60 s**
  (`no_ack_duty: sent 17:39:26Z`, "You are duty"), director at **120 s**
  (`no_ack_director: sent 17:40:26Z`, "You are director"), and `ack: None` — the
  escalation is **not** recorded as an acknowledgement. Matches `NoAckAfter=60s`.
- **Early callback:** fired the deadline callback 60 s early on the new binary →
  `no-op-early`, step stays `worker`, **no cancel/dispatch/settlement**, and the
  unit is re-armed (2 arm lines).
- **A / shutdown / conformance on the new binary:** `a-cli-timeout idle` →
  `timed-out`, 1 director wake, `timeout-ack` command in the notice,
  `callback_lateness: 2s`; `refused` → cancel failure recorded, director told.
  `c-stop-experiment` notifier SIGTERM **0.008 s**, `Result=success`. Shipped
  `conformance conformance/cases` → **rc=0, 125/125 cases, 1751 steps**.
- **Go tests:** the 11 closure/timer tests pass
  (`NeverAcked…`, `AnAckStops…`, `FailedNoAckSendIsRetried…`,
  `NoAckEscalationRefusesAChangedPrincipal`, `EarlyCallbackRearms…`,
  `RearmRefusesWrongAction…`, `TheOnlyDuplicateNoticeIsBounded`,
  `RearmHostReusesTheWaitingUnit…`, `CommandAt/For`, `CancelReceipts`);
  `go test ./...` all ok; mutation **110/110**.

## Obligation-by-obligation (prior unsupported → now)

1. **Never-acked bounded escalation — SUPPORTED (bounded).** Duty ≤ 60 s + pass
   interval + pass time (~90–95 s); director ≤ 120 s + same. Failed sends are
   recorded `failed …` and retried, **never** `sent` (Go test); a later valid ack
   still stops escalation; escalation ≠ ack/recovery. Carried: **no escalation
   while `run` is stopped** (liveness owns it) — the bound assumes the loop is
   running.
2. **Clock treatment — SUPPORTED within stated limits.** `FakeClock` proves the
   loop side: early callback is `no-op-early` + authoritative re-arm at the
   original instant (not `now+duration`), late callback settles with true
   `callback_lateness`, discontinuity yields an owned non-green state.
   **Limit (carried):** real systemd calendar delivery after a **host clock
   rollback is not established**; qualification assumes a non-discontinuous host
   UTC, and a real discontinuity invalidates the timing sample and requires
   reconciliation.
3. **Duplicate-notice exception — SUPPORTED (narrow).** `TestTheOnlyDuplicateNoticeIsBounded`:
   exactly 2 director notices (failed-cancel settlement + the later delivered
   replay), 2 cancel attempts (1 failed + 1 delivered), **1 dispatch**; same
   `T-<action>` incident, `At`/`Action` unchanged across reopen/replay. No
   per-tick flood, no second cancel/dispatch.

## Retained suites / frozen

- Conformance 125/125; L6 three-interval predicate (`plans/live-driver.sh`
  `9a2a1795`, unchanged); shutdown <1 s; timer regressions — all retained.
- `internal/core`, `internal/py`, `conformance/cases` frozen (empty diff); main
  and installed preview untouched.

## Carried residuals (for the live signature)

- No escalation while `run` is stopped; a re-arm happens only if the early
  callback actually runs (systemd never firing falls to the liveness check).
- Real host-clock rollback → calendar delivery not established (above).
- A re-armed unit keeps the original name (disarm stops it when the step ends).
- L4a/L4b, live ack latency and step-timer precision on real seats are proved only
  in the signed live run.

No new source edits by corvid; no main/install/live. **PASS** returned to Tern for
fresh prep/live signature; no automatic cutover.
