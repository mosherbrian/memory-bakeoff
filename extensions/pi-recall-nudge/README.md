# pi-recall-nudge

Companion to
[pi-project-recall](../pi-project-recall/): appends the fixed **F2 nudge
sentence** to the first prompt of each session so the recall habit does not
depend on the user remembering to type it. No tools, no writes.

## Why this exists

The RERUN-20260910 evidence chain, in one line each:

- **F1 (null):** with the store verifiably reachable and natural resume
  prompts, the model used `project_recall` **0/8** — spontaneity is not there.
- **F2 (descriptive, both criteria met):** with one fixed nudge sentence
  appended to the prompt, the model used the tool **8/8**, and seeded
  prior-session content surfaced and was used.
- **f3 (exploratory, n=2, suggestive):** with read-path relaxation active,
  the nudged runs flipped the failure-critical case from 0/4 to 2/2.

This extension automates exactly the F2 intervention — same sentence, same
delivery shape (appended to the current user prompt, seen on the model's
first LLM call of the session) — so the prompted half of the habit is
always on when the recall tool is installed.

## What it does

On the session's first LLM call, if all gates pass, the sentence

> Before you edit anything, use the project_recall tool to check this
> project's past sessions for decisions or constraints relevant to the task.

is appended to the current user prompt **for the model's eyes only** — the
`context` event's message list is transformed per request; the session
transcript and the pi-lcm store keep the prompt exactly as typed. Within
that first turn the appended sentence is re-applied on every LLM call so the
model's context stays consistent; later turns are untouched.

Gates (any miss ⇒ quiet skip, logged to stderr with the reason):

- `PI_RECALL_NUDGE=0` — runtime kill switch, no settings edit needed.
- `project_recall` actually registered (never nudge toward a missing tool).
- The project's store exists with ≥ 2 conversations — the live session plus
  at least one prior one. Fresh projects have nothing to recall and stay
  quiet.
- The prompt does not already contain the sentence (no double-appending).
- `project_recall` not already invoked this session.

Receipts, not claims: every application (and every skip) emits one stderr
line and a durable `pi-recall-nudge` session entry via `appendEntry`.

## Install (one line, fully reversible)

Add the absolute path after `pi-project-recall` in `packages` in
`~/.pi/agent/settings.json`:

```json
{ "packages": [
    "/abs/path/to/extensions/pi-project-recall",
    "/abs/path/to/extensions/pi-recall-nudge"
] }
```

Remove the line to uninstall. Nothing is ever written; there is no state to
clean up. Without `pi-project-recall` the extension stays silent.

## Properties

- **No tools, no writes**: only the per-request `context` transform plus
  stderr/session-entry receipts.
- **Read-only store check**: opens the store with `node:sqlite`'s readOnly
  flag (WAL-permitted alongside pi-lcm's writer) to count conversations,
  then closes it. Any error means "do not nudge" — this extension must
  never be the reason a request fails.
- **No dependencies**: node builtins only (Pi 0.84.4 runs under node
  ≥ 22.13; `bun:sqlite` fallback for store parity with the sibling
  extension).

## Tests

```bash
bun test extensions/pi-recall-nudge/                     # unit + gate controls
node extensions/pi-recall-nudge/test/node_smoke.ts       # node:sqlite runtime smoke
```

Controls included: the sentence is the predeclared F2 wording verbatim;
append is idempotent and never mutates message objects; every gate skips
with its reason; mid-turn consistency holds and later turns are untouched;
a 1-conversation (fresh-project) store yields no nudge.
