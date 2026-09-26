# R46 readiness — restart memory on Claude Code (Brian's Max login)

**Status: DESIGN_ACCEPTABLE (proposed, for review) · HOST_CAPABILITY_OBSERVED: yes · EXECUTION_READY: no.**

**Route (evidence/auth-status-redacted.json).** `claude auth status` under `env -i`: loggedIn, authMethod claude.ai, apiProvider firstParty, subscriptionType max; no ANTHROPIC_* variables in the launch env, so there is no API-key fallback. Nothing in Brian's settings or credentials was changed.

**F1 correction.** The R45 claim that `cat`/`less` is refused is withdrawn. Tool permissions are not an isolation proof. The effective permission behaviour is what the init event shows (acceptEdits in session 1; dontAsk and Read-only in session 2). scan.py inspects Read paths, Bash command text, every tool input string and tool results for transcripts, history.jsonl, other project slugs, other arm paths, operator/config/credential files; interpreter or indirect Bash is AMBIGUOUS -> attribution unavailable, raw outcome kept. Demo without models (scan-demo/): clean 0; transcript read 1; other slug 1; `cat history.jsonl` 1; `python -c` 2. Same-user obfuscation remains a limit.

**Exit capture.** Both launch scripts drop `set -e` and record `exit=<rc>`; stub claude returning 7 was recorded as exit=7 (stub/).

**Frozen for the smoke.** Model `claude-sonnet-5` (init event confirms); flags `--setting-sources project --strict-mcp-config --disable-slash-commands`; tools and modes above; prompts evidence/prompt-session{1,2}.txt; cwd /tmp/campaign4-r46-smoke-f7iP (fresh, unique).

**Smoke (2 calls, both exit 0).**
- Session 1 `147b313a…`: Write of memory/preferred-test-phrase.md and a MEMORY.md index line; memory_paths.auto = this cwd's slug only.
- Boundary: memory hashes unchanged before session 2 (survived); new id `4efd7f5d…`, no resume/continue.
- Session 2: **zero tool calls**; answered "From my memory notes… amber-otter-42". So the fact arrived through the **host-injected MEMORY.md index**, whose line itself carries the fact, not through a detail read. scan.py: clean.
- Inherited context: init lists only built-in plugins (agents-md, telemetry), mcp_servers [], skills [], no hook events; no claude-mem, escalation or re-grounding hooks ran.

**What this shows / does not.** Shows: auto-memory stays active under `--setting-sources project`; saved memory survives a real restart and reaches a fresh session through index injection on the existing Max route. Does not show: work benefit (neutral fact), leak-free delivery in general, or behaviour with Bash enabled.

**Implication for R44/R45 design.** Index lines can carry the rule, so "index_delivered" is the main delivery channel and detail_read is secondary; the save prompt/index wording is part of the treatment and must be frozen per arm.

**Next step (one).** Freeze the nine-arm execution contract on this route: R40/R42 tasks in fresh per-arm cwds, session-2 Bash limited as in R45 plus scan.py; honest_report retained with measured/restored. Estimate: prep 20 min + review 10 + Tern 5; execution 9 x (2 Max calls, ~12 min) + corvid 9 x 5 + final 10.
