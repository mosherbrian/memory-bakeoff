# Gen109 — the reader layer, opened as a design and integrity generation

**Nothing was executed.** No engine, model, reader, sidecar or GPU. This
generation builds the ruler and freezes it *before* any model answers, which is
the discipline Gen85 skipped.

**The reader question is OPEN and UNRUN.** Gen109 is not a reader result.

Frozen contract: `reader-interference-v1`, sha256 `bc00267aed3da0e8…`
Artifact: `results/gen109/attempt1/reader_interference_v1.json` (+ verifying `MANIFEST.json`)

## The question

Round 3 established that every engine co-returns the superseded record beside
the current one — 192 of 192 — and that only explicit lineage removes it. It
never asked the question that makes any of that matter: **does a stale record
sitting next to the current one change the answer?**

## The Gen85 audit

**Gen85's reader material is not on `main`.** It exists only on the unmerged
branch `reader-layer-gen85`. Nothing was reconstructed from narrative summaries.
The `superseded_attempt_1` directories that *do* appear on `main` belong to Gen58
and Gen61 — different experiments.

**The defect, read from source rather than from the story.** The branch's own
fix comment records it: attempt 1 compiled the citation as `^\s*CITE:` under
`re.MULTILINE`. A reply that cited **inline** did not match, was classified
`UNPARSED`, and was then **scored by the substantive scorer as a failure**.

Two errors, and the second is the load-bearing one:

1. A presentation choice decided whether a valid reply parsed.
2. **Parse status and semantic grade were entangled**, so a parser failure was
   reported as a reader failure.

Every surviving Gen85 artefact is now marked
`QUARANTINED / NOT EVIDENCE` in `research/GEN85_READER_QUARANTINE.md`. It may not
seed a fixture, set a threshold, serve as a baseline, or supply examples.

## What is frozen

**Five conditions**, from the four Round 3 cores verbatim — no new semantic
neighbourhoods, and each core's current truth, stale truth, ids, scope and
configuration preserved exactly:

| condition | records shown | purpose |
|---|---|---|
| `CLEAN_CURRENT` | current only | the baseline |
| `CONFLICT_STALE_FIRST` | both, stale first | the effect under test |
| `CONFLICT_CURRENT_FIRST` | both, current first | order as a variable |
| `CLEAN_STALE_NEGATIVE_CONTROL` | stale only | proves the item *can* drive the stale answer |
| `INSUFFICIENT_CONTROL` | none | requires exact abstention |

20 cases: 4 cores × 5 conditions. **The two conflict conditions differ in
nothing but sequence** — `assert_conflict_pair_differs_only_in_order` raises if
prompt, schema, budget, temperature or any other field drifts, and also if the
two ever present different records.

**Parsing is separated from grading, in different functions with different
vocabularies.** The parser returns `PARSED` or one of three `UNPARSED_*` states
and assigns no grade. The deterministic grader assigns one of seven outcomes
from benchmark truth plus the parsed reply. **No model self-report decides its
own grade**, and `assert_parse_and_grade_are_separate` raises if an unparsed
reply is ever charged as a substantive answer.

The seven outcomes stay distinct and are never pooled: correct current,
prohibited stale, mixed/contradictory, correct insufficiency, incorrect
abstention, citation mismatch, unparsed.

**Q1–Q5 are pre-registered with mechanical verdict rules**, all reported per
core. Only `REPLICATED_ACROSS_CORES`, `PARTIAL_REPLICATION` or
`FIXTURE_SPECIFIC` may generalise across cores, under predeclared rules. Cores
are never averaged.

## The execution boundary, defined and not crossed

A future run must consume this fixture and contract **unmodified**; record
model/backend, exact model id, prompt hash, temperature, seed where supported,
request and response fingerprints, and repetition number per cell; use
predeclared repetitions and **report variation** rather than silently choosing
one answer when sampling is not deterministic; and write only under
`immutable-evidence-v1` attempt paths. It must not manufacture a product-linked
mapping from missing historical cells.

## Tests

40 deterministic tests. They fail if Gen85 output influences anything; if
citation placement changes parsing; if parse status and semantic decision are
collapsed; if the four outcome classes are pooled; if the conflict pair differs
in anything but order; if a fixture crosses core, scope or configuration; if
cores are averaged; if the freeze script imports an engine or model client; if
an artefact could overwrite a prior attempt or sit outside the evidence
contract; or if the frozen contract changes without its hash changing.

The Gen85 defect itself is now a permanent regression test: inline and
line-separated citations must parse **byte-identically**.

## What this does not establish

Nothing about reader behaviour. No model has been asked anything. The contract
is a ruler, and a ruler is not a measurement.
