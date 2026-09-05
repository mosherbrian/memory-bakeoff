# Gen80: the first real capability difference on this axis

Gen78 gave every engine its native scope key and every engine isolated perfectly
— a configuration artefact, not a capability difference. Gen79 froze a second,
independent primitive per engine. Gen80 asks the narrower question: **inside one
scope, can two configurations coexist without bleeding into each other?**

One variable moves. The Gen79 configuration binding is layered on the unchanged
Gen78 scope binding; scope identity, ingest policy and every other adapter
behaviour are untouched.

## The result — and this time they differ

One qualifying case (`LQ03`: same scope, expects the C1 observation, prohibits
the C2 one), three repetitions:

| engine | primitive | original Round-2 | configuration-bound |
|---|---|---|---|
| **perseus** | `category` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **mem0** | `agent_id` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **hindsight** | `tags` | 3/3 collapse | **0/3 collapse, 3/3 clean** |
| **agentmemory** | `project` | 3/3 collapse | **3/3 collapse, 0/3 clean** |

Three engines separate configurations inside a scope. **agentmemory does not.**

This is the first axis in the whole Round-2 re-examination where the engines
genuinely differ once the harness is fair to all of them. Every previous
apparent difference — temporal, scope — dissolved into configuration once the
adapters were corrected. This one does not.

## Clean retrieval, reported explicitly

An engine returning nothing also avoids `configuration_collapse`, so passing
required more than an absent flag. Each result records `returned_expected` and
`returned_prohibited` separately, and both are asserted:

- the three isolating engines return `L001` — the C1 observation — and never
  `L003`;
- agentmemory returns `L001, L002, L003, L004` in every repetition. It is not
  failing to retrieve; it is retrieving across the configuration boundary.

## Gen13's prior evidence is confirmed

The frozen agentmemory adapter recorded that *"smart-search does not isolate by
project"*. That note was carried into Gen79 as prior evidence to be **confirmed
or overturned, not baked into expectations** — and deliberately so, because the
structurally identical caveat carried into Gen77 was **overturned** by Gen78,
where `agentId` isolated perfectly.

So the same class of caveat has now been wrong once and right once. That is
precisely why it is treated as evidence rather than assumption: the note was
about a specific parameter, and only running it distinguishes a real limitation
from a stale one.

## What this does and does not say

It says that on this fixture, with these bindings, agentmemory's `project` does
not separate configurations within an agent, while perseus's `category`, mem0's
`agent_id` and hindsight's `tags` do.

It does not say agentmemory cannot isolate configurations at all — only that its
`project` parameter, the one candidate its API exposes alongside the agent used
for scope, does not. Whether another arrangement would work is a different
question, and not one this generation asked.

Scope is unchanged throughout: one case, three repetitions, four named builds,
one fixture.

## Artifacts

- `results/configuration_isolation_gen80/{perseus,mem0,hindsight,agentmemory}.json`
- `scripts/run_gen80_configuration_isolation.py` - perseus, mem0, agentmemory
- `scripts/run_gen80_hindsight.sh`, `scripts/gen80_hindsight_repetition.py`
- `tests/test_configuration_isolation_gen80.py` - 23 checks, including that the failure stays visible
