# Round 3 — Supersession: the canonical account

This supersedes `research/PI_SUPERSESSION_ABLATION_GEN102.md`, which was computed
from a run whose ingest order was wrong. That report is kept, not deleted, and
carries a pointer here — the same discipline the experiment is measuring.

Evidence: Gen102 arms re-run on the corrected order (Gen104 for AgentMemory,
Gen105 for Perseus and Hindsight), `interference-v3`, frozen Gen96 retrieval,
unchanged scorer, 4 cores × 4 loads × 3 repetitions.

## The result, per mechanism kind, never summed

### Perseus — `EXPLICIT_LINEAGE` — **works completely, at no cost**

Stale co-return removed in **48 of 48 cells**. The current record lost in **0**.
The scorer returns no mechanisms at all: the only clean arm in Round 3. The
current record's rank rises in 41 of 48 cells, which is the stale record leaving
the window — the effect, not a cost.

A trap worth keeping: the supersede tool's *summary* says it relates "a new fact
to an old one" while its *parameter* descriptions say `from_key` is the old
entity. They disagree; the parameters are authoritative and measured behaviour
agrees with them. The inverted run is retained as
`perseus-on-INVERTED-SUPERSEDED.json`, and read the right way it is strong
evidence the mechanism works — it retired exactly the record it was named.

### Hindsight — `STATE_TRANSITION` — **accepted, and recall-identical**

Stale removed in **0 of 48**. Nothing lost either. **Not one of the 48 paired
cells differs between the arms** — same mechanisms, same `target_present`, same
ranks. `update_memory(state="invalidated", reason=...)` returns without error and
recall returns the identical decision at every core, load and repetition.

Whether the state changed in the store is **not established**. What is
established is that recall is unchanged. This is the same shape as Gen70's
`query_timestamp`: two different parameters on the same engine, both accepted,
neither affecting what comes back.

### AgentMemory — `PRODUCT_DECIDES` — **keeps current truth; suppression is lexical**

Unpaired by design: the mechanism is automatic, so an OFF arm is a configuration
the product does not offer.

The current record is retained in **48 of 48 cells**. Stale co-return is removed
in **12 of 48** — all twelve in `oncall:kestrel`, the one core whose wording
clears the product's 0.7 Jaccard threshold, where the write-time rule retires the
stale row and search stops returning it. In the other three cores the threshold
never fires and stale interference persists.

The mechanism is sound; **its reach is lexical**, not semantic.

### Mem0 — `PRODUCT_DECIDES` — **`NOT_AVAILABLE_IN_PINNED_PROFILE`**

`infer=True` routes through mem0's LLM extractor and the pinned profile is
deliberately no-LLM. Supplying an LLM would add a component the profile never
had, moving far more than one variable and making the ON arm incomparable to its
own OFF arm. Measured, not assumed; the runner refuses the arm with that reason.

## What is not concluded

**There is no supersession score.** Explicit lineage, a state transition and a
product decision are three different mechanisms. They are reported separately and
never summed. One engine has a mechanism that works; one has a mechanism with no
effect on recall; one has an automatic mechanism whose reach is lexical; one has
a mechanism unavailable in the tested profile.

Nothing was deleted to produce any of this.

## What was retracted along the way

- **Gen100's explanation** of AgentMemory's kestrel behaviour (retracted Gen102).
- **Gen102's AgentMemory result** — the current record was never lost; that was
  the harness (retracted Gen104).
- **Gen103's named suspect** — the provenance mapping was sound; the defect was
  ingest order (retracted Gen104).

Gen97 and Gen99 are unaffected: their fixtures' resolver order coincided with
construction order, measured 0/4 and 0/16 cases changed.

## Provenance, stated honestly

The Gen104/105 arms were written before the Gen106 evidence contract existed, to
an **unmanifested** legacy directory, and the re-runs **destroyed the
pre-correction cell-level artefacts**. The aggregate comparison is sound —
Gen102's 16/16 and 0/16 are quoted in the committed report and both reproduce
exactly — but no cell-level diff between the old and new runs is recoverable.

Those artefacts are not reconstructed and no manifest is back-dated over them.
From Gen106 every run writes to `results/gen<N>/attempt<M>`, refuses to overwrite
an existing evidence set, and hashes each artefact into a `MANIFEST.json`.
