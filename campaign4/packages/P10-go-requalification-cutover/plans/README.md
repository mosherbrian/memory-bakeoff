# P10 plan repair 1: executable plans for stage C (live) and stage D (cutover)

Source pin: agent-loop `p10-liveness` @ 1341f04, binary sha256 c1c49a29 (release
`/home/bmosher/projects/agent-loop-releases/agent-loop-1341f0469fba`). No code or binary
changed. These files supersede `docs/P10-LIVE-PLAN.md` and `docs/P10-CUTOVER-PLAN.md` on that branch.

| File | Role |
|---|---|
| `live-inputs.template.env` | late-bound inputs for stage C: fresh fixture IDs, private root, start deadline. Filled and hashed before Tern signs |
| `live-driver.sh` | one-shot stage C driver: L1 to L7, evidence, exact-ID cleanup |
| `cutover-inputs.template.env` | late-bound inputs for stage D |
| `cutover.sh` | stage D: `capture`, `switch`, `handoff`, `rollback` |
| `tasks/*.md` | every task text the plans send (fixture worker, verifier, no-claim worker, ack, production handoff task and verify) |
| `rehearsal/` | offline DRY=1 rehearsal output with stub PATH. NOT systemd evidence |

## Tern's required corrections: where each is fixed

| Correction | Fix |
|---|---|
| No ellipses, no sed placeholders | Every command is literal. Unit files come from the template by one explicit sed (`live-driver.sh:111`; the `%h` there is the pattern that removes `%h`). No `...` in any script or task |
| Causal pre-first-pass control | L7c (`live-driver.sh:157-166`): a drop-in makes the main process sleep 40 s before `exec run`, so the check reads `starting` in a window the plan controls, not one it hopes for |
| Case order and quiet rest | SETUP, L1, a 3-minute rest window with no open package, L2, L3a, L7c, L3b, L4a, L7a, L7b, L6+L5, L4b last (it stops the duty seat) |
| notify / exit 64 assertions | L5 asserts `ExecMainStatus=64` from systemd (`:213`), records the stray start's rc instead of assuming 0 (`:215`), and greps the journal for "Scheduled restart" instead of trusting NRestarts (`:217`) |
| Actual drain of running callbacks | `cutover.sh` `drain()`: waits (bounded 120 s) until each service is inactive, then stops it. Used for the old owners in `switch` and for agent-loop's callback services in `rollback` |
| Absolute rollback paths | All paths start with `/home/bmosher`. No `%h` in any shell command. The previous binary is `agent-loop.prev-c124d82` |
| One-shot driver, finally exact-ID cleanup | `trap cleanup EXIT` (`live-driver.sh:92`), and a wall-stop armed with `systemd-run` before any task (`:99`). Cleanup names only this run's units and seat IDs |
| Production handoff tasks | `tasks/handoff-task.md`, `tasks/handoff-verify.md`, dispatched by `cutover.sh handoff` through agent-loop, verifier fixed to corvid |
| Open TSV dispatches | `switch` refuses while any DISPATCHED row has no result row, and returns it to Tern |
| Rollback without loss or resend | `rollback` archives the ledger and claims, writes `open-items.json`, and wakes cairn with it. Nothing is re-sent |

## L7b note

A stopped unit reads as "down" before the pass is examined. So L7b pauses run with SIGSTOP
(well under the 90 s watchdog) and then injects the future pass (`:201-205`).

## Rehearsal limits (offline only)

- In DRY mode `prop` returns empty values and task texts are not written into the private root. Command construction is shown; systemd behaviour is not.
- No real unit, seat, main binary or install was touched. Stage C evidence comes only from the signed live run.
