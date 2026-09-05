# Gen92 — Perseus Scored-Read Surface Feasibility

**Contract:** `perseus-scored-read-gen92-v1`
**No benchmark rerun.** MCP tool enumeration on the pinned binary plus a live
shape probe on a scratch database.

## The one question

Gen91 could not say why perseus ranks a superseded record above its replacement:
the committed results carry `canonical_id`, `native_id`, `provenance_exact` and
`rank`, and no score. That left one prerequisite — **does perseus 2.23.2 expose a
read that returns per-hit relevance scores while preserving the Round-2 retrieval
semantics?**

Round 2 used `perseus_vault_recall` with `mode="hybrid"`: fts5 plus dense, fused
by reciprocal rank fusion. A candidate qualifies only if it is that operation and
that mode. **A different search mode does not qualify merely because it exposes
scores** — using one would answer what a *different* strategy ranks and report it
as an explanation of the strategy actually measured.

## What the build offers

173 MCP tools. The read surfaces that matter:

| candidate | same semantics | scored | why |
|---|---|---|---|
| `recall (mode=hybrid)` | **yes** | **no** | 35 per-hit fields, none a relevance score |
| `recall (mode=fused)` | no | yes | TEMPR-style multi-strategy: fts5 + dense + **graph + temporal**, weighted RRF, token-budget truncation |
| `semantic_search` | no | yes | dense-only, "ranked purely by embedding similarity (no keyword fallback)" |
| `recall_batch` | no | — | fuses across a *batch* of queries; the unit of retrieval differs |
| `declared_query` | no | no | explicitly "the no-ranking arm" |
| `retrieval_telemetry` | no | no | aggregate concentration/diversity, not per-hit scores |

**Scored reads exist. Every one of them is a different retrieval strategy.**

## The hybrid response, read from a live call

Not from documentation — two records written to a scratch database and recalled
through the Round-2 path. The response carries **35 fields per hit**:

`agent_id, always_on, archive_reason, archived, assertion_text, body_json,
canonical_record_id, category, certainty, created_at_unix_ms, decay_score,
efficacy_status, encoding_strength, epistemic_state, follow_count, follow_rate,
hints, id, key, last_accessed_unix_ms, layer, links, memory_type, miss_count,
retrieval_count, source, status, tags, topic_path, type, untrusted, verified,
visibility, why_served, workspace_hash`

**Not one of them is a relevance or ranking score.**

Three fields look score-shaped and are not, and the probe shows it rather than
arguing it:

- **`decay_score`** — a lifecycle importance floor. **0.5 for both records**,
  identical.
- **`why_served`** — a governance projection: memory class, promotion state,
  support count, and the fixed string `"matched the recall query"`. **Byte-identical
  for both records.** It explains *that* a record was served, never how it ranked.
- **`retrieval_profile`** — one string, `"shared"`, at the top level. Not per-hit.

## The product refuses the scored trace on the Round-2 mode

`include_selection_decisions` attaches a per-candidate projection with source-arm
ranks and disposition codes — exactly the evidence needed. Its description says
"fused mode only", and rather than take that on trust the call was made:

```
mode="hybrid", include_selection_decisions=true
  -> isError: true
  -> "include_selection_decisions requires mode='fused' and a searchable query"
```

```
mode="fused", include_selection_decisions=true
  -> fused_trace: selection_decisions, fusion, rerank, strategies, truncation
```

**This is a product constraint, not an adapter omission.** The scored trace is not
something Round 2 forgot to ask for; the build declines to attach it to the mode
Round 2 used.

## Verdict

**`OPAQUE`. The perseus share of the LQ11 ranking failures closes as
`NOT_DEMONSTRABLE`.**

There is no path to freeze, so **Gen93 is not unblocked** — a targeted LQ11 rerun
has nothing to run against. Stopping here is the result, not a gap in it.

## The other two mechanisms close as established

Neither needs another experiment.

- **mem0 — `NEAR_TIE`, CLOSED.** No meaningful preference; the pair is separated
  by 1.2% of the distance to the next record in its own list.
- **hindsight — `MEANINGFUL_PREFERENCE`, CLOSED.** A real stale preference,
  localised to the reranker: keyword identical, semantic gap 0.001655, reranker
  gap 0.078265.

Further work on either is warranted only if a later question specifically targets
tie-breaking or reranker quality.

## What this does not say

It does not say perseus ranks badly — that is exactly what cannot be shown. It
does not say the fused or dense modes would rank the same way; they might rank
better or worse, and either result would be about them. And it does not say the
scores do not exist inside the engine: they plainly do, since the fused trace
reports them. It says **this interface does not surface them on the path that was
measured**, and that no honest substitute is available.
