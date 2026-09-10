# pi-project-recall

Read-only **cross-session recall** over the project's existing
[pi-lcm](https://github.com/mosherbrian/pi-lcm) store. One tool, zero writes,
zero new dependencies.

## The gap this closes

pi-lcm persists every message of every session in a project into one SQLite
store (`~/.pi/agent/lcm/<sha256(cwd)[:16]>.db`) with an FTS5 index — but every
search it exposes (`lcm_grep`, `lcm_expand`, `lcm_describe`) filters to the
**current** `conversation_id`. A new session in the same project starts blind
to all prior sessions, even though they sit in the same database file. This
extension adds exactly one tool, `project_recall`, that runs the same queries
**without** the conversation filter, so a fresh session can find decisions,
rejected approaches, failure explanations and prior work state recorded by
earlier sessions in the same project.

## Install (one line, fully reversible)

Add the absolute path to `packages` in `~/.pi/agent/settings.json` (the same
mechanism that loads pi-lcm):

```json
{ "packages": ["/abs/path/to/extensions/pi-project-recall"] }
```

Remove the line to uninstall. The tool never writes, so there is no store
cleanup to undo. `PI_PROJECT_RECALL=0` disables it at runtime without editing
settings.

## The tool

```
project_recall(query, scope: "messages" | "summaries" | "all", limit?, after?, before?)
```

- Searches `messages` via FTS5 (`messages_fts MATCH`, terms ANDed, quoted so
  FTS operators cannot be injected; LIKE fallback if FTS is unavailable) and
  `summaries` via LIKE — the same search shapes pi-lcm uses, minus the
  conversation filter.
- Every hit carries `conversation_id`, `session_id`, session start and
  timestamp, and the output header warns that older hits may be superseded —
  stale recall is surfaced, not hidden.
- No store, no matches and empty queries all return explicit truthful notices;
  nothing is ever fabricated.

## Properties

- **Read-only**: opens the store with the driver's `readOnly` flag
  (`node:sqlite` preferred — Pi runs under node ≥ 22.13; `bun:sqlite`
  fallback, mirroring pi-lcm's `src/db/driver.ts`). Separate connection; WAL
  permits it alongside pi-lcm's writer.
- **Store location parity**: `LCM_DB_DIR` env, else `lcm.dbDir` in
  `~/.pi/agent/settings.json`, else `~/.pi/agent/lcm` — pi-lcm's precedence,
  with the same `..` rejection guard.
- **No dependencies**: node builtins only; parameters are a plain JSON schema.

## Tests

```bash
bun test extensions/pi-project-recall/                            # unit + controls
node extensions/pi-project-recall/test/node_smoke.ts              # driver smoke under the Pi runtime
```

Controls included: a query matching nothing returns empty without fabricating;
a known message from a *prior* conversation is found; writes through the
tool's connection are rejected; `PI_PROJECT_RECALL=0` disables the tool.
