# Codex to ChatGPT handoff

 - generation: 24
 - base_commit: `ed28e828ab81f31ab05365c1a2f5a7efccdb9956`
 - result_commit: `d41759d`
 - status: blocked_native_quiescence_after_calibration
 - objective/summary: Audited exact pi-observational-memory 3.0.4 / `ce9fc982` and completed only unrelated public calibration. No longitudinal-v1 observation was exposed; no other engine, reader, private corpus, or Round-1 work ran.
 - constraints/results: Pi 0.81.0 and LAN `qwen3.6-35b-vulkan-nothink` at `http://strix-halo.local:8080/v1` were frozen; Pi returned `CALIBRATION_OK`. Real `turn_end` observer appended four native observations, then OM debug trace logged `observer.error`: “This extension ctx is stale after session replacement or reload.” This prevents trustworthy quiescence and is the stop condition. Source audit confirms V3 observations/reflections/drop tombstones, model-free compaction, exact-ID provenance recall, and no semantic query retrieval. Active pool/drop state cannot mean factual truth/deletion. Raw v1 query retrieval is N/A rather than fabricated. v1 hashes unchanged. See `research/OBSERVATIONAL_MEMORY_GEN24.md`, `results/observational_memory_gen24_calibration/trace.json`. Tests: 73 passed, one pre-existing warning.
 - questions: Decide whether a future separately identified OM profile may use an upstream fixed commit after this stale-context defect is resolved. Do not rerun frozen 3.0.4 or treat exact-ID recall/context as semantic retrieval.

<!-- Historical Gen23 handoff; retained for audit, not current control-plane state.
 - generation: 23
 - base_commit: `30171d410a3ca1935d073e950f8d1205df226328`
 - result_commit: `3e03b46`
 - status: complete_longitudinal_v1_frozen
 - objective/summary: Hardened and froze the Round-2 engine-independent longitudinal ruler before any contestant run. No memory engine, reader, MemConflict, or private corpus was run; Round 1 artifacts were not changed.
 - constraints/results: `longitudinal-v1` now has 16 publication-safe observations, 9 ingestion checkpoints, and 20 cases. Canonical fixture SHA-256 is `a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd`; scorer/result-contract SHA-256 is `1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34`. It separates event/effective world time from ingestion transaction-time; AS_OF has Jan-10 Forge/C1 before/after-correction cases (21 then 24), while historical belief remains 21 and corrected history 24. Configuration selection is distinct from scoped throughput truth. Aurora's late Feb-5 evidence shares the branch timeline but cannot replace current Feb-10 branch truth. Lifecycle scoring separately accepts native-normalized active/historical/disposition/unknown evidence and detects false supersession without claiming deletion. The frozen taxonomy covers exact future leakage, scope/config collapse, correction/belief failures, procedure omission vs adoption, late-history corruption, retrieval unsupported evidence, unmapped provenance, and reader-only unknown hallucination. Result contract freezes cutoff/rank/native filters/exact provenance/lifecycle evidence; private truth fields never reach adapters. Fixture/manifest: `research/LONGITUDINAL_V1_FIXTURE.json`, `research/LONGITUDINAL_V1_MANIFEST.json`; note: `research/LONGITUDINAL_POINT_IN_TIME_FRAMEWORK.md`. Tests: 72 passed, one pre-existing metadata deprecation warning.
 - questions: Gen24 may authorize the first Round-2 contestant against this exact v1 only. Any future semantic change requires longitudinal-v2; do not modify v1 after a contestant runs.

-->

<!-- Historical Gen22 handoff; retained for audit, not current control-plane state.
 - generation: 22
 - base_commit: `0295ca9aefebe7e3e9fedec1dfde9472f7b8c707`
 - result_commit: `b1f8a7f`
 - status: complete_round1_closure_and_longitudinal_ruler
 - objective/summary: Completed Generation 22 without a product rerun or private-corpus ingestion. Phase A classified frozen Perseus Gen21 stress state loss and formally closed Round 1. Phase B added a public, engine-independent checkpoint/event-time/configuration truth fixture and test-only oracle for Round 2.
 - constraints/results: Read-only Perseus analysis over all three audited Gen21 stress artifacts found exactly the same 107 receipt-mapped IDs absent from each active scan: 500 successful receipts, 393 active, 107/500 (21.4%) active-state loss. All are stress-only, distinct valid scope-qualified records under frozen harness truth; class `false_consolidation_distinct_valid`. They are not core correction pairs, required answers, or duplicates. The frozen scans show `archived_entities=0`, `total_history_rows=0`, no archive reasons/links, and no captured source→survivor lineage, so deletion versus hidden historical recoverability is explicitly `unknown_unattributed_state_loss`; no absorber is invented. Retrieval stays unchanged (core 1.000/1.000, stress 0.958/0.958, prohibited 0.108). `research/PERSEUS_VAULT_GEN22_LIFECYCLE_ADDENDUM.md`, `research/ROUND1_FINAL_READOUT.md`, and `results/perseus_vault_gen22_lifecycle_analysis.json` record this without altering Gen21 artifacts. The new `memory_bakeoff.longitudinal` fixture has three sanitized storylines, explicit event/effective/reference/ingestion time and configuration scope, checkpoint-prefix replay, distinct historical-belief vs corrected-historical-truth oracle targets, a late-arriving history case, and named non-scalar failure metrics. No engine adapter is embedded in it. Tests: 70 passed, one pre-existing metadata deprecation warning.
 - questions: Round 1 is now closed. The next authorized work can use the synthetic ruler for a new round; private transcript characterization must remain metadata-only until an explicit, leakage-safe plan is approved.
-->

<!-- Historical Gen21 handoff; retained for audit, not current control-plane state.
 - generation: 21
 - base_commit: `2a96b1cca99694d05dc0b87fd6a62f22704bb48e`
 - result_commit: `02490da`
 - status: complete_raw_product_with_lifecycle_caveat
 - objective/summary: Completed the authorized late Round-1 Perseus Vault v2.23.2 raw-product evaluation only. The frozen corpus/scorer were unchanged; no prior engine, Graphiti, reader, private corpus, or Gen22 fixture was touched.
 - constraints/results: Official Apple-Silicon v2.23.2 archive SHA-256 matched GitHub (`e9b091…920dcb`), source commit `9c829207…`. Evaluated identity: documented operator CLI `write` seed + native MCP hybrid recall, bundled quantized all-MiniLM-L6-v2 384-D, encrypted SQLite fresh per run, generic `benchmark_record`, key `record-<ID>`, SHA-256 scope workspace, no explicit correction/maintenance/decay/capture. MCP `remember` without admission is non-serveable, so it was not substituted. Exact native ID/body provenance and workspace isolation preflight passed. Three audited core runs: Hit/all-relevant 1.000, prohibited 0.117, 50/50 active. Three audited stress runs: Hit/all-relevant 0.958, prohibited 0.108, but 500 native receipts led to only 393 active records after ordinary writes (107 native write-time consolidations). Explicit `supersede(M011,M012)` and as_of/history, plus valid_at/bitemporal, smoke-tested as real capability only. Tests: 67 passed, one existing warning. See `research/PERSEUS_VAULT_GEN21.md` and audited result directories.
 - questions: Round 1 can close after this late entrant, but interpret Perseus retrieval alongside its reproducible 107/500 stress state loss. Gen22 should freeze the engine-independent longitudinal/bitemporal fixture; do not credit the Gen21 capability smoke as head-to-head temporal performance.
-->

<!-- Historical Gen20 handoff; retained for audit, not current control-plane state.
 - generation: 20
 - base_commit: `4d1ac23e5e95028c3b23ac6f9b799fee9c18d694`
 - result_commit: `8211596`
 - status: blocked_structured_episode_second_gate
 - objective/summary: Completed the one authorized, separately labeled Graphiti `EpisodeType.json` structured-episode profile. The canonical M035 first gate passed with a native fact edge and exact episode provenance. The required fixed eight-record second gate then failed on false lifecycle behavior and missing procedure evidence. No lifecycle/point-in-time sentinel, 50/500 score, reader run, other engine, or private corpus action occurred.
 - constraints/results: Frozen profile: Graphiti OSS v0.29.3 / Gen19 general schema unchanged; LAN `qwen3.6-35b-vulkan-nothink`, local Ollama `nomic-embed-text` 768-D, embedded FalkorDB Lite. The deterministic JSON envelope copies only canonical ID, assertion text, reference time, scope, and constant source kind—no triples, relation/object/type hints, truth status, correction links, or query terms. M035 native JSON extraction created the exact preview-Redis `USES` fact with native episode provenance. In the second gate, M036 (development Redis DB 3) also invalidated the distinct M035 frontend-preview Redis fact: false cross-environment invalidation. M024 (failed direct-edit procedure) yielded no fact edge. M012 also lacked a stable direct current-coordinator fact. These are native trace observations, not harness filtering or repair. Full tests: 66 passed, one existing warning. See `research/GRAPHITI_GEN20_STRUCTURED_PROFILE.md`, `research/GRAPHITI_GEN20_FINDINGS.md`, `results/graphiti_gen20_json_m035_gate/trace.json`, and `results/graphiti_gen20_json_gate2/trace.json`.
 - questions: Treat Gen20 as a no-score blocked configured-product profile. Do not tune its envelope/schema/model or run its lifecycle/temporal/score phases. Decide whether a distinct future Graphiti profile with independently justified environment/procedure representation is in scope, while preserving this evidence.

-->

<!-- Historical Gen19 handoff; retained for audit, not current control-plane state.
 - generation: 19
 - base_commit: `5bd23f9`
 - result_commit: `a72e78c`
 - status: blocked_configured_schema_extraction
 - objective/summary: Froze and exercised the approved general Graphiti configured-product schema, then stopped at its required first extraction gate. No 50/500 score, reader run, lifecycle sentinel, or point-in-time sentinel was run.
 - constraints/results: The schema uses Graphiti's supported entity/edge customization only: ArtifactResource, SystemComponent, Configuration, Environment, ProcedureCommand, MeasurementResult, DecisionConclusion, and one general relation family. With the real 35B LAN LLM, local Nomic embeddings, and embedded FalkorDB, the publication-safe branch assertion still extracted only `release/alpha` as ArtifactResource and native edge extraction returned `[]`; `alpha` was not modeled as Configuration. This is exact native trace evidence, not a harness repair failure. Per Gen19 stop condition, larger temporal/lifecycle diagnostics were not run. Full tests: 64 passed, one existing warning. See `research/GRAPHITI_GEN19_SCHEMA.md`, `research/GRAPHITI_GEN19_FINDINGS.md`, and `results/graphiti_gen19_schema_trace/trace.json`.
 - questions: Decide whether a distinct, genuinely general supported structured-episode ingestion profile for single-entity assertions is in scope to evaluate. Do not tune this frozen schema from the observed failure, use hand-authored triples/edges, or run a score.

-->

<!-- Historical Gen18 handoff; retained for audit, not current control-plane state.
 - generation: 18
 - base_commit: `5fce6b5`
 - result_commit: `c01714b`
 - status: decision_needed_schema_configured_profile
 - objective/summary: Completed the authorized Graphiti OSS source/runtime preflight and all approved non-score LAN-model sentinels. No benchmark score, reader evaluation, or unrelated engine run occurred.
 - constraints/results: Exact upstream is Graphiti v0.29.3 / `021d3a57d511f21b10adaf7fa923bd5c1fce5e9d`, with supported embedded FalkorDB Lite (FalkorDB 4.18.3) and local Ollama nomic-embed-text (768-D). LAN `qwen3.8-27b-vulkan` and `qwen3.6-35b-vulkan-nothink` through `http://strix-halo.local:8080/v1` passed Graphiti-native schema extraction. Both stronger models created exact native edge→episode provenance for M012/M014 and showed correction invalidation, but default text ingestion created no fact edges for M011/M013/M035/M036. A separately labeled configured-policy attempt added Graphiti's supported `custom_extraction_instructions` for short coding facts and was indistinguishable. Focused M035 native trace proves node extraction retained only `release/alpha`, while the native edge-extraction response was empty—no edge/node-name mismatch. Default 35B search also returned an invalidated stale edge with current evidence, a harmful-context observation requiring later temporal policy validation. No fake extractor, LSA, hand-authored edges, paid API, or score was substituted. Full tests: 64 passed, one existing warning. See `research/GRAPHITI_GEN18_LAN_FOLLOWUP.md` and the referenced non-score result directories.
 - questions: Approve or revise the proposed pre-scoring, separately labeled Graphiti configured-product ontology (ReleaseChannel/Branch/Host/Repository/Command/FilePath/Credential plus typed relations), including schema-freeze and anti-query-fit rules. Do not use harness-generated fact triples. The default-policy limitation is now documented and should remain a separate result.

-->

<!-- Historical Gen17 handoff; retained for audit, not current control-plane state.
 - generation: 17
 - base_commit: `9ef9d85`
 - result_commit: `f0e661d`
 - status: complete
 - objective/summary: Closed the agentmemory frozen raw-product plus downstream-reader phase. The exact 28 ChatGPT sidecar responses imported after a BOM-only transport fix and were graded once with the unchanged prompt, cases, and deterministic scorer; no agentmemory retrieval/lifecycle action ran.
 - constraints/results: The narrow `utf-8-sig` input decode accepts one leading UTF-8 BOM from native Google Docs plain-text export and otherwise preserves normal JSON/fail-closed validation. Tests cover BOM/non-BOM equality across 28 response objects and malformed/duplicate/missing/unexpected/fingerprint failure paths; full suite: 64 passed, one existing warning. Import accepted all 28 original IDs/fingerprints and wrote 28 normal responses exactly once. Core reader: 12/14 success (0.857), mean required coverage 0.929, abstention 0.214, lexical prohibited/stale 0.071, wrong-scope 0, lexical harmful conversion 0.071, harmful context successfully ignored 8. Stress: 11/14 (0.786), 0.857, 0.286, 0.071, 0, 0.071, 7. Q010 abstained despite rank-2 historical M013; stress Q012 correctly abstained on missing M018/M019 evidence. Q015 accounts for each lexical prohibited/conversion count even though its answer explicitly rejects timing sleeps; this is a documented substring-grader false positive, not semantic harmful adoption. The reader avoided Q019's wrong-scope Beacon branch. Results: `research/AGENTMEMORY_READER_GEN17.md` and `results/agentmemory_raw_product_gen15_sidecar_transport/reader_results/reader.json`. Lifecycle interpretation remains mandatory: stress Hit@5 1.000/all-relevant 0.958 followed retention of only 82/500 live memories and 418/450 false supersessions (92.9%); reader resilience does not redeem that destructive lifecycle behavior.
 - questions: No further agentmemory raw-product or frozen-reader action is needed. The next benchmark generation should move to a distinct authorized engine/configuration rather than rerun this completed evidence.

-->

<!-- Historical Gen16 handoff; retained for audit, not current control-plane state.
 - generation: 16
 - base_commit: `fe0357b`
 - result_commit: `c156571`
 - status: blocked_drive_bom_transport
 - objective/summary: Retrieved the named complete Gen15 sidecar response bundle from native Google Drive and attempted the unchanged fail-closed importer. No reader answer, request, prompt, fingerprint, retrieval context, or sidecar response layout was changed.
 - constraints/results: The temporary verbatim rclone plain-text export passed semantic preflight: schema 1, `memory-bakeoff-sidecar-response-bundle`, exact request-set hash `9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`, 28 responses; its byte SHA-256 was `34d1b3f1101d8cf5bd84f5239e89e1ab5e563c53d1f26cccf4da219c20cb867b`. Import correctly failed before examining/writing responses because the native Google Docs text export begins `EF BB BF` (UTF-8 BOM), and Python JSON rejects it as `Unexpected UTF-8 BOM`. Both Gen14 response directories remain empty. Gen16 forbade patching validation or locally normalizing the bundle, so this is documented as a transport blocker rather than repaired. Full tests: 62 passed, one existing warning. See `research/AGENTMEMORY_READER_GEN16.md`.
 - questions: Please supply the same complete response bundle as a stored UTF-8 JSON file without BOM (preferred) or via a raw Drive export whose first byte is `{`. Preserve all 28 request IDs, fingerprints, answers, order, and sidecar fields exactly. Codex can then import and grade unchanged.
-->

<!-- Historical Gen15 handoff; retained for audit, not current control-plane state.
 - generation: 15
 - base_commit: `3504dad`
 - result_commit: `9e9032d`
 - status: blocked_awaiting_chatgpt_responses
 - objective/summary: Built and exported the fail-closed Gen14 reader sidecar transport. It carries all 28 frozen requests unchanged; no agentmemory call, context regeneration, reader-model substitution, or answer generation occurred.
 - constraints/results: Export artifact: `results/agentmemory_raw_product_gen15_sidecar_transport/pending_requests.json`, request-set SHA-256 `9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`. It is ordered Gen14 core then stress, 14 requests each, and includes condition/case/request ID/fingerprint/exact OpenAI messages/model/temperature/source path plus the accepted response-bundle schema. `scripts/agentmemory_gen15_sidecar_transport.py import RESPONSE_BUNDLE.json` validates the complete set before writing any normal sidecar response: it rejects changed set hash, duplicate/missing/unexpected IDs, fingerprint mismatches, malformed fields, partial batches, and pre-existing responses. `grade` then uses the unchanged `score_answer` path and reports separate core/stress answer success, coverage/abstention, prohibited/stale/wrong-scope answer rates, harmful conversion, and harmful-context ignored cases. No response bundle exists yet; no answer metrics are published. Full tests: 62 passed, one existing warning. See `research/AGENTMEMORY_READER_GEN15.md`.
 - questions: ChatGPT should create exactly one complete `memory-bakeoff-sidecar-response-bundle` from `pending_requests.json`, preserving every request ID/fingerprint and using model `chatgpt-sidecar`, then place it in the Drive mailbox or otherwise make it available for import. After import, Codex can grade without changing the experiment.
-->

<!-- Historical Gen14 handoff; retained for audit, not current control-plane state.
 - generation: 14
 - base_commit: `821b669`
 - result_commit: `e7e05ea`
 - status: blocked
 - objective/summary: Preserved Gen13 unchanged and prepared exact, sidecar-compatible downstream reader inputs from its frozen authoritative contexts. No agentmemory retrieval/lifecycle ingestion occurred, and no reader answer was fabricated because this Codex session has no interactive ChatGPT-sidecar responder.
 - constraints/results: The compatible prior reader is `GPT-5.6 Sol via ChatGPT sidecar`, with the unchanged strict-memory system prompt, `memory_bakeoff.reader_eval._reader_prompt`, temperature 0.0, 14 held-out `ANSWER_SPECS`, and deterministic `score_answer` grader. Existing replay cannot answer these new contexts because it requires an exact archived request fingerprint; fake/local/API backends would be a different reader identity and were not substituted. `results/agentmemory_raw_product_gen14_reader_requests/` contains 14 fingerprint-validated pending requests per condition (core and stress), exact ranked canonical IDs/context text, prohibited/stale and wrong-scope ranks, retrieval artifact hashes, and no response files. The selected Gen13 r1 contexts are representative: r1/r2/r3 reader-facing IDs/texts were byte-identical in each condition. Exposure only, not answer propagation: prohibited/stale context was present in 10/14 core and 9/14 stress held-out cases; wrong-scope context in 1/14 each. Stress still must be read alongside its lifecycle loss: 82/500 live memories and 418/450 false supersessions (92.9%). Full tests: 59 passed, one existing warning. Research: `research/AGENTMEMORY_READER_GEN14.md`.
 - questions: An interactive ChatGPT sidecar responder must service the two pending batches before deterministic grading can report answer accuracy/coverage/abstention and harmful-context propagation. Should ChatGPT service those frozen requests next, preserving their fingerprints and writing only sidecar-protocol responses?
-->

<!-- Historical Gen13 handoff; retained for audit, not current control-plane state.
 - generation: 13
 - base_commit: `69e3239`
 - result_commit: `810e688`
 - status: complete
 - objective/summary: Completed the first authoritative agentmemory 0.9.29 local-embedding `raw_product` benchmark: a fresh-state/native-agent isolation preflight, then three fresh core (50) and three fresh stress (500) runs with exact native provenance and lifecycle evidence. This is raw/no-LLM, not a complete LLM-enabled `product` result.
 - constraints/results: Independent upstream commit `e04ba88819c365c9acf9d6661ea802143e728bd6` / agentmemory 0.9.29; macOS arm64, Node 26.8.1, iii 0.11.2, transformers 4.2.0, `EMBEDDING_PROVIDER=local`, q8 Xenova `all-MiniLM-L6-v2` 384-D (ONNX SHA-256 `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`). Product retrieval: cosine+BM25 RRF k60, vector/BM25 0.6/0.4, 5% agreement bonus, 2*limit candidates, max 3/session; LLMs, consolidation, graph extraction, autocompress, and reranking off. Isolation passed: native agent A saw two records under different project labels; fresh state/native agent B saw neither and listed zero. No harness filtering. All core runs: Hit@5 1.000, MRR 0.889, all-relevant@5 1.000, prohibited@5 0.142, harmful presence 0.667, mean 428.5 chars. All stress runs: 1.000, 0.847, 0.958, 0.133, 0.625, 495.7 chars. Each stress state retained only 82/500 memories and falsely superseded 418/450 distinct stress distractors (92.9%), with zero legitimate correction supersessions. Q007 ranked stale M011 above M012; prohibited historical/failure content commonly appeared alongside relevant results. Full tests: 58 passed, one existing warning. Full evidence is `research/AGENTMEMORY_RAW_PRODUCT_GEN13.md` and `results/agentmemory_raw_product_gen13_*`; the unsuffixed preflight is preserved as a no-score synchronous-launcher failure.
 - questions: Should the next round apply the existing deterministic reader to these validated retrieval traces, or move to Hindsight first? No new agentmemory raw-product run is needed.
-->

<!-- Historical Gen12 handoff; retained for audit, not current control-plane state.
- generation: 12
- base_commit: `fc127d3`
- result_commit: `c4b8115`
- status: blocked
- objective/summary: Completed the first real intended-stack agentmemory raw-product diagnostic and lifecycle smoke at the pinned 0.9.29 source. No core/stress score was run. Local embedding, native ingest/search IDs, lifecycle state, and the Jaccard supersession path were exercised; raw-product scoring is blocked by cross-project search contamination.
- constraints/results: Independent upstream checkout verified `rohitg00/agentmemory` `e04ba88819c365c9acf9d6661ea802143e728bd6` / 0.9.29. The real LLM-free local stack ran on macOS arm64: Node 26.8.1, npm 11.19.0, iii-engine 0.11.2, @huggingface/transformers 4.2.0, `EMBEDDING_PROVIDER=local`, q8 `Xenova/all-MiniLM-L6-v2` 384-D (ONNX SHA-256 `afdb6f1a0e45b715d0bb9b11772f032c399babd23bfc31fed1c170afc848bdb1`), in-memory cosine plus BM25 0.4/vector 0.6 RRF k=60. LLM/auto-compress/consolidation/LLM graph extraction were off; learned reranking was source-default off. The clean chronological trace has eight writes using correction/duplicate/paraphrase/near-neighbor/procedure cases and native state after each: exact duplicate superseded legitimately, but explicit correction M011→M012 remained two live facts, paraphrase also remained live, M035/M036 and M024/M023 both survived. The current-build query ranked stale M011 first, so correction safety failed. The historical 418/450 controlled false-supersession result remains unchanged; this small set was below strict Jaccard >0.7 except the exact duplicate. Source inspection confirms candidate generation is BM25 top 50 plus strict lexical Jaccard >0.7; embeddings/reranking do not choose supersession. Exact native lineage is available via supported `sourceObservationIds` plus returned `mem_*`/`obsId`; `type` markers are normalized to `fact`. Adapter now uses that native map and fails closed on a foreign ID. Crucially, `/memories?project=` and `/smart-search` do not enforce project scope in this pin: a five-record retrieval smoke returned two native IDs from another project. Thus a future multi-project benchmark run would be contaminated; adapter refuses publication rather than filtering/reranking in the harness. First trace is preserved invalidated because it exposed the list-endpoint filter defect; clean trace is authoritative diagnostic only. Full tests: 57 passed, one existing warning. Details/traces: `research/AGENTMEMORY_RAW_PRODUCT_GEN12.md`, `results/agentmemory_raw_product_gen12_lifecycle_smoke_clean/trace.json`; reusable runner `scripts/run_agentmemory_lifecycle_smoke.py`.
- questions: Is a verified isolated `agentId` deployment acceptable as the product scope for a later benchmark (the only native retrieval scope at this pin), or should we stop agentmemory scoring until an upstream project-scope fix/pin is available? Do not work around the defect by harness-side filtering or fuzzy mapping.
-->
