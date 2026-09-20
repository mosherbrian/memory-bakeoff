# muse-drafter: contradiction-term fan-out, pass 2 (spark pulse 2026-09-14)

Second pass of the vocabulary fan-out (`CORVID-DISCOVERY-VOCABULARY.md` §3),
running its **contradiction half** (`negative result`, `no improvement`,
`fails to improve`, `replication`, `contamination`) against long-horizon agent
memory. Named as "next" in `SPARK-VOCABULARY-FANOUT-20260914.md`. Candidate
discovery only — **no score import**; every hit still needs a primary-source card.

## Method

Three queries (2026-09-14): agent memory + `"long-context baseline" no
improvement`; belief revision + `negative result / fails to improve`; memory
benchmark + `replication / contamination`. Deduped by grep against
`RD-THREADS.md` / `ECOSYSTEM-MAP.md` / `QUEUE.md` / `team/*.md`.

## Already known (fan-out re-surfaced — not a finding)

AMA-Bench / AMA-Agent (`2602.22769`, already in the intelligence directive and
Alice's spot-check, 57.22 exact), StateMemBench (`2608.19652`, card 6), STALE
(`2605.06527`, card 3), Supersede (`2606.27472`, card 3), EvoMemBench
(`2605.18421`, card 8), BeliefShift (`2603.23848`, fan-out 1). Their
contradiction framing — long-context baseline is strong; memory often
underperforms — is **already our E-1/long-context-null** and needs no new row.

## Net-new candidates (none present in the ledger)

| # | Candidate | ID / date | Fit | Why it is worth one card |
|---|---|---|---|---|
| 1 | **MemStrata** — "Temporal Validity in Retrieval Memory: Eliminating Stale-Fact Errors" | `arXiv:2606.26511`, 2026-06 | **G1/G2, axis C, E-7** | deterministic `(subject, relation, object)` supersession over a **bi-temporal ledger**, no similarity threshold, no LLM on the read path; says RAG serves stale facts **15–40%** when forced to answer, MemStrata drives to ~0; proposes a **marker-free invariant** (a stale-marker in text silently inflates RAG). Closest published mechanism to our supersession/stale-use discipline — a *method*, not just a benchmark. |
| 2 | **Cost-Performance Analysis of Fact-Based Memory vs. Long-Context** | `arXiv:2603.04814`, 2026-03 | **long-context null / break-even** | second independent break-even study (first was our known one): long-context GPT-5-mini beats a Mem0-style system by 33–35 pts on LongMemEval/LoCoMo; memory becomes cheaper only after ~10 turns at 100k tokens. Directly overlaps our break-even + long-context threads; check for convergences/conflicts with the existing study. |
| 3 | **Cross-Scenario Generality of Agentic Memory** (AutoMEM) | `arXiv:2606.04315`, 2026-06 | **G4/G5** | no method dominates across five task families; index-based stores build-time-commit and lose step/action evidence; an agent harness (grep/read) has the best generality. Convergent with our "mechanism over brand" and our transcript-mining substrate. |
| 4 | **Contamination pairs** — "Contamination Inflates Scores but Rarely Reorders Leaderboards" (`2609.02899`, 2026-07) and "LLM Benchmark Datasets Should Be Contamination-Resistant" (`2605.19999`, 2026-05) | — | **design corner 5 (corpus contamination)** | the first gives a calibrated anchor-item-invariance measure and the finding that contamination inflates absolute scores but rarely reorders (rank corr 0.997); the second proposes latent-form contamination-resistant release. Useful when we argue our own corpus's contamination posture. |

## Reading

The contradiction half of the fan-out is **lower yield than the mechanism half**:
most hits are the same long-context-null story we already own, restated per
benchmark. The four net-new are not new *benchmarks* but a **mechanism paper**
(MemStrata), a **cost/break-even study**, a **cross-scenario generality study**,
and a **contamination-methodology pair** — all four feed existing threads rather
than opening new goals. Ranked: MemStrata first (only direct supersession
mechanism), then the break-even study (checks against a number we cite).

$0, web reads only, no Muse batching. — muse-drafter (Spark)
