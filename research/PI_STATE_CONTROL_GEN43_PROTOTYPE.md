# The first Pi state/control prototype

**Evidence class:** `architecture_prototype_no_score`. This generation establishes that the
separations in `ARCHITECTURE.md` are implementable on the installed Pi and behave as designed on
a fixed synthetic trace. It makes **no** claim about coding-task success, reasoning quality,
token savings under a live model, or tool-churn reduction. Those remain unmeasured.

No model ran. No network, no API, no GPU, no reader, no benchmark corpus.

## Pi identity, and where it actually lives

Pi is installed on the Linux workstation, not on the Mac that holds this repository. The characterization and the extension load test therefore ran there, against the installed package, and their output is committed here.

| field | value |
| --- | --- |
| package | `@mariozechner/pi-coding-agent` |
| version | 0.73.0 (CLI reports 0.73.0) |
| runtime | bun |
| extension events exposed | 29 |

The hooks that matter for this architecture, read from the installed package's own type
definitions rather than from documentation or recollection:

| responsibility | hook |
| --- | --- |
| session start / resume | `session_start (reason: startup|reload|new|resume|fork)` |
| user prompt submission | `input -> {action: continue|transform|handled}` |
| **context transformation** | `context -> {messages?: AgentMessage[]} REPLACES the message array` |
| provider payload | `before_provider_request -> replacement payload (result type is unknown)` |
| system prompt | `before_agent_start -> {systemPrompt?, message?}` |
| compaction | `session_before_compact -> {cancel?} and session_compact` |
| tool pre / post | `tool_call -> {block?, reason?}; tool_result -> {content?, details?, isError?}` |
| stop / completion | `turn_end, agent_end, session_shutdown` |
| persistence | `SessionManager / session entries; session_start carries previousSessionFile` |
| token accounting | `ContextUsage and calculateContextTokens/estimateTokens are exported` |

What is **not** available, stated so a later generation does not assume it:

- no hook replaces the persisted session transcript itself; context replacement is per request
- before_agent_start cannot replace history, only the system prompt and an added message

## H1: a Pi-native extension, with no core patch

The prototype extension was loaded into the installed Pi by Pi's own loader and its handlers were
driven with synthetic events. Nothing was forked, patched or copied out of the package.

| observation | value |
| --- | --- |
| extension loaded | True |
| load errors | 0 |
| handlers registered | before_agent_start, context, input, session_before_compact, session_shutdown, session_start, tool_call, tool_result, turn_end |
| Pi core patched | False |

The decisive one is the `context` hook. Handed a synthetic transcript of
80 messages and 46,031 bytes, the extension returned
1 composed message of 413 bytes. The
transcript was not replayed. That is the mechanism the whole architecture depends on, and it is a
public extension hook rather than something that needs Pi to change.

Compaction was also cancellable from the extension, which matters: history here is externalized,
not destructively compacted. Deleting the past is not how the context stays small.

## The frozen contract

`pi-state-control-v1`, state schema 1, contract sha256
`b022359a2bee52b4f335a0f19c97b6ef00809c8d7f91625d3748e6cbbf59e09e`, frozen before the trace was measured.

Transitions: {"blocked": ["inspect", "plan", "implement", "validate"], "done": [], "implement": ["validate", "plan", "blocked"], "inspect": ["plan", "blocked"], "plan": ["implement", "inspect", "blocked"], "validate": ["done", "implement", "blocked"]}. Entering `done` requires a
`validation_receipt`. State is bounded at 4,096 bytes with
per-field list bounds; overflow is archived to history with a reference rather than dropped.

Patches are transactions: `{base_revision, ops}` with `set` / `append` / `remove` on schema
fields. A phase change is deliberately **not** a patch — control owns that.

## The synthetic trace

59 steps, digest `a1fed1d82cacead5`, invented and unrelated to
every corpus in this repository. It contains repository inspection, a plan revision, two
implementation attempts, a failed validation followed by a fix, a large irrelevant tool output, an
early decision that becomes relevant again after it has been archived out of active state, a check
result superseded by a newer one, an intentionally illegal transition, a stale patch, a malformed
patch, and a restart boundary.

Executing it produced 70 history events and ended in phase
**done** — reached only after a passing receipt existed.

## H2: bounded context, lossless history

| step | history events | history bytes | state bytes | composed context bytes | tool output kept only in history |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 646 | 311 | 705 | 0 |
| 10 | 11 | 9,817 | 544 | 949 | 5,505 |
| 20 | 22 | 14,010 | 828 | 1,239 | 5,505 |
| 30 | 32 | 19,558 | 1,001 | 2,186 | 6,771 |
| 40 | 46 | 31,597 | 973 | 1,379 | 12,259 |
| 59 | 70 | 52,248 | 1,018 | 1,358 | 21,951 |

History grew from 646 to 52,248 bytes, a factor of
81. The composed live context went from
705 to 1,358 bytes and peaked at
3,762. Active state peaked at 1,036 bytes against a
4,096-byte guard. At the end the live context is
2.6% of the history it can still reach.

The peak is worth naming rather than smoothing: context tracks the size of the *latest
observation*, so a single large kept tool result moves it. What it does not track is the length of
the run. That is the property being tested.

21,951 bytes of tool output never entered the live context at
all and remain retrievable by event id.

Patches accepted 25, rejected 2. Transitions
accepted 6, rejected 2. Rejections are
events in the log, not silent no-ops.

## H3: restart recovers from persisted evidence only

At the declared boundary the prototype object was destroyed and rebuilt from `state.json` and
`history.ndjson` alone.

| quantity | before | after |
| --- | --- | --- |
| phase | implement | implement |
| state digest | `915a808f17e061b7` | `915a808f17e061b7` |
| history head | `608d0a68ed1937c6` | `608d0a68ed1937c6` |
| history events | 63 | 63 |
| identical | | **True** |

And the part that makes it more than a serialization test: an early decision that had been
archived out of active state by the list bound was still recoverable from history
(True), was recalled on demand, and did **not** silently
reinstall itself into active state afterwards
(False for "still in active state"). Retrievable
is not the same as always present.

## H4 and H5: fail-closed behaviour

| case | outcome | detail |
| --- | --- | --- |
| artifact mutation invalidates completion | closed | [{"path": "check.json", "kind": "validation_receipt", "valid": false, "reason": "digest  |
| done gate rejects mutated artifact | closed | validation_receipt check.json: digest changed: 8915102749f4 -> a1392851d442 |
| history stuffed into state rejected | closed | active state is 39900 bytes, over the 4096 bound |
| illegal transition from done | closed | illegal transition |
| missing history reference rejected | closed | no history event 'e999999' |
| phase change via patch rejected | closed | phase changes go through the control layer, not a patch |
| restart without persisted state rejected | closed | no persisted state at /private/tmp/pi-state-control-gen43/broken |
| stale revision rejected | closed | stale patch: base 28 != 31 |
| tampered history detected | closed | e000003: content does not match its digest |
| type violation rejected | closed | 'goal' takes str, got int |
| unknown field rejected | closed | unknown field 'not_a_field' |

All 11 cases failed closed. Nothing was
silently repaired. The artifact case is H5: after `done` was legitimately earned, the receipt's
file was edited, and both the artifact status and the completion gate immediately rejected it.
State said the checkpoint was valid; the artifact disagreed; the artifact won.

## What this does not establish

Everything about a real agent. No model produced any of these tokens; the trace is a fixture. The
context numbers are bytes of composed context under this prototype's composer, not tokens under a
pinned model, and there is no comparison against Pi's ordinary context assembly under load — that
needs a live session and is deliberately out of scope here.

H6 stands unmeasured by design: whether this design improves coding-task success, reduces tool
churn or saves tokens is a paired experiment, not a prototype.

Scientific digest `e3d629c5cf7e2219c9554a73a46974a99da58a76d300949f65a9aadd5a2bcf34`, rebuilt with wall-clock, host and install paths excluded.
Contract `src/memory_bakeoff/pi_state_control/contract.py`, sha256 `b022359a2bee52b4f335a0f19c97b6ef00809c8d7f91625d3748e6cbbf59e09e`.
