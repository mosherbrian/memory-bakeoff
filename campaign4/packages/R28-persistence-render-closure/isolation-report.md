# R28 isolation report: the actual R27 participant texts from the pre-nudge binary

**Result: isolation established.** The exact pre-nudge agent-loop (`~/.local/bin/agent-loop.prev-r23-47f69dfd`, sha256 47f69dfd...) dispatched all six R27 arms (pairs A, B, C x C and T) through its real `dispatch` CLI in an isolated temp root. The captured worker texts:
- Control texts contain **neither** platform-nudge variant ("What happens next, who does it..." or "If it is yours, do it now...", nor "Before you end your turn" or "What might I have dropped"), and **no** treatment packet.
- Treatment texts contain the R27 packet.md **exactly once** and no platform nudge.
- After the declared substitutions (packet vs "No additional notes.", arm letter, execution id), C and T are byte-identical in every pair (offline/run2/checks.json).

## How
`offline/render.sh OUTDIR` creates `/tmp/r28-render-XXXX` with its own config, SQLite DB, stream, claims and artifacts dirs. Its config names only executable stubs for wake, systemd-run, systemctl and agent-deck (a fixed four-seat registry). Every dispatch runs under `env -i HOME=<temp> PATH=<stubs>:/usr/bin`. The stubs record argv to calls.jsonl. The only calls were `systemd-run --user` (the worker deadline timer, not created) and `wake K` (the kiln text, captured). No real socket, unit, production DB or config was touched. The script refuses to run if the binary hash is not the expected one (fail-closed). Task texts are composed mechanically from R27 task-pair-X.md: the "Common body" lines with <ARM>/<EXEC>/<OUT> substituted, plus packet.md (T) or "No additional notes." (C) above the body. They are not edited by hand.

## Evidence
- `offline/run2/`: the witness. commands.txt (six dispatches, all rc 0), texts/R27-{A,B,C}-{C,T}.txt (raw rendered), stub-calls.json, isolated-config.json, checks.json (hashes and results).
- `offline/run3/`: reproduction. Identical texts except the random temp-root path inside the loop's claim instruction.
- `offline/control-v2/`: positive control. The same render with the installed v2 binary (eb9cc019); its control text DOES contain the nudge, so the check can fail.
- `offline/run1-failed-probe.txt`: first attempt, aborted in stub generation before any dispatch (kept, labelled).

## Proposal for execution (not authorised here)
Run R27 through a **private loop instance on the pre-nudge binary**: config `~/.config/agent-loop/campaign4-r27.json` with the same seat IDs (kiln, corvid, tern, cairn), its own `db`, `claims_dir`, `artifacts_dir` subfolder and project name, so its timer units are `agent-loop-r27-*`, separate from production. `bin` is the 47f69dfd binary. Dispatch with that binary and config. Deadlines are owned by that instance's own systemd timers. The director is Tern. Supervision: a `run` process for the private config (a transient user service) plus Tern's director timer as backstop. Production's loop must not dispatch to kiln while a private arm runs (one-at-a-time, as in R24). Stop the private run service and retire its units after the last arm. The R23 nudge stays out because the private instance never runs the nudged binary. Before each arm: kiln idle, R10 checks, /new.
