Package P11-production-handoff-1, verifier step. Check the worker's two files against the live host, read-only:
1. Recompute every hash in /home/bmosher/memory-bake-off/campaign4/packages/P11-live-driver-qualification/operator-handoff-manifest.json from the files it names; all must match.
2. Run each status/pin command the handoff lists and compare the output with what the handoff says.
3. Confirm with `systemctl --user is-enabled` / `is-active` that openwork.timer, coax-dry.timer and shadow-watch.timer are disabled and inactive, and agent-loop@campaign4.service and agent-loop-liveness@campaign4.timer are enabled and active.
Write your findings, one line per check with PASS or FAIL, to /home/bmosher/memory-bake-off/campaign4/packages/P11-live-driver-qualification/operator-handoff-verification.md. Then run exactly one of these and end your turn:
   all PASS: /home/bmosher/.local/bin/agent-loop claim --config /home/bmosher/.config/agent-loop/campaign4.json --qid P11-production-handoff-1 --step verify --outcome completed --artifact review=packages/P11-live-driver-qualification/operator-handoff-verification.md
   any FAIL: the same command with --outcome failed
