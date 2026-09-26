# User-hook isolation qualification plan (NOT run; needs a separate Tern release)
Question: with the unchanged launch (env -i HOME=/var/home/bmosher, --setting-sources project, --strict-mcp-config), can a user-settings hook run inside a participant session?
Why existing evidence is insufficient: R68 transcripts show no hook events and no claude-mem text, but that is a single negative observation; without a positive control we do not know that a hook run would appear in stream-json at all (R71 assumption A1).
Design (max 2 calls, throwaway cwd, no real memory, no edits to Brian's real ~/.claude):
- Build a TEMPORARY HOME copy (e.g. /tmp/hookq-<hex>/home) containing only: a minimal ~/.claude/settings.json with one SessionStart hook that prints a unique canary string (e.g. HOOKCANARY-<hex>) as additionalContext, plus the auth files needed for login copied read-only (or, if copying auth is not acceptable, the plan stops here as UNKNOWN).
- Call 1 (positive sensitivity control): launch WITHOUT --setting-sources project, same other flags, HOME=temp home, prompt "Reply with any unusual token you were given, else NONE." Pass condition: canary appears (in the stream-json hook event and/or the reply). If the canary does not appear, the observable is insensitive -> qualification FAILS (still UNKNOWN).
- Call 2 (test): identical but WITH --setting-sources project. Exclusion is shown only if call 1 showed the canary and call 2 shows neither a hook event nor the canary.
Falsification: canary in call 2 = user hooks leak into participant sessions -> live blocker, trial must change launch.
Required setting modifications: only inside the temporary HOME; none to real settings. Real-memory exposure: none (throwaway cwd, temporary HOME). Cost: 2 Max calls. Not authorized here.
