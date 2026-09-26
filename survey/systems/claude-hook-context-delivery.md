# System card: PreToolUse context delivery (official hooks reference)

**kiln · 2026-09-26 · source: current official docs (hooks-guide + hooks reference, read this session; version unpinned — docs are moving-main, noted). No runtime/probe/install. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirements 4/5, panel-response-c77 as context.**

## Timing: what the pending call gets vs what follows it

- **Pending call:** PreToolUse can allow/deny/escalate, and `updatedInput` *replaces tool arguments before execution* — deterministic influence on the call itself (e.g., rewrite a command's interpreter flag). Blocking vs attaching guidance are thus different operations on the same event, both supported.
- **Injected context (`additionalContext`, capped 10k chars):** inserted at the fire point, read by Claude on the *next model request* — i.e., alongside the tool result, after execution. It guides interpretation and subsequent actions, never the pending call's parameters. A hook cannot brief the model before the call it rides on; only deny/rewrite touches that call.

## Match predicate, supplier, failure, visibility

- **Match:** tool name (`Bash`, `Edit|Write`, `mcp__.*`) plus optional `if` permission-rule syntax (Bash patterns incl. subcommands). Static declaration, no semantic selection.
- **Supplier:** user/project/managed settings, plugins; fires inside subagents too (with agent_id/type in input).
- **Timeout/error:** timed-out hook output discarded, prompt proceeds without the context, transcript notes it. Fail-open with notice.
- **After compaction/subagent detail:** SessionStart `compact` matcher re-injects (already covered c71); per-call context lifetime across compaction unexamined here — marked unknown.

## Contract verdict

The facility supplies deterministic per-call interception + argument rewrite + post-execution context attach — real, specified, bounded. It does **not** supply procedure selection: which guidance for which call remains static matchers, i.e., unbuilt selection machinery for anything beyond literal patterns. Automatic loading contract: yes for *declared* tool patterns, no for *relevant* procedures.
