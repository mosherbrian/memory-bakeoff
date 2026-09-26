# Cycle74 — concrete loading, incomplete protection

Tern ·26 September2026 ·All three reports incorporated; cycle complete. No installation or probe.

**Corvid: accept the deterministic loading mechanism; split the claimed coverage.** Root instruction delivery and path-triggered procedure loading are different contracts. Add a narrowly named project-root/main-conversation loader with requirement4=yes on documented startup and compaction delivery. Keep the broader native-memory row partial. Add a rules component with requirement5=partial: reading a matching file triggers the loader mechanically, but the actor still chooses whether to read; actions without that event are not covered. This is a useful removal of explicit rule selection, not universal applicability.

The source also corrects two details: brace-expansion budget overflow does not invalidate every pattern in a rule; and most subagents load project instructions, with Explore/Plan and configured exceptions. Main auto-memory exclusion is distinct. Preserve enabled-source, file-size and host boundaries in the linked card; no guarantee of obedience follows from delivery.

**Exact cell changes so far:**
- Claude Code instructions and auto memory ×2: no→partial (documented post-write overflow error, write still succeeds).
- New Claude project-root loader ×4: yes, enabled main-conversation scope, startup and compaction.
- New Claude unscoped/path rules ×4 and ×5: partial, source/event and read-trigger limits.
- Letta ×2 stays partial: commit rejection verified, universal writer/merge/compile coverage not established.
- cc-safety-net ×3 stays partial: optional configuration-path protection identified; self-protection and disabling paths remain incomplete.

**Action implication:** explicit persistent directions have an existing deterministic main-session carrier, distinct from the auto-memory index. The proposed guard still addresses checkable behavior. No configuration migration or new loading framework is authorized by this source result.

Sources: [Corvid](opinions/corvid-c74.md), [lead source reconciliation](systems/claude-deterministic-rule-loading.md), [auto-memory bound](systems/claude-memory-load-bounds.md).

**Kiln:** accept optional-off configuration-path protection as a real mechanism and keep requirement3 partial. Source-identified remove/override/uninstall paths are bypass candidates, not successful adversarial tests. “Same UID = same authority” is too broad: a sandbox or external policy controller can constrain processes sharing a UID. Root-owned files are one candidate boundary, not the only possible one; parent-directory replacement, elevated credentials, executable/config paths and disabling the guard still matter. Managed-settings precedence alone is not filesystem write protection. No installed-use result was established. [Protection card](systems/rulebook-protection.md).

**Cairn:** accept actual pre-commit rejection, stronger than /doctor warnings. Lead read of [memory-git-hooks.ts](https://github.com/letta-ai/letta-code/blob/main/src/agent/memory-git-hooks.ts) confirms staged-content validation and error exit under the configured layout. Reject the categorical conclusion that no ordinary/background oversized change reaches active context: the note itself says not every writer was traced, and it cites no compile call site proving committed-only consumption. Hooked commits are one path; merges/fast-forwards and alternate Git writes need their own boundary. Keep Letta2 partial, with the concrete rejection fact replacing the vague qualifier. Recipient character-versus-token limits remain distinct from bypass coverage. [Reader trace](reading/c74-letta-budget-enforcement.md).

**Next, chosen from matrix gaps:** cycle75 examines an operator-owned policy boundary (3), Letta's commit/merge-to-context path (2), and deterministic subagent skill preloading (5). These are bounded source questions, not rollout gates; guard pilot and optional Letta recommendation remain opinionated and unchanged.
