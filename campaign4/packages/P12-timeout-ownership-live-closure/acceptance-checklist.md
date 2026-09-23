# P12 — preregistered per-family acceptance checklist (corvid, before author)

Pinned before author release. Each item is a concrete check with a required
outcome. DRY/command-printing cannot establish behavioural PASS; inspect every
results row, not process exit. A failed required wait/assertion yields
FAIL/INCOMPLETE, never hidden behind rc0. Baseline P11 failures must be reproduced
on the pinned `1341f04` before any fix.

## General gates

- [ ] Contract/pins unchanged: `package.md 6391857222e0…` (`1315196`), all 12
      `inputs.json` hashes; base Go `1341f04…`; new binary/source/manifest/claims/
      diffs pinned and immutable.
- [ ] Go change bounded to timeout ownership/shutdown/service/tests/status/driver;
      Python/core frozen; separate worktree; main/installed preview untouched.
- [ ] Retained core125 conformance; host parity adjudicated with explicit named case
      diffs (no requirement changed-Go == known-broken Python).
- [ ] Real argv/CLI tests; no always-success transport oracle; author tests separated
      from independent checks; one unshared negative per new authority/failure
      boundary.
- [ ] Contained systemd experiments: exact names, bounded automatic cleanup, no real
      seats/tasks, no global config changes; `daemon-reload` global-unit inventory
      recorded; host effects never claimed zero; no uncontained P10 baseline.
- [ ] Every raw failure and scope effect preserved; DRY rows marked DRY.

## A — timeout settlement (idle-cancel)

- [ ] Reproduce P11: idle-worker `/cancel` → `nothing running`; then fix.
- [ ] Already-idle is **not** a cancellation failure, but **no** generic transport
      error is swallowed: exact receipt/session/action classified; missing/wrong/
      ambiguous transport remains **owned failure**, not cancelled-success.
- [ ] Timeout settlement + director escalation persist **without relying on a live
      worker turn**.
- [ ] Crash/reopen/retry neither lose escalation nor duplicate cancellation/dispatch.
- [ ] Genuine cancellation failure reaches owned escalation with truthful evidence.
- [ ] Tests use real response/error shapes and cover running/idle/missing/rebound
      sessions and failed transport.
- [ ] One unshared negative: a wrong/ambiguous receipt must not be accepted as
      cancelled-success.

## B — step-timeout acknowledgement

- [ ] Ack authorizes the current principal for exact package, execution/action and
      timeout incident; trusted recorded time; explicit next action and response
      deadline; durable/readable status.
- [ ] Reject forged/stale/wrong-actor, wrong-action, invalid/past/unbounded
      deadlines, conflicting ack.
- [ ] Replay stable; restart durable; ack is neither resume nor terminal accept;
      expired response is owned/escalated.
- [ ] Static owner or sent wake is **never** counted as acknowledgement.
- [ ] Timeout notification exposes the exact ack command, executable on the fixture
      principal.
- [ ] One unshared negative: a delivery-only (no ack) state must not pass the
      ownership bound.

## C — normal stop/restart diagnosis

- [ ] Reproduce P11 `stop-sigterm` timeout **before** edits.
- [ ] Normal SIGTERM and intentional stop shut down promptly inside declared
      `TimeoutStopSec`; outstanding identity preserved; restart without resend.
- [ ] Watchdog SIGABRT treated as possibly expected — not classified a bug merely
      because abort appears.
- [ ] If an ordinary-stop defect is reproduced, repair narrowly; otherwise report
      exact cause/evidence, no invented change. Core frozen.

## D — driver

- [ ] Zone-aware UTC/epoch journal windows (no zoneless `--since`); deterministic
      idle baseline may be `rest`; no failed wait hidden.
- [ ] L4a proves actual `start-limit-hit` with verified unit/onset properties.
- [ ] L4b unavailable duty reaches actual director ack; observed crash vs
      restart-loop classified accurately; required restart-loop case not weakened.
- [ ] Re-run L5-rest/stopped, L7a, L5-stray, L3a, L4a/L4b, L2/L6 and dependents on
      fresh fixtures; raw outcomes preserved.

## E — wall enforcement

- [ ] Reproduce real `daemon-reload` interactions with exact timer configuration
      while the driver is blocked; do not infer from a stopped-unit snapshot.
- [ ] Repeated real reloads; actual schedule before/after each reload (raw timer
      properties + capture times).
- [ ] Actual firing terminates driver **and children**, then cleanup, with no later
      workload effects.
- [ ] Independent fallback survives the same reloads.
- [ ] Stubbed reload is insufficient.
- [ ] Calendar timer allowed **only** with explicit UTC, exact next-instant
      assertion, actual firing/reload proof, and clock-discontinuity treatment; no
      zoneless absolute timers; charter relative-timer exception is scoped.
- [ ] Candidate step-timer accuracy satisfies known-deadline detection 30 s on real
      systemd; any Go timer-adapter precision narrowly specified and proven.
- [ ] Internal guard alone is **not** accepted as stopping blocked work.

## F — fresh live + cutover (separate signed releases)

- [ ] Cairn prep15/binding10/live75/live-review25; Tern signs exact binary, plans,
      units/config, fresh four fixture identities/incarnations, fault actors/onsets,
      clock-read deadline, independent cleanup.
- [ ] P10 section C full L1–L7 + P12 ack + wall proof; detection 30 s, suspicion
      180 s, recovery or actual ack owner/next/deadline 60 s; totals 90/240; known
      timeout expiry explicit, never reclassified suspicion.
- [ ] L6 must PASS both detection and acknowledged ownership/recovery; direct send
      alone insufficient; live idle-worker timeout and blocked/running cancellation,
      ack/reopen; failed transport branch with controlled evidence.
- [ ] Any missing required case → NOT READY, no cutover.
- [ ] Cutover: P10 section D, first real task `P12-production-handoff-1`, new
      production ledger/config, authoritative bindings, retire campaign4 openwork/
      watch/coax/shadow-watch/Cairn manual dispatch, no dual control, rollback
      reconciles in-flight identities and restores one owner; corvid verifies the
      handoff through actual Go, not manual substitutes.

---

## C supplement — shutdown causal evidence (incorporated before author)

Source: `shutdown-causal-evidence.json` (`293b08af…`, Tern `16:51:51Z`), base
`1341f04`. Verified independently at base: `cmd/agent-loop/loop.go`
`dd351d74…` (signal.Notify at :273, nonblocking check before the blocking wait,
`time.Sleep` fallback at :329) and `internal/host/notify.go` `6e4fd20a…`
(`DirNotifier.Wait` at :38). Technical correction accepted: **`Wait` uses
`syscall.Select`, not `poll`.** Causal hypothesis (idle wait vs 20 s
`TimeoutStopSec`) is concrete but not universally assumed.

Additional C checks:

- [ ] **Synchronized baseline repro:** drive a baseline run into the idle wait,
      then `SIGTERM` via a **real isolated systemd stop**; capture elapsed time,
      exit code, journal, and presence/absence of `stop-sigterm` timeout / SIGABRT.
      Reproduce before any fix.
- [ ] **Corrected prompt clean exit:** idle shutdown **< 1 s on a healthy host**,
      independently measured; clean exit 0; never the 20 s forced timeout.
      Distinguish D-Bus command latency from process exit time; record actual
      values, not only rc.
- [ ] Exercise **both** the notifier and the fallback wait paths; `SIGINT` and
      repeated stop/restart; no leaked watcher goroutines/fds; no missed or
      duplicate handoff on restart.
- [ ] Retain deliberate-stop marker **exit 64**, watchdog abort behaviour, and
      independent liveness semantics as distinct; do **not** raise `TimeoutStopSec`
      globally to hide delayed signal handling.
- [ ] Narrow notifier **cancellation interface** change permitted under C if needed
      (author chooses cancelable wait design); retained host parity/regressions with
      named adjudication; core frozen; no broad host rewrite; budget 365 m unchanged.
