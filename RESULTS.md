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

## Round 2 — the point-in-time ruler, pi-observational-memory, and Perseus

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
| 29 | Perseus Vault v2.23.2, operator CLI write + native hybrid recall | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance on every hit, transaction-time belief answered correctly | valid-time is collinear with transaction time in this write path, so every corrected-history and late-history case fails; configuration collapse and stale persistence are real; nothing was lost at 16 records | [gen29](research/PERSEUS_VAULT_GEN29_LONGITUDINAL.md) | [longitudinal](results/perseus_vault_gen29_longitudinal) |
| 30 | Perseus Vault v2.23.2, agent-facing MCP `remember` + admission review | `no-score diagnostic` | post-hoc write-surface ablation, **blocked**: `remember` honours a retroactive `valid_from`, but the approval that makes a record serveable resets it to the approval instant | serveable and retroactive are mutually exclusive in this version, so no independent application-time axis exists to score; Gen29 stands unchanged | [gen30](research/PERSEUS_VAULT_GEN30_MCP_VALID_TIME_ABLATION.md) | [admission probe](results/perseus_vault_gen30_mcp_valid_time) |
| 31 | Hindsight v0.9.2, raw/no-LLM retain + native hybrid recall with learned CPU reranker | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance on every hit, and **zero correction failure and zero history erasure** — a vantage-point query reaches the earlier state | scope collapse and belief/truth confusion appear where Perseus had none; the event-time axis (`occurred_*`) is unreachable in the raw profile, so mention time is the only axis | [gen31](research/HINDSIGHT_GEN31_LONGITUDINAL.md) | [longitudinal](results/hindsight_gen31_longitudinal) |
| 32 | Mem0 2.0.19, raw `Memory.add(infer=False)` + embedded Qdrant dense+BM25 | `raw_product` | 3 identical repetitions against `longitudinal-v1`: zero future leakage, exact provenance, and **all seven cross-engine failure classes reproduced in an engine with no temporal retrieval surface at all** | one extra `stale_persistence` (LQ20) is the direct cost of having no as-of filter; Mem0 can filter on scope metadata but the scored Gen10 identity deliberately does not | [gen32](research/MEM0_GEN32_LONGITUDINAL.md) | [longitudinal](results/mem0_gen32_longitudinal) |
| 33 | agentmemory 0.9.29, native remember + smart-search with **write-time supersession enabled** | `raw_product` | 3 identical repetitions: retirement activates twice per run and **halves configuration collapse** (6→3) and reduces false persistence (9→6) | it is the only engine that falsely supersedes (lifecycle `false_supersession` 3); the rule is lexical Jaccard >0.7 over tokens longer than two characters, so `C1`/`C2` are invisible to it | [gen33](research/AGENTMEMORY_GEN33_LONGITUDINAL.md) | [longitudinal](results/agentmemory_gen33_longitudinal) |
| 34 | Round-2 reporting-layer integrity audit (no product run) | `no-score diagnostic` | every cross-engine number rebuilt from leaf evidence through a fail-closed reporting layer; **all Round-2 conclusions survive independent derivation unchanged** | the old summarisers carry 45 default-fallback patterns where missing evidence becomes a number; historical scripts left intact, future publication routes through the common reporter | [gen34](research/ROUND2_REPORTING_INTEGRITY_GEN34.md) | [ledger](results/round2_gen34_integrity) |

OM exposes no natural-language semantic query surface, so no Hit@k or ranking
score exists for it in any generation.

Gen29 is the first Round-2 contestant run against the frozen ruler. Its numbers
answer a different question from Gen27/28 and are not comparable to them: OM has
no query surface and Perseus does.

Gen29, Gen31, Gen32 and Gen33 are the Round-2 contestants so far. Hindsight repairs
exactly what Perseus's collapsed time axis broke and breaks two things Perseus got
right; Mem0, which has no temporal retrieval surface at all, then reproduces all
seven of the classes the first two shared — five of them at identical counts.

Gen33 moved the one variable the other three held fixed. agentmemory retires on its
own, and the trade is visible: configuration collapse halves, false persistence
falls, stale persistence is unchanged, and it becomes the only engine that falsely
supersedes a record that was still true. Neither architecture is safe — append
everything and you cannot say what is current; retire on similarity and you delete
what was true. This is a contrast across products, not a controlled experiment
within one.

**Correction, 2026-09-03, verified in Gen34.** Gen31's originally published
lifecycle numbers were never measured: three SQL queries in its collector failed
silently and returned plausible empty answers, and the "false supersession 0"
claim for the append-only engines was read from the case-level stream, where that
class cannot appear. Gen31 was re-run with a collector that fails loudly — its
case results are byte-identical and its lifecycle is genuinely clean.

Gen34 then rebuilt every Round-2 cross-engine number from committed leaf evidence
through a fail-closed reporting layer, replaying the frozen lifecycle scorer and
reconciling against stored aggregates. **Every conclusion survived unchanged**,
including the five identical classes and the retirement trade. The append-only
engines' `false_supersession 0` is now MEASURED_ZERO from the lifecycle scorer
rather than absent from the wrong table: the statement is the same, its evidential
basis is entirely different.

## Reading rules

Retrieval, safety, lifecycle, and reader evidence are reported separately and
are never folded into one scalar. Lifecycle loss is never rewarded as retrieval
precision. A `raw_product` row is not a product row. Configuration scope travels
with every number.
