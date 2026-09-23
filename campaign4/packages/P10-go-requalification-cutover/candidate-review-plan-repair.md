# P10-go-requalification-cutover — plan-repair verification

- **Reviewer:** corvid-dsh
- **Action:** `P10-planverify-1` (existing ≤20 m grant)
- **Brief:** `plan-repair-receipt.json` / `plan-repair-decision.json` (`555db72`);
  prior candidate PASS `f0ee7b9c…` preserved.
- **Bound bytes:** candidate source `p10-liveness` `1341f0469fba…` (clean, no new
  commit), binary `c1c49a293ed9434c1f6e1f539fd5d9ebf89a0fab220580cf69ddd821547afac8`
  (unchanged), plan dir `plans/`.
- **Scope:** read-only; offline DRY rehearsal with stubs only, no real units/seats/
  main/install.

## Verdict

**PASS (bounded).** The corrected executable plans and task texts are complete and
internally consistent; the frozen candidate binary is unchanged; and offline
construction/effect checks reproduce the corrected mechanisms (no ellipses, no
`%h` in shell, causal pre-first-pass window, notify/exit-64 assertions, real
callback drain, absolute rollback paths, one-shot driver with `trap` cleanup and
wall-stop). Residuals are the expected DRY-mode limits. No live/cutover release.

## Frozen candidate

- Branch `p10-liveness` HEAD `1341f0469fba…`, working tree clean; no commit added
  by this repair (`plans/` is package-local, not on the branch).
- Binary `c1c49a29…` recomputed equal to the reviewed candidate; installed
  `~/.local/bin/agent-loop` untouched. Source pin `1341f04` stated explicitly.

## Plan files / hashes

`plans/` — 11 declared files, all sha256 **match** `plan_files_sha256`:
`live-driver.sh`, `cutover.sh`, `live-inputs.template.env`,
`cutover-inputs.template.env`, `README.md`, and six `tasks/*.md`
(`l-worker`, `l-verify`, `l-noclaim-worker`, `ack`, `handoff-task`,
`handoff-verify`).

## Corrections verified (README map + source)

- **No ellipses / sed placeholders:** no literal `...` in any non-comment line of
  `live-driver.sh`/`cutover.sh`; the only `%h` is the sed *pattern* at
  `live-driver.sh:111` (which removes `%h`) plus comments.
- **Causal pre-first-pass control:** L7c installs a drop-in
  `ExecStart=/bin/sh -c "sleep 40; exec $A run …"` + `TimeoutStartSec=120`, waits
  for the new InvocationID, then asserts the controlled `starting` window
  (`:157-167`) — not a hoped-for race.
- **Case order / quiet rest:** SETUP → L1 → 3-min rest window → L2 → L3a → L7c →
  L3b → L4a → L7a → L7b → L6+L5 → L4b last (stops the duty seat).
- **notify / exit-64 assertions:** L5 waits on
  `ExecMainStatus … grep -qx 64`, records the stray start rc instead of assuming 0,
  and greps the journal for "Scheduled restart".
- **Actual callback drain:** `cutover.sh` `drain()` polls `systemctl --user
  is-active` (active/activating) up to 120 s then stops each service; used for the
  old owners in `switch` and for agent-loop's callback services in `rollback` —
  listing timers is not the proof.
- **Absolute rollback paths:** rollback re-creates campaign4-watch with the
  absolute `/home/bmosher/.config/agent-deck/campaign4-watch` (no `%h`), restores
  `agent-loop.prev-c124d82`, and wakes cairn with `open-items.json` (no resend).
- **One-shot driver + cleanup:** `trap cleanup EXIT` (`:92`) and a wall-stop
  `systemd-run --on-active=…` armed before any task (`:99`); cleanup names only
  this run's units and seat IDs.
- **Production handoff:** `cutover.sh handoff` dispatches
  `P10-production-handoff-1` with `--worker kiln --verifier corvid` and the shipped
  `tasks/handoff-task.md` / `handoff-verify.md`.

## Offline construction/effect rehearsal (independent)

- `DRY=1 EV_DIR=… live-driver.sh live.env` → rc0, every command printed, none run,
  `trap cleanup EXIT` ran the exact-ID cleanup (units reset/removed, wall-stop
  stopped, seat stop/remove listed).
- `DRY=1 cutover.sh cut.env {capture,switch,handoff,rollback}` → all rc0; switch
  drains old services then enables agent-loop; handoff dispatches through
  agent-loop; rollback uses absolute paths and hands open items to cairn.
- **DRY limits (expected):** `prop()`/`state` return empty, so systemd-dependent
  cases print FAIL/DRY in the rehearsal `results.tsv` (e.g. L1/L2/L3/L7b) — that is
  command-construction evidence only, **not** systemd evidence. Late-bound inputs
  (`RUN`, `ROOT`, fixture IDs, deadlines, cutover run id, production IDs) remain
  `<...>` templates and must be materialized and hashed before Tern's signature.

## Effect

One bounded verdict: **PASS (bounded)** — corrected plans complete and rehearsed
offline, candidate binary frozen and unchanged, all declared plan hashes exact.
No live/cutover release; Tern must materialize/hash the late-bound inputs and sign.
Returned to Tern.

---

## Reconciliation — Tern reproducer BLOCKER on the exact plans (no source edits)

Preserved: the construction PASS above stands as historical evidence, but the
exact plans are **NOT live-signature-ready**. `director-plan-repair-reproducer.json`
(`912b55b2…` = `live-driver.sh`) reproduced a blocker on the unchanged helper
functions with a **valid REST** state file; my own re-read confirms the cause.

### 1. `out()` contaminates captured stdout → `verdict`/`state_is` fail (BLOCKER)

`log()` writes to **stdout** (`echo … | tee -a driver.log`) and `out()` calls
`log "+ … (captured)"` **before** running the command, whose stdout is not
redirected. So `state() { out cat "$ROOT/$P.db.liveness.json"; }` emits the log
line **followed by** the JSON; `verdict()` pipes that into `json.load` → parse
error → `verdict_rc=1`, and `state_is()` (`grep -q "^$1 "`) is always false. Every
`wait_for … state_is …` and `quiet_window` therefore fails even on a healthy run.
Tern's probe with a valid `{"last_verdict":{"state":"rest"}…}`: `verdict_rc=1`,
`state_is_rc=1`. DRY mode masked this (`out` returns `DRY`, parser yields empty).
**Smallest correction (plan text, no source):** keep captured stdout clean — send
the `out`/`log` banner to stderr or `driver.log` only (e.g.
`out() { log "+ $* (captured)" >&2; …; }`), or have `state()`/`prop()` read the
file/command directly without `out`.

### 2. Wall-stop cleanup does not terminate the original driver

`cleanup()` stops the liveness/run units, removes units/seat IDs and the wall-stop
timer, but never terminates the **original `live-driver.sh` process** (no PID is
recorded). The wall-stop unit runs `live-driver.sh INPUTS cleanup` in a *separate*
process at the deadline, so after it fires the original driver can still issue
`run`/`dispatch`/`restart` commands against removed units, and its own `trap
cleanup EXIT` runs cleanup again later. **Smallest correction:** record the driver
PID (`echo $$ > "$EV/driver.pid"`) and have the wall-stop stop the original driver
first (kill that PID / run the cleanup *after* terminating it), then perform
exact-ID cleanup; the driver must stop issuing effects at/after the wall deadline.

### 3. L2 open work before later rest assertions

L2 (`live-driver.sh:137-147`) dispatches a no-claim worker (`--duration 15m`) and
kills run during the worker step; the package is left **open** (worker, no claim)
and is never claimed, decided or cancelled. Later cases require `rest` with no open
package — `wait_for "L4a settled" 90 state_is rest` (`:190`), `wait_for "L7b
recovered" 150 state_is rest` (`:206`) — and `quiet_window … rest` counts only
`rest`. With L2 (and later L6) open, those assertions cannot hold. **Smallest
correction:** dispose L2 (owned decision/interrupt/cancel) before the later `rest`
assertions, or assert the correct state for an open package (`ok`/`held`) and keep
pure-rest windows before any open-work case; do not count an open package as rest.

### Effect (reconciled)

The plan-repair PASS is preserved, but the plans must be corrected for (1) the
`out`/`verdict` stdout blocker, (2) wall-stop termination of the original driver,
and (3) L2-open-vs-rest ordering before Tern signs any live/cutover plan. No source
edit was made; findings returned to Tern.
