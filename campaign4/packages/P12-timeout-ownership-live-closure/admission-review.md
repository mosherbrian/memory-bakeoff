# P12-timeout-ownership-live-closure — admission review (independent)

- **Reviewer:** corvid-dsh; action `P12-admission-1`, start `16:51:11Z`, deadline
  `17:06:11Z`.
- **Contract:** `package.md` sha256
  `6391857222e07851fdcdec0893be660d04fcecfe6c13290e7b84c76349d5a46f`, matching
  commit `1315196`; `inputs.json`; `sponsor-allocation.json` (365 m).
- **Verdict: ACCEPTED** — pins verified, scope complete against the P11 findings,
  allocation reconciles, per-family checklist preregistered.

## Pins / integrity

- All **12 `inputs.json.paths_sha256` recomputed equal**, including P11
  `package.md ca512b21…`, `repair-1-review.md eef3be95…`,
  `live-review-1.md cf360060…`, `live-evidence-defects-1.json 54eb0d18…`,
  `live-timeout-idle-finding.json ebf540a4…`, `live-wall-timer-finding.json
  9bb711fd…`, `terminal-successor-decision.json 63f0f066…`,
  `live-end-manifest.json d3cfba25…`, the P11 plans, and P10 `package.md`.
- `base_go 1341f04…`; `P11_live_commit cd720fa` resolves; `package.md` at `1315196`
  is byte-identical to the working copy.
- **P11 terminal preserved:** `terminal-successor-decision.json` keeps **NOT READY**
  and records the snapshot correction (16:45:50 follows cleanup 16:45:25; stopped
  properties do not prove reload-disarm). No retro PASS.
- **Allocation reconciles:** 15+75+30+40+25+15+10+75+25+45+10 = **365** = sponsor
  365 m; +105 over the 260 m tentative; no hidden reserve; P11 unused cutover 55 m
  cancelled, not transferred.

## Scope completeness (covers every P11 blocker)

| P11 blocker | P12 scope |
|---|---|
| Idle `/cancel` → `nothing running` aborts L2/L6 settlement + director wake | A (classify exact receipt; never swallow errors; durable settlement/escalation without a live worker turn; crash/reopen/retry no lose/duplicate) |
| L6 ack NOT READY | B (authenticated ack for exact package/execution/action/incident; trusted time, next action, response deadline; forged/stale/wrong/past/conflicting rejected; delivery not ack) |
| Recurring `stop-sigterm`→SIGABRT / watchdog abort | C (reproduce before edits; prompt SIGTERM within `TimeoutStopSec`; watchdog abort not auto-bug; core frozen) |
| Zoneless journal windows, setup `ok` vs `rest`, L4a/L4b injection & classification | D (UTC/epoch windows; idle baseline may be `rest`; no hidden failed wait; L4a real `start-limit-hit`; L4b real director ack + crash-vs-restart-loop) |
| Wall enforcement NOT PROVEN | E (real repeated `daemon-reload`; exact timer config; schedule before/after; actual firing terminating driver+children; fallback independence; stubbed reload insufficient; calendar exception with explicit UTC/exact instant/clock jumps; 30 s detection precision) |
| PASS-only cutover | P10 section D, `P12-production-handoff-1`, new ledger, retire old owners, rollback, corvid postcutover |

## Boundary checks (acceptable)

- Go unfreeze is **bounded** (loop/transport timeout ownership, normal shutdown,
  service integration, tests/status, package-local live driver); Python/core frozen;
  separate worktree/private binary; main/installed preview unchanged until signed
  cutover.
- L6 must now pass **both** detection and acknowledged ownership; P11's NOT READY
  predeclaration is **not** inherited as a waiver.
- Real isolated systemd scope/timer/reload experiments authorized with exact names,
  bounded cleanup, no real seats/tasks, no global config changes; `daemon-reload`
  global-unit inventory required and recorded, **never claim zero host effects**;
  uncontained P10 baseline forbidden; failed experiments remain evidence.
- Retained core125 conformance, host-parity adjudication with named case diffs, and
  one unshared negative per new authority/failure boundary; real argv/CLI tests; no
  always-success transport oracle; author tests separated from independent checks.
- One optional 40 m repair + 25 m review on explicit director release; no automatic
  second attempt/extension.

## Effect

**ACCEPTED.** Checklist filed as `acceptance-checklist.md`; on the unchanged pinned
contract, Cairn may conditionally release Claude's 75 m author grant via
`notify-claude tern`. No author start before admission; candidate PASS returns Tern
with no automatic prep/live/cutover. No source/live/cutover change made by corvid.

---

## C supplement incorporated (append; ACCEPTED preserved)

Read `shutdown-causal-evidence.json` (`293b08af…`). Independently verified at base
`1341f04`: `loop.go dd351d74…` (signal.Notify :273; nonblocking check; `time.Sleep`
fallback :329) and `notify.go 6e4fd20a…` (`DirNotifier.Wait` :38). Technical
correction accepted: **`Wait` uses `syscall.Select`, not `poll`.** The C checks
(baseline synchronized real-systemd idle-stop repro; corrected < 1 s clean-exit
target measured independently; both notifier+fallback paths; SIGINT/repeated
stop/restart; no leaked goroutines/fds; retain stop64/watchdog/no-resend; no global
`TimeoutStopSec` increase) are appended to `acceptance-checklist.md`. A narrow
notifier cancellation-interface change is permitted under C; core frozen; contract
365 m unchanged. **Verdict unchanged: ACCEPTED.**
