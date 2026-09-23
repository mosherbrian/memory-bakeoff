# P8-go-unattended-qualification — Stage B qualification (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P8-qualification-1`, start `05:14Z`, deadline `05:59Z`
- **Brief:** `stageB-receipt.json`; contract `package.md` (`b496b5b2…`), admission
  `450f1afc…`.
- **Frozen candidate:** source commit `4a00d675…` (checkout clean), installed
  binary `/home/bmosher/.local/bin/agent-loop` sha256 `8cc149bf…`, intake file
  hashes verified; toolchain `go1.27.1` at `/home/bmosher/sdk/go/bin`.
- **Scope:** fresh scoped pass; Go binary under test; Python used only as the test
  driver (`stageB-driver.py`); no source edits, no live seats/network. Evidence
  root `/tmp/p8qual`, `/tmp/p8e`.

## Verdict

**PASS (bounded) for Stage B.** Green Go suite and conformance, plus black-box CLI
evidence that the safe/authorization/evidence behaviours hold (handoff, one send
per action, input invalidation, dependency gate, same-principal binding refusal,
owned refusal on wrong/stale/early callbacks). **Not black-box/live-exercised**
(unit-proven only, must be exercised in Stage C): the due-deadline interrupt,
crash-before/after-ack and atomic-close/reopen variants, and the missing-escalation
bound. A green unit suite is not deployed-host proof, so Stage C remains required;
no live adoption is certified.

## Suite / conformance

- `PATH=/home/bmosher/sdk/go/bin:$PATH go test ./...` on `4a00d675` (clean) →
  **ok** all packages (`internal/coax,conform,core,host,loop,shadow`; rc0).
- `agent-loop conformance conformance/host` → **3/3 ok**; adjudicated case →
  **1/1 ok**. Five corrected host-port outcomes live in
  `conformance/host/adjudicated.json` (`E_NO_ESCALATION_BOUND`, atomic
  terminal-rest, `E_FORGED_DISPOSITION`, `E_CLOSE_UNRESOLVED`) and are asserted by
  `internal/host/closure_test.go`.

## Black-box CLI cases (real binary, private config/stubs)

Stubs for `wake`/`systemd-run`/`systemctl`/`agent-deck` in a private `bin/`
(logged, no real seats/timers). Matrix mapping:

- **8 Handoff:** `dispatch → run --once → claim worker → turn-end → run → claim
  verify → turn-end → run → decide` → worker and verifier each woke **exactly
  once**, verdict **PASS**, package **closed** after `decide question_answered`;
  a bogus `timer-callback` afterwards produced **no further wakes**.
- **3 Independence:** two names mapped to one session id (`kiln=K, corvid=K`)
  → `dispatch` refuses `E_SEAT_BINDING: session K is kiln, not corvid` (rc3); the
  same-principal verifier cannot even be registered. Verdict-level producer guard
  is covered by `internal/host` tests.
- **4 Input validity:** `dispatch --input nope.md` → **rc3 refused**; a declared
  input mutated after worker start, before verifier release → `run` shows
  `Q1: blocked: E_INPUT_CHANGED: spec.md changed during the work; verifier not
  dispatched`, **no verifier wake**, and `status` carries the owned reason.
- **6 Dependency/judgment:** `dispatch --after Q1` while Q1 open →
  `Q2 registered, held until Q1 close`; **0 wakes** while Q1 open; after
  `decide question_answered` on Q1, `run` releases Q2 once (1 wake).
- **2 Hung/owned (partial):** correct-but-early `timer-callback` →
  `{"decision":"no-op-early","dedup":true}` with no effects; unknown/stale
  identity → `E_UNKNOWN_PACKAGE` rc3, no effects; `decide` before verdict →
  `E_PHASE_MISMATCH` refused. **Due-deadline interrupt not black-box exercised**
  (real clock; unit/fake-clock only).
- **7 Evidence/atomicity (partial):** mismatched/absent claims refused by the
  handoff path; full crash-before/after-ack and interrupted-write/reopen recovery
  are **unit-proven** (`internal/host/closure_test.go`, `loop_test.go`), not
  live-exercised here. WAL alone not treated as proof.
- **5 Exhaustion:** dispatch-with-no-retry policy observed (no automatic retry
  after a blocked/failed step in the CLI cases); no new retry invented.

## Unit vs CLI vs live separation (per contract)

- **Go unit/conformance (green):** core/host/loop/conform/shadow, including
  destructive crash, atomicity and fake-clock deadline cases.
- **Black-box CLI (green):** handoff, one-send, input invalidation, dependency
  gate, binding refusal, owned callbacks/decisions.
- **Not live (deferred to Stage C):** real transport/turn-watcher/timers, actual
  due-deadline interrupt + cancellation, real hung-step enforcement/restart, and
  confirmation that destructive crash variants behave the same on the host path.

## Limitations / NOT READY triggers

- No real seats, timers or notifications were used; the `wake` stub is not proof
  of live cancellation. One worker dispatch recorded `held-ambiguous` in the
  outbox while still invoking the wake — conservative no-resend behaviour, but
  live receipt semantics must be confirmed in Stage C.
- `examples/campaign4.json` is explicitly an example; fresh isolated fixture
  identities are required and the wrong-`corvid` blocker is corrected at this pin
  (`493c0317…`). No main-seat fault injection.
- No Python controller was used; the driver only orchestrates and observes.

## Effect

One bounded verdict: **Stage B PASS (bounded)** — suite/conformance green and the
safe/authorization/evidence behaviours reproduced black-box; destructive/live and
deadline behaviours remain unit-proven only and are deferred to a separately
signed Stage C. No adoption/P9 from this. Returned to Tern.
