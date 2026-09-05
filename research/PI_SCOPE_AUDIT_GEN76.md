# Gen76: the scope ruler works; three of four engines were never asked

Gen75 closed the temporal line with a method rather than a table: **prove a
failure class can fire before reporting its zero, and separate what an engine
cannot do from what the harness never asked it to do.** Gen76 applies that to
scope, before anyone interprets Gen68's scope numbers. No engine was run.

## The ruler is sound

Both scope-related classes were driven through the frozen scorer with synthetic
answers and controls:

| class | fires when violated | control stays clean |
|---|---|---|
| `scope_collapse` | **yes** | **yes** |
| `configuration_collapse` | **yes** | **yes** |

The fixture genuinely contains both kinds of violation — a prohibited
observation in a *different scope*, and one in the *same scope with a different
configuration*. Neither class is structurally silent. That was worth checking:
both sit in an `elif` chain behind several other classes, so a case can satisfy
the condition and still be charged something else.

## But scope was only ever asked of one engine

| adapter | what "scope" is | passed on write | passed on query | verdict |
|---|---|---|---|---|
| **perseus** | `workspace_hash = sha256(scope)` | yes | yes | **measured** |
| mem0 | metadata field; query filters a constant `user_id` | no | no | **not demonstrable** |
| hindsight | `bank_id` per repetition; scope only inside a context string | no | no | **not demonstrable** |
| agentmemory | one agent, one project, for every scope | no | no | **not demonstrable** |

Quoted from the adapters' own contracts: mem0's is *"scored_filter: constant
user_id only"*; agentmemory's is *"never a project or agent per scope"* and
*"smart-search does not isolate by project anyway"*; hindsight's recall arguments
are `bank_id`, `query`, `max_tokens` — no scope term at all.

**Only Perseus is given a scope filter to honour.** For the other three, a scope
violation is not the engine failing to isolate; it is the harness never asking.

## Two true statements, kept apart

For mem0, hindsight and agentmemory:

- **The tested configuration collapses scopes.** True, and worth recording — it
  is what a user of that configuration would experience.
- **The engine's scope capability is `NOT_DEMONSTRABLE`.** Also true. Nothing in
  these runs bears on whether the product can isolate scopes when asked.

Reporting only the first would repeat the Gen73 error exactly: reading an adapter
decision as a fact about the product. Reporting only the second would hide a real
property of what we ran.

## What this qualifies

Gen68 reported scope truth as perseus 6 of 9 clean, the other three 0 of 9. The
gap is now attributable, and mostly not to the engines: **Perseus was the only
one asked.** That row should not be read as a scope-isolation comparison, and any
future comparison needs adapters that actually pass a scope filter on both paths.

Whether to build those adapters is a design decision — it changes the tested
configuration for three engines — and it belongs to the control plane, not to me.

## What this does not establish

Nothing about whether mem0, hindsight or agentmemory *can* isolate scopes. Each
exposes some namespacing concept — a user id, a bank, a project — that the frozen
adapters bind to a constant rather than to the case scope. Whether binding them
per scope is faithful to the product's intended use is exactly the question a new
adapter revision would have to answer, with its own provenance, as Gen74 did for
Perseus.

## Artifacts

- `results/scope_audit_gen76/scope_audit.json` - reachability proofs, controls, per-adapter verdicts
- `src/memory_bakeoff/scope_audit.py` - the isolated/not-exercised distinction and its contract
- `scripts/run_gen76_scope_audit.py` - drives the frozen scorer only; no engine, no re-score
