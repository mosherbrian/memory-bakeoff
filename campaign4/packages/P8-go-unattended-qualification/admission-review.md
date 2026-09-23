# P8-go-unattended-qualification — admission review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P8-admission-1`, start `05:12Z`, deadline `05:32Z`
- **Brief:** `package.md` sha256
  `b496b5b294efa098d7cca633937a5ea01fe8f754639d349e03f0472265c482b0`; director
  release `44a5a4d3…`; `candidate-intake.json`.
- **Scope:** read-only admission + pinned checklist. No edits, no Python
  substitution, no live effects.

## Verdict

**ACCEPTED (bounded).** Pins resolve and are frozen: the repo checkout is at
`4a00d675…` (clean), the installed binary hash `8cc149bf…` matches intake, and all
six declared input hashes match byte-exact. The four prior readiness blockers now
have visible mechanisms at this pin (input invalidation, dependency gate,
adjudicated host-port close, corrected corvid identity), so a Stage B adversarial
pass is warranted. **NOT READY triggers remain:** Stage B must independently
reproduce corrected outcomes (not accept reported evidence), and the Go toolchain
is not on `PATH` (it is at `/home/bmosher/sdk/go/bin/go`). No Python controller may
stand in for missing Go behavior.

## Pin / intake resolution (verified)

- Source commit `4a00d675d4384f3bb43d9ab25a291847c7944cb2`; repo
  `/var/home/bmosher/projects/agent-loop` HEAD matches, `git status` clean.
- Installed `/home/bmosher/.local/bin/agent-loop` sha256
  `8cc149bf5c74a0c39b720691787b4ed9a47c9621368250ddcecaad791a872c0b` = intake.
- Intake file hashes recomputed equal: `go.mod 8d940d07…`, `go.sum fc5de4c8…`,
  `conformance/host/adjudicated.json f7fe5e1f…`, `internal/host/closure_test.go
  472cf3e3…`, `internal/loop/loop.go 56511d0e…`, `examples/campaign4.json
  b954fa91…`.
- Toolchain reported `go1.27.1`; present at `/home/bmosher/sdk/go/bin/go` (add to
  `PATH` for Stage B) — **not** on the ambient `PATH`.
- Inputs resolve `95b44c3`, `38bfb23`, `753a36c`, `bb3cc30`, `7857c0ce`.
- `agent-loop --help`/`version` run read-only (rc0); public CLI:
  `dispatch/run/status/claim/decide/stop/check/timer-callback/conformance/shadow/
  coax/version`. `go.mod` pins `modernc.org/sqlite` (pure-Go) and pinned transitive
  modules; no CGO requirement asserted.

## Prior blockers at this pin (mechanisms present; independent proof required)

- **B1 declared-input validity:** `internal/loop/loop.go` emits
  `E_INPUT_MISSING` (`:449,:509`) and `E_INPUT_CHANGED` (`:452`); test references
  `E_INPUT_CHANGED: spec.md` (`loop_test.go:373`). Must be reproduced black-box.
- **B2 dependency/judgment gate:** `E_DEPENDENCY_UNMET` (`:537`); test at
  `loop_test.go:463`. Must be reproduced with unknown/cyclic refs too.
- **B3 host-port close:** `conformance/host/adjudicated.json` records five
  corrected outcomes (findings 1/2); `closure_test.go` asserts the atomic close.
  Reported, **not** independently reproduced in this admission.
- **B4 role/session config:** `examples/campaign4.json` now has
  `"corvid": "493c0317-1790000758"` (the real corvid) with an explicit "EXAMPLE
  ONLY, not a live binding" note; fresh isolated fixture identities still required
  for any Stage C.

## Pinned Stage B checklist (preregistered; exact commands/observations)

Environment: `PATH=/home/bmosher/sdk/go/bin:$PATH`; frozen checkout at
`4a00d675`; private `/tmp` roots/config/DB; **Python may be a test driver only** —
all behavior under test is the Go binary; no Python controller filling missing Go
behavior. Inspect actual ledger/outbox/receipts/status and process calls, not just
rc. Record command/env/rc/logs + source/binary/config hashes and actual test
origin.

1. **Restart/no duplicate:** `go test ./...` + conformance/closure; black-box
   crash before transport ack and after delivered-but-unacked; reopen same action
   identity → one execution or owned ambiguous block, never blind resend; include
   already-acknowledged completion and repeated `timer-callback`.
2. **Hung/owned:** exact registered deadline interrupts once; cancellation targets
   the correct principal; escalation acknowledged or explicit undelivered with
   bounded retry/owner; wrong/stale/missing callback identity → no effects;
   missing escalation bound → owned `E_NO_ESCALATION_BOUND`, not crash.
3. **Independence:** distinct names mapped to one principal cannot self-verify;
   actual-producer same-principal verdict rejected before mutation; other verifier
   allowed.
4. **Input validity (B1):** missing registration input refused; mutate/delete a
   declared file after registration, before verifier release → no dispatch, owned
   `E_INPUT_CHANGED`/`E_INPUT_MISSING` visible in `status`; no silent
   re-registration.
5. **Exhaustion:** allocation/no-retry terminal policy retained; Go product does
   not invent automatic retries after refused/failed work.
6. **Judgment/dependencies/status (B2):** `--after` unresolved holds without sends;
   recorded `question_answered`/`successor_opened` permits once per policy; other
   terminals block; unknown/self/cyclic refs refused; immutable preexisting graph
   invariant; `status` names decision/owner/dependents/next step and changes after
   resolution, no canned current-state text or false quiet.
7. **Evidence/atomicity (B3):** interrupted claim write/SQLite publication/reopen
   recover or block preserving facts; invalid disposition first/retry/reopen NEVER
   closes; atomic successful close once; crash before/after commit; historical
   partial verdict eligible only for missing decide; conflicting/wrong
   action/execution/question reject; missing/tampered evidence fails closed; WAL
   alone is not proof.
8. **Handoff:** `dispatch/run/claim/decide` performs worker→verifier→decision/rest
   with artifact recomputation, no Brian prompt, one send per action; failure
   rejection must not COMPLETE; quiet terminal polling/reopen has no new sends or
   alarms and reports a finite observed cycle. No exact-source-latency/source-time
   overlay required.

Every case must separate unit/CLI/injected/live evidence and limitations; a green
unit suite cannot mark deployed-host checks proven. Reported mutation results are
recorded separately unless independently reproduced — do not burn budget rerunning
all 58 to repeat claims.

## Scope / boundaries

No new Connect round, no Python fixture-runner/timing-gate port, no source edits or
main-checkout mutation, no dependency additions (sponsor-allowed `modernc` SQLite
+ pinned transitives only), no Python controller substitution, no live/real
seats/timers/notifications in admission. Stage C (real-host witness) requires a
separate exact Tern release.

## Bounds

Corvid admission 20 m (this); conditional Stage B corvid 45 m in a fresh scoped
pass (only after this unchanged ACCEPTED contract + pinned checklist, no overlap);
Stage C prep/live separately signed. Total 180 m prospectively allocated inside the
4 h ceiling; remaining 60 m not automatic. One eligible 30 m repair only on Tern
release; no P8-r2. No installed-binary adoption/P9 allocation on PASS.

## Effect

Admission **ACCEPTED (bounded)** with the preregistered 8-case checklist and the
Stage B reproduction/toolchain obligations. No implementation or live release
conferred. Returned to Tern.
