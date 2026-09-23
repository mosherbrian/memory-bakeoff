# P8-go-unattended-qualification — repair-1 postreview (Parts A+B)

- **Reviewer:** corvid-dsh
- **Action:** `P8-repairreview-1` (existing ≤20 m grant)
- **Brief:** `repair-1-director-receipt.json`, `repair-1-release.md`, claim
  `repair-1-claim.json`; proposal `repair-1-proposal.md`.
- **Bound bytes:** branch `p8-repair-1` commit
  `71318c4e7a0ed142acd61d4553f31e5bad0fb474`, private binary
  `/tmp/claude-1000/…/p8r1-build/agent-loop` sha256
  `3a84efb36e1f79ffc1a03bcc4924b26cd060e52ae2d597a2f4000012f176b8e0`.
- **Scope:** read-only verification on the bound branch/binary; no live seats/
  services, no source edit.

## Verdict

**INCOMPLETE (bounded) — amended after Tern steering (`repair-1-intake.json`).**
Parts A (authority freeze) and most of B are verified on the bound branch/binary
(core/host/py unchanged, suite/conformance green, manifest exact, unshared
negative rebind refusal and liveness duty-wake/persisted incident), but steering
focus exposed a real **Part B heartbeat defect**: a future-dated `loop-pass` is
accepted as green. See the **Steering addendum** at the end; the earlier PASS
reasoning stands per-part except the liveness heartbeat. No adoption.

## Pin / branch verification

- Worktree `/var/home/bmosher/projects/agent-loop-p8r1` on `p8-repair-1`, HEAD
  `71318c4e7a0e…`, clean. `git diff 4a00d675 HEAD -- internal/core internal/host
  internal/py` is **empty** (frozen core/host/python); changed = 13 files exactly
  as claimed (authority.go/liveness.go + tests + loop.go/loop_test.go +
  cmd/loop.go/main.go + deploy/systemd units + README + mutate_go.py).
- Private binary `3a84efb36e1f…` present (13,475,833 bytes); `go version -m`:
  `go1.27.1`, `-trimpath=true`, `CGO_ENABLED=0`, `GOOS=linux/amd64`,
  `vcs.revision=71318c4e…`. Installed `/home/bmosher/.local/bin/agent-loop`
  remains `8cc149bf…` (main unchanged).
- Claim `manifest_sha256`: **191 entries, 0 missing, 0 drift**, including all 13
  changed files.

## Independent suite reproduction

- `go vet ./...` clean; `go test -count=1 ./...` → **ok** all packages.
- Private binary `conformance conformance/cases` → **125/125 cases, 1751 steps**.
- (`TestParity` 316/321 + 5 adjudicated and `mutate_go.py 71/71` are **reported**
  by the claim; I did not rerun the full mutation sweep within the bound.)

## Part A — authority freeze (verified)

- `internal/loop/authority.go`: `bindPrincipals` records registry-confirmed
  principal/role/session at dispatch; `authority`/`authorities` return the core
  cast actor only if the package's recorded principal still matches, else
  **`E_AUTHORITY_MISSING` / `E_AUTHORITY_CHANGED`** before mutation — no silent
  backfill from current config.
- **Unshared CLI negative:** after rebinding `director`/`duty` in the config,
  `decide` on the registered package → rc3
  `E_AUTHORITY_CHANGED: Q1: director was tern (T), config now binds tern (X9)`.
- Unit (`authority_test.go`, in the green suite): exact live-1 failure with
  fixture principals ± reopen; on-pass close; director/worker rebind refusals;
  record-without-principals `E_AUTHORITY_MISSING`; duty≠worker/verifier; timer
  callback refused on a rebound duty. Worker/verifier/director sessions stay
  distinct; CLI remains a trusted-host boundary (unchanged, documented).

## Part B — supervised liveness, stop, incidents (verified)

- `internal/loop/liveness.go`: `Assess` is a pure decision with **unknown never
  green**; `QueryUnit`, pass/stop-marker handling, incidents, ack binding, and
  owned escalation. New CLI: `start`, `liveness`, `liveness-ack`.
- **Unshared CLI negatives:** with an unreadable ledger → verdict
  `{"state":"unknown","alarm":true,...}`, incident opened, **duty woken once**
  with the exact `liveness-ack … --by tern --next … --within 15m` command, and the
  incident persisted in `<db>.liveness.json` with a wake receipt (`rc0`,
  `state:sent`). `stop` → marker + documented "stop is not cancellation"; next
  `liveness` → `{"state":"stopping","alarm":false}` (quiet) with the incident
  closed `stopped-intentionally`.
- Unit (`liveness_test.go`, green): Assess table incl. unknown/rest/stopped/
  stop-pending/crashed/restart-loop/down/hung/erroring and unreadable inputs; ack
  binds owner/next/deadline, **ack is not recovery**, invalid acks refused, expired
  ack escalates; no repeat within 15 min, closed only on a fresh servicing pass;
  intentional-stop quiet over 5 checks while the same unit without the marker
  alarms `down`; restart-loop escalates; error streak recorded/reset.
- **Timing correction applied** as the release requires: stale 100 s, check every
  45 s, `AccuracySec=1s`, `RandomizedDelaySec=0`, bounded local calls — documented
  as a deviation from the proposal. Per-action timers remain effective while
  `run` is stopped (documented, asserted by design).

## Residuals (adopted; honest, bounded)

Real systemd behaviour (`Restart=always`, `WatchdogSec=90`, exit-64 semantics,
start-limit, 45 s accuracy) is unexercised; the 90 s watchdog vs a long Tick is
unmeasured; a broken wake script leaves an incident recorded but nobody told (no
third route); the liveness timer itself is unwatched; CLI is not
caller-authenticated (trusted host); the timer-callback duty check and core
callback are two ledger opens (small non-atomic window); pre-4a00d67 packages
without principals cannot be continued (by design, no backfill); per-action timers
fire while stopped by design. These require the separately signed live witness —
not a candidate PASS.

## Effect

One bounded verdict: **PASS (bounded)** — Parts A and B implemented on the bound
branch/binary, suite+conformance+manifest verified, unshared negatives reproduced,
residuals named. No live/repair successor/adoption. Returned to Tern for the exact
live witness release.

---

## Steering addendum (`repair-1-intake.json` focus, bound 191/191 + binary unchanged)

Bound re-checked: branch `71318c4e` / binary `3a84efb36e1f` / manifest 191/191
zero drift (unchanged). Focus items reviewed against `internal/loop/liveness.go`
and reproduced on the private binary with a private config/stub (`/tmp/p8s`).

### 1. Heartbeat incarnation / future time — **DEFECT (NOT READY)**

- Code: `Assess` computes `age := now.Sub(at)` and only flags `age > StaleAfter`;
  a **future** `at` gives a negative age that passes every guard, so a
  future-dated pass renders green. There is also **no incarnation binding**: the
  pass record carries `pid` but `Assess` never checks it against the current run
  (unit `InvocationID`/`MainPID`), so a prior run's recent pass can read green for
  a new run.
- Reproduced: with unit `active` and `loop-pass.at = now + 10 min` →
  `{"state":"rest","alarm":false}` (green). Control: `at = now − 200 s` →
  `{"state":"hung","alarm":true}` with duty woken (`why: no completed pass for …`).
- Effect: a clock jump/forged/future heartbeat, or a fresh pass from a *different*
  run, can suppress a real stall — contradicting the release's "unknown is never
  green" and intake's "fresh historical pass is not proof current run serviced
  work". **Smallest correction:** in `Assess`, treat `at > now + tolerance` (and
  unparsable/negative ages) as `unknown`/alarm, and bind the pass to the current
  run incarnation (PID/InvocationID) so a prior run's pass cannot certify the
  current one. No source edit made here.

### 2. Malformed incident / state file — **FAIL-CLOSED (verified)**

- `loadState` returns the `json.Unmarshal` error; the `liveness` command exits
  **rc1** with the parse error rather than starting with empty state.
  Reproduced with a corrupted `loop.db.liveness.json` → rc1, no silent loss of an
  open incident. Bounded consequence: the liveness check cannot run until the
  state is repaired (documented as a residual).

### 3. Actual acknowledgements vs transport sends — **VERIFIED (separate)**

- `Wake.Status` is only `sent/queued/failed/ambiguous` and is explicitly "never an
  acknowledgement"; `Ack` is a separate record (`liveness-ack`), and `Check`
  escalates on an **expired ack** ("acknowledged by … but not recovered by …") or
  a missing ack ("duty did not acknowledge"), and closes only on a fresh servicing
  pass. Unit tests in the green suite cover ack-not-recovery and expiry
  escalation. A transport send is never counted as recovery.

### Amended effect

Parts A and the suite/binding remain verified; Part B liveness carries one
**NOT READY** defect (future-time heartbeat + no incarnation binding) plus the
fail-closed malformed-state behaviour. A live witness should not be signed until
the heartbeat future-time/incarnation guard is corrected and re-verified.
