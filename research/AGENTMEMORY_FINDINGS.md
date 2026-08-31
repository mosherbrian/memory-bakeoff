# agentmemory controlled-core findings

Pinned source: `rohitg00/agentmemory` commit
`e04ba88819c365c9acf9d6661ea802143e728bd6`.

## What is real upstream code in this arm

The Node worker executes byte-identical upstream files for:

- `SearchIndex` (BM25 + stemming + synonym expansion)
- `VectorIndex` (cosine search)
- English stemmer
- synonym table

The worker transcribes the BM25/vector portion of upstream `HybridSearch`:
weighted reciprocal-rank fusion (`0.4` BM25 / `0.6` vector, `k=60`), the 5%
stream-agreement bonus, tie breaking, and session diversification. Graph retrieval
and the optional Hugging Face reranker are explicitly disabled. Shared 32-D LSA
vectors keep the representation controllable and offline.

The `/remember` lifecycle arm additionally reproduces the upstream memory shape,
vector text (`title + content`), candidate search, and `Jaccard > 0.7` write-time
supersession rule.

## Pure retrieval result

With supersession disabled so all 500 records remain searchable:

- core Hit@5: **0.958**; all-relevant@5: **0.958**
- 500-record stress Hit@5: **0.583**; all-relevant@5: **0.500**
- stress prohibited@5: **0.042**

This is the appropriate retrieval-only row. It does not beat the strongest lexical
baselines under near-neighbor pressure.

## Lifecycle result: aggressive false consolidation

With the actual `/remember` Jaccard supersession behavior enabled, the 500-record
stress store collapses to **82 live indexed memories**. It supersedes **418 of 450
stress distractors (92.9%)**. No original core memory is superseded.

The apparent retrieval score then improves to:

- stress Hit@5: **0.792**
- all-relevant@5: **0.750**

But this is not a retrieval win: most of the adversarial corpus has been deleted from
the indexes.

The stress records are deliberately distinct facts scoped to different repos,
services, credentials, quotas, commands, and incidents. Examples of false
supersession observed from the exact write-path transcription:

- a **delta** Redis migration fact replaced by a **fjord** Redis migration fact
  (Jaccard 0.867)
- an **archive** canary deployment command replaced by a **search** canary command
  (0.750)
- a **search** import-utility behavior replaced by **reporter** (0.895)
- a **mailer** synthetic-traffic quota replaced by **catalog** (0.765)
- a **catalog** race investigation replaced by **archive** (0.867)

Therefore the benchmark must report write-time consolidation accuracy separately from
retrieval. A memory system should not receive retrieval credit for removing valid
near-neighbor facts unless the consolidation itself is correct.

## Benchmark implication

Add lifecycle metrics for future contestants:

- false-supersession / false-merge rate
- correct stale-version consolidation rate
- live-record retention after ingestion
- retrieval quality both **before** and **after** lifecycle transformations

This prevents aggressive deduplication from gaming a distractor-heavy retrieval test.
