# Gen100 — Native Supersession Feasibility Audit

**Contract:** `supersession-surface-gen100-v1`
**No engine runs.** Surfaces read from the pinned builds and the frozen adapter
contracts; agentmemory's rule reimplemented and applied to the fixture text.

## The question before the conclusion

Gen99 measured stale-version interference in **192 of 192** observations. Calling
that a ranking defect requires one prior answer: **was any engine ever told that
one observation supersedes another?**

Round 2 spent five generations discovering that three adapters were never given a
scope to honour. The same shape was available here — and it is what the audit
found.

## Every engine has a mechanism. Three were never called.

| engine | mechanism | status |
|---|---|---|
| **perseus** | `perseus_vault_supersede` | **SURFACE_PRESENT_BUT_UNUSED** |
| **mem0** | `Memory.update` / `delete`, and `add(infer=True)` consolidation | **SURFACE_PRESENT_BUT_UNUSED** |
| **hindsight** | `update_memory`, `clear_memory_observations`, `update_document`, curate | **SURFACE_PRESENT_BUT_UNUSED** |
| **agentmemory** | write-time supersession during `remember` | **ALREADY_EXERCISED** |

**No engine lacks a surface.** `NO_USABLE_SUPERSESSION_SURFACE` does not occur.

**Only Perseus names the relationship explicitly.** Its tool takes `from_key`,
`to_key` and `relationship` and *"create[s] a 'supersedes' relationship from a new
fact to an old one, setting the old entity's status to 'deprecated'"*. The others
express replacement or removal, not lineage.

And in each of the three unused cases the frozen contract says so in its own
words: perseus's write path is *"documented operator CLI write (**no**
supersede/update/delete/maintenance)"*; mem0's is *"lifecycle_calls: none"* with
`infer=False`; hindsight's is *"no curate, invalidate, revert, update or delete
call is issued"*.

**So for three of four engines the 192/192 stale co-return is not yet a ranking
defect. It is a question that was never asked.**

## The exception, and what it explains

AgentMemory's mechanism **was** enabled, so its stale co-return is a real product
observation. Its rule is lexical: Jaccard over whitespace tokens longer than two
characters, threshold **0.7**, one predecessor per write, **the new write retires
the old near-duplicate**.

Reimplemented and applied to the four cores:

| core | Jaccard | rule can fire |
|---|---|---|
| throughput:atlas | 0.250 | no |
| branch:vega | 0.667 | no |
| **oncall:kestrel** | **0.714** | **yes** |
| budget:solstice | 0.300 | no |

**It can fire in exactly one core — and that is the core where Gen99 found
AgentMemory unable to retrieve the current fact at all, at zero distractors.**

The mechanism is the explanation. The fixture writes the **current** record
first and the **superseded** record second. In kestrel the second write is a
near-duplicate above threshold, so the product retired the **current** one —
correct behaviour under its own recency rule.

**This is both a product rule and a harness defect, and neither excuses the
other.** The rule is real and last-write-wins. The ingest order is ours, and it is
**backwards from the world it models**, where the superseded fact is written first
and the current one arrives later. Gen99's finding — "AgentMemory never finds the
current fact in kestrel" — stands as an observation and is now explained; it is
not evidence that AgentMemory cannot retrieve, and it should not be read that way.

## What was not done

**Supersession is never manufactured by deleting old records in the harness.**
Deleting the superseded record would make every engine look perfect and would
measure nothing but our own delete call. Verified structurally rather than by
banning a word: an AST walk asserts that neither the module nor the runner imports
any engine client, so nothing here can call anything.

That check replaced a substring ban that flagged the audit's own *descriptions* of
the surfaces it catalogues — the same over-broad shape as the Gen99 pooling guard,
caught the same way.

## What follows

A genuine native mechanism exists on all four. The minimal binding for each is
recorded here and can be frozen as a **configuration ablation** — one variable
moved, the Gen78/Gen80 pattern — before any claim is made about supersession
behaviour. The fixture's ingest order needs correcting first, or the ablation will
measure the same backwards ordering with a supersession call layered on top.
