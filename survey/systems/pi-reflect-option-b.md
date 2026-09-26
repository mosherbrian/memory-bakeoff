# System card: pi-reflect as option-B reflector (interface read)

**kiln · 2026-09-26 · source: jo-inc/pi-reflect @ 33a7288 (`extensions/reflect.ts`, `index.ts`; read-only clone, nothing run). Quoting ROLES fit duty. Roadmap inputs, principles, matrix upkeep boundary as context.**

## Trigger/filter interface (current source)

- `transcriptSource: {type: "pi-sessions" | "command"}` plus `transcripts[]` arrays and files/url context sources. A `"command"` source emits the transcript stream from shell stdout — a trained prefilter CLI slots in **with no new wrapper**: config points the source at the classifier command, concatenated with separators, byte-capped.
- Trigger: `schedule: "daily" | "manual"` is a config label; actual firing is manual `/reflect` or headless (`pi -p --no-session`) via external cron/launchd. No internal scheduler — independence comes from cron, not the product.
- Files changed: only the configured `target.path`, plus timestamped backup copies and a history log. Writes are single-file scoped.

## Application/versioning: c14 findings stand

`git add -A` + `commit --no-verify` at the repo root (current lines ~1342–1345): stages unrelated dirty work and bypasses hooks. Unchanged since c14. So the reflector is versioned but not hook-safe; the commit scope exceeds the edit scope.

## Fit verdict: sensible existing reflector with one fenced defect

Supplied config accepts preselected streams; unbuilt integration is nil (a config block, not code). Sensible for option B **iff** the commit path is fenced first (scope the commit to the target file, drop `--no-verify` or document why it stays) — otherwise scheduled reflection periodically sweeps bystander changes past hooks. That fence is a small config/code change proposed, not made. **Medium confidence** (direct functions read; scheduling/trigger semantics from config + docs comments).
