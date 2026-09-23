# P8-go-unattended-qualification — Stage B completion review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P8-qualification-completion-1` (continuation of `P8-qualification-1`,
  original deadline `05:59Z`, no reset)
- **Brief:** `stageB-completion-instruction.md` + `stageB-completion-receipt.json`;
  prior bounded `qualification-review.md` (`2310db38…`) retained.
- **Evidence:** `stageB-evidence/` (preserved `/tmp/p8qual`, `/tmp/p8e`, plus new
  `p8e2-*`, `p8f-*` private fixtures; no caches). No source edits, no live seats.

## Verdict

**Stage B COMPLETE (bounded).** All eight blocking-matrix rows now have **exact
CLI and/or unit evidence with labels**, the misleading conformance count is
corrected, and the installed-binary provenance is tied to the frozen commit by
build metadata. Residuals are named precisely; live/deployed-host behaviours
remain for a separately signed Stage C. No adoption/P9.

## Compaction corrections (per instruction)

- **Conformance coverage corrected.** From the checkout root
  `/var/home/bmosher/projects/agent-loop`:
  `agent-loop conformance` → **125/125 cases ok, 1751 steps** (real core suite).
  `agent-loop conformance conformance/host` → **3/3 *files*, 0 steps** — the host
  directory holds 3 non-case JSON files (`scenarios.json` 23 scenarios,
  `expected.json`, `adjudicated.json` 5), so 3/3 is **not** scenario coverage and
  must not imply 23/321. (Run from this package's cwd the relative paths resolve
  0/0 — the command is checkout-relative.) Host `316/321 + 5 adjudicated` and the
  `58/58` mutation runs are **reported**, not independently reproduced here.
- **Build provenance.** `go version -m /home/bmosher/.local/bin/agent-loop`:
  `go1.27.1`, `GOOS=linux/amd64`, `CGO_ENABLED=1`, `vcs=git`,
  **`vcs.revision=4a00d675d438…`**, `vcs.modified=false`, `mod agent-loop
  v0.0.0-20260923050852-4a00d675d438`; deps pinned (`modernc.org/sqlite v1.59.0`,
  `x/sys v0.47.0`, …). Source tie is by **build metadata**, not by the clean
  checkout. A byte rebuild (`/tmp/agent-loop-rebuild` `7f874dcd…`) differs from
  the installed `8cc149bf…` (Go build non-reproducible without `-trimpath`, paths
  embedded in build id) — explained; the installed binary remains the selected
  artifact.

## 8-row evidence matrix

| # | case | CLI evidence (private stubs) | unit evidence (exact test) | label |
|---|---|---|---|---|
| 1 | Restart/no duplicate | wake stub rc1: `run` ×3 → outbox `held-ambiguous/failed`, wake invocations stayed **1** (no blind resend); kv `msg:msg-Q1-w1-1` `{rc:1,state:failed}`, `outbox-sent`/`outbox-pending` retained | `TestRestartDoesNotResend`, `TestCrashBeforeCommitReconciles`, `TestCrashAfterCommitDoesNotRepeat` | CLI+unit |
| 2 | Hung/owned | duration `1s`, real clock: callback → `{"decision":"interrupted","dedup":false}`, cancel to worker `K`, director `tern` told (`deadline-expired`), status `timed-out`; repeats → `already-handled`; early → `no-op-early`; unknown → `E_UNKNOWN_PACKAGE` | `TestDeadlineCancelsTheTurnAndTellsTheDirector`, `TestMissingEscalationBoundIsOwned` (`E_NO_ESCALATION_BOUND`), `TestNoTimerNoDispatch` | CLI+unit |
| 3 | Independence | same session for `kiln`/`corvid` → `dispatch` refused `E_SEAT_BINDING: session K is kiln, not corvid` | `TestSeatBindingIsCheckedBeforeDispatch`, `TestWrongIdentityRejects` | CLI+unit |
| 4 | Input validity | missing input → `dispatch` rc3 refused; declared input mutated before verifier release → `E_INPUT_CHANGED`, **no verifier wake**, reason in `status` | `TestChangedInputBlocksTheVerifierDispatch`, `TestHeldPackageWithChangedInputIsNotSent` | CLI+unit |
| 5 | Exhaustion/no-retry | no automatic retry observed after refused/failed steps; `decide` before verdict `E_PHASE_MISMATCH`; no invented retry | `TestDispatchRefusals` | CLI+unit |
| 6 | Judgment/dependencies/status | `--after NOPE` refused rc1; self `--after QQ` refused; non-permitting predecessor (`decide blocked`) → dependent `blocked` `E_DEPENDENCY_UNMET: Q1 closed blocked`; positive `question_answered` released the dependent **once** | `TestPendingDecisionHoldsDependents` (no dedicated cycle test found; self/unknown refusal covers) | CLI+unit |
| 7 | Evidence/atomicity | absent and **truncated** verifier claim → no verdict/close across repeated `run`; `status` never `closed` | `TestInvalidDispositionNeverRests`, `TestAtomicCloseSucceedsOnce`, `TestConflictingDispositionRejects`, `TestPartialVerdictGetsOnlyTheDecide`, `TestCrashBefore/AfterCommit…` | CLI+unit |
| 8 | Handoff | full `dispatch→run→claim→end→run→claim→end→run→decide`: one wake per action, verifier `PASS`, closed by `question_answered`; bogus callback no effects; terminal reopen ×2 → **0 new wakes** | `TestHappyPathToDecision`, `TestOnPassClosesWithoutADecision`, `TestVerifierFailWaitsForTheDirector`, `TestTamperedArtifactIsOwnedRecovery` | CLI+unit |

`go test ./...` on `4a00d675` (clean) → **ok** all packages; `internal/host` 10
tests and `internal/loop` 13 tests all PASS (names above).

## Residuals (named, not silently deferred)

- Real-host transport/turn-watcher/timers, real due-deadline cancellation of a
  live seat, and confirmation the destructive crash variants behave identically on
  the host path remain **unit-proven only** → Stage C.
- Host scenario/adjudicated comparison (`316/321+5`) and mutation `58/58` are
  reported by the director; not independently rerun here (per contract).
- No dedicated dependency-**cycle** unit test found; self/unknown refusals and
  the immutable preexisting graph are covered indirectly (`TestPendingDecisionHoldsDependents`).
- Build not byte-reproducible (explained above).
- `examples/campaign4.json` remains an example; fresh isolated fixture identities
  required for any Stage C.

## Effect

One bounded verdict: **Stage B COMPLETE (bounded)** — 8-row matrix with exact
CLI+unit labels, corrected conformance counts, binary provenance; live/deployed
rows deferred to a separately signed minimum real-host witness. No live/prep/
adoption release. Returned to Tern.
