# Round 1 final readout

Round 1 is closed as an evidence map, not a generic engine leaderboard. The
harness's 50-record core, 500-record stress corpus, provenance gates, harmful
context metrics, and lifecycle labels remain authoritative. Scores below are
only comparable within their stated experiment class and evaluated profile.

## Valid evidence at a glance

| System / evaluated configuration | Class | Strongest valid stress evidence | Lifecycle / maturity caveat |
|---|---|---|---|
| BM25, TF-IDF, dense LSA, hybrid RRF | baseline | BM25/TF-IDF Hit@5 0.792; dense 0.583; hybrid 0.708 | deterministic harness anchors, not products |
| Habitus real pinned core | controlled_core | Hit@5 0.792, prohibited@5 0.025 | core diagnostic; no full product claim |
| MemBukkit shared-LSA bucket routing | controlled_core | Hit/all 0.583/0.542, ~32.9% bank opened | routing finding only, not intended encoder/reranker |
| MemBukkit documented fallback | raw_product | Hit/all 0.875/0.750 | intended fine-tuned model repositories unavailable |
| Mem0 infer=False, explicit dense+BM25 stack | raw_product | Hit/all 0.958/0.917; negative-empty 0 | no LLM update/lifecycle semantics in this lane |
| Hindsight v0.9.2 raw/no-LLM learned-reranker path | raw_product | Hit/all 0.833/0.708 | composite DB/model/runtime identity must travel with row |
| agentmemory isolated native agentId | raw_product | Hit/all 1.000/0.958 | 82/500 live; 418/450 stress distractors falsely superseded |
| Claude-Mem FTS/semantic policy | controlled_core | default 90-day Hit@5 0.208; no-window shared-dense 0.583 | no compression worker/product score |
| Graphiti Gen18–20 | no-score diagnostic | — | extraction/lifecycle gates failed; includes cross-environment false invalidation |
| Perseus Vault v2.23.2 CLI-write + MCP hybrid recall | raw_product | Hit/all 0.958/0.958; prohibited@5 0.108 | 393/500 active after successful writes; 107 distinct-valid active-state losses; historical recoverability unknown |

The raw-product labels mean actual product retrieval paths with a documented
no-LLM/raw ingestion profile where stated. They do not mean normal end-to-end
product behavior. Controlled rows intentionally hold representation or policy
constant. No-score diagnostics demonstrate blocks or safety gates, not weak
contestant scores.

## Retrieval, safety, and reader evidence are separate

Retrieval reports Hit@5, all-relevant@5, exact context size, and prohibited
context. Negative-query behavior is also independently measured. Lifecycle
reports state retention, correction/supersession, scope safety, and historical
recoverability; it never converts deletion of hard competitors into a retrieval
gain. Provenance/reproducibility requires pinned code/configuration and exact
native canonical-ID mapping. Downstream reader evidence exists for baselines
and the frozen agentmemory contexts, but it cannot redeem a destructive
lifecycle transform and is not attributed to engines without a corresponding
reader run.

The baseline reader trace shows dense LSA and hybrid RRF at 14/14 on its
14-case set; agentmemory's later frozen-context reader result was 12/14 core
and 11/14 stress. Those are reader-plus-context observations, not a common
product ranking.

## Conclusion

The evidence supports a methodological conclusion rather than a winner claim:
retrieval relevance is often strong across very different systems, while
lifecycle truth, configuration/scope preservation, correction handling,
historical access, refusal, and exact provenance determine whether remembered
evidence is safe and useful over time. Perseus's stable unexplained active
state loss reinforces this conclusion; it does not establish destructive
deletion, because frozen Gen21 artifacts lack the lineage needed to make that
claim. Round 2 should use the engine-independent point-in-time ruler before
any private longitudinal corpus is ingested.
