Package P10-production-handoff-1 (the first real package on agent-loop). Write two files:

1. /home/bmosher/memory-bake-off/campaign4/OPERATOR-HANDOFF-20260923.md, an operator handoff for the deployed loop, with these sections, each filled from the live host (run the commands; do not copy from plans):
   - Pins: `sha256sum /home/bmosher/.local/bin/agent-loop`, `/home/bmosher/.local/bin/agent-loop version`, the source commit (from `go version -m /home/bmosher/.local/bin/agent-loop | grep vcs.revision`), `sha256sum /home/bmosher/.config/agent-loop/campaign4.json`, `systemctl --user cat agent-loop@campaign4.service agent-loop-liveness@campaign4.timer`.
   - Commands: install, run (the units), status (`agent-loop expose --config /home/bmosher/.config/agent-loop/campaign4.json`), stop (`agent-loop stop`), start, restore/rollback (from /home/bmosher/memory-bake-off/campaign4/packages/P10-go-requalification-cutover/plans/cutover.sh rollback).
   - Effect ownership: which units are enabled and active now (`systemctl --user list-timers --all`, `systemctl --user is-enabled` for openwork.timer coax-dry.timer shadow-watch.timer agent-loop@campaign4.service agent-loop-liveness@campaign4.timer), and that cairn is duty only.
   - Known limits: copy the list from `agent-loop expose --json` (known_limits).
2. /home/bmosher/memory-bake-off/campaign4/packages/P10-go-requalification-cutover/operator-handoff-manifest.json: {"handoff_sha256": <sha256 of the .md>, "binary_sha256": <sha256 of /home/bmosher/.local/bin/agent-loop>, "config_sha256": <sha256 of /home/bmosher/.config/agent-loop/campaign4.json>, "units": {<unit>: <sha256 of its file>}, "generated_at": <`date -u +%FT%TZ`>}.

Then run this exact command and end your turn:
   /home/bmosher/.local/bin/agent-loop claim --config /home/bmosher/.config/agent-loop/campaign4.json --qid P10-production-handoff-1 --step worker --outcome completed --artifact handoff=OPERATOR-HANDOFF-20260923.md --artifact manifest=packages/P10-go-requalification-cutover/operator-handoff-manifest.json
