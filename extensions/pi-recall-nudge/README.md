# pi-recall-nudge

Companion to [pi-project-recall](../pi-project-recall/): automatically
delivers the tested recall nudge so Brian's personal trial (planner
recommendation: 5 session resumptions, same short nudge) needs no manual
coaxing. No tools, no store access, no writes — it only injects a visible
message on prompts its gates select.

## What it injects

By default, the exact F2 sentence (byte-for-byte, the wording F2/f3 tested):

> Before you edit anything, use the project_recall tool to check this
> project's past sessions for decisions or constraints relevant to the task.

delivered as a persistent, displayed session message —
`[recall-nudge] <sentence>` — so every firing is visible in the UI and
logged in the session file for the trial record. Message injection (not
system-prompt) is the default because it matches what F2/f3 actually
tested: the nudge riding in the message stream. A durable
`pi-recall-nudge` session entry (`appendEntry`) records each firing with
its gates and timestamp.

## Gates (union, deduped — at most ONE nudge per prompt)

| Gate | Default | Fires on |
|---|---|---|
| `onResume` | `true` | the first prompt after a `session_start` with reason `resume` or `fork` |
| `everyPrompt` | `false` | every prompt |
| `everyNPrompts` | `0` (off) | every Nth prompt, N ≥ 1 |

Overlapping gates never double-nudge: a prompt matching several gates gets
one message, and the receipt names every gate that fired. The resumption
window is the *first* prompt after resume/fork and is consumed even if that
prompt is skipped (kill switch, absent tool) — it does not slide to the
next prompt.

**Counter caveat (documented per dispatch):** the `everyNPrompts` counter
is in-memory and resets per Pi process. A console Pi lives minutes; a deck
worker's `pi --mode rpc` process can live for days — which is exactly why
the gate exists — but restart the worker and the count starts over.

**Tool guard:** a nudge is injected only when `project_recall` is active
this turn (the turn's `selectedTools`, falling back to registered tools);
otherwise the extension skips silently — a nudge toward a nonexistent tool
is noise.

## Config (`recallNudge` key in the agent `settings.json`)

```json
{
  "recallNudge": {
    "enabled": true,
    "nudge": "Before you edit anything, use the project_recall tool to check this project's past sessions for decisions or constraints relevant to the task.",
    "onResume": true,
    "everyPrompt": false,
    "everyNPrompts": 0,
    "delivery": "message"
  }
}
```

- `delivery`: `"message"` (default, required mode) — the visible session
  message; `"systemPrompt"` — that message **plus** the sentence appended
  to the system prompt.
- `PI_RECALL_NUDGE=0` in the environment overrides everything (mirrors
  `PI_PROJECT_RECALL=0`).
- Nonsensical values (wrong types, negative/fractional N, unknown keys) are
  rejected **loudly** at load: an explicit notice names the key and the
  default that took its place.

### The two real trial regimes

Console, resume-only (the default config — install and forget):

```json
{ "recallNudge": { "onResume": true } }
```

agent-deck long-lived worker — nudge every 4th prompt because the worker
process survives for days and `resume` only fires on respawns:

```json
{ "recallNudge": { "onResume": true, "everyNPrompts": 4 } }
```

## Install / uninstall (one line, fully reversible)

Add the absolute path to `packages` in the agent `settings.json` (the same
mechanism pi-lcm uses; `pi-project-recall/` itself stays untouched):

```json
{ "packages": ["/abs/path/to/extensions/pi-recall-nudge"] }
```

Remove the line to uninstall. Without `project_recall` registered the
extension stays silent.

## Tests

```bash
bun test extensions/pi-recall-nudge/                # 22 unit tests
node extensions/pi-recall-nudge/test/node_smoke.ts  # node-runtime smoke
```

Controls included: the sentence is the F2 wording byte-for-byte;
resume-only, everyPrompt and every-N gating (including the per-process
counter reset), union dedupe, tool-absent skip, env kill switch, loud
config rejection with defaults holding, and the required delivery shape
(`customType: "recall-nudge"`, `[recall-nudge] ` prefix, `display: true`).
