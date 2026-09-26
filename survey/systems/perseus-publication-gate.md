# System card: Perseus publication gate (missing seam, named)

**kiln · 2026-09-26 · source: perseus-ctx 1.0.26 wheel, `perseus.py` direct call sites (cmd_render ~30521, _enforce_budgets ~33852, cmd_prompt_size ~33900, directive specs ~1397–1431; read-only extraction, no import/run). Lead c78 cards as context. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirement 2 as context.**

## What exists (call-site verified)

- `cmd_render` renders source → adapters → atomic file write. No budget call on this path.
- `_enforce_budgets` is referenced only at its definition and three call sites, all inside `cmd_prompt_size` — an analysis command, never invoked by render, watch, or publish flows.
- External-memory directives (`@mimir` external Mneme server with local fallback, `@memory` local FTS5, `@focus` bounded-32 working set, `@capture` vault writes) expand the final view beyond what prompt-size analyzes; adapters add further content at host-render time.

## The missing seam, exactly

No single command or config path checks the **final host view** (post-adapter, post-memory-expansion rendered bytes) against a strict budget before atomic publication. The pieces all exist — render, analyzer, atomic write — but unwired: the gate lives in a different command from the publication it should guard.

## Smallest coherent extension boundary

Wire `_enforce_budgets` over post-adapter final text inside the render→publish path (or a `publish` command composing render + budget check + atomic write), so one invocation either publishes within budget or fails loudly. That is a small extension to an existing seam, not a wrapper collection — and it stays unbuilt until someone builds it; no such path is claimed.
