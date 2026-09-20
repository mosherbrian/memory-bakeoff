# muse-drafter: Phase-B frontier-harvest closeout index (spark pulse 2026-09-14)

All 8 named benchmarks carded + companions; license/grounding status per card. No score import anywhere.

| # | Card | Code license | Data terms | Grounding |
|---|---|---|---|---|
| 1 | MemOps (`CANDIDATE-CARD-MEMOPS.md`) | MIT (`MemTensor/MemOps`) | generated in-repo, no third-party corpus | design ref (lifecycle-ops trace schema) |
| 2 | StreamMemBench | MIT code; data under upstream EgoLife terms | EgoLife terms (verified in EGOLIFE note) | design ref (two-step commit ablation) |
| 3 | STALE + Supersede | STALE MIT; Supersede Apache-2.0 | STALE CC-BY-4.0 (+LongMemEval MIT distractors); Supersede data MIT (LongMemEval KU) | design ref (implicit-conflict class, SR/PR/IPA probes) |
| 4 | MemSecBench + GateMem | MemSecBench: none (no artifact); GateMem MIT | GateMem data CC-BY-4.0 | design ref only (Write→Execute→Forget; governance MGS shape) |
| 5 | HaluMem | CC-BY-NC-ND-4.0 (repo + HF dataset, ND bars adapted sharing) | same | design ref (operation-level extraction/updating/QA split; `is_update` lineage analogue) |
| 6 | StateMemBench | none (unreleased, watch open) | none | design ref (fixed-by-construction supersession probes) |
| 7 | LongMemEval-V2 | repo (see LMEV2 license note); paper CC-BY-4.0 | see data-license note | design ref (context-gathering formulation; gotcha/premise item shapes) |
| 8 | EvoMemBench (+EvoArena/EvoMem) | EvoMemBench: none (ARR); EvoArena: none (license "to be added", ARR) | per-source terms if adapters ever built | design ref (scope×content grid; git-like patch trail + chain accuracy) |

Reuse-green code lanes: MemOps, GateMem, STALE, Supersede, StreamMemBench-harness (MIT/Apache-2.0). Read-only/ARR: EvoMemBench, EvoArena, HaluMem-adaptations, MemSecBench (no artifact), StateMemBench (no artifact).
Known residuals (other owners): QUEUE row 38 "row 36 HaluMem" text (Corvid); MEMOPS implicit card-1 numbering (trivial, left as-is per Verity).

## Fan-out candidates — 5 draft cards filed 2026-09-14 (post-harvest, vocabulary pass)

| # | Card | Code license | Data terms | Grounding |
|---|---|---|---|---|
| F1 | CodeTracer / CodeTraceBench (`CANDIDATE-CARD-CODECRACER.md`) | **MIT** (repo) | **MIT** (HF `NJU-LINK/CodeTraceBench`) | design ref (trace tree + failure-onset localization; G4/G5 + provenance) |
| F2 | CSTM-Bench (`CANDIDATE-CARD-CSTM-BENCH.md`) | not located (dataset release only) | **MIT** (HF `intrinsec-ai/cstm-bench`) | design ref (cross-session threat taxonomy; `CSR_prefix` serving-stability metric) |
| F3 | PrecisionMemBench (`CANDIDATE-CARD-PRECISIONMEMBENCH.md`) | **MIT** (repo) | **MIT** (HF `tenurehq/precisionmembench`) | retrieval method ref (required+prohibited belief IDs); **vendor-operated**; second-driver receipts exist |
| F4 | MemoryArena (`CANDIDATE-CARD-MEMORYARENA.md`) | **NO LICENSE** (preview, ARR) | **CC-BY-4.0** (HF `ZexueHe/memoryarena`) | data-only design ref (multi-session Memory–Agent–Environment loop) |
| F5 | BeliefShift (`CANDIDATE-CARD-BELIEFSHIFT.md`) | **none** (no artifact) | none | taxonomy ref only (evidence-driven revision vs model-induced drift; CRR shape) |

Fan-out reuse-green: CodeTracer (both lanes), CSTM-Bench (data), MemoryArena (data only), PrecisionMemBench (code, but vendor-operated). Unreleased/ARR: BeliefShift, MemoryArena code, CSTM code.

$0, synthesis of existing notes, no Muse batching. — muse-drafter (Spark)
