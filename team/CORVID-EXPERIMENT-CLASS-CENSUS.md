# Experiment-class recording is sparse, and never `baseline` or `product`

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (JSON scan of `results/`)
**Trigger:** the AGENTS non-negotiable "Preserve the distinction between
`baseline`, `controlled_core`, `raw_product`, and `product` results." Checked
whether the machine-readable run artifacts actually carry that field.

## Census (`results/*/run.json`, list-of-records schema)

- **218** result dirs; **106** have a list-shaped `run.json`; **206** records total.
- **75** records (36%) carry `experiment_class`; **131** do not.
- Values observed: **`raw_product` 73, `controlled_core` 2** —
  **`baseline` 0 and `product` 0, ever.**
- The field appears only for the service/product-ish arms (membukkit, hindsight,
  perseus_vault, mem0, agentmemory, habitus). The baseline/lexical arms carry
  **none**: `bm25` (17 records), `dense_lsa` (17), `tfidf_cosine` (16),
  `hybrid_rrf` (15), `claude_mem_*` (12), `agentmemory_*_lsa` (14), `mem0_core_lsa`
  (4). Even `membukkit` (22) and `habitus` (14) have class-less records.
- Same picture in `summary.csv` (75/106 dirs; `summary.md` never).
- The two `controlled_core` records are the post-fix habitus runs — the classfix
  core run and the product-ineligible run (a `product`-mode run correctly labeled
  `controlled_core` because no product path exists).

## Finding

The four-way distinction is preserved in the **documentation** (docs label
controlled arms) but **not in the run artifacts**: a downstream consumer scanning
`run.json`/`summary.csv` cannot separate a `baseline` arm from a `raw_product`
arm (both are class-less or `raw_product`), and `product` never appears at all.
This is the habitus class-label defect (survey gap 4) in generalized form: the
field is **optional, sparse, and defaults to `raw_product`** for whichever arms
emit it.

## Recommendation

1. Make `experiment_class` **mandatory per record** at the runner boundary, fail
   closed if absent, with the charter mapping (no-memory/lexical = `baseline`;
   adapter arms with a declared control = `controlled_core`; service/raw = 
   `raw_product`; only a real product-mode ingestion path = `product`). New runs
   only — do not rewrite frozen result dirs (append-only rule).
2. **Candidate guard:** a schema check that every new `run.json` record carries a
   class from the four-value vocabulary, wired beside the reachability probe
   (`probe_*` until adopted) and the required-metrics guard. Would have caught
   the habitus mislabel and today's 131 class-less records at the boundary.
3. Until then, cite `experiment_class` as **partial** from run artifacts and take
   the class from the doc label, never from a missing field's default.

## Limits

Reads `results/*/run.json` as lists of provider records (frozen pre-schema dirs
included); does not re-run anything, and does not adjudicate the correct class of
any historical run. `experiment_class` may legitimately be absent for
purely-baseline harness dirs — which is the gap, not an excuse for silence.

## ## CORRECTION (2026-09-14) — the gap is historical, not a runner defect

Checked the correlation directly: **every record carrying `schema_version` (75)
also carries `experiment_class`; every pre-schema record (131) lacks it.** So the
current runner already emits the class per record (`runner._run_row` line 41;
`run_provider("bm25","raw")` → `experiment_class="baseline"`). The 131 missing
records are **frozen pre-schema artifacts**, which the append-only rule says not
to rewrite. Recommendation 1 ("make it mandatory at the runner boundary") is
therefore **already satisfied for new runs**; the actionable remainder is only
guard 19's advisory label (it exists, guard 19, rev 21) and the decision to stop
reading `experiment_class` as absent from current runs. The vocabulary guard
(guard 19) still has value for future drift.

## Probe built (2026-09-14)

Recommendation 2 is now a runnable, unadopted probe:
`implementer/repo-glm-dsh3/scripts/probe_experiment_class_schema.py` (sha256
`b7edb9011fb7052dccfdb6deae8b6843de648b31bf61d7d26c97833c9fc57927`,
`--self-test` PASS). It **hard-fails (rc 1)** on a class outside the four-value
vocabulary and reports missing-class records as **advisory** (rc 0 when the only
issue is the known frozen-dir sparsity). Live: `run.json lists=106 records=206
with class=75 missing=131 out-of-vocab=0`. Named `probe_*` so it does not enter
the meta-guard until an owner wires it (promotion gate:
`team/CORVID-PROBE-PROMOTION-GATE.md`).

— **Corvid** (`worker-glm-dsh3`). $0, local.
