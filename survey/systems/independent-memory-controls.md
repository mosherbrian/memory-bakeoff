# Independent memory controls: enforcement, index budget, scheduled mining

**kiln · 2026-09-26 · source inspection only: Claude Code hooks guide (read this session), Brian's local MEMORY.md measured read-only (sizes/counts only, no content copied), existing cards (pi-reflect, ReMe, Hindsight). No install/hook edit/job/probe. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs, principles, COVERAGE as context.**

## 1. One enforceable preference: PreToolUse interception (docs-verified)

Hooks are shell commands the client runs at lifecycle points regardless of model choice: PreToolUse fires before a tool call, matchers scope by tool name, exit-2 or deny-JSON blocks, most-restrictive-wins across parallel hooks, stderr returns to Claude as feedback. A checkable preference ("python3→python", i.e. sponsor direction: python rather than python3; "no rm -rf", "kill by PID") encoded as a matcher+script is *interception*, not advice: the action cannot execute as formed even when the actor ignores its memory. Verified-vs-unknown: interception semantics are documented current behavior; Brian's installed hook set was not audited here. Limits (same source): only covered tools fire (Bash-written files need a Stop-hook git scan or FileChanged watch); managed deny lists still apply; prompt/agent hook types reintroduce model fallibility — use command-type checks for enforcement. Pi/local: no equivalent verified (Pi extension API has tools, not documented pre-execution veto — unconfirmed, not absent).

## 2. Mechanical index-load-budget check (measured just now)

Brian's main MEMORY.md: 301 lines, 45,202 bytes. Cap is 200 lines *or* 25KB, whichever first — the byte cap binds at ~line 193, leaving ~108 lines unproven-loadable (measured remainder, not an observed cutoff; lines are not entries — do not equate with the sponsor's 109). Deterministic, re-меasurable in one command, no model involved: `awk`-level check that fails loudly when the index exceeds budget. This is the load-cap guard: it cannot make the model obey, but it converts silent truncation into a visible, countable condition. Unknown: which entries fall past the line on any given host/version (order-dependent), and Pi/local equivalents.

## 3. Independently triggered mining/injection (from existing cards)

- **pi-reflect headless/cron:** scheduled runs, guarded file edits, recidivism metrics — trigger independent of the actor; extraction still LLM-fallible; failures need visible logs.
- **ReMe auto_memory/dream:** transcript→daily→digest pipeline with scheduled triggers; model keys required; consolidation quality unevaluated here.
- **Hindsight hooks/MCP:** auto-recall/auto-retain on session events; server + billing ops; lifecycle unevaluated.
Unavoidable glue for any of them: a scheduler, failure visibility (dead jobs must page, not rot), and a named fallback when extraction misfires. None is recommended; each is specified enough to price.

## If the actor ignores the lesson, what changes

Hook-covered actions: blocked before execution (observable: denial + feedback). Index budget: truncation becomes counted, not silent (observable: line/byte counts). Scheduled mining: extraction starts without the actor (observable: job runs + metrics), but interpretation stays fallible. Residual judgment everywhere else — these controls shrink the diligence surface; they do not certify outcomes.

## Lead qualifications (cycle69, same evidence)

The sponsor example is **python rather than python3**, reversing the arrow above. The local line/byte counts are reported measurements; the cutoff calculated from the stated host limit is not an observed installed-loader trace. Lines and index entries are different units. Treat the exact limit/loaded prefix as a pilot assumption to check, not an established109-entry reproduction. Hook guarantees apply only to covered tool paths/configuration. Configuration plus invoked scripts/dependencies must all appear in the coherent design; no additional script is recommended here. Proposed owners and tests belong in the recommendation—running all tests beforehand is not required to recommend a pilot. [Synthesis](../panel-response-c69.md).
