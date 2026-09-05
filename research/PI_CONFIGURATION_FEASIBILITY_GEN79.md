# Gen79: all four engines can separate configurations without reusing the scope key

Gen78 showed every engine isolates scopes once given its own scope key. The
remaining question is narrower and harder: can a system separate **two
configurations inside the same scope**? No engine was run.

## The constraint that shapes the answer

The scope key may not be repurposed. Reusing it would make two configurations
look like two scopes, and the resulting "isolation" would be relabelling rather
than a capability. So each engine needs a **second, independent** primitive,
present on both write and retrieval, that leaves the scope coordinate untouched.

That is asserted in a test for every engine, not just described.

## What the pinned builds expose

| engine | configuration primitive | write | query | scope key (untouched) |
|---|---|---|---|---|
| **perseus** 2.23.2 | `category` | `write_gate {category}` | `recall {category}` | `workspace_hash` |
| **mem0** 2.0.19 | `agent_id` | `add(agent_id=…)` | `search(filters={"agent_id": …})` | `user_id` |
| **hindsight** 0.9.2 | `tags` | `retain(tags=[…])` | `recall(tags=[…], tags_match="all")` | `bank_id` |
| **agentmemory** 0.9.29 | `project` | `/remember {project}` | `/smart-search {project}` | `agentId` |

Read from the surfaces themselves:

- Perseus's MCP write gate takes `body_json, category, key, workspace_hash`, and
  `perseus_vault_recall` takes `category` alongside `workspace_hash` — two
  genuinely independent axes on both paths. The frozen Gen29 adapter pins
  `category` to a constant, so binding it per configuration changes exactly one
  thing.
- mem0's `_build_filters_and_metadata` treats `user_id`, `agent_id` and `run_id`
  as independent session identifiers, written to metadata and accepted as query
  filters. Gen78 took `user_id`; `agent_id` is free.
- hindsight's `tags` are independent of `bank_id`, and `recall` offers
  `tags_match` for exact-set semantics.

**No engine needed `NO_USABLE_CONFIGURATION_SURFACE`** — again a real possible
outcome, again it did not arise.

## The caveat that is load-bearing

Gen13 measured that agentmemory's `smart-search` **does not isolate by
`project`**. That is a behaviour finding about a surface that exists, not an
absent surface — exactly the shape of the caveat carried into Gen77, which Gen78
then showed was wrong about the product.

So `project` is recorded feasible, with the caveat attached to the binding
itself. Feasibility asks whether the question can be posed symmetrically;
whether the answer is isolation belongs to the run. **Recording it feasible is
not a prediction**, and this is now the second time that distinction has mattered
in three generations.

## Proved before any run — 25 tests

- two configurations yield **distinct write and query coordinates**, every
  engine;
- **no binding touches the scope primitive** — the hard constraint, checked
  directly;
- the configuration primitive **differs from** that engine's Gen78 scope
  primitive, and each engine's recorded `scope_primitive` matches the Gen78
  binding, so independence is verified against the other module rather than
  asserted in prose;
- a configuration token can never collide with a scope token — different hash
  namespaces;
- the same configuration is stable across calls, and write and query carry the
  same token;
- tokens are hashed, carrying no fixture wording into a store that might match
  textually.

## What this does not establish

Nothing about whether any engine separates configurations. Gen78's scope
bindings are untouched, and `configuration_collapse` remains unmeasured under
any binding. The question can now be asked of all four without manufacturing
symmetry — which is what the run needs.

## Artifacts

- `src/memory_bakeoff/providers/configuration_bound.py` - the four bindings and the hard constraint
- `tests/test_configuration_bound.py` - 25 proofs, including scope-independence
