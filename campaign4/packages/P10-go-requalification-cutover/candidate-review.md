# P10-go-requalification-cutover — candidate review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P10-review-1` (fresh 30 m candidate review per release)
- **Brief:** `dispatch-receipt.json` (`P10-initial-1`, release `55a66a0`);
  contract `9a8b6b66…`, admission `a97de1ab…`.
- **Bound bytes:** branch `p10-liveness` commit
  `1341f0469fba84787112a705b0d107e096644085` (base `c124d82`), private binary
  `c1c49a293ed9434c1f6e1f539fd5d9ebf89a0fab220580cf69ddd821547afac8`, archive
  `41cb0d22…`, manifest `4de2ef53…`.
- **Scope:** read-only verification on the bound branch/binary; no live/cutover.

## Verdict

**PASS (bounded) for the candidate stage.** The three P8 liveness blockers are
fixed on the bound branch and independently reproduced (baseline false-green
reproduced; corrected owned UNKNOWN/hung/starting behavior confirmed through the
real CLI), core/host/py are byte-unchanged, the retained suite and 125 conformance
are green on the shipped binary, the manifest/evidence hashes are exact, and
unshared malformed-state mutations reject as owned UNKNOWN. Live/systemd and
cutover remain for their separately signed stages.

## Pins / frozen control

- Worktree `agent-loop-p10` on `p10-liveness`, HEAD `1341f04…`, clean;
  `git diff c124d82 HEAD -- internal/core internal/host internal/py` **empty**;
  changed = 9 files exactly as claimed (`cmd/loop.go`, `internal/loop/liveness.go`,
  `expose.go`, tests, `mutate_go.py`, docs). Installed `~/.local/bin/agent-loop`
  `221bb3aa…` and main `c124d82` unchanged.
- Binary `c1c49a29…`, archive `41cb0d22…`, `MANIFEST.sha256 4de2ef53…` recomputed
  equal; `sha256sum -c` **16/16 OK**; all five `evidence_sha256` files match.

## Gate

- `go test ./...` on the worktree → **ok** all packages (incl. `internal/loop`,
  `internal/expose`). Shipped binary `conformance conformance/cases` → **125/125,
  1751 steps**. Host parity `316/321 + 5` and `mutate_go.py 92/92` are
  author-reported (not rerun here).

## Three blockers — baseline fails reproduced, corrected passes confirmed

Ran `evidence/liveness-cases.sh` on the installed base binary (`221bb3aa`) and the
candidate (`c1c49a29`):

- **Base (false green):** `1a/1b/1d` exit 1 with **no alarm**; `1c` closes an
  id-less incident as "recovered"; `2a–2c` (future/clock-back) and `3a–3f`
  (prior incarnation/PID reuse/no identity) all report **`rest`**.
- **Candidate (owned):** `1a` malformed → `unknown` alarm + duty woken;
  `1b` truncated → `unknown`; `1c` invalid partial → `unknown` (never "recovered");
  `1d` unreadable → `unknown` (original untouched); `2a` 6 s future → `unknown`
  ("clock stepped back?"); `2b` 5 s boundary → `rest` (accepted by design);
  `2c` clock back → `unknown`; `3a/3c/3d` → `hung` alarm; `3b` restart-in-grace →
  `starting` (quiet, **not recovered**); `3e` no InvocationID → `unknown`;
  `3f` same invocation, other pid → `unknown`.
- Implementation matches: `FutureTolerance = 5s`, pass records `INVOCATION_ID`,
  `QueryUnit` reads `InvocationID,MainPID,ExecMainStartTimestamp`, damaged state is
  copied/verified (`Damage`/`Quarantine`/`PriorIncident`/`PriorAck`), and the pass
  is written only by run's loop after a completed Tick (no hidden goroutine).

## Unshared mutations (independent)

Three malformed state files not in the author's set, candidate binary:
`{"open": ["not-an-object"]}` → owned `unknown` alarm + duty woken (no crash);
`{"history": "x", "open": 5}` → owned `unknown`; a valid incident with a malformed
ack deadline + missing ledger → `unknown` alarm with duty continuity preserved.
No silent empty-state reset; failures stay loud/owned.

## Residuals (adopted)

Nothing is observed on real systemd (restart, watchdog, exit 64, start limit,
`INVOCATION_ID`, 45 s timer) — the live stage's to prove. `Type=notify` exit-64
start semantics to confirm in L5; if both state dir and working copy are
unwritable the alarm repeats loudly each check; prior-incident continuity is
best-effort regex evidence (not a restored live ack); a pass from a run without
`INVOCATION_ID` never counts while a unit is configured; per-action deadline
timers still run while stopped (by design, L6). Author parity/mutation reported,
not rerun here.

## Effect

One bounded verdict: **PASS (bounded)** — three blockers fixed and independently
reproduced (base false-green, candidate owned), frozen control, suite/conformance
green, manifest exact, unshared negatives reject. No live/cutover release. Returned
to Tern for the qualification live stage.
