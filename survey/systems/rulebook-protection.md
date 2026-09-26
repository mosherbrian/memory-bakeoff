# System card: rulebook/config protection boundaries

**kiln · 2026-09-26 · sources: cc-safety-net source (secret.ts CLI-config rules, secret-protection.ts gating, policy/ dir) + custom-rules/installation docs; Claude managed-settings docs (prior c2 read). Read-only clone, no install/probe. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirement 3 (edit protection, not labels; local checks not necessarily bypass-proof) as context.**

## cc-safety-net: config-edit protection exists, off by default, bypassable same-user

- **Mechanism (source-verified):** `SECRET_CODING_CLI_RULES` include config paths (`~/.claude/settings.json`, project `.claude/settings.local.json`, `.mcp.json`, codex/copilot/gemini equivalents), gated per-rule by `isSecretRuleEnabled`. When enabled, agent Read/Edit/Write/search access to those paths is denied like any secret path.
- **Default (docs-verified):** blocking the CLI's own settings is *optional, off until turned on*. Default posture protects credentials, not configuration.
- **Bypass paths (same-user assumption):** the guarded agent with shell/config access can `rule remove` sources, set overrides `"off"`, toggle via GUI, edit rulebooks directly, or uninstall the hook — the guard checks commands, not its own config writes (no self-protection rule found; allow-paths even exclude the guard root from secreting itself away, which is about allowlisting, not edit-blocking). Nothing in the inspected code distinguishes operator edits from agent edits: same UID = same authority.
- **Operator-owned policy (the actual boundary):** Claude enterprise managed settings (root-owned paths) cannot be excluded or overridden by user/project settings (docs-verified). OS file ownership is what keeps the acting agent from editing its own rules — available to Brian only via admin/root-owned policy files, not via any in-agent mechanism. Installed/used state on Brian's hosts: unknown.

## Proposed matrix cell changes (requirement 3)

- **cc-safety-net rulebook:** stays **partial**, qualifier rewritten: veto rules active + CLI-config edit protection exists but optional-off; same-user bypass paths (remove/override/uninstall/edit) unverified-closed. Not a promotion: the bypass defeats the protection under the standard deployment.
- **No yes anywhere on requirement 3** from inspected sources: no component is bypass-proof for a same-user acting agent; the only full boundary found is OS-owned managed policy, whose installed use is unknown. Do not manufacture yes by dropping the same-user condition.
