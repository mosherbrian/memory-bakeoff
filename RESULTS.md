# Evidence index

This is a map of what has actually been measured, not a leaderboard. A score is
only comparable inside its own experiment class and evaluated configuration, so
every row carries its class, its caveat, and links to the authoritative write-up
and the machine-readable artifacts behind it.

Round 1 is closed. Its authoritative narrative is
[`research/ROUND1_FINAL_READOUT.md`](research/ROUND1_FINAL_READOUT.md); prefer it
over any older score text elsewhere in this repository. Round 2 is the
engine-independent point-in-time work and the pi-observational-memory
generations. The full generation ledger is
[`handoff/CODEX_TO_CHATGPT.md`](handoff/CODEX_TO_CHATGPT.md).

## Evidence classes

| Class | Meaning |
|---|---|
| `baseline` | Harness-owned deterministic retrieval. Not a product. |
| `controlled_core` | Real upstream code with a shared or replaced component so one variable is isolated. |
| `raw_product` | The real product retrieval path in a documented raw/no-LLM mode. Not normal end-to-end behavior. |
| `full_product_context_production` | The product's own agent-visible context, produced by its own compaction. |
| `no-score diagnostic` | A block, gate, or defect demonstrated. Not a weak score. |

## Round 1 — retrieval, safety, and lifecycle

| System / evaluated configuration | Class | Strongest valid evidence | Lifecycle / safety caveat | Research | Results |
|---|---|---|---|---|---|
| BM25, TF-IDF, dense LSA, hybrid RRF | `baseline` | stress Hit@5: BM25/TF-IDF 0.792, dense 0.583, hybrid 0.708; reader 14/14 for dense LSA and hybrid | deterministic harness anchors, not products | [Round 1 readout](research/ROUND1_FINAL_READOUT.md) | [baseline findings](results/BASELINE_FINDINGS.md), [reader findings](results/READER_FINDINGS.md), [top-k](results/TOPK_FINDINGS.md) |
| Habitus, real pinned core | `controlled_core` | stress Hit@5 0.792, prohibited@5 0.025 | core diagnostic only; no full product claim | [retrieval credit](research/HABITUS_RETRIEVAL_CREDIT.md) | [core](results/habitus_core), [stress](results/habitus_stress) |
| MemBukkit, shared-LSA bucket routing | `controlled_core` | Hit/all-relevant 0.583/0.542 while opening ~32.9% of the bank | routing finding only; not the intended encoder/reranker | [intended model](research/MEMBUKKIT_INTENDED_MODEL_GEN7.md) | [stress LSA](results/membukkit_stress_lsa), [core](results/membukkit_core) |
| MemBukkit, documented fallback | `raw_product` | Hit/all-relevant 0.875/0.750 | intended fine-tuned model repositories unavailable | [fallback](research/MEMBUKKIT_FALLBACK_GEN8.md) | [hybrid 1.0](results/membukkit_hybrid_1.0), [stress](results/membukkit_stress) |
| Mem0, `infer=False`, explicit dense+BM25 | `raw_product` | Hit/all-relevant 0.958/0.917; zero non-empty negatives | no LLM update or lifecycle semantics in this lane | [findings](research/MEM0_FINDINGS.md), [gen10](research/MEM0_RAW_PRODUCT_GEN10.md), [lifecycle gen11](research/MEM0_PRODUCT_LIFECYCLE_GEN11.md) | [core r1](results/mem0_raw_product_gen10_core-r1), [stress clean r1](results/mem0_raw_product_gen10_stress-clean-r1) |
| Hindsight v0.9.2, raw/no-LLM learned-reranker path | `raw_product` | Hit/all-relevant 0.833/0.708 | composite DB/model/runtime identity must travel with the row | [findings](research/HINDSIGHT_FINDINGS.md), [reranker gen6](research/HINDSIGHT_LEARNED_RERANKER_GEN6.md), [external Postgres gen5](research/HINDSIGHT_EXTERNAL_POSTGRES_GEN5.md) | [gen4 core r1](results/hindsight_gen4_core_r1), [gen5 external stress r1](results/hindsight_gen5_external_local_stress_r1) |
| agentmemory 0.9.29, isolated native `agentId` | `raw_product` | Hit/all-relevant 1.000/0.958 | **82/500 live memories; 418/450 stress distractors falsely superseded (92.9%)** | [gen13](research/AGENTMEMORY_RAW_PRODUCT_GEN13.md), [findings](research/AGENTMEMORY_FINDINGS.md) | [core r1](results/agentmemory_raw_product_gen13_core-r1), [stress r1](results/agentmemory_raw_product_gen13_stress-r1) |
| agentmemory frozen-context reader | `raw_product` | reader 12/14 core, 11/14 stress over frozen contexts | reader evidence cannot redeem the lifecycle loss above | [reader gen17](research/AGENTMEMORY_READER_GEN17.md) | [gen14 requests](results/agentmemory_raw_product_gen14_reader_requests) |
| Claude-Mem, FTS/semantic policy | `controlled_core` | default 90-day window Hit@5 0.208; window disabled 0.583 | no compression worker; no product score | [findings](research/CLAUDE_MEM_FINDINGS.md) | [core](results/claude_mem_compare_core), [stress](results/claude_mem_compare_stress450) |
| Graphiti, Gen18–20 | `no-score diagnostic` | extraction and lifecycle gates failed; includes a cross-environment false invalidation | no score exists; do not infer one | [gen19](research/GRAPHITI_GEN19_FINDINGS.md), [gen20](research/GRAPHITI_GEN20_FINDINGS.md) | [gen20 json gate](results/graphiti_gen20_json_gate2), [gen18 sentinel](results/graphiti_gen18_sentinel) |
| **Perseus Vault v2.23.2, CLI-write + MCP hybrid recall** | `raw_product` | **Hit/all-relevant 0.958/0.958; prohibited@5 0.108** | **393/500 active after successful writes; 107 distinct-valid active-state losses; historical recoverability unknown** | [gen21](research/PERSEUS_VAULT_GEN21.md), [gen22 lifecycle addendum](research/PERSEUS_VAULT_GEN22_LIFECYCLE_ADDENDUM.md) | [gen22 lifecycle analysis](results/perseus_vault_gen22_lifecycle_analysis.json), [audited core r1](results/perseus_vault_gen21_audited_core_r1), [audited stress r1](results/perseus_vault_gen21_audited_stress_r1) |

Perseus holds one of the strongest retrieval results in the field **and** the
largest unexplained active-state loss. Both halves are the result. The frozen
Gen21 artifacts lack the lineage to call that loss destructive deletion, so it
is reported as loss with unknown historical recoverability.

## Round 2 — the point-in-time ruler and pi-observational-memory

The engine-independent ruler is frozen as `longitudinal-v1`:
[framework](research/LONGITUDINAL_POINT_IN_TIME_FRAMEWORK.md),
[fixture](research/LONGITUDINAL_V1_FIXTURE.json),
[manifest](research/LONGITUDINAL_V1_MANIFEST.json).

| Generation | Evaluated profile | Class | Evidence | Caveat | Research | Results |
|---|---|---|---|---|---|---|
| 24 | OM 3.0.4 audit + calibration | `no-score diagnostic` | native `observer.error`: extension ctx stale after session replacement | stop condition; no observation exposed | [gen24](research/OBSERVATIONAL_MEMORY_GEN24.md) | [calibration](results/observational_memory_gen24_calibration) |
| 25 | OM 3.0.4 under persistent Pi RPC | `no-score diagnostic` | three calibrations reached native quiescence; Gen24 stale-context failure avoided | calibration only; no v1 result published | [gen25](research/OBSERVATIONAL_MEMORY_GEN25_RPC.md) | [calibration](results/observational_memory_gen25_rpc_calibration) |
| 26 | OM 3.0.4 longitudinal-v1 ingestion | `raw_product` | 3/3 repetitions, 16/16 barriers, all nine checkpoints | Pi compaction declined; no agent-visible context, no retrieval score | [gen26](research/OBSERVATIONAL_MEMORY_GEN26_LONGITUDINAL.md) | [longitudinal](results/observational_memory_gen26_longitudinal) |
| 27 | OM 3.0.4 `om-context-production-v1` | `full_product_context_production` | 3 repetitions, 40/40 barriers each, 67 native `om.folded` folds; reader 28/36 under the v1 contract | zero wrong answers and zero prohibited hits; all 8 failures were citation-provenance failures under a defective citation contract | [gen27](research/OBSERVATIONAL_MEMORY_GEN27_CONTEXT_PRODUCTION.md) | [context production](results/observational_memory_gen27_context_production) |
| 28 | `om-context-production-v2` citation contract | scorer correction over Gen27 captures | same frozen responses regraded: **33/36**, 11/12 in each repetition | not a new product run and not new fixture exposure; v1 remains 28/36 as historical evidence | [gen28](research/OBSERVATIONAL_MEMORY_GEN28_CITATION_CONTRACT_V2.md) | [citation contract v2](results/observational_memory_gen28_citation_contract_v2) |

OM exposes no natural-language semantic query surface, so no Hit@k or ranking
score exists for it in any generation.

## Reading rules

Retrieval, safety, lifecycle, and reader evidence are reported separately and
are never folded into one scalar. Lifecycle loss is never rewarded as retrieval
precision. A `raw_product` row is not a product row. Configuration scope travels
with every number.
