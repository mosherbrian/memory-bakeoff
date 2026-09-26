# R71 isolation evidence (read-only; no calls; no personal content copied)
## Directly observed
O1 ~/.claude/CLAUDE.md (user-level instructions) does NOT exist. /tmp/CLAUDE.md, /CLAUDE.md, /tmp/AGENTS.md, /AGENTS.md, ~/.claude/AGENTS.md do not exist; ~/.claude/rules absent.
O2 /var/home/bmosher/CLAUDE.md exists but is not an ancestor of any participant cwd (/tmp/c4x-<hex>); ancestor discovery from /tmp/c4x-* reaches /tmp and / only.
O3 All 14 R68 transcripts' init events: mcp_servers [], plugins only builtin agents-md + telemetry, skills [], slash_commands [], output_style default, apiKeySource none, memory_paths.auto = the arm's own ~/.claude/projects/-tmp-c4x-<hex>/memory/ only.
O4 User settings (~/.claude/settings.json) enable claude-mem and fakechat plugins and define PreToolUse/SessionStart/UserPromptSubmit/Stop/PreCompact hooks; NONE of those plugins appear in any R68 init event, and no transcript contains any hook-related event or claude-mem text (event types seen: system/init, system/thinking_tokens, assistant, user, rate_limit_event, result).
## Assumptions (not proven)
A1 That stream-json --verbose would emit a system event if a user hook ran (so absence of such events = hooks did not run). Plausible, not verified here.
A2 That the host injects no other user-level content outside what init lists (e.g. undocumented global memory).
## Conclusion
User-level CLAUDE.md exclusion: PROVEN by absence (O1) - nothing to include. Ancestor/project instruction exposure: PROVEN absent for /tmp/c4x cwds (O1, O2). User plugins/MCP: observed excluded (O3, O4). User hooks: probably excluded (O4 + A1) - UNKNOWN until A1 is verified. Real-memory exposure: auto-memory path is per-cwd project (O3); other projects reachable only by tool access, which the scanner flags.
Status: ISOLATION_UNKNOWN_FOR_HOOKS (live blocker). Minimal separate qualification (NOT run): one instrumented stub-free session in a throwaway cwd with a harmless user-settings SessionStart hook that echoes a canary, launched with the unchanged flags; pass if the canary never appears in the transcript or model context. Needs a separate Tern release (1 call) and must not edit Brian's real settings - use a temporary HOME copy only if the release allows; otherwise stays UNKNOWN.
