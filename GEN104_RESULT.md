# Gen104 — AgentMemory Gen102 Path-Integrity Localization

**Scope kept:** AgentMemory only. No broad rerun. No scorer change.

## The result

Gen102's AgentMemory finding was a harness defect, and it is now located
precisely — not by naming a suspect, but by tracing identity end to end.

**The defect is in `observations_for`, and it is about order, not identity.**

```python
# before
visible = set(VISIBLE_IDS(fixture, case))
return [o for o in fixture.observations if o.id in visible]
```

Taking a `set` of the resolver's output and then iterating `fixture.observations`
discards the resolver's sequence entirely. So swapping in `interference-v3` —
whose only purpose is to write the superseded record **before** the current one —
changed *which* records were ingested and never *the order they were written in*.

**Gen102 ran the v2 order throughout while reporting itself as v3.**

The provenance mapping I named in the Gen103 handoff as "the likely area" was
sound. That guess was wrong.

## The trace

The instrumented path, before the fix, at kestrel load 0:

```
wrote C2-CUR   rows=[(C2-CUR, isLatest=True)]
wrote C2-SUP   rows=[(C2-CUR, isLatest=False), (C2-SUP, isLatest=True)]
raw hit -> C2-SUP
```

The current record was written first and the product correctly retired it when
the stale one arrived. After the fix:

```
wrote C2-SUP   rows=[(C2-SUP, isLatest=True)]
wrote C2-CUR   rows=[(C2-SUP, isLatest=False), (C2-CUR, isLatest=True)]
raw hit -> C2-CUR
```

Every hit mapped to a stored identity in both runs. There was never an identity
break. AgentMemory did exactly what Gen103 measured it doing, on the input the
harness actually gave it.

## Blast radius, measured not assumed

| fixture | cases whose ingest order the defect changed |
|---|---|
| `interference-v1` (Gen97) | 0 / 4 |
| `interference-v2` (Gen99) | 0 / 16 |
| `interference-v3` (Gen102) | **16 / 16** |

v1 and v2 resolver order happened to match fixture-construction order, so the
defect could not bite. **Gen97 and Gen99 are untouched. Only Gen102 ran the wrong
order.**

## The corrected AgentMemory arm

| core | cells | current kept | stale co-returned | clean |
|---|---|---|---|---|
| throughput:atlas | 12 | 12 | 12 | 0 |
| branch:vega | 12 | 12 | 12 | 0 |
| oncall:kestrel | 12 | 12 | **0** | **12** |
| budget:solstice | 12 | 12 | 12 | 0 |
| **total** | **48** | **48** | **36** | **12** |

**Retracted:** Gen102 reported the current record absent in kestrel at every
load. It is present in **48 of 48** cells. That was the harness.

**What AgentMemory actually does:** its automatic write-time supersession is
real and it works — in the one core whose wording clears the 0.7 Jaccard
threshold, it retires the stale record and search stops returning it, giving 12
clean cells with no loss of the current record. In the other three cores the
threshold never fires and stale interference persists. The mechanism is
sound and its **reach is lexical**, which is a product property worth stating
plainly rather than a ranking artefact.

Note this arm is unpaired by design: AgentMemory's supersession is automatic, so
an OFF arm is a configuration the product does not offer and the runner refuses
to manufacture one.

## The invariants

Two, both raising rather than reporting:

- **`assert_ingest_order_preserved`** — the records must be *written* in the
  order the resolver returned them. This would have caught Gen102 at the first
  write. The set was right; the sequence was not; nothing checked the sequence.
- **`assert_hits_map_to_live_identity`** — the invariant Gen104 was asked for.
  Every raw search hit must resolve to a stored identity, **and** that identity
  must be live. A hit mapping to nothing is a provenance break; a hit mapping to
  a retired row means search and the store disagree, and either way the run is
  not reporting the engine.

Scorer unchanged, as instructed.

## Exposure that Gen104 does not close

Gen102's **perseus and hindsight** arms ran through the same broken
`observations_for` on the same v3 fixture. Their supersession is an explicit call
naming both records by id, so which record is *current* is not decided by write
order — the conclusions are very likely intact. But their retrieval ranking saw
the wrong ingest order, and I have not measured whether that moves the numbers.

Re-verifying those two arms on the corrected path is the recommended Gen105. I
have **not** done it here, because Gen104 was scoped to AgentMemory with no broad
rerun, and widening scope on my own judgment is how the last three retractions
started.

## Self-correction inside this generation

The first version of `test_observations_for_preserves_resolver_order` used a
substring check that matched the docstring *describing* the defect — the Gen100
mistake, repeated. Replaced with an AST walk.

## State

`1069 tests passing`. HEAD `e140138`.
