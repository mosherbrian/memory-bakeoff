<!-- superseded-by: ROUND3_SUPERSESSION_RESULT.md -->
> **SUPERSEDED — DO NOT CITE AS CURRENT.** This report was computed from a run
> whose ingest order was wrong: `set(visible_ids(...))` discarded the
> `interference-v3` chronology, so Gen102 ran the v2 order while reporting
> itself as v3 (located in Gen104). Its AgentMemory result is **retracted**; its
> Perseus and Hindsight conclusions were re-measured in Gen105 and hold.
>
> Canonical account: **`ROUND3_SUPERSESSION_RESULT.md`**.
>
> Kept, not deleted — the same discipline this experiment measures.

# Gen102 — Native Supersession Ablation Run

**Fixture:** `interference-v3` (corrected chronology, frozen Gen101)
**Retrieval:** frozen Gen96 setup, unchanged · **Scorer:** unchanged
4 cores × 4 loads × 3 repetitions per arm.

## The question

Gen99 measured stale-version interference in 192 of 192 observations. Gen100 found
that three of four engines were never asked to express supersession at all.
**When each engine is actually told that one fact supersedes another, does the
stale co-return go away — and does saying so hide the current fact or destroy
useful history?**

## The result, per mechanism kind, never summed

| engine | kind | stale removed | current newly lost |
|---|---|---|---|
| **perseus** | `EXPLICIT_LINEAGE` | **16 of 16** core/load cells | **0** |
| **hindsight** | `STATE_TRANSITION` | **0 of 16** | 0 |
| mem0 | `PRODUCT_DECIDES` | *arm unavailable* | — |
| agentmemory | `PRODUCT_DECIDES` | *single arm; see below* | — |

**Explicit lineage works completely and costs nothing.** With
`perseus_vault_supersede` issued once, the stale record disappears from every
core at every load, the current record is still retrieved everywhere, and the
scorer returns **no mechanisms at all** — clean. That is the first arm in Round 3
to score clean.

**A state transition is accepted and changes nothing.** Hindsight's
`update_memory(state="invalidated", reason=...)` returns without error, and the
invalidated record **still comes back in recall at every core and load**. Nothing
is lost either — it simply has no effect on retrieval. Whether the state actually
changed in the store is not established here; what is established is that recall
is unchanged.

That is the same shape as Gen70, where hindsight's `query_timestamp` was accepted
and ignored. Two different parameters on the same engine, both accepted, both
without effect on what comes back.

## A defect in my own binding, caught by the data

The first Perseus ON arm **lost the current record and kept the stale one** —
exactly backwards. Not an engine failure: my Gen101 binding had `from_key` and
`to_key` inverted.

The tool's **summary** description says it creates a relationship *"from a new fact
to an old one"*. Its **parameter** descriptions say `from_key` is *"the OLD entity
being superseded"* and `to_key` is *"the NEW entity that supersedes"*. **They
disagree, and the parameters are authoritative** — the measured behaviour agrees
with the parameters. Perseus did precisely what it was told and deprecated the
answer.

The inverted run is kept as `perseus-on-INVERTED-SUPERSEDED.json`, and the trap is
recorded in the binding itself. It is also, read the other way, strong evidence
the mechanism works: it retired exactly the record it was named.

## mem0's arm is not available in this profile

`infer=True` routes through mem0's LLM extractor, and the frozen Round-2 profile
is deliberately no-LLM; the call fails against the placeholder key. Supplying an
LLM would add a component the profile never had, moving far more than one variable
and making the ON arm incomparable to its own OFF arm.

Recorded as **`NOT_AVAILABLE_IN_PINNED_PROFILE`**, measured rather than assumed,
and the runner now refuses the arm with that reason. `Memory.update` remains
declined for the Gen101 reason: it would replace the old content, the harness
deciding instead of the engine.

## AgentMemory: the Gen100 explanation is RETRACTED

AgentMemory ran one arm — its automatic mechanism, on the corrected fixture. An
OFF arm would be a configuration the product does not offer.

**It still loses the current record in the kestrel core**, at every load, exactly
as in Gen99.

Gen100 explained that result as the product's recency rule meeting our backwards
ingest order: the current record was written first, so the later near-duplicate
retired it. Gen101 corrected the order and predicted the repair would fix it.
**It did not.**

The two runs together rule that explanation out:

| fixture | order written | retired |
|---|---|---|
| v2 | current, then superseded | **the current record** |
| v3 | superseded, then current | **the current record** |

The record retired is the same one regardless of position, so **position is not
the rule**. My Gen100 account was wrong, and it predicted the v2 outcome by
coincidence rather than by mechanism.

What remains true: the ingest order in v2 *was* backwards and *is* worth
repairing. What is retracted: that the order explained AgentMemory's kestrel
behaviour. The real cause is not established, and I am not proposing a second
guess.

## What is not concluded

**There is no supersession score.** Explicit lineage, a state transition and a
product decision are three different mechanisms; they are reported separately and
never summed. One engine has a mechanism that works, one has a mechanism that does
nothing to recall, one has a mechanism unavailable in the tested profile, and one
has an automatic mechanism whose behaviour on this fixture is still unexplained.

And nothing was deleted to make any of this happen.
