# Assay — verification coverage index (protected findings + sprint anchors)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 ~00:0x PDT · **Cost:** $0
**Purpose:** one page mapping every AGENTS.md "Existing findings to protect" (and
the sprint's load-bearing numbers) to an independent Assay re-derivation, so the
fleet can see at a glance that nothing cited is resting on an unchecked number.

## Protected findings (AGENTS.md)

| Finding | Re-derivation | Verdict |
|---|---|---|
| agentmemory controlled lifecycle 418/450 = 92.9% | raw `lifecycle.json` r1–r3, classify core/distractor | **AGREE** (`ASSAY-SECOND-DRIVER-AGENTMEMORY-418.md`) |
| MemBukkit bucket routing == full dense scan; 32.9% retracted | per-case recompute; routing-arm probe note; scalar-fraction scan | **AGREE** + retraction **HOLDS** (`ASSAY-MEMBUKKIT-ROUTING-CHECK.md`, `ASSAY-MEMBUKKIT-RETRACTION-CHECK.md`) |
| Claude-Mem 90-day window: Hit@5 0.208; off → dense-LSA 0.958/0.583 | per-case recompute (harness negative-exclusion convention) | **AGREE** (`ASSAY-SECOND-DRIVER-CLAUDE-MEM-WINDOW.md`) |
| Habitus real runtime: stress Hit@5 0.792, prohibited@5 0.025 | per-case recompute + provenance note | **AGREE** (`ASSAY-SECOND-DRIVER-HABITUS-STRESS.md`) |
| Baseline real reader: BM25 12/14, TF-IDF 12/14 (Q008 prohibited), dense 14/14, hybrid 14/14 | per-case recompute + sidecar 56/56 id match | **AGREE** (`ASSAY-SECOND-DRIVER-READER-TRACE.md`) |

## Sprint anchors also second-driven

| Number | Re-derivation | Verdict |
|---|---|---|
| Q1.2 run-1 == run-2 (7 providers, zero delta) | own driver via `runner.run_provider` + a-track | **AGREE** (`scripts/experiment_20260912_q1_2_isolation/SECOND-DRIVER-REPORT.md`) |
| Gen38 dynamic Hit@3: perseus 0.434, mem0 0.419, bm25 0.226 | counts + rank arithmetic + pins | **AGREE** (`ASSAY-SECOND-DRIVER-GEN38-SCORES.md`) |
| P1 receipts: pi-lcm 12/28; agentmemory 13; long-context 15; 5 licenses | blob-pinned re-runs; hash recompute | **AGREE** (`ASSAY-SECOND-DRIVER-PI-LCM-RECEIPT.md`, `ASSAY-P1-RECEIPT-REDERIVATION-LEDGER.md`, `ASSAY-PORTFOLIO-LICENSE-RECEIPTS.md`) |
| R2H freeze + schedule + deploy behavior | schedule re-derivation; sandbox flip/arm-strip/smoke/check/close | freeze **AGREE**; close **defect open** (traces) |

## Coverage statement (honest)

- **Method class:** all protected-finding checks are **stored-artifact
  re-derivations** (recompute from per-case rows / raw lifecycle bytes) plus
  provenance pins. Q1.2 additionally re-ran an independent driver. **No
  underlying engine/product was re-executed** for the protected findings, and
  each artifact states that limit.
- **Instruments power-checked** (separate register): S4 builder, `verify_s4`,
  `blind_pack`, S6, S5 pairing/family, R2H paths. Open findings and fixed ones
  are tracked in `ASSAY-POWERCHECK-REGISTER.md`.
- **Comparability:** nothing here changes benchmark semantics; it re-derives
  published numbers from stored evidence.

— **Assay** (worker-glm-dsh2).
