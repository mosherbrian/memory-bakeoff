# S8-7 design — the door: what the model was actually HANDED

Row S8-7 (admitted from BACKLOG-NEXT rank 11 on Brian's instruction, 2026-09-17).
Author: kiln-flash, 2026-09-18. Everything below was fixed before any run; the
declaration on disk was written before the runner existed in executable form,
and every run row carries the declaration's sha256.

Card, cited before any build: `team/EXTERNAL-ADEBENCH-20260917.md` — the door
is "the exact text a client actually receives from memory AFTER the system's
final composition step". The card adopts the METHOD only; adebench's 2,400-char
door and its ranking are explicitly not imported ("ours would be declared
before the run"). Its published numbers appear nowhere in this artifact.

## Prior measurement: none exists (re-measurement rule, stated up front)

No prior measurement of delivered-text evidence presence or irrelevant
delivered bytes at a declared budget has been made on any adapter in this
project. S6-2 (`team/S6-SELECTIVITY/`) scored retrieved-ID set-F1 — which
records what the store RETURNED, not the text the model was handed. S7-4
(`team/S7-KD-WORLDS/`) scored upstream family pass rates on a different
corpus. Neither measured the door; this row is the first measurement of it.
What this run should differ from, per the rule: from nothing — there is no
baseline number; the expectation recorded before the run is qualitative only,
that pressure (competing tool output in the same store) can lower evidence
presence and raise irrelevant delivered bytes for some adapters while a
binding budget may mask or cause both.

## Items (frozen, sha-bound into the declaration)

The five retrieve cases of the S6-2 frozen corpus, reused verbatim
(`team/S6-SELECTIVITY/corpus.jsonl`, sha256 pinned below). Reasons: (1) their
helpful sets were declared before ANY run (S6-2 manifest, verified by corvid
2026-09-17) and independently re-derived twice — the evidence strings are
already adjudicated, which is exactly what this row must not improvise;
(2) each case has exactly one helpful record among plausible distractors, so
"helpful-evidence present" and "irrelevant bytes" have clean meanings. The
five abstain cases are NOT door items: the gate's items schema requires
non-empty helpful_evidence, and abstention behaviour was S6-2's question, not
this row's. corpus.jsonl sha256:
see declaration-time pin in `declare.py` output (constant in the runner).

item_id = the corpus case_id (sel-001..sel-005); helpful_evidence = the exact
text of the manifest's declared helpful record (sel-001-r2, sel-002-r1,
sel-003-r2, sel-004-r3, sel-005-r2 respectively).

## Adapters (three memory adapters, as pinned in S6-2/S4-14)

| declared name | provider | pin | top_k |
|---|---|---|---|
| `bm25` | `BM25Provider`, repo `src/memory_bakeoff/providers/bm25.py` @ canonical `be2bfa9` | S6-2 arm `bm25`: top-1 iff score > 0 | 1 |
| `pi_lcm_toollevel` | `PiLcmToolLevelProvider`, `team/s4-14-crossengine-rerun/run_s4_14.py` (verbatim relaxedVariants port; exact AND first, then <=6 bounded variants) | S4-14 pin, exercised in S6-2 | 5 (full match set, S6-2 semantics) |
| `claude_mem_chroma_lsa_no_recency` | `ClaudeMemChromaLSANoRecencyProvider`, repo `src/memory_bakeoff/providers/claude_mem_core.py` | S4-14 row-mandated primary: 90-day window disabled | 3 |

Controls are not adapters and are not declared: return-everything /
return-nothing / oracle are not memory systems and have no composition step;
the gate's recomputation is itself the oracle here (it re-derives both numbers
from the delivered text). Adaptation labels carried from S6-2, unchanged:
4-record per-item store (plus pressure load below); record ts fixed
2026-09-01T00:00Z uniform (RECORD_TS from `run_crossengine.py`), no time
behaviour in scope; session_id `sess-<item_id>` for every record.

## Declared budget: 600 characters

Normal-condition deliveries of these adapters on ~75-char records run
~75-400 chars, so 600 leaves the normal door loose; under pressure, 2 KB-class
tool-output records make the budget bind. The budget is the DOOR, applied as
the final composition step (the card's "cut to a budget"), identically to
every adapter and both conditions.

Composition rule (declared): the adapter's returned records, in return order,
joined with a single "\n". Records are appended whole while the joined length
stays <= 600 chars; appending stops at the first record that would not fit
whole. If the FIRST record alone exceeds the budget it is hard-truncated to
exactly 600 chars. Rationale: a record cut mid-text is a corrupted datum —
the door either hands a record or it does not; only an oversized first record
is truncated because a zero-record door would be a harness artefact, not a
measurement.

## Pressure condition (declared)

"Competing tool-output pressure" is modelled the only way a local, no-LLM
harness can make it real: the tool output enters the memory write path, as it
does in production sessions (claude-mem ingests transcript tool output; a
store reader indexes whatever was stored). Under `pressure`, before the query
runs, the item's store is augmented with 10 tool-response records generated
from 10 fixed template families (file-tree listing, backup log tail, DNS
lookup table, CI matrix, metrics samples, ticket export, cache stats, HTTP
access log, config dump, queue snapshot), parameterised from fixed value
pools by a seeded RNG (seed = int of sha256("door-press|" + item_id),
fully deterministic). Sizes ~2 KB each; total >= 20,000 UTF-8 bytes per item
(the declared `pressure.tool_output_bytes`), and `competing_bytes` on each
pressure row is the exact byte total injected. Under `normal`, nothing is
injected and `competing_bytes` is 0. Tool chunks are ingested AFTER the item's
own 4 records (ingest order is the declared tie-break everywhere). Hard
pre-run assertion in the runner: no generated chunk contains any item's
helpful_evidence string (whitespace-collapsed, case-blind) — the run aborts
before writing anything if the pressure load could fake or destroy presence
by construction. Chunks MAY share vocabulary with the query; that is the
phenomenon under test (relevance competition), not a fault.

## Scoring (the gate's rules, restated; recomputed independently there)

- `helpful_evidence_presence` (per item): 1 if every helpful string appears
  in the delivered text (whitespace-collapsed, case-blind), else 0; reported
  as the mean over the 5 items.
- `irrelevant_delivered_bytes` (per item): UTF-8 bytes of the delivered text
  minus the bytes of the helpful string(s) present, each counted ONCE (a
  repeated chunk is irrelevant); floored at 0; mean over items.
- The two numbers are reported separately everywhere. No blended figure
  exists in this artifact.

## Chain of custody

items.jsonl frozen -> declaration.json (declared_at, budget, scoring, load,
items sha, adapters) written once by `declare.py` BEFORE the runner executes
-> `run_door.py` (reads the declaration, binds every row to its sha256, rows
in run order) -> results.jsonl -> verdict.json (both numbers recomputed here
by independent code, then re-recomputed by the gate). Neither items.jsonl nor
declaration.json is touched after the run; any edit breaks every row's hash
and the gate says so. No score, number or ranking is imported from the card
or anywhere upstream.
