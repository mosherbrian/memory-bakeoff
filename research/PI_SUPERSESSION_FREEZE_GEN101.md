# Gen101 — Supersession Fixture Repair + Ablation Freeze

**Fixture:** `interference-v3`, superseding `interference-v2` · **Scorer:** unchanged
**Bindings:** `supersession-binding-gen101-v1` · **No engine runs.**

## The repair: one thing changed

Gen100 found that `interference-v2` writes the **current** record first and the
**superseded** record second — backwards from the world it models, where a fact is
stated and a later fact replaces it. AgentMemory's write-time rule retires the
*older* near-duplicate, so on our order it retired the record we meant to keep,
and Gen99 read that as "AgentMemory never finds the current fact in kestrel".

**The rule was right. The fixture was wrong.**

`interference-v3` writes the **superseded record first and the current record
second**. Same four semantic cores, same load levels, same scope and configuration
bindings, same foreign record on both axes, same query, same scorer. **Only the
sequence.** A test asserts the record sets are identical to v2 and the orders are
not.

**v2 is not rewritten.** It is untouched, its hashes stay valid for every
committed Gen99 result, and the defect stays on the record. A test asserts v2
still puts the current record first — the repair carries its own version rather
than editing history.

## Control 1 — the corrected order is visible to the rule

AgentMemory's rule can fire in exactly one core. That core is where the repair has
to show:

| core | Jaccard | rule fires | v2 would retire | **v3 retires** |
|---|---|---|---|---|
| throughput:atlas | 0.250 | no | nothing | nothing |
| branch:vega | 0.667 | no | nothing | nothing |
| **oncall:kestrel** | **0.714** | **yes** | **the current record** | **the superseded record** |
| budget:solstice | 0.300 | no | nothing | nothing |

**In the one core where the product's own mechanism engages, v2 retired the answer
and v3 retires the thing it replaces.** That is the repair, demonstrated against
the product's rule rather than asserted.

## The four minimal bindings

**Three kinds of mechanism, named rather than blurred.** They are not equivalent,
and reporting them as one comparison would manufacture an equivalence the
interfaces do not support.

| engine | kind | binding |
|---|---|---|
| **perseus** | `EXPLICIT_LINEAGE` | `perseus_vault_supersede` — names both records and the relationship; the old entity becomes `deprecated` |
| **hindsight** | `STATE_TRANSITION` | `update_memory(state="invalidated", reason=...)` — the lifecycle state changes, **the text is not replaced** |
| **mem0** | `PRODUCT_DECIDES` | `add(infer=True)` — the engine decides; `infer` flips and nothing else moves |
| **agentmemory** | `PRODUCT_DECIDES` | **unchanged** |

Only Perseus can name the relationship. Hindsight's pinned build accepts exactly
two states, `valid` and `invalidated` — there is no "supersedes" to express, so
this is labelled a state transition and not dressed up as lineage.

**mem0 deliberately does not use `Memory.update`.** It exists, and it would replace
the old record's content — the harness deciding the outcome instead of the engine.
`infer=True` is the engine's own consolidation, which is the honest analogue of
agentmemory's automatic rule.

**AgentMemory's binding is the empty change.** Its mechanism was already exercised
in Round 2 and stays exactly as it was. For that engine the *only* variable Gen101
moves is the fixture's ingest order — which is precisely the point.

## Control 2 — nothing manufactures success by deleting

Every binding leaves the superseded record in the store. `assert_no_deletion`
refuses a binding whose call names a destructive operation, or one that does not
retain the old record, and the freeze drives it with `Memory.delete(memory_id)` to
show it raises. A test feeds it four destructive calls.

Deleting the superseded record would make every engine look perfect and would
measure nothing but our own delete call.

## What this generation does not do

It runs nothing. Both contracts are hashed and frozen before any engine sees
either. Gen102 can now ask the question this was all for: **when each engine is
actually told that one fact supersedes another, does stale interference
disappear?**
