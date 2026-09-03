# agentmemory Gen33 — longitudinal-v1 with native retirement enabled

## Status

`complete_raw_product_longitudinal_native_retirement_activated`.

Three fresh repetitions of agentmemory 0.9.29 in its exact Round-1 raw identity
against the frozen `longitudinal-v1` ruler, with the product's **own write-time
supersession left enabled**. This is the fourth Round-2 contestant and the first
that retires anything. No reader, no LLM, no GPU.

## Identity

Upstream `rohitg00/agentmemory` `e04ba88819c365c9acf9d6661ea802143e728bd6`,
package 0.9.29; native `/agentmemory/remember` and `/agentmemory/smart-search`;
local q8 `Xenova/all-MiniLM-L6-v2` 384-D via `@huggingface/transformers` 4.2.0;
native cosine + BM25 RRF (k=60, vector 0.6 / BM25 0.4, 5% stream-agreement
bonus, at most three per session), top-k 5. LLM extractor, consolidation, graph
extraction, auto-compression and learned reranking all disabled, with every API
key blanked in the service environment so "no LLM" is enforced rather than
configured. Fresh iii data directory and a distinct `agentId` per repetition,
one project namespace, never a project or agent per scope.

Ruler unchanged: fixture `a5c67e7b…`, scorer `1dd831e8…`. Adapter
`agentmemory-longitudinal-adapter-v1`, contract `a06482525d718dd…`, frozen
before the first scored query.

Unlike Hindsight and Mem0, agentmemory's pinned model lives inside the repository
checkout rather than a temp directory, so it is not exposed to the cleanup hazard
recorded in Gen31 and Gen32.

## The retirement rule, pinned and measured

From `src/functions/remember.ts` and `src/state/schema.ts`:

- similarity is **strict lexical Jaccard**, not embedding distance;
- tokens are whitespace-split, **length > 2**, case- and punctuation-sensitive;
- supersede when similarity **> 0.7**, against `isLatest` candidates only;
- **one predecessor per write** — `supersededId` is a single value;
- never across an explicit project boundary;
- the retired row keeps `isLatest = false`, **stays in KV**, and is removed from
  the search index. Absence from search is therefore not deletion, and the
  report treats it accordingly.

Validated live on an unrelated synthetic domain before any scored exposure: two
sentences differing only in `55` versus `62` superseded, because both are
two-character tokens the tokenizer discards. The retired row remained addressable
in KV and vanished from search, exactly as the source claims.

## Treatment activation

The generation required activation to be measured, not inferred. It was, per
ingestion step, with predecessor and successor identifiers:

| step | predecessor | successor | classification |
|---|---|---|---|
| 3 | L001 | L003 | **false supersession** |
| 4 | L002 | L004 | legitimate supersession |

Identical in all three repetitions. Predicted before running: an offline replica
of the tokenizer scored `L001/L003` and `L002/L004` at Jaccard **1.000** — the
only fixture pairs above 0.7 — because `C1`/`C2` and `21`/`29` are all
two-character tokens that are thrown away. Every other pair scored 0.600 or less.

The two firings are the same rule reaching opposite outcomes. "Forge selected C1
as active" genuinely is superseded by the C2 selection. "Nimbus Forge C1 measured
21 t/s" is **concurrent** with the C2 measurement, not superseded by it. The rule
cannot tell those apart, because at token level they are the same sentence.

By CP04 the store holds two retired rows permanently, so 14 of 16 observations
remain searchable for the rest of the run.

## Results

Three repetitions, identical totals, provenance exact on every returned item.

| Failure class | Per repetition | Three repetitions |
|---|---|---|
| `stale_persistence` | 4 | 12 |
| `false_persistence` | 2 | 6 |
| `history_erasure` | 2 | 6 |
| `scope_collapse` | 2 | 6 |
| `belief_truth_confusion` | 2 | 6 |
| `missing_required_truth` | 2 | 6 |
| `unsupported_evidence` | 2 | 6 |
| `configuration_collapse` | 1 | 3 |
| `correction_failure` | 1 | 3 |
| `failed_procedure_adoption` | 1 | 3 |
| `late_history_corruption` | 1 | 3 |

Lifecycle, scored separately by `score_lifecycle_state`: **`false_supersession`
1 per repetition, 3 across the run.** That number agrees exactly with the
harness's independent classification of the product's own retirements — two
measurements taken different ways, reaching the same answer.

## The four-engine picture

| | Perseus | Hindsight | Mem0 | agentmemory |
|---|---|---|---|---|
| retires? | no | no | no | **yes** |
| `configuration_collapse` | 6 | 6 | 6 | **3** |
| `false_persistence` | 9 | 9 | 9 | **6** |
| `stale_persistence` | 12 | 12 | 15 | 12 |
| `correction_failure` | 12 | 0 | 0 | 3 |
| `history_erasure` | 9 | 0 | 0 | 6 |
| `scope_collapse` | 0 | 6 | 6 | 6 |
| `false_supersession` (lifecycle) | 0 | 0 | 0 | **3** |

Retirement **halves configuration collapse and reduces false persistence**. It
leaves stale persistence essentially unchanged. And it introduces a failure class
no append-only engine exhibits: falsely retiring a record that was still true.

`history_erasure` and `correction_failure` are shared with Perseus but absent
from Hindsight and Mem0 — reached by two unrelated mechanisms, Perseus by
collapsing its time axis and agentmemory by removing rows from the index. They
are not "introduced by retirement" in any causal sense and are not reported as
such.

## What this establishes

Neither architecture is safe. Append everything and the store cannot say which
statement is current; retire on similarity and it deletes things that were true.
The same blind lexical rule produced one correct retirement and one wrong one
from an identical score of 1.000.

This is a contrast **across products**, not a controlled experiment within one.
agentmemory differs from the append-only three in storage, retrieval, embedding
and service architecture as well as in retirement, so the trade is attributable
to the architecture as a whole rather than to the retirement mechanism alone.

## A methodological correction

While completing this generation, its own test caught a reporting fault in Gen31.
Three queries in the Gen31 lifecycle collector were failing silently — a
`document_id` column read from the wrong table, a `state` column that does not
exist, and a helper that returned an empty string on a failed query rather than
raising. The result was a lifecycle stream that reported every record inactive
and every invalidation count as zero. Published Gen31 lifecycle numbers were
therefore fabricated, and the "false supersession 0" claim reached the earlier
reports from the case-level stream, which never carries that class at all.

Gen31 has been re-run with a collector that reads `memory_units.document_id`,
counts `invalidated_memory_units`, asserts all sixteen markers are present at
every checkpoint, and raises on any failed query. Its case results are
byte-identical to what was published; its lifecycle is genuinely clean. The
conclusion survived, but for two generations it rested on a number nobody had
measured.

All four summaries now carry **both** scorer streams with an explicit note that
they must never be merged, and a regression test enforces it.

Worth stating plainly: across five engine profiles, every error found tonight was
in the code that compares, aggregates and presents results. The runs themselves
have been deterministic, reproducible and provenance-exact throughout. A silently
failing query is indistinguishable from a clean result, and in a benchmark about
memory loss it reads as "nothing was lost".

## Verification

Full suite: 134 passed, one existing warning, with `node` on `PATH`. Focused
tests cover ruler and adapter hashes, public-only write payloads with native
provenance, the refusal to send scope or configuration as fields, the
supersession classifier against frozen truth, product-owned retirement with no
harness lifecycle calls, measured activation with exact predecessor/successor
ids, that `false_supersession` is read from the lifecycle stream and never the
case table, and that retired rows are never called deleted.

Reproduce with `scripts/run_agentmemory_gen33_longitudinal.py` then
`scripts/summarise_gen33.py`; the rule audit is
`scripts/preflight_agentmemory_gen33.py`.
