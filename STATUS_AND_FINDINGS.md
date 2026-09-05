# Memory Bake-off — Status and Findings

**Snapshot:** 2026-09-02 (America/Los_Angeles)  
**Harness tests:** 97/97 passing  
**Evidence index:** [`RESULTS.md`](RESULTS.md) is the maintained map of every measured result; [`research/ROUND1_FINAL_READOUT.md`](research/ROUND1_FINAL_READOUT.md) is the authoritative Round-1 view. Rows below that predate them are historical.  
**Canonical corpus:** 50 coding-memory records, 26 held-out queries  
**Stress corpus:** 500 total records = 50 core + 450 deterministic near-neighbor distractors  
**Real reader trace:** 56/56 archived request/response pairs, replay-verified

This document is the fastest way to understand where the project stands. It deliberately separates:

1. **real runtime/product behavior** — stock or pinned upstream behavior actually executed;
2. **controlled-core/policy ablations** — real upstream retrieval/lifecycle code with shared deterministic components so one architectural variable can be isolated;
3. **not-yet-run product configurations** — no score is substituted when a required service/model/runtime is unavailable.

The harness owns ground truth, grading, lifecycle labels, and leaderboard data. Model self-report never determines correctness.

---

## Executive summary

The benchmark is now mature enough to produce useful failures, but it does **not** yet have a fair final product winner.

The strongest current conclusions are:

1. **Simple retrieval is hard to beat.** BM25, TF-IDF, dense LSA, and a simple RRF hybrid remain strong baselines, especially under adversarial near-neighbor load.
2. **Habitus deserves further investigation.** It does not dominate recall, but it surfaces markedly fewer stale/failed/prohibited memories under stress.
3. **MemBukkit's bucket routing is genuinely useful in the controlled arm.** With the same LSA representation as the dense baseline, it preserves top-5 recall while opening only ~33% of the bank.
4. **agentmemory's current write-time Jaccard supersession is dangerous on heterogeneous coding memories.** It falsely supersedes 418/450 distinct stress memories (92.9%), making retrieval appear better by deleting valid near-neighbor facts.
5. **Policy/lifecycle choices can dominate embedding quality.** Claude-Mem's default 90-day semantic-search window, Mem0's threshold/abstention behavior, agentmemory's supersession, and Habitus's inactive superseded history materially change outcomes without changing the underlying semantic model.

The emerging thesis is therefore:

> Long-term agent memory may depend at least as much on memory lifecycle, temporal policy, evidence competition, contamination control, and abstention as on the embedding model itself.

The next phase should run the **complete products with their intended models/services** on a normal networked machine, then run the same downstream reader/agent evaluation against each.

---

## Evaluation status by engine

| Engine | Current status | What was actually tested | Most important current finding | Next required test |
|---|---|---|---|---|
| BM25 | complete baseline | deterministic lexical retrieval | Still strongest stress Hit@5 among simple baselines | keep as anchor |
| TF-IDF cosine | complete baseline | deterministic sparse cosine | Strong stress recall, but produced one stale/prohibited reader answer | keep as anchor |
| Dense LSA | complete baseline | deterministic 32-D corpus-fit LSA | Perfect 14/14 reader result on current reader set; stress recall drops under near-neighbor load | add modern pretrained dense baseline |
| Hybrid RRF | complete baseline | BM25 + dense-LSA RRF | Perfect 14/14 reader result; stress better than dense alone | keep as anchor |
| Habitus | **real pinned runtime core** | upstream remember/recall core, byte-verified | Stress Hit@5 ties BM25/TF-IDF with much lower prohibited-memory rate | product/learning round and retrieval-credit experiment |
| MemBukkit | **controlled real core** | upstream MemorySystem bucket routing/storage with shared LSA | Same stress Hit/all-relevant as full dense scan while opening 32.9% of bank | run intended encoder/reranker weights |
| agentmemory | **controlled real core + lifecycle** | upstream BM25/vector indexes and `/remember` supersession behavior | 92.9% false supersession of distinct stress memories | run full service, graph lane, real embeddings/reranker; lifecycle remains separate score |
| Mem0 | **controlled search-policy arm** | pinned scoring policy + shared LSA | Positive retrieval ~= dense control; threshold abstains on half of negative cases | run full Qdrant/fastembed/entity/reranker stack |
| Claude-Mem | **controlled search-policy arms** | current FTS5 and semantic-recency policy, not compression worker | Default 90-day window reduces current semantic Hit@5 to 0.208; disabling it restores dense-LSA result | run actual worker + compression pipeline |
| Hindsight | **raw_product scored** | v0.9.2 raw/no-LLM learned-reranker path on a networked host | stress Hit/all-relevant 0.833/0.708; composite DB/model/runtime identity must travel with the row | run product mode with its normal LLM pipeline |

---

## Baseline retrieval scoreboard

### 50-memory core, k=5

| Provider | Hit@5 | All relevant@5 | Prohibited@5 | Notes |
|---|---:|---:|---:|---|
| BM25 | 0.917 | 0.792 | 0.125 | strong exact/lexical anchor |
| TF-IDF cosine | 0.875 | 0.833 | 0.153 | strong sparse baseline |
| Dense LSA | **0.958** | **0.958** | 0.125 | deterministic dense control |
| Hybrid RRF | **0.958** | 0.917 | 0.125 | lexical+dense fusion |
| Habitus | 0.875 | 0.750 | **0.097** | two misses are intentional historical/as-of cases |
| MemBukkit bucketed/shared-LSA | **0.958** | **0.958** | 0.125 | controlled architecture arm |
| agentmemory core/shared-LSA | **0.958** | **0.958** | 0.125 | controlled retrieval arm |
| Mem0 policy/shared-LSA | **0.958** | **0.958** | 0.169 | controlled policy arm |

### 500-memory stress, k=5

| Provider | Hit@5 | All relevant@5 | Prohibited@5 | Notes |
|---|---:|---:|---:|---|
| BM25 | **0.792** | 0.667 | 0.092 | strongest simple stress Hit |
| TF-IDF cosine | **0.792** | **0.750** | 0.101 | best completeness among simple stress baselines |
| Dense LSA | 0.583 | 0.542 | 0.050 | near-neighbor pressure hurts corpus-fit LSA |
| Hybrid RRF | 0.708 | 0.667 | 0.058 | recovers some dense loss |
| Habitus | **0.792** | 0.667 | **0.025** | unusually clean evidence set |
| MemBukkit bucketed/shared-LSA | 0.583 | 0.542 | 0.042 | same recall as dense with ~32.9% bank opened |
| agentmemory core/shared-LSA | 0.583 | 0.500 | 0.042 | all 500 records retained; lifecycle off |
| Mem0 policy/shared-LSA | 0.583 | 0.542 | 0.050 | same semantic representation as dense control |

Do **not** combine these into a single product leaderboard. Several third-party rows deliberately hold the representation constant and test only policy/architecture.

---

## Real LLM reader experiment

A real ChatGPT sidecar experiment exercised 14 deterministic answer cases for each of four baseline retrievers. GPT-5.6 Sol saw only the retrieved context; the harness graded answers deterministically. All 56 requests and responses are archived under `results/sidecar_reader_trace/` and replay-verified by fingerprint.

| Provider | Reader pass | Required coverage | Prohibited-answer rate |
|---|---:|---:|---:|
| BM25 | 12/14 (0.857) | 0.857 | 0.000 |
| TF-IDF cosine | 12/14 (0.857) | 0.857 | **0.071** |
| Dense LSA | **14/14 (1.000)** | 1.000 | 0.000 |
| Hybrid RRF | **14/14 (1.000)** | 1.000 | 0.000 |

The two 12/14 results fail differently:

- **BM25:** Q012 and Q016 omitted required evidence, so the grounded reader safely returned `INSUFFICIENT_MEMORY`.
- **TF-IDF:** Q016 was also an omission, but Q008 retrieved an obsolete deploy command without its current correction. The reader therefore confidently emitted a **prohibited stale command**.

This is why retrieval quality must distinguish omission from contamination: the downstream agent behaves very differently.

See `results/READER_FINDINGS.md` for exact cases and IDs.

---

## Per-engine findings

### Habitus

Pinned runtime core: `munch2u-a11y/Habitus-AI` commit `f93b770e4b3c1875151dc13eb90421598c3efa5f`.

Nine memory/runtime modules were transferred from upstream and verified by Git blob SHA. The benchmark executes the real dependency-free memory core.

Key observations:

- Core Hit@5 = 0.875; stress Hit@5 = 0.792.
- Stress prohibited@5 = **0.025**, substantially lower than BM25/TF-IDF.
- Two of its three positive core misses are deliberate as-of/history questions. Stock Habitus marks superseded records inactive and does not expose historical retrieval.
- On positive non-as-of cases, Hit@5 is 21/22 = 0.955.
- It effectively plateaus at about three unique hits on this corpus, making its small context footprint real.

Interpretation: not evidence for a magical new cognitive substrate, but its selectivity/contamination tradeoff is worth deeper testing.

### MemBukkit

Pinned core: `memseekai/membukkit` commit `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`.

Nine semantics-bearing routing/storage/pipeline files match upstream Git blob SHAs. Because pretrained encoder/reranker weights were unavailable in the sandbox, the primary controlled arm feeds MemBukkit the exact same 32-D LSA representation as the dense baseline and uses the real bucket-routing/search machinery.

Key result on 500 memories:

- full dense LSA: Hit@5 0.583 / all-relevant 0.542, scanning all records;
- MemBukkit bucketed/shared-LSA: **0.583 / 0.542**, opening **32.9%** of the bank on average.

This is the strongest clean architectural result so far: substantial scan reduction with no top-5 recall loss in the controlled arm.

The upstream CI fake reranker lowered stress Hit@5 to 0.458; that is retained only as a code-path diagnostic, not a product-quality result.

### agentmemory

Pinned core: `rohitg00/agentmemory` commit `e04ba88819c365c9acf9d6661ea802143e728bd6`.

With all 500 stress records retained, its controlled BM25+vector core scores Hit@5 0.583 / all-relevant 0.500 / prohibited 0.042.

The major finding is lifecycle behavior. Reproducing the real `/remember` Jaccard > 0.7 supersession rule collapses the stress store from 500 to **82 live memories** and falsely supersedes **418 of the 450 deliberately distinct stress distractors (92.9%)**. Apparent Hit@5 rises to 0.792 only because most difficult near-neighbor records have been deleted from the indexes.

This is a lifecycle-safety failure, not a retrieval win. Future leaderboards must report false merge/supersession rates separately.

See `research/AGENTMEMORY_FINDINGS.md`.

Generation 13 additionally completed the first authoritative LLM-free local
embedding **raw_product** retrieval run under a verified isolated native
`agentId` deployment (the product's `project` field still does not scope
search).  Three fresh core runs were identical at Hit@5 1.000 / MRR 0.889 /
all-relevant@5 1.000 / prohibited@5 0.142; three fresh stress runs were
identical at 1.000 / 0.847 / 0.958 / 0.133.  Exact native provenance was
verified for all returned rows.  The lifecycle safety result is unchanged and
must accompany those scores: each stress run retained only 82/500 live
memories and falsely superseded 418/450 distinct stress distractors (92.9%),
with zero legitimate benchmark correction supersessions.  See
`research/AGENTMEMORY_RAW_PRODUCT_GEN13.md`.

Generation 14 froze (without rerunning retrieval) the compatible 14-case
ChatGPT-sidecar reader inputs for both Gen13 core and stress contexts.  The
interactive sidecar responder is not available in the Codex session, so no
reader answer or derived propagation rate is published.  The complete pending
request packages, exact contexts, source hashes, and fingerprints are in
`results/agentmemory_raw_product_gen14_reader_requests/`; see
`research/AGENTMEMORY_READER_GEN14.md`.

Generation 15 exports those unchanged 28 pending requests as one reviewable
sidecar transport artifact and adds a fail-closed response importer plus the
unchanged deterministic grading path.  No response bundle was available, so
there is still no answer-propagation result.  See
`research/AGENTMEMORY_READER_GEN15.md`.

Generation 16 received the complete sidecar bundle but its verbatim native
Google Docs plain-text export carried a UTF-8 BOM, so the fail-closed importer
rejected it before writing any responses.  No reader answers or metrics are
published; a BOM-free stored JSON bundle or equivalent raw export is required.
See `research/AGENTMEMORY_READER_GEN16.md`.

Generation 17 resolved the native-Docs BOM transport encoding only, imported
the unchanged 28 sidecar answers, and graded the frozen Gen13 contexts. Core
reader success was 12/14 (0.857) and stress 11/14 (0.786); no wrong-scope
answer was recorded. The sole lexical prohibited-answer count in each arm is
Q015's explicit rejection of timing sleeps, a documented substring-grader
false positive rather than semantic failure adoption. Retrieval/lifecycle
identity remains distinct: 92.9% stress false supersession is not redeemed by
reader resistance. See `research/AGENTMEMORY_READER_GEN17.md`.

### Mem0

Pinned scoring policy: `mem0ai/mem0` commit `19cb89aff472325c707f64b2f34ae6afdbf7faf7`.

The sandbox could not run the full Qdrant/fastembed product stack. The controlled arm uses shared LSA for semantic representation while executing current Mem0 over-fetch/threshold/ranking policy.

- Core Hit/all-relevant = 0.958 / 0.958.
- Stress = 0.583 / 0.542.
- Negative-empty-rate = **0.50** because the semantic threshold refuses weak matches rather than always filling k.

The interesting behavior is therefore abstention policy, not superior embedding retrieval.

See `research/MEM0_FINDINGS.md`.

### Claude-Mem

Pinned source inspected for the controlled policy result: `thedotmack/claude-mem`
commit `fa6a1e9ec12d23f98326a9b26e243acb0819e105`, package **13.18.0**. The prior
10.6.1 label was a provenance error: npm 10.6.1 instead records git commit
`d54e574251d7736cfd6030f8ba86b15fbebd3b50`. Historical result artifacts are
preserved unchanged; this correction does not represent a rerun.

The generated worker bundle was not available in the sandbox, so the current rows are controlled search-policy ablations rather than product runs.

Current semantic policy:

- only 9/50 core memories fall inside the implicit 90-day default window;
- current-policy core/stress Hit@5 = **0.208 / 0.208**;
- disabling only the 90-day filter restores **0.958 core / 0.583 stress**, exactly matching the dense-LSA control.

Therefore the large recall loss in this controlled arm is caused by recency policy, not semantic representation.

Current FTS5 fallback also scores zero on the paraphrase-heavy corpus because the whole natural-language query is wrapped as a quoted phrase. That is a policy result, not a claim that FTS5 itself is incapable.

See `research/CLAUDE_MEM_FINDINGS.md`.

### Hindsight

Target release: `vectorize-io/hindsight` v0.9.2, tag commit `ebad478240d3171bb88201ececda5e8d9883d22d`.

No synthetic Hindsight score exists. Its recall path is a real DB-backed multi-arm system: semantic/vector, BM25/full-text, graph, temporal, then fusion/optional reranking.

Infrastructure proof already completed:

- pg0 0.15.1 transferred from a GitHub Actions artifact;
- successfully started **PostgreSQL 18.1 + pgvector 0.8.5** as an unprivileged user;
- SQL accepted and shutdown cleanly;
- Hindsight's official OpenAI embeddings provider accepts a custom base URL/dimensions, so a shared-LSA controlled endpoint can be used without patching Hindsight.

The sandbox then stopped at compiled Python package transfer (`asyncpg`, etc.). On a normal networked machine this should be the first real external product/core test attempted.

See `research/HINDSIGHT_FINDINGS.md`.

---

## Methodological lessons already encoded in the harness

### Retrieval must not be rewarded for deleting the corpus

agentmemory demonstrated that lifecycle transforms can game a distractor-heavy retrieval score. Future product runs should report:

- false-supersession / false-merge rate;
- correct stale-version consolidation rate;
- valid-record retention after ingestion;
- retrieval before and after lifecycle transformations.

### Prohibited fraction is not enough

As k grows, `prohibited@k` can fall cosmetically because the denominator grows even if the stale memory is still present. The harness therefore also records harmful presence/count and useful-before-harmful ordering.

### Context budget is a real cost

Exact returned characters/words are recorded so a system cannot receive free credit merely for retrieving more context. The top-k sweep is in `results/TOPK_FINDINGS.md` and `results/topk_sensitivity.csv`.

### Product mode and raw mode are separate experiments

If a product uses an LLM to extract/compress/rewrite memory, that model is part of the evaluated system. Do not compare a hand-bypassed raw path with a full product run without labeling the distinction.

### Provenance is a release gate

A product that rewrites observations must still map returned evidence reliably to benchmark source records. Fuzzy text matching must not silently become ground truth.

---

## What remains to run on a normal networked host

Priority order:

1. **Hindsight v0.9.2 real service** — easiest major blocked engine now that the DB/embedding seams are understood.
2. **MemBukkit intended pretrained encoder/reranker** — test whether the promising bucket efficiency survives real models.
3. **Mem0 full raw stack** — explicit embedder + Qdrant/fastembed BM25/entity/reranker configuration.
4. **agentmemory full service** — test keyless BM25/graph and local-embedding vector mode; preserve lifecycle safety metrics.
5. **Claude-Mem actual worker/compression pipeline** — test normal product ingestion, then current default search policy and explicit long-range retrieval.
6. **Third-party reader/agent round** — run the same deterministic reader cases downstream of each real engine.
7. **Repeated local/API model runs** — once product plumbing is stable, use multiple seeds/runs where generation introduces variance.

`CODEX_HANDOFF.md` contains exact execution guidance.

---

## Important files

- `CODEX_HANDOFF.md` — tomorrow's execution plan and stop conditions
- `AGENTS.md` — instructions Codex should obey when working in this repo
- `BUILD_MANIFEST.md` — what actually ran vs did not run
- `RUN_EXTERNAL.md` — external-engine launch notes
- `EXPERIMENT_PLAN.md` — benchmark design
- `results/READER_FINDINGS.md` — real 56-call reader experiment
- `results/BASELINE_FINDINGS.md` — baseline interpretation
- `results/TOPK_FINDINGS.md` — context-budget/top-k findings
- `research/AGENTMEMORY_FINDINGS.md`
- `research/CLAUDE_MEM_FINDINGS.md`
- `research/MEM0_FINDINGS.md`
- `research/HINDSIGHT_FINDINGS.md`
- `research/MEMBUKKIT_INTENDED_MODEL_GEN40.md` — intended-model path reproduced (no score)
- `research/MEMBUKKIT_INTENDED_ROUND1_GEN41.md` — intended models on the frozen Round1 ruler
- `research/MEMBUKKIT_MEMCONFLICT_GEN42_CALIBRATION.md` — MemConflict calibration (development-exposed)
- `research/PI_STATE_CONTROL_GEN43_PROTOTYPE.md` — first Pi state/control prototype (no score)
- `research/PI_STATE_CONTROL_GEN44_PILOT_DESIGN.md` — paired pilot design, frozen (no score)
- `research/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md` — first live paired pilot, 24 runs
- `research/PI_STATE_CONTROL_GEN46_HARNESS_STATE_DESIGN.md` — harness-maintained state arm, frozen (no score)
- `research/PI_STATE_CONTROL_GEN47_HARNESS_STATE_LIVE.md` — harness-maintained state, live: 12/12 against 9/12
- `research/PI_HUMAN_DIRECTION_FLOOR_GEN48_DESIGN.md` — human-direction floor arm, frozen (no score)
- `research/PI_HUMAN_DIRECTION_FLOOR_GEN49_LIVE.md` — the floor, live: no task-success gain, reported as such
- `research/PI_FAILURE_AUDIT_GEN50.md` — failure audit: none of five failures was a context problem
- `research/PI_EVIDENCE_AND_QUIESCENCE_GEN51.md` — evidence retention fixed; quiescent stop calibrated offline, K=3
- `research/PI_QUIESCENT_COMPLETION_GEN52_LIVE.md` — the stop rule live: fired once, stopped a self-reverted run, and missed a 144-repeat check loop
- `research/PI_QUIESCENT_COMPLETION_GEN53_REFINEMENT.md` — v2 over 72 runs: the loop repair works, the revert repair is inert because the tree digest counts build artifacts
- `research/PI_TRACKED_DIGEST_GEN54.md` — fingerprint corrected to ignore build output; the revert refusal is now real at every K, zero stops on an unchanged tree
- `research/PI_QUIESCENT_COMPLETION_GEN55_LIVE.md` — the corrected controller live: 2 legal stops, 0 hard failures, 3 baseline timeouts against none
- `research/PI_ARTIFACT_AUTHORITY_GEN56.md` — quiescence closed in ARCHITECTURE.md; breadth would have blocked 0 of 14 false assurances, so the gap is artifact coverage
- `research/PI_ARTIFACT_COVERAGE_GEN57.md` — coverage probes are sensitive but fire on ~70% of correct runs; the false assurance is clean and the good run is flagged
- `research/HABITUS_RETRIEVAL_CREDIT.md`
- `research/CHATGPT_SIDECAR.md`
- `research/TOOL_LOOP_RPC.md`
- `results/repro_manifest.json`
