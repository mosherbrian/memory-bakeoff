# R50 readiness (offline repair; zero model calls)

**Corrected**
- Scanner v3 (scan.py) accepts every stream-json event shape and never dereferences string `message` fields. It correlates tool_use ids with results and permission_denied events: denied attempts are listed apart and never count as access. Quoted heredoc bodies are data; unquoted heredocs, indirection and unknown tools are ambiguous. Exits: 0 clean, 1 contaminated, 2 ambiguous, 3 evidence invalid (missing, empty, malformed, non-object), 4 scanner error. A crash can no longer read as contamination. Regressions: scan-tests/summary.txt (16 cases, all as expected).
- Real R49 A-N transcripts: s1 clean; s2 clean with 6 executed calls and 2 denied attempts (A-N-reanalysis.json, labelled reanalysis).
- Launcher copy records the exact argv with the prompt as its sha256; child exit and wrapper status are recorded separately (stub: exit=5, wrapper_rc=0; stub/stub-meta.txt; diff launch/session.sh.diff).

**Proposed for a NEW cohort (not R49 continuation, no pooling)**
- One identical line added to every session-2 task: "Run one shell command per Bash call, and create or change files with the Write tool." It adds no stop/start/restore hint. The words "restart"/"start" already in the R40 task text ("the watchdog would restart the server") are unchanged and identical in all arms.

**Unverified**
- That the model follows the line, and that dontAsk then approves each `./svc` call. The R47 qualification showed a compound `./svc …; ./bench.sh` line approved, and R49 showed a line with `cat` denied. Per-subcommand approval rules are not documented in the installed help.
- Permissions remain auto-approval, not a sandbox.

**Capacity note (corrected).** fleet-spend-stop's daily figure is an advisory pace from this laptop's opencode.db. It is not the provider balance. Provider capacity was last observed on Brian's Go dashboard at 2026-09-25 23:47Z (82% of the $60 month used, resets ~2026-10-14). The overflow ("use available balance") setting is still unconfirmed and owned by Claude. Participant calls use the Max route, not Go.

**One next step.** A single-arm qualification on the new cohort's frozen launcher and task (one save call + one task call, an N arm on a fresh cwd, not a research outcome). It checks that one-command discipline lets restore calls through under dontAsk. Budget: 2 Max calls, operator 15 min, corvid 5 min, Tern 5 min.
