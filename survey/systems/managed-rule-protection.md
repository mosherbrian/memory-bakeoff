# System card: managed policy + sandbox locks (Claude official docs)

**kiln · 2026-09-26 · source: current official docs (managed-settings, settings precedence; read this session). No install/probe. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirement 3 (edit protection, not labels; local checks not necessarily bypass-proof) as context.**

## The guarantee, exactly as documented

- **Precedence:** managed sources (server/MDM-or-HKLM/file, ranked) beat user/project/local/`--settings` unconditionally, apart from narrow stricter-lower exceptions. Locks (`allowManagedHooksOnly`, MCP/server allowlists, `disableBypassPermissionsMode`, sandbox locks) take the strictest value; several fail *closed* when invalid (empty allowlists until fixed).
- **Sandbox boundary:** network/filesystem allowlist locks read from every admin source; sandboxed runs constrain files/network/commands per policy. MCP/agent surfaces (Cowork, SDK) inherit or narrow the policy; managed settings bind Claude Code only, not other tools.
- **Invalid config:** unparseable managed file → refuse to start (fail-closed); invalid entries dropped with warnings via `/status`/`doctor`. Opposite of cc-safety-net's degrade-and-continue.
- **Verification surfaces:** `/status` setting-sources line, `claude doctor`, startup dialogs — enforcement inspectable without trusting the agent.

## Deployment assumptions (all load-bearing)

1. A managed source actually deployed (MDM profile, HKLM, root-owned file, or server-managed) — absent file is not a failure, sessions just run unmanaged.
2. The agent runs **unprivileged**: docs state a local admin can edit the managed source itself (MDM redeploy-on-schedule is the mitigation). Brian-as-admin on his own box weakens root-ownership to a speed bump unless MDM/server-managed reasserts (server polls hourly; cache edits die at next fetch).
3. Same-user file writes outside managed paths remain the agent's (user/project settings editable — but they cannot override managed keys).
4. Parent-directory replacement, shell escape to unmanaged tools, and credential misuse are outside this mechanism's scope — sandbox + locks cover declared paths, not the universe.

## Scope verdict

Within explicit scope — managed deny/hook/MCP locks on Claude Code surfaces, deployed source, unprivileged agent — the documented guarantee is complete: user, project, and agent-side edits cannot lift it. Outside that scope (admin agent, other tools, undeclared paths), unknown — not covered, not claimed.


## Tern cycle78 sponsor recheck

[Official managed-settings docs](https://code.claude.com/docs/en/managed-settings), re-read26September, confirm protected system/admin sources and precedence over lower settings. Requirement3 is **already yes in the dedicated managed-policy row**, not unknown. That does not protect separately referenced handlers automatically. Brian having admin rights does not mean the acting process has elevation; assess the process's effective permissions. Scheduled redeployment is recovery, not continuous protection. No installed policy, permissions or bypass test was performed; the broad ordinary-memory row retains its distinct scope.
