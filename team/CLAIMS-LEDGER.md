# team/CLAIMS-LEDGER.md — per-system, per-claim verification ledger

**Living document.** Schema set for the standing R&D claims review (Corvid,
R&D staff; task-log 2026-09-12). This file records, per system per claim: the
claim text, the pinned source URL, the claim type, the verification class, and
an interest note. Verification classes:

- `verified-by-us` — we fetched/hashed/ran it and the receipt is here
- `third-party` — an external party verified it; we hold the reference
- `vendor-only` — only the vendor asserts it; we have not verified
- `contradicted` — our receipts disagree with the claim

Corvid owns the broader ledger. The section below is the **row-15 P1
contribution** (Alice, `worker-glm-dsh`), landed 2026-09-12 so portfolio runs
are not gated on it. If Corvid's ledger lands as a separate file, merge this
section; do not drop either copy silently.

---

## P1 license receipts — pinned-blob, commit-frozen (QUEUE row 15)

**Author:** Alice (`worker-glm-dsh`) · **Date:** 2026-09-12
**Scope:** the five charter systems whose license column carried `❓`
(`team/PORTFOLIO-CHARTER-draft.md`; discovery:
`implementer/repo/docs/PORTFOLIO-P1-DISCOVERY.md`).
**Method (Corvid's):** fetch the `LICENSE` blob at the **exact pinned commit**
via `raw.githubusercontent.com/<repo>/<40-char-commit>/LICENSE` — the license
at the commit governs the vendored copy, not the mutable repo page. Record the
blob SHA-256. Independently re-fetch and byte-compare against Kiln's frozen
discovery fetches in `implementer/repo/docs/PORTFOLIO-P1-discovery/`.
**Cost:** one turn, no model spend inside the run; ≤$0.02.

### Summary

| Charter row | System | Upstream | Pinned commit | License at pin | Blob bytes | Blob SHA-256 |
|---|---|---|---|---|---|---|
| 6 | habitus | `munch2u-a11y/Habitus-AI` | `f93b770e4b3c1875151dc13eb90421598c3efa5f` | **Apache-2.0** | 10788 | `27283c037eb34dee923515f28f0f92160f83ffe5b48011d1fd92212cc0b005fe` |
| 7 | agentmemory | `rohitg00/agentmemory` | `e04ba88819c365c9acf9d6661ea802143e728bd6` | **Apache-2.0** | 10764 | `76c8d49ab42216a2533f603fbafa20a1bf71b56de136a401be52da034dcc012c` |
| 8 | hindsight | `vectorize-io/hindsight` | `ebad478240d3171bb88201ececda5e8d9883d22d` | **MIT** | 1075 | `01fde0bedf83bdc185065d7af524a61690efe576a67f922eaff3a1280c17b63a` |
| 9 | membukkit | `memseekai/membukkit` | `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` | **Apache-2.0** | 11358 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| 10 | claude_mem | `thedotmack/claude-mem` | `fa6a1e9ec12d23f98326a9b26e243acb0819e105` | **Apache-2.0** | 11358 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |

**All five: verification class `verified-by-us`. No copyleft blocker at P1.**
membukkit and claude_mem legitimately share one SHA-256: both blobs are the
standard unmodified Apache-2.0 text (Kiln flagged the same), so identical bytes
are expected, not a copy error. habitus/agentmemory use a shorter Apache-2.0
boilerplate variant (10,788 / 10,764 bytes); membukkit/claude_mem use the
variant with the application appendix (11,358 bytes). Both are valid
Apache-2.0.

### Per-system receipts

#### 6 — habitus — Apache-2.0 (`verified-by-us`)
- **claim:** the license governing the pinned Habitus-AI tree is Apache-2.0
- **source URL:** `https://raw.githubusercontent.com/munch2u-a11y/Habitus-AI/f93b770e4b3c1875151dc13eb90421598c3efa5f/LICENSE`
- **commit pin:** `f93b770e4b3c1875151dc13eb90421598c3efa5f`
- **blob:** 10,788 bytes, sha256 `27283c037eb34dee923515f28f0f92160f83ffe5b48011d1fd92212cc0b005fe`
- **identification:** Apache License, Version 2.0, January 2004 (no SPDX header; terms + `END OF TERMS AND CONDITIONS`)
- **copyright line in blob:** `Copyright 2026 HUMAN Project / Fractal Memory Contributors`
- **cross-check:** byte-identical to Kiln's frozen `docs/PORTFOLIO-P1-discovery/habitus-LICENSE.fetch`
- **interest note:** charter row 6; the vendored `vendor/habitus/` tree ships **no** LICENSE file, so upstream-at-pin is the only honest license surface

#### 7 — agentmemory — Apache-2.0 (`verified-by-us`)
- **claim:** the license governing the pinned agentmemory tree is Apache-2.0
- **source URL:** `https://raw.githubusercontent.com/rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6/LICENSE`
- **commit pin:** `e04ba88819c365c9acf9d6661ea802143e728bd6`
- **blob:** 10,764 bytes, sha256 `76c8d49ab42216a2533f603fbafa20a1bf71b56de136a401be52da034dcc012c`
- **identification:** Apache License, Version 2.0, January 2004 (no SPDX header)
- **copyright line in blob:** `Copyright 2026 Rohit Ghumare`
- **cross-check:** byte-identical to Kiln's frozen `docs/PORTFOLIO-P1-discovery/agentmemory-LICENSE.fetch`
- **interest note:** charter row 7 (Patch 2 marked ✅; this is the pinned-blob receipt that backs the mark). Known-bad supersession is a scored dimension, unrelated to license.

#### 8 — hindsight — MIT (`verified-by-us`)
- **claim:** the license governing the pinned hindsight tree is MIT
- **source URL:** `https://raw.githubusercontent.com/vectorize-io/hindsight/ebad478240d3171bb88201ececda5e8d9883d22d/LICENSE`
- **commit pin:** `ebad478240d3171bb88201ececda5e8d9883d22d`
- **blob:** 1,075 bytes, sha256 `01fde0bedf83bdc185065d7af524a61690efe576a67f922eaff3a1280c17b63a`
- **identification:** `MIT License`, with the standard `Permission is hereby granted, free of charge` grant (no SPDX header)
- **copyright line in blob:** `Copyright (c) 2025 Vectorize AI, Inc.`
- **cross-check:** byte-identical to Kiln's frozen `docs/PORTFOLIO-P1-discovery/hindsight-LICENSE.fetch`
- **interest note:** charter row 8; same upstream as the local `pg0` Postgres launcher (`vendor/pg0-bin/UPSTREAM.md`)

#### 9 — membukkit — Apache-2.0 (`verified-by-us`)
- **claim:** the license governing the pinned membukkit tree is Apache-2.0
- **source URL:** `https://raw.githubusercontent.com/memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807/LICENSE`
- **commit pin:** `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`
- **blob:** 11,358 bytes, sha256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- **identification:** Apache License, Version 2.0, January 2004, with `APPENDIX: How to apply the Apache License to your work` (no SPDX header)
- **copyright line in blob:** none detected — standard template, no filled copyright holder
- **cross-check:** byte-identical to Kiln's frozen `docs/PORTFOLIO-P1-discovery/membukkit-LICENSE.fetch`
- **interest note:** charter row 9; `vendor/membukkit/` ships no LICENSE

#### 10 — claude_mem — Apache-2.0 (`verified-by-us`)
- **claim:** the license governing the pinned claude-mem tree is Apache-2.0
- **source URL:** `https://raw.githubusercontent.com/thedotmack/claude-mem/fa6a1e9ec12d23f98326a9b26e243acb0819e105/LICENSE`
- **commit pin:** `fa6a1e9ec12d23f98326a9b26e243acb0819e105` (package 13.18.0)
- **blob:** 11,358 bytes, sha256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- **identification:** Apache License, Version 2.0, January 2004, with the application appendix (no SPDX header)
- **copyright line in blob:** none detected — standard template, no filled copyright holder
- **cross-check:** byte-identical to Kiln's frozen `docs/PORTFOLIO-P1-discovery/claude_mem-LICENSE.fetch`
- **interest note:** charter row 10; pin `fa6a1e9e` = package 13.18.0 (the earlier 10.6.1 association is already corrected)

### What this establishes, and what it does not

- **Establishes:** the `LICENSE` blob at each pinned commit, byte-for-byte,
  with SHA-256; the SPDX identification and any copyright line present in that
  blob; and that our re-fetch equals Kiln's frozen discovery fetch.
- **Does not establish:** per-file/per-subtree licensing across the whole tree;
  no `SPDX-License-Identifier` headers were audited, and dual-license or
  third-party vendored code inside a repo is out of scope. All five pinned
  `LICENSE` blobs are permissive and carry no copyleft terms.
- **Boundary:** git commit SHAs are immutable, so these URLs are commit-frozen
  by construction; the mutable repo page and release tarballs were not used.
- **Method limit:** `web_search` is unconfigured on this endpoint (Corvid's
  logged limitation); direct pinned-URL fetch works and was used. Raw bytes
  were fetched with `curl` (not a text decoder) so SHA-256 is over exact bytes.

### Reproduction

```bash
BASE=https://raw.githubusercontent.com
fetch() { curl -sL "$BASE/$1/LICENSE" | sha256sum; }
fetch munch2u-a11y/Habitus-AI/f93b770e4b3c1875151dc13eb90421598c3efa5f
fetch rohitg00/agentmemory/e04ba88819c365c9acf9d6661ea802143e728bd6
fetch vectorize-io/hindsight/ebad478240d3171bb88201ececda5e8d9883d22d
fetch memseekai/membukkit/f28a2e58cdc0e77758c0f6d9a1e050f80dcad807
fetch thedotmack/claude-mem/fa6a1e9ec12d23f98326a9b26e243acb0819e105
# compare against the SHA-256 column in the summary table
```

— Alice (`worker-glm-dsh`), row 15. P1 license gate satisfied; portfolio runs are not blocked on this.

---

## Claims DISCOVERY — the seven CLAIMED items in ECOSYSTEM-MAP §4

**Author:** builder-claude (web-research seat, GiLMore dispatch) · **Date:** 2026-09-12
**Scope:** discovery only. Every row is `vendor-only` by default; Corvid
classifies and verifies. Keys are ECOSYSTEM-MAP slot ids.
**Method:** WebSearch for each system's benchmark claims, then WebFetch of
the primary source. GitHub sources are pinned to the default-branch commit
fetched today. arXiv sources are pinned to the version.

**Read these limits before you use a row:**
1. **Quotes are extracted by a model, not copied from bytes.** WebFetch runs a
   small model over the page. Quote marks below mean "the fetch reported these
   as verbatim". Before a row moves off `vendor-only`, re-fetch the source and
   byte-check the quote. arXiv abstracts are the most reliable. GitHub README
   and blog extracts are the least reliable.
2. **Blog URLs are mutable — four blog-carried claims pinned 2026-09-12.** The
   Wayback availability API failed on this host; the CDX endpoint worked. Pins
   (`ALICE-MUTABLE-SOURCE-PINS.md`): Letta `82e12dc9…` (2025-08-13), Zep
   `bd6041c0…` (2025-01-22), Mem0 `b1e5525d…` decoded (2026-08-20), LangChain
   `d47cf779…` (2026-05-12, `not-contemporaneously-pinned`). Live fetch shas
   identify the fetch-date copy only.
3. **"Competitor-published"** means a system's numbers come from a rival's
   page, not its own. The class is still `vendor-only` (nobody independent),
   but the interest note says whose page it is.
4. Nothing was run, hashed, or reproduced. No row here is a receipt.

### Summary

| Row | Slot | System | Headline claim (short) | Source kind | Class |
|---|---|---|---|---|---|
| L-S12-01 | S-12 | letta | MemGPT tiered "virtual context management" | paper v2 | vendor-only |
| L-S12-02 | S-12 | letta | 74.0% LoCoMo, gpt-4o-mini, files only | vendor blog | vendor-only |
| L-S12-03 | S-12 | letta | disputes Mem0's MemGPT-on-LoCoMo numbers | vendor blog | vendor-only |
| L-S13-01 | S-13 | langmem | capability claims; **no benchmark numbers** | vendor blog | vendor-only |
| L-S13-02 | S-13 | langmem | 58.10 LoCoMo judge; p95 ≈60 s | competitor pages | vendor-only |
| L-S14-01 | S-14 | a_mem | "superior improvement against existing SOTA baselines", six models | paper v11, NeurIPS 2025 | vendor-only |
| L-S14-02 | S-14 | a_mem | up to six-fold multi-hop; 85–93% token cut | `2502.12110v1` body | vendor-only (narrowed; 85–93% derived-not-stated) |
| L-S15-01 | S-15 | memobase | 75.78 LoCoMo judge (v0.0.37) vs mem0/zep/langmem/openai | vendor repo doc | vendor-only |
| L-S15-02 | S-15 | memobase | <100 ms online latency; ~40–50% token cost cut | vendor README | vendor-only |
| L-S15-03 | S-15 | memobase | profile drift | — | **UNCLAIMED** (none found) |
| L-S16-01 | S-16 | memos | memory as OS resource; MemCube (no numbers in abstract) | paper v4 | vendor-only |
| L-S16-02 | S-16 | memos | LoCoMo 88.83 / LongMemEval **(split unspecified)** 89.20 / PersonaMem v2 40.58 / HaluMem 80.91 | vendor README | vendor-only |
| L-S16-03 | S-16 | memos | +159% temporal, +38.97% overall vs OpenAI memory, −60.95% tokens | search summary only | vendor-only (unsourced) |
| L-S17-01 | S-17 | Zep/Graphiti | DMR 94.8% vs MemGPT 93.4% | paper v1 | vendor-only |
| L-S17-02 | S-17 | Zep/Graphiti | LongMemEval **(split unspecified; competitor table lists LongMemEval-S 71.2 under the official judge)**: up to +18.5% accuracy, −90% latency | paper v1 | vendor-only |
| L-S06-01 | S-06 | habitus | qualitative only; **no numeric claims** | vendor README @ pin | vendor-only |

### Per-row detail

#### S-12 — letta (MemGPT)

**L-S12-01** · claim type: architectural
- **claim:** "we propose virtual context management, a technique drawing inspiration from hierarchical memory systems in traditional operating systems … we introduce MemGPT (Memory-GPT), a system that intelligently manages different memory tiers in order to effectively provide extended context within the LLM's limited context window"
- **source URL:** `https://arxiv.org/abs/2310.08560v2` (MemGPT: Towards LLMs as Operating Systems, v2 2024-02-12)
- **interest note:** the abstract has no head-to-head number against flat recall. The map's §4 wording "hierarchical blocks beat flat recall" is **stronger than the vendor's own abstract**. Corvid: check the paper body before you keep that wording.

**L-S12-02** · claim type: benchmark-score
- **claim:** "Letta agents running on `gpt-4o-mini` achieve 74.0% accuracy on LoCoMo by simply storing conversation histories in files"; "significantly above Mem0's reported 68.5% score for their top-performing graph variant"
- **source URL:** `https://www.letta.com/blog/benchmarking-ai-agent-memory/` (2025-08-12; **pinned** 2025-08-13, sha `82e12dc9…`)
- **interest note:** this is **anti-hierarchy evidence from the vendor itself**. A filesystem agent, not MemGPT tiers, gets the headline score. It bears directly on E-1/E-8 (a simple store beats specialized memory) and on the long-context null S-18.

**L-S12-03** · claim type: dispute
- **claim:** Mem0 "published controversial results claiming to have run MemGPT on LoCoMo"; the Letta team "was unable to determine a way to backfill LoCoMo data into MemGPT/Letta"; Mem0 "did not respond to requests for clarification"
- **source URL:** same as L-S12-02
- **interest note:** any MemGPT/Letta LoCoMo number published by Mem0 is disputed by the vendor. Do not use one as a Letta claim.
- **repo pin (for runs):** `letta-ai/letta@5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a` (2026-09-10)

#### S-13 — langmem

**L-S13-01** · claim type: capability
- **claim:** "a library that helps your agents learn and improve through long-term memory"; "Extract information from conversations, optimize agent behavior through prompt updates, and maintain long-term memory about behaviors, facts, and events"; "You can use its core API with any storage system and within any Agent framework"
- **source URL:** `https://www.langchain.com/blog/langmem-sdk-launch` (2025-02-18; the old `blog.langchain.com` URL 301s here; **pinned** 2026-05-12 = `not-contemporaneously-pinned`, sha `d47cf779…`)
- **interest note:** **the vendor publishes no benchmark, latency, or scale numbers.** The map's §4 claim "write-time extraction is production-viable" has **no vendor source**. The only numbers are the competitors' in L-S13-02. That wording is ours, not LangChain's.
- **repo pin:** `langchain-ai/langmem@9d033b47d9ce53e37e92c92241b0496c0278932e` (2026-09-09)

**L-S13-02** · claim type: benchmark-score + latency · **competitor-published**
- **claim:** LoCoMo LLM-judge overall 58.10 (Single-Hop 62.23, Multi-Hop 47.92, Open Domain 71.12, Temporal 23.43); judge `gpt-4o`. Mem0's blog: judge "58.1%", p95 latency "60 s", tokens/query "≈130*". Search snippets from the Mem0 paper give search p50 17.99 s / p95 59.82 s (not fetched).
- **source URLs:** `https://github.com/memodb-io/memobase/blob/358c16bbc6d687937d79bc2f984a11c3be8da901/docs/experiments/locomo-benchmark/README.md`; `https://mem0.ai/blog/benchmarked-openai-memory-vs-langmem-vs-memgpt-vs-mem0-for-long-term-memory-here-s-how-they-stacked-up` (dated 2026-07-21 on page; **pinned** 2026-08-20, sha `b1e5525d…` decoded); Mem0 paper `https://arxiv.org/abs/2504.19413` (version not recorded)
- **interest note:** two competitors report the same 58.10. It is probably one run copied, not two independent measurements. Corvid: trace it to its origin before you count it as corroboration.

#### S-14 — a_mem

**L-S14-01** · claim type: comparative
- **claim:** "Empirical experiments on six foundation models show superior improvement against existing SOTA baselines."
- **source URL:** `https://arxiv.org/abs/2502.12110v11` (2025-10-08; NeurIPS 2025). README at `agiresearch/A-mem@ceffb860f0712bbae97b184d440df62bc910ca8d` repeats it with no numbers.
- **interest note:** eval code is `WujiangXu/A-mem`; the memory system is `WujiangXu/A-mem-sys`. Our charter's harness may use either. Check which one before a run. The abstract says nothing about "curation beats passive stores", so the map's §4 wording is again stronger than the source.

**L-S14-02** · claim type: benchmark-score · **vendor-only (narrowed)**
- **claim:** "up to a six-fold improvement in complex multi-hop reasoning tasks and reduces memory operation token usage by 85-93%"
- **source:** `https://arxiv.org/pdf/2502.12110v1` (A-MEM, v1) body; frozen fetch `arxiv-2502.12110v1.pdf`, sha256 `5d94b7aa544ca07c2653d75b79ee6043a6843ed1508633299e1227258025f630` (`team/builder-provenance-fetches/MANIFEST.md`). Body verbatim: "The Multi-Hop category showcases particularly striking results, where Qwen2.5-15b with A-MEM achieves a ROUGE-L score of 27.23, dramatically surpassing LoComo's 4.68 and ReadAgent's 2.81 — representing a nearly six-fold improvement"; and "Our approach requires only 1,200-2,500 tokens, compared to the substantial 16,900 tokens needed by LoComo". The **85–93% is derived, not stated**: 1−2500/16900 = 85.2%; 1−1200/16900 = 92.9%.
- **interest note:** narrowed rule — cite the six-fold only as **multi-hop / ROUGE-L / one model (Qwen2.5-15b)**; never cite 85–93% as vendor-stated. Only v1 was re-read; the v11 body remains unchecked (the claim is vendor-only either way).

#### S-15 — memobase

**L-S15-01** · claim type: benchmark-score
- **claim:** Memobase (v0.0.37) LoCoMo LLM-judge overall **75.78** (Single-Hop 70.92, Multi-Hop 46.88, Open Domain 77.17, Temporal 85.05); v0.0.32 overall 70.91. Same table: Mem0 66.88, Mem0-Graph 68.44, LangMem 58.10, Zep 65.99, OpenAI 52.90. Judge: OpenAI `gpt-4o`. README: "achieves top-tier search performance in the LOCOMO benchmark" and SOTA at 0.0.37.
- **source URLs:** `https://github.com/memodb-io/memobase/blob/358c16bbc6d687937d79bc2f984a11c3be8da901/docs/experiments/locomo-benchmark/README.md`; `https://github.com/memodb-io/memobase/blob/358c16bbc6d687937d79bc2f984a11c3be8da901/readme.md`
- **interest note:** it is the vendor's own table, and it scores rivals on the same run. The temporal 85.05 is the outlier: it is ~27 points above the next system. That makes it the first row worth reproducing.

**L-S15-02** · claim type: latency + cost
- **claim:** "keeping online latency under 100ms"; "reducing the number of LLM calls in a single run from approximately 3-10 times to a fixed 3 times, which reduces token costs by approximately 40-50%"; search "500~1000ms" (v0.0.36)
- **source URL:** memobase `readme.md` at the pin above
- **interest note:** "<100ms online" and "500~1000ms search" are two different paths. Do not merge them.

**L-S15-03** · profile drift
- **finding:** no vendor or third-party claim found that Memobase profiles "survive drift". The README mentions a 900-turn real-world profile comparison with mem0, with no metrics in the fetch.
- **interest note:** the map's §4 item "memobase's profiles survive drift" has **no source**. It moves to UNMEASURED unless Corvid finds one.

#### S-16 — memos (MemOS)

**L-S16-01** · claim type: architectural
- **claim:** "we propose MemOS, a memory operating system that treats memory as a manageable system resource. It unifies the representation, scheduling, and evolution of plaintext, activation-based, and parameter-level memories"; "a MemCube encapsulates both memory content and metadata such as provenance and versioning"
- **source URL:** `https://arxiv.org/abs/2507.03724v4` (2025-12-03)
- **interest note:** MemCube "provenance and versioning" is the closest thing in this set to an E-7 lineage claim. It is worth a row-2-style probe against Perseus EXPLICIT_LINEAGE.

**L-S16-02** · claim type: benchmark-score
- **claim (README table, extracted):** LoCoMo 88.83 · LongMemEval **(split unspecified)** 89.20 · PersonaMem v2 40.58 · HaluMem 80.91 — via the "OmniMemEval" framework (MemOS 2.0 "Stardust")
- **source URL:** `https://github.com/MemTensor/MemOS/blob/de8069428a9247bfa7a3d35f59a9b39fa8f231d2/README.md`
- **interest note:** the judge model, answer model and metric are not in the fetch. 88.83 is not comparable to Memobase's 75.78 until the metric is known. OmniMemEval is the vendor's own framework.

**L-S16-03** · claim type: comparative · **unsourced**
- **claim (search summary, NOT verbatim):** "159% improvement in temporal reasoning over OpenAI's global memory, with an overall accuracy gain of 38.97% and 60.95% reduction in token overhead"; "consistently ranks first in all categories, outperforming … mem0, LangMem, Zep, and OpenAI-Memory"
- **source:** not in the v4 abstract. It is probably in the earlier MemOS paper or v1–v3 of 2507.03724. Not located.

#### S-17 — Zep / Graphiti (parked by Brian; claims recorded anyway)

**L-S17-01** · claim type: benchmark-score
- **claim:** "In the DMR benchmark, which the MemGPT team established as their primary evaluation metric, Zep demonstrates superior performance (94.8% vs 93.4%)."
- **source URL:** `https://arxiv.org/abs/2501.13956v1` (2025-01-20). Vendor blog copy: `https://blog.getzep.com/zep-a-temporal-knowledge-graph-architecture-for-agent-memory/` (**pinned** 2025-01-22, sha `bd6041c0…`)
- **interest note:** the margin is 1.4 points on a benchmark the paper itself calls less representative.

**L-S17-02** · claim type: benchmark-score + latency
- **claim:** "Zep achieves substantial results with accuracy improvements of up to 18.5% while simultaneously reducing response latency by 90% compared to baseline implementations." "These results are particularly pronounced in … cross-session information synthesis and long-term context maintenance"
- **source URL:** same as L-S17-01
- **interest note:** "up to" and "baseline implementations" are unspecified in the abstract. The map's §4 item "wins on temporal reasoning" is close to this, but the abstract says cross-session synthesis, not temporal reasoning by name. Competitor-published counter-number: Memobase's table has Zep LoCoMo 65.99 / temporal 49.31 (L-S15-01). The repo pin for Graphiti is `getzep/graphiti@c035afb7990b6077331a81e98b04efcfd9bf8184` (2026-09-11).

#### S-06 — habitus

**L-S06-01** · claim type: architectural (qualitative)
- **claim (extracted):** "zero-external-runtime-dependency"; "Ultra-Fast Local Execution: 0 external database servers required"; comparison table "Direct Top-3 Rail (Zero Eviction)" vs "(Eviction Prone)" for vector/graph RAG
- **source URL:** `https://github.com/munch2u-a11y/Habitus-AI/blob/f93b770e4b3c1875151dc13eb90421598c3efa5f/README.md` (same pin as P1 license row 6)
- **interest note:** **the vendor makes no numeric or efficiency claim.** The map's §4 item "habitus's efficiency holds outside core5" is **our own hypothesis** from our core5 receipt, not a vendor claim. It belongs under UNMEASURED/novelty, not CLAIMED. "Zero Eviction" is a testable harm claim that fits row 1's co-return finding.

### What discovery found about the map's §4 wording

Four of the seven §4 CLAIMED sentences are stronger than, or absent from,
what the vendors actually say:

- letta "beats flat recall": the vendor abstract has no such comparison. The vendor blog promotes a flat filesystem agent.
- langmem "production-viable": the vendor publishes no numbers. The only numbers are the competitors' (58.10; p95 ≈60 s).
- memobase "profiles survive drift": no source found.
- habitus "efficiency holds": this is our hypothesis, not a claim.

Corvid classifies. Under the §7 contract, the map changes only on ledger
moves, so this section proposes and does not rewrite.

— builder-claude, discovery pass, 1 turn. No runs, no hashes; every row open.

---

## CLASSIFICATION — builder's 16-source claims-discovery batch (QUEUE row 17)

**Author:** Alice (`worker-glm-dsh`) · **Date:** 2026-09-12 · **Cost:** 1 turn,
$0 model spend inside the run (curl only), ≤$0.02.
**Scope:** assign a verification class to each of the 16 rows in §"Claims
DISCOVERY" above. Classification, not reproduction: **no engine or benchmark
was run.** Every source was re-fetched and byte-checked; raw bodies + URL +
pin + size + sha256 are in `team/row17-claims-fetches/` (see `MANIFEST.md`).

**Plain English (for Brian):** I checked whether each advertised number really
appears in the source it is attributed to, and whether anyone independent has
confirmed it. The quotes check out. The *numbers* do not become facts by being
quoted — none of the 16 is independently verified, and one table that looked
like a rival's independent measurement turns out to be copied from another
vendor's paper. One negative is now solid: Habitus's README makes no numeric
claim at all.

### Classification rule (and the one place it departs from the default)

The file's four classes describe the **substantive claim**, not the quote:

- `vendor-only` — the asserting vendor is the only source. **Byte-confirming a
  vendor's own quote is an attribution receipt, not substantive verification**;
  a LoCoMo score does not become `verified-by-us` because we re-fetched the
  page that advertises it. `verified-by-us` is reserved for claims our own
  receipt establishes (a run, a hash, or a negative existence check).
- `third-party` — a party with no stake in the claimed system measured it and
  we hold the reference. A **rival's** page is not independent (builder note 3);
  no row in this batch qualifies.
- `verified-by-us` — used here for exactly one row (L-S06-01), where the claim
  is about what the pinned README contains, so fetching the README settles it.
- `contradicted` — no row qualifies: no receipt we hold disagrees with a claim.
  (Two cross-vendor *discrepancies* are flagged below, but they are vendor-page
  instability, not our contradictory receipt.)
- Two dispositions fall outside the four classes and are carried as such
  rather than forced into one: `unsourced` (no primary located → not citable)
  and `no-claim` (nothing found to classify).

### Summary

| Row | Slot / system | Claim (short) | Class | Attribution receipt |
|---|---|---|---|---|
| L-S12-01 | S-12 letta | MemGPT virtual context / memory tiers | `vendor-only` | arXiv `2310.08560v2`, pinned; quote verbatim; sha `938d54ff…` |
| L-S12-02 | S-12 letta | 74.0% LoCoMo, gpt-4o-mini, files only | `vendor-only` | letta blog, pinned 2025-08-13 sha `82e12dc9…`; verbatim; live sha `35a15187…` |
| L-S12-03 | S-12 letta | disputes Mem0's MemGPT-on-LoCoMo run | `vendor-only` | same letta blog; pinned `82e12dc9…`; verbatim |
| L-S13-01 | S-13 langmem | capability; **no benchmark numbers** | `vendor-only` | langchain blog, pinned 2026-05-12 (**not-contemporaneously-pinned**) sha `d47cf779…`; phrases present; live sha `1669df96…` |
| L-S13-02 | S-13 langmem | 58.10 LoCoMo judge; p95 ≈60 s | `vendor-only` (competitor-published) | memobase pin `e9839f54…` has 58.10; Mem0 blog pinned 2026-08-20 sha `b1e5525d…`, live `f5b72e56…` has 58.1% / 60 s; **one origin** (flag 2) |
| L-S14-01 | S-14 a_mem | "six foundation models … superior … SOTA" | `vendor-only` | arXiv `2502.12110v11`, pinned; verbatim; Comments: NeurIPS 2025; sha `08dc74e0…` |
| L-S14-02 | S-14 a_mem | six-fold multi-hop; 85–93% token cut | `vendor-only` (narrowed) | `2502.12110v1` body; fetch sha `5d94b7aa…`; 85–93% derived-not-stated |
| L-S15-01 | S-15 memobase | 75.78 judge vs mem0/zep/langmem/openai | `vendor-only` | memobase pin `e9839f54…`; verbatim; rivals' rows are **pasted from Mem0's paper** (flag 1) |
| L-S15-02 | S-15 memobase | <100 ms online; ~40–50% token cut | `vendor-only` | memobase `readme.md` pin `165358fb…`; verbatim |
| L-S15-03 | S-15 memobase | profile drift | **`no-claim`** | none found (UNMEASURED candidate) |
| L-S16-01 | S-16 memos | memory as OS resource; MemCube provenance | `vendor-only` | arXiv `2507.03724v4`, pinned; verbatim; sha `550400fb…` |
| L-S16-02 | S-16 memos | 88.83 / 89.20 / 40.58 / 80.91 | `vendor-only` | MemOS pin `9c2ec97b…`; verbatim; judge/metric absent from fetch |
| L-S16-03 | S-16 memos | +159% temporal; +38.97%; −60.95% tokens | **`unsourced`** | not in v4 abstract; not located |
| L-S17-01 | S-17 Zep/Graphiti | DMR 94.8% vs 93.4% | `vendor-only` | arXiv `2501.13956v1`, pinned; verbatim; sha `6773db62…` |
| L-S17-02 | S-17 Zep/Graphiti | up to +18.5% accuracy; −90% latency | `vendor-only` | same `2501.13956v1`; verbatim |
| L-S06-01 | S-06 habitus | qualitative; **no numeric claim** | **`verified-by-us`** (negative only) | habitus pin `8449b7e7…`; quotes present; **no benchmark number found**; map item stays our hypothesis |

**Counts:** 13 `vendor-only` · 1 `verified-by-us` (negative existence) ·
0 `third-party` · 0 `contradicted` · 1 `unsourced` · 1 `no-claim`.
**Located and byte-checked:** 14 of 16 rows (11 commit/version-pinned artifacts,
3 blog-primary rows Wayback-pinned 2026-09-12, plus 2 secondary blog pins on
commit-/arXiv-pinned rows — four blog-carried claims total). The other 2 are the one `unsourced` row
and the `no-claim` row. **Substantive verification: 0 of 16.**
*(Counts amended 2026-09-13 by Corvid, custodian, per
`team/ALICE-LEDGER-UNSOURCED-ROWS-AUDIT.md`: L-S14-02 `unsourced` →
`vendor-only (narrowed)` after the A-MEM v1 body was located; L-S16-03 stays
`unsourced`. No other class moved.)*

### Per-row notes (only where this pass adds something)

- **L-S12-01** — the paper text is verbatim at v2. The paper contains **no
  head-to-head number against flat recall**; the §4 item "hierarchical blocks
  beat flat recall" is the map's wording, not the vendor's. No class change.
- **L-S12-02 / L-S12-03** — both quotes verbatim on the **live** blog
  (2026-09-12) and present in the **Wayback pin** 2025-08-13 (sha `82e12dc9…`);
  builder limit 2 no longer stands for these rows. The vendor's own blog is *anti-hierarchy*: a flat filesystem
  agent gets the headline score. This is evidence relevant to §4, but it is
  the vendor's claim about its own run, so the rows stay `vendor-only`.
- **L-S13-01** — the live page does carry the capability phrases; it still
  carries **no benchmark, latency, or scale number**, so the §4 item
  "production-viable" has no vendor source. **Pinned** 2026-05-12 but
  **not contemporaneously** (no pre-2026-05 snapshot exists); cite the live
  `datePublished` 2025-02-18 with the 2026 snapshot, per
  `ALICE-MUTABLE-SOURCE-PINS.md`.
- **L-S13-02** — the 58.10 is real at the memobase pin **and** real on Mem0's
  live blog, but those are not two measurements (flag 2). Class stays
  `vendor-only` under the builder's competitor-published rule; if a reviewer
  prefers to call a rival's run `third-party`, the COI and single-origin
  caveats must travel with it.
- **L-S15-01** — Memobase's own v0.0.37 row (75.78 overall) is the only row in
  the table it claims to have run; the v0.0.32 row (70.91) is its own earlier
  run too. Everything about rivals is copied (flag 1). The temporal 85.05
  outlier is the single highest-value reproduction target in this batch.
- **L-S16-02** — numbers verbatim, but the judge model, answer model, and
  metric are **not in the fetched README**; 88.83 is not comparable to
  Memobase's 75.78 until the metric is known (builder note confirmed).
- **L-S17-01/02** — abstracts verbatim; "DMR … the MemGPT team established as
  their primary evaluation metric" is an attribution claim we did not chase
  into the MemGPT paper; no class change.
- **L-S06-01** — this is the one row our receipt *establishes*: the pinned
  README (sha `8449b7e7…`) has quotes present and **no `Hit@5`, `0.955`, or
  other benchmark number**; line 167 points readers to `DEVELOPMENT.md` for
  "LLM-free experimental benchmarks." The §4 item remains a hypothesis, not a
  vendor claim.

### Flags this pass produced (for owners, not edits here)

1. **Correction to the builder's L-S15-01 note (load-bearing).** The discovery
   section says Memobase's table "scores rivals on the same run." The pinned
   README says the opposite, verbatim: *"We ran Memobase results and pasted
   the other methods' result from [Mem0: Building Production-Ready AI Agents
   with Scalable Long-Term Memory](https://arxiv.org/pdf/2504.19413)."* So the
   mem0 / mem0-graph / langmem / zep / openai rows are **Mem0's paper numbers,
   copied**, not Memobase's measurement. Consequence: Memobase's table is not
   independent corroboration of any rival number.
2. **L-S13-02's "two competitors agree" is one origin, confirmed.** The 58.10
   in Memobase's table is pasted from the Mem0 paper (flag 1); the Mem0 blog's
   58.1% is Mem0's own. One eval codebase, two pages. It is **not** two
   independent measurements, and must not be counted as corroboration.
3. **Mem0's LoCoMo number is unstable across its own and others' mutable
   pages:** 66.88 (Mem0 paper, as pasted into the pinned Memobase table),
   68.5% (the figure Letta's blog cites for "their top-performing graph
   variant"), 92.5% (Mem0's live blog headline). Any citation of "Mem0's
   LoCoMo" must name the source, its date, and the algorithm version — or it
   is meaningless. This is a vendor-page discrepancy, not a receipt of ours,
   so no row is classed `contradicted`.
4. **Pointer check for `RESEARCH-4-ENGINES-SURVEY.md` (Corvid).** Its Habitus
   row cites `README.md:134-139` for "22 non-as-of positives Hit@5 0.955."
   The pinned README (173 lines, sha `8449b7e7…`) contains no `Hit@5` and no
   `0.955`; line 167 sends benchmarks to `DEVELOPMENT.md`. The number may be
   real elsewhere — the *pointer* is wrong. Read-only flag; the survey owner
   decides.
5. **Mutable sources — RESOLVED 2026-09-12:** L-S12-02, L-S12-03, L-S13-01,
   and the Mem0 blog behind L-S13-02 now have Wayback pins
   (`ALICE-MUTABLE-SOURCE-PINS.md`: `82e12dc9…`, `d47cf779…`
   not-contemporaneous, `b1e5525d…` decoded, `bd6041c0…`). Live-response sha256
   values in the manifest identify the fetch-date copy only.

### What would move each row

| Row(s) | To reach substantive `verified-by-us` |
|---|---|
| L-S15-01 | Reproduce Memobase v0.0.37 under a pinned reader/judge, especially temporal 85.05 (the 27-point outlier). |
| L-S13-02, L-S12-02 | **Provenance done 2026-09-12/13** — Letta Wayback-pinned (`82e12dc9…`) + harness located (`802a7942…`), langmem origin named (`2504.19413v1` Table 2) and one-origin established; cannot reach `verified-by-us` without running the vendor's harness. |
| L-S17-01/02 | Independent DMR / LongMemEval reproduction (parked by Brian; vendor-only meanwhile). |
| L-S16-02 | **Metric pinned 2026-09-13** (OmniMemEval: `gpt-4.1-mini` answer / `gpt-4o-mini` judge); remaining: a matched run (TiMem's independent values already recorded in L-S16-02b). |
| L-S14-01 | Run a_mem on core5 / memconflict under the frozen instrument. |
| L-S12-01, L-S16-01 | Architectural claims: no run verifies the *wording*; the map owner (Stratum) should reword to match the sources. |
| L-S06-01 | Nothing vendor-side to verify; the "efficiency holds outside core5" hypothesis is a portfolio arm (memconflict). |
| L-S14-02 | **Done 2026-09-12/13** — traced to `2502.12110v1` body; narrowed to multi-hop / ROUGE-L / one model. Do not cite 85–93% as stated. |
| L-S16-03 | Trace to a paper version or drop from citations — still `unsourced` (first located in an author comment on the HF paper page, not paper text). |

**Edit checklist for this table:** re-read it after any provenance or class move;
a completed prerequisite is marked `Done` / `Provenance done` / `Metric pinned`.
*(Added 2026-09-13 per Alice's action-table audit. This table is judgment, not
machine-guarded — `check_ledger_counts.py` derives the `### Summary` counts and
`Located` line only.)*

### Boundaries

- This section proposes classes; it changes no ECOSYSTEM-MAP tag. Per §7 the
  map moves only on ledger moves, and no claim here moved from CLAIMED.
- The builder's discovery section above is unchanged (append-only).
- Consistent with the row-15 P1 license receipts, but the scope differs:
  a LICENSE blob **is** the claim, so fetching it earns `verified-by-us`;
  a README advertising a benchmark score is not, so fetching it earns only an
  attribution receipt.
- Reproduction: `team/row17-claims-fetches/MANIFEST.md` lists every URL, pin,
  byte count, and sha256; re-fetch the pinned URLs and byte-compare, or diff
  the stored bodies directly.

— Alice (`worker-glm-dsh`), row 17. Classified, not reproduced: 0 of 16
substantive claims are `verified-by-us`; 13 of 16 sources are byte-checked.

---

## PROVENANCE — where each `vendor-only` claim first appeared (QUEUE row 20)

**Author:** Alice (`worker-glm-dsh`) · **Date:** 2026-09-12 · **Cost:** 1 turn,
$0 model spend (curl + GitHub API only), ≤$0.02.
**Method:** first-appearance scan — for each number, walk the artifact's public
history (GitHub commits API + the raw file at every commit; arXiv version
abstracts; full-text HTML of the Mem0 and Zep papers; live page
`datePublished`). Every body, API response, and scan output is in
`team/row20-claims-provenance/` (`MANIFEST.md` has URL + pin + sha256).

**Plain English (for Brian):** I traced every vendor-only number back to the
first page or commit that carries it. The thirteen claims come from **ten origin
artifacts, not thirteen independent sources**. One artifact — Mem0's own paper —
is the origin of four separate "competitor" numbers that other vendors
republish as if independent. Two advertised numbers (MemOS's) are **not in the
paper they are attributed to at all**. And the commits the ledger pinned are
months *later* than the first appearance: pinning was byte-stable, not
earliest.

### Origin table (earliest located appearance)

| Row | Claim (number) | First appeared | Origin artifact | Downstream / chain |
|---|---|---|---|---|
| L-S12-01 | MemGPT virtual context / memory tiers | 2023-10-12 | arXiv `2310.08560`**v1** abstract (v1≡v2) | — |
| L-S12-02 | Letta 74.0% LoCoMo, files only | 2025-08-12 | `letta.com/blog/benchmarking-ai-agent-memory` (`datePublished` 2025-08-12; mutable) | cites "Mem0's 68.5%"; **resolved 2026-09-13 (Alice):** Mem0's own figure is **68.44** — paper v1 Table 2 + prose, `grep 68.5 = 0` on a byte-stable fetch (sha `999aea13…`); only v1 exists; current README and pinned blog carry no 68.5. So Letta's 68.5 is a **one-decimal mis-round** (68.44 → 68.4), not a Mem0-reported number; no Mem0 artifact located states it (`team/ALICE-LETTA-685-PROVENANCE.md`) |
| L-S12-03 | Letta disputes Mem0's MemGPT-on-LoCoMo run | 2025-08-12 | same Letta blog | — |
| L-S13-01 | langmem capability; no benchmark numbers | 2025-02-18 | `langchain.com/blog/langmem-sdk-launch` (`datePublished` 2025-02-18) | — (no numbers exist to trace) |
| L-S13-02 | langmem **58.10** judge; p95 ≈60 s | **2025-04-28** | arXiv `2504.19413`**v1** (Mem0 paper) **Table 2**: `LangMem 127 17.99 59.82 18.53 60.40 58.10 ±0.21%` — Mem0's own adapted run | → memobase locomo README commit `56b63369` (2025-07-12); → Mem0 blog (2026-07-21) as "58.1% / 60 s / ≈130" |
| L-S14-01 | a_mem "six foundation models … SOTA" | 2025-02-17 | arXiv `2502.12110`**v1** abstract (v11 repeats; abstract text differs, this sentence is v1) | — |
| L-S14-02 | a_mem "six-fold" multi-hop; 85–93% token cut | **2025-02-17** | arXiv `2502.12110`**v1** body (multi-hop analysis; `pdftotext -layout` lines 1124–1134) | "nearly six-fold" = Multi-Hop, one model ("Qwen2.5-15b" [sic]), **ROUGE-L** 27.23 vs LoComo 4.68 / ReadAgent 2.81; "1,200-2,500 vs 16,900 tokens" is v1 body, but the **"85–93%" string is not in the paper** (grep 0) — aggregator arithmetic (85.2% / 92.9%). Shares the a_mem v1 origin with L-S14-01 |
| L-S15-01 | Memobase **75.78** / 70.91 | **2025-07-12** | memobase commit `56b63369` ("feat: add event gist… #102"), `docs/experiments/locomo-benchmark/README.md` | rival rows (mem0 66.88 · mem0g 68.44 · langmem 58.10 · zep 65.99 · openai 52.90) = **Mem0 paper v1**; README says "pasted" |
| L-S15-02 | <100 ms online; 40–50% token cut; 500~1000 ms search | 2025-08-11 (first two, commit `578e172ca0` "reduce token usage … #120"); 2025-07-16 (`500~1000ms`, `3a8f6fcb50` "docs: update readme") | memobase `readme.md` history | — |
| L-S16-01 | MemOS memory-as-OS / MemCube | 2025-07-04 | arXiv `2507.03724`**v1** abstract (v1≡v4) | — |
| L-S16-02 | MemOS **88.83** / 89.20 / 40.58 / 80.91 | **2026-07-09** | MemOS README commit `40f8e832` ("docs: rewrite README…") | **not in paper v1 or v4** (grep 88.83=0, OmniMemEval=0); the same first-appearance commit's prose says **92.34 / 93.40** |
| L-S17-01 | Zep DMR 94.8 vs 93.4 | 2025-01-20 | arXiv `2501.13956`**v1** | Zep blog (2025-01-22) carries identical text |
| L-S17-02 | Zep up to +18.5%; −90% latency | 2025-01-20 | same `2501.13956v1` | Zep blog (2025-01-22) |

**Ten distinct origin artifacts for thirteen rows:** MemGPT paper v1; Letta
blog; LangChain blog; Mem0 paper v1; a_mem paper v1; memobase locomo-README
commit; memobase readme commits; MemOS paper v1; MemOS README commit; Zep
paper v1. (Letta's blog, Zep's paper, and the a_mem paper each carry two rows:
L-S12-02/03, L-S17-01/02, and L-S14-01/02.)

*Amended 2026-09-13 by Alice: L-S14-02 added after the 09:48 class move
(`unsourced` → `vendor-only (narrowed)`), so the "every `vendor-only` row" scope
is complete again. Origin re-derived from the frozen v1 PDF in
`team/builder-provenance-fetches/` (sha `5d94b7aa…`); see
`team/ALICE-LEDGER-UNSOURCED-ROWS-AUDIT.md`.*

### Findings

1. **The Mem0 paper is a supernode.** One artifact — arXiv `2504.19413v1`,
   2025-04-28, Table 2 — is the origin of **langmem 58.10, zep 65.99, openai
   52.90, mem0 66.88, mem0-graph 68.44**. The memobase table's entire rival
   half is a copy of it (verbatim: *"pasted the other methods' result
   from [Mem0 paper]"*), and the Mem0 blog re-reports langmem 58.1%. So
   L-S13-02's "two competitors report the same 58.10" is **one measurement,
   published twice** — Mem0's, with Mem0's conflict of interest. Copy-counting
   is not corroboration.
2. **Letta's quoted "68.5%" is a mis-round of the Mem0 paper's 68.44 —
   resolved 2026-09-13.** Grep of the paper for `68.5` = 0; the graph variant's
   figure is **68.44** (2025-04-28), which rounds to 68.4, not 68.5. A fresh
   fetch of `2504.19413v1` (sha `999aea13…`) shows only `68.44` (twice), and the
   current Mem0 README and the pinned Mem0 blog carry no `68.5`; the earliest
   located `68.5` is Letta's own blog (2025-08-12). So the string originates on
   Letta's side: **not an independent Letta measurement**, not a number Mem0
   published as written, and not located in any Mem0 artifact
   (`team/ALICE-LETTA-685-PROVENANCE.md`).
3. **The MemOS 88.83 numbers are not in the MemOS paper.** Grep of
   `2507.03724` full text at v1 and v4: `88.83`=0, `OmniMemEval`=0. They first
   appear in the **README** on 2026-07-09 (`40f8e832`). Worse, that first
   commit's prose reads *"92.34 on LoCoMo and 93.40 on LongMemEval"* while its
   own table reads 88.83/89.20 — the vendor's number was self-conflicting at
   birth and the prose was later edited to match the table. Citing "the MemOS
   paper" for these is wrong; citing the README requires naming OmniMemEval
   and the version.
4. **The pinned commits are later than the origins.** memobase's ledger pin
   `358c16bb` is dated **2026-01-11**, but 75.78 first appeared 2025-07-12
   (`56b63369`); MemOS's pin `de806942` is **2026-09-08**, but 88.83 first
   appeared 2026-07-09 (`40f8e832`). Neither pinned commit is a
   path-history commit for the number — which is exactly why a provenance
   claim must cite the first-modification commit, not any later stable pin.
5. **The Mem0 LoCoMo series is three different algorithms, not one number:**
   66.88 (base) / 68.44 (graph) from the 2025-04-28 paper, then **92.5%** on
   the 2026-07-21 blog with no paper receipt. Any portfolio use of "Mem0 on
   LoCoMo" must name the version, date, and page; the three are not
   interchangeable and their ordering is not a trend.
6. **Architectural claims are stable from v1** (L-S12-01 MemGPT 2023-10-12,
   L-S14-01 a_mem 2025-02-17, L-S16-01 MemOS 2025-07-04): the quoted wording is
   present in the first arXiv version, so there is no earlier vendor source to
   chase. L-S13-01 has no numbers at all, so its origin (the launch blog) is
   the whole provenance.
7. **Zep's two claims are one paper.** The blog and paper carry identical DMR
   text; paper v1 (2025-01-20) precedes the blog (2025-01-22), so the blog is
   a copy, not corroboration. The Mem0 paper's Zep 65.99 (LoCoMo) and Zep's
   own DMR 94.8 are different benchmarks from different vendors — neither is
   independent of its author.

### What would move these rows

- **The Mem0 supernode (L-S13-02 + the rival half of L-S15-01):** exactly one
  upstream measurement stands behind four rows. Substantive verification
  requires reproducing Mem0's Table 2 harness locally, or finding an
  independent reproduction. More copies will never add evidence.
- **L-S16-02:** obtain OmniMemEval's metric/judge definition and resolve
  88.83 vs 92.34 — the vendor's own conflict is unresolved.
- **L-S15-01 (Memobase's own 75.78/70.91):** reproduce v0.0.37 under a pinned
  reader/judge (unchanged from §CLASSIFICATION).
- **L-S12-02 (Letta 74.0%):** ~~self-reported with no located harness~~ **CORRECTED
  2026-09-13 (Alice): the harness IS located and was linked by the blog itself** —
  `letta-ai/letta-leaderboard` `leaderboard/locomo/locomo_benchmark.py`
  (`LoCoMoQAFileBenchmark`: session/secom/turn/time_window chunking,
  `text-embedding-3-large`@1536, tools `search_files`+`answer_question`, LLM-judge
  `grade_sample`); fetched sha `0a2f9751…`, commit-pinned recipe (harness + agent
  prompt + judge/driver + the in-repo `locomo10.json`, 10 samples / 1986 QA) at
  commit `802a7942…`: `team/ALICE-LETTA-LOCOMO-RECIPE-PINNED.md`, receipts
  `team/row-letta-locomo-harness-receipts/`. The run is still **vendor-only**
  (we did not execute it and the repo is now archived into `letta-ai/letta-evals`),
  but a reproduction path exists — no local re-implementation is required to
  attempt it.
- **Pin status (CORRECTED 2026-09-13):** the four blog sources are **not
  unpinned** — Wayback snapshots landed 2026-09-12 (`team/ALICE-MUTABLE-SOURCE-PINS.md`;
  Letta `82e12dc9…`, Zep `bd6041c0…`, Mem0 `b1e5525d…` decoded; LangChain
  `d47cf779…` is `not-contemporaneously-pinned`). The CLASSIFICATION/"still lack
  Wayback pins" lines were stale; **applied 2026-09-13 by the custodian** — they
  now carry the pin status.

### Method limits

- "First appearance" is bounded by what is queryable: GitHub **default-branch
  path history**, arXiv versions, and live pages. A number could have appeared
  earlier on a branch, a deleted page, a release tarball, or social media; I
  did not search those (no authenticated code search). The GitHub commits API
  returns only commits that **modify** the path, which is why the pinned
  commits above do not appear in their own file's history.
- Blog dates come from live `datePublished`/JSON-LD. The pages are mutable, but
  the four blog-carried claims were Wayback-pinned 2026-09-12
  (`ALICE-MUTABLE-SOURCE-PINS.md`); live sha256 values identify the fetch-date
  copy only. *(Pin-status amended 2026-09-13 by Corvid, custodian.)*
- No benchmark was run; this is provenance, not verification. All thirteen rows
  remain `vendor-only`.

— Alice (`worker-glm-dsh`), row 20. Ten origins, not thirteen; the Mem0 paper
measures four of the "independent" numbers.
*(Amended 2026-09-13 by Corvid, custodian: "twelve" → "thirteen" after L-S14-02
joined the vendor-only scope; caught by `check_ledger_counts.py`.)*

---

## LongMemEval-S claim audit — two vendor claims (Corvid, R&D mode, 2026-09-12)

**Author:** Corvid (`worker-glm-dsh3`), ledger custodian. **Scope:**
attribution audit of the two LongMemEval-S headlines; no engine run, no
reproduction. Byte receipts: `team/rd-threads-fetches/MANIFEST.md`; full note:
`team/RESEARCH-RD-THREADS-CORVID.md` §Thread 2. (Complementary to Alice's row
20: these two claims are not in the builder's 16-source batch.)

| Row | Slot / system | Claim | Pinned source (sha256) | Metric / reader / judge | Class |
|---|---|---|---|---|---|
| L-LME-01 | agentmemory | LongMemEval-S R@5 95.2 / R@10 98.6 / MRR 88.2 | README `e04ba888` `49b467eb…`; `benchmark/LONGMEMEVAL.md` `72a5f411…`; `benchmark/COMPARISON.md` `d74a5290…` | `recall_any@K`, **no LLM / no judge**; `all-MiniLM-L6-v2` | `vendor-only` |
| L-LME-02 | MemBukkit | LongMemEval-S 92.6% | README `f28a2e58` `a462d9cc…`; `docs/guide/benchmarks.md` `11c34675…` | end-to-end QA accuracy; reader `gpt-5.4`; **official `gpt-4o` judge**; `text-embedding-3-large@1536` | `vendor-only` |

**Findings.** (1) The two numbers are different metrics and are **not
comparable** — retrieval recall vs judged answer accuracy. (2) agentmemory
explicitly disclaims the QA interpretation ("We do NOT claim these as
'LongMemEval scores'"). (3) Our own LongMemEval is a third thing — oracle
split, `knowledge-update`, reader-attribution. (4) Both claims are
vendor-self-measured; no independent reproduction is held. (5) MemBukkit's
rival numbers (Hindsight 91.4 judge-swapped to GPT-OSS-120B, Mem0 Cloud 94.4
own GPT-5 judge, etc.) are competitor-published, not independent.

**Checklist adopted from this audit (Muse batch2 item 2.3).** Every benchmark
row must record, or be marked incomplete, **split + metric + reader + judge +
encoder + backend + top-k/thresholds + returned context size**. Applies to
future ledger rows; not retrofitted here.

## Habitus experiment-class settlement (Corvid, R&D mode, 2026-09-12)

`HabitusProvider` (`src/memory_bakeoff/providers/external.py:146`) inherits the
`raw_product` / `product` defaults (`base.py:28-29`) but the evaluated
configuration is **`controlled_core`**: the vendored run uses the upstream
`DeterministicHashEmbedder`, whose own docstring
(`vendor/habitus/src/habitus_ai/embeddings.py:37-44`) calls it an offline
**test/demo stand-in** and says production callers should supply an actual
semantic model. The written evidence pages (`RESULTS.md:80`,
`ROUND1_FINAL_READOUT.md:14`) are correct; the adapter default is the defect.
Fix = explicit class override + `product_ingest=False` (no product path exists);
owner = implementer/build. The claim itself is unchanged and remains
`controlled_core`.

— **Corvid** (`worker-glm-dsh3`), R&D mode. Two claims added, one class
settled; nothing promoted off `vendor-only`.

---

## Builder provenance update — L-S14-02, L-S16-03 (2026-09-12 17:41)

Raw bytes + sha256: `team/builder-provenance-fetches/MANIFEST.md`. Detail and
exact quotes: `team/RD-THREADS.md` § builder / Log. No class changes. Classes
are Corvid's and Alice's to set.

- **L-S14-02 (A-MEM)** was "unsourced" and is now traced to 2502.12110v1 body.
  "Nearly six-fold" = Multi-Hop, one model ("Qwen2.5-15b" [sic]), **ROUGE-L**
  27.23 vs LoCoMo 4.68. "85–93%" is **derived** by aggregators from "1,200-2,500
  tokens, compared to … 16,900 tokens"; the paper does not state it. v11 body
  not checked.
- **L-S16-03 (MemOS)** is still unsourced in any paper. The three numbers are
  absent from 2507.03724 v1–v4 and 2505.22101 v1. First visible appearance:
  Hugging Face paper-page comment by `UglyToilet` ("hanyu Wang", which matches
  arXiv author "Wang, Hanyu" by name only), 2025-07-08T03:16:43Z. It is an
  author-side post, not paper text.

— builder

---

## R&D output check — Corvid / Assay / Stratum (Alice, checker duty, 2026-09-12)

**Author:** Alice (`worker-glm-dsh`) · **Dispatch:** GiLMore (Ledger flagged the
day's R&D outputs had no second-seat check) · **Cost:** $0, one turn.
**Method:** hash-verify every claimed receipt, then **re-run** what is
re-runnable and diff; cross-check Stratum's demo numbers against the files it
cites. Re-runs were non-destructive (B7 pointed at a scratch `--out`, so
Assay's sealed receipt was untouched). Check receipts:
`team/alice-rdcheck-receipts/MANIFEST.md`.

**Verdict: 4 of 4 artifacts pass. All 7 claimed hashes match. All three
re-runnable artifacts reproduce byte-identically. One minor citation omission
(not a numeric error).**

### 1. Corvid — Habitus provenance probe (`repo-glm-dsh3/scripts/probe_20260912_habitus_provenance/`)

| Check | Result |
|---|---|
| `probe.py` sha256 = `d130f76a…` | ✓ matches claim |
| `probe-output.txt` sha256 = `234cb391…` | ✓ matches claim |
| Re-run `python3 probe.py` | rc 0; output **byte-identical** to stored `probe-output.txt` |
| Claim as scoped | ✓ `probe.available True`; `raw=raw_product product=product`; returned ids = native set `M001–M003`; `status verified`, `publishable True`, `methods native: 3`; VERDICT native path |

**No overclaim.** The script docstring and Corvid's log both scope this as
evidence about the *current adapter*, not a receipt for the frozen Gen
artifacts; the log says the frozen rows are "consistent with" native
provenance and that the gap is historical. That limit is stated, not hidden.
The probe also re-confirms the wrong `raw_product` default it reports.

### 2. Assay — B7 powercheck + leak scan (`repo-glm-dsh2/scripts/verify-20260912-assay-row1/`)

| Check | Result |
|---|---|
| `s4_b7_power_check.py` `83d4d77a…` · `powercheck.json` `f529539c…` · `packet_leak_scan.py` `1fc8e6c9…` | ✓ all match |
| Re-run B7 into a scratch dir | `powercheck.json` **byte-identical** to the sealed one |
| Gap reproduces | B7 prints `PASS` (markers 1 == raw 1) while `turn-001.json` carries `key=record-secret-xyz`, `key=record-novel`, `[perseus-maint]` |
| Independent canary grep of the emitted packet | ✓ 1 each of the three canaries |
| `packet_leak_scan.py` on leaky packets | **FAIL** — entries 2 and 3, both `key=record-` |
| `packet_leak_scan.py` on the sealed clean control | **PASS** (rc 0) |

The two checks disagree exactly on the failure class Assay claims. Detection
stays canary-vocabulary-bound, which Assay states as a remaining limit.

### 3. Assay — agentmemory 418/450 second-driver

| Check | Result |
|---|---|
| Script `b1a0dfd6…` · sealed `second_driver.json` `a748575a…` | ✓ match |
| Re-run offline | output **byte-identical** to sealed |
| Numbers | r1/r2/r3: core live/lost `50/0`; distractor live/lost `32/418`; `418/450 = 0.928889`; `all_three_agree true`; verdict `AGREE` |
| Denominator note | ✓ `false_supersession_rate_of_retired = 1.0` is `418/418`, a different quantity; Assay flags it explicitly |
| Bonus: license `76c8d49a…`; UPSTREAM pin `e04ba888…` | ✓ both match (pin identical in all three trees) |

### 4. Stratum — SPRINT-1-DEMO cold-read claims (`team/SPRINT-1-DEMO.md`)

| Claim | Source check | Result |
|---|---|---|
| 14 cited source paths | all exist on disk | ✓ |
| "five serious findings" / "12-item fix list" | `REVIEW-agentdeck-design.md`: S1-1…S1-5; fix table rows 1–12 | ✓ exact |
| agentmemory "13 tests PASS" | `PORTFOLIO-P1-ADAPTER-RECEIPTS.md`: "13 passed in 2.67s" | ✓ |
| long-context null "7-contract; 15 combined" | same file: 7-test contract suite; 15 passed combined | ✓ |
| "182 MB pinned dataset" | same file: `external/MemConflict` 182 MB, pin `ec51d5d` | ✓ |
| S1 CLOSED, 0 Brian confirms | `SCOREBOARD` change-log: "S1 CLOSED … 0 Brian confirms" | ✓ |
| S4 counting since ~14:21; 14/14 | `SCOREBOARD` §S4 and change-log | ✓ |
| S6 "0 violations" | `SCOREBOARD` §S6 | ✓ |
| window-open Perseus hash | `WINDOW-OPENING.md`: `c8a222ec…` | ✓ |
| Muse "9 → 3 ACCEPT / 5 DUPLICATE / 1 REJECT" | `MUSE-IDEATION-01.md` tally | ✓ |
| Q1.2 seven providers, leaky `+0.96` | `RESEARCH-Q1.2…`: seven providers, `+0.958` (demo rounds) | ✓ |

**One minor finding (citation hygiene, not a number error).** The S3 sample
"11 confirmed writes, 8 by agents" is real — its source is
`team/ROW9-BLIND-HARNESS.md:19` ("11 items = 8 agent-confirmed + 3
operator-confirmed") — but that file is **not** in §3's cited source list
(`WINDOW-OPENING`/`SCOREBOARD`/`CAMPAIGN-1`). Recommend adding it. Every other
number traced to a listed source.

**Disclosed staleness, no action.** §2 says rows 16–17 were "still open";
row 17 closed 16:33 and row 16 before 16:50. The demo's own method limit pins
state at ~16:28, so this is honest, not an error.

### What was not checked

- No live/blinding-coupled instrument was re-run (live S4 packets, fire log,
  S6 scans, trial smoke) — consistent with rater blinding. Only synthetic and
  committed instruments were re-executed.
- Stratum's demo is assembly; I verified numbers against their source files,
  not the underlying measurements (that is Assay's/Corvid's receipts, which I
  did verify).
- No engine or benchmark was run; this is receipt verification, not
  reproduction.

— Alice (`worker-glm-dsh`), checker duty. 4/4 pass; the batch is
second-seat checked.

---

## Hindsight "independently reproduced" claim — audited (Corvid, R&D, 2026-09-12)

**Scope:** public-source provenance audit; no engine, no run. Full note:
`team/RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md`.

| Row | Claim | Source | Reference found | Class |
|---|---|---|---|---|
| L-HS-01 | benchmark data "independently reproduced by research collaborators at the Virginia Tech Sanghani Center … and The Washington Post" | Hindsight `README.md` @ `ebad4782` L48 | ACL 2026 demo `2026.acl-demo.27`: three VT researchers (Srivastava, Wang, Ramakrishnan) are **co-authors** | `contradicted` |
| L-HS-02 | 94.6% LongMemEval, "highest score of any memory system" | live `vectorize.io/benchmarks` | the same vendor's ACL paper reports **91.4%** (Gemini-3 Pro) / **83.6%** (20B OSS) | ~~`contradicted` / unsourced~~ **SUPERSEDED — see "L-HS split" below: L-HS-02a `vendor-only` (94.6 number), L-HS-02b `not established` (superlative)** |
| L-HS-03 | 91.4 LongMemEval | MemBukkit guide (judge swapped GPT-OSS-120B); ACL paper (Gemini-3 Pro); README (no model) | same number, three attributions | `vendor-only` + **`third-party-attributed`** (Chronos paper cites Hindsight's 91.4; it does not measure Hindsight — see "Class refinement"; supersedes the `third-party` label) |

**Findings.** (1) "Independently reproduced by … collaborators" is a
self-contradiction; the reproducers co-authored the system. (2) The live 94.6%
headline conflicts with the vendor's own peer-reviewed paper (91.4/83.6).
(3) No Washington Post reference located. (4) The vendor page cites LongMemEval
as arXiv `2512.12818`; our substrate is ICLR-2025 LongMemEval `2410.10813`
(oracle split) — not the same paper.

— **Corvid** (`worker-glm-dsh3`). The independence claim now has a reference,
and the reference refutes it.

**Body verification addendum (2026-09-12).** ACL PDF fetched (sha
`c1bc5839…`, `pdftotext` text in `team/rd-threads-fetches/`). The title block
lists `The Washington Post, USA` and `Virginia Tech, USA` as **author
affiliations**; the paper's own acknowledgements thank those co-authors "for
independently reproducing the benchmark results," and Table 2's LongMemEval-S
maximum is **91.4** (Gemini-3) — no 94.6. Independence claim and 94.6 headline
both stay `contradicted`. Full detail:
`team/RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md` §Addendum.

**94.6% provenance addendum (2026-09-12).** The live page's "full benchmark
results" link resolves to **AMB** (`vectorize-io/agent-memory-benchmark`),
whose README says "We built AMB because we wanted to be honest about how
Hindsight performs." So 94.6% is from a **vendor-built benchmark** (Gemini
generation + Gemini judge), labeled "LongMemEval" on the page, and it exceeds
the vendor's own ACL paper's LongMemEval-S max (91.4). L-HS-02 stays
`contradicted` as a LongMemEval-S claim (later **superseded** — see "L-HS split"
below: L-HS-02a `vendor-only`, L-HS-02b `not established`).

---

## Awaiting-item merge notes (Corvid, 2026-09-12)

**Zep number collision (scoreboard Awaiting line 1242).** Two different Zep
numbers circulate around Memobase's table: the table's Zep row is **65.99**,
which Alice's row-20 chase shows was pasted from the **Mem0 paper**, while the
Memobase README elsewhere reports a separate **Zep\* 75.14** (issue #101).
Annotation: L-S15-01's Zep cell is Mem0-paper-origin, **not a Memobase
measurement**; the Zep\* 75.14 is a different number with no located
measurement. Cite neither as a Memobase-run Zep result.

**Mem0 LoCoMo headline (scoreboard Awaiting line 1249).** The live Mem0 blog's
**92.5%** headline traces to no shipped artifact; the shipped run is **91.56**.
The paper's **66.88** and Letta's cited **68.5** are further copies. Per Alice
(20:01), the 2025 Mem0 code has no category names, so pre-2026 LoCoMo
per-category numbers must be cited by numeric id (1 multi-hop, 2 temporal,
3 open-domain, 4 single-hop, 5 adversarial) or not at all.

Annotation only; no number is promoted and no class changes.

— **Corvid** (`worker-glm-dsh3`), ledger custodian.

---

## L-HS split — Hindsight classification dispute resolved (Corvid + Alice, 2026-09-12)

The Awaiting item (scoreboard L1318) asked the ledger owner + Alice to split
L-HS-02 into the **number** and the **superlative**. The original row conflated
two claims whose evidence differs. Superseding table:

| Row | Claim | Evidence | Class |
|---|---|---|---|
| L-HS-01 | benchmark data "independently reproduced by research collaborators at the Virginia Tech Sanghani Center … and The Washington Post" | ACL title block: both institutions are **co-authors** (Corvid + Alice agree) | `contradicted` |
| **L-HS-02a** | **94.6% on LongMemEval** | reproduces exactly from AMB's published raw rows (**473/500**; `ALICE-HINDSIGHT-AMB-REDERIVE.md`); AMB is a **vendor-operated** harness (Gemini answerer + Gemini judge) | **`vendor-only`** — not `contradicted`: our recompute agrees with the number |
| **L-HS-02b** | "highest score of any memory system" | AMB's own external rows put Chronos 0.956 above it, but that is Chronos **High on Claude Opus 4.6** vs Hindsight on **Gemini 3.1 Pro**; the GPT-4o-matched Chronos is **92.60 < 94.6**, and AMB labels the rows "not directly comparable" (`ALICE-CHRONOS-956-CHECK.md`) | **`not established`** — contradicted only in a non-matched comparison |
| L-HS-03 | 91.4 LongMemEval | the Chronos paper (`arXiv:2603.16862`, Table 2) independently attributes Hindsight **91.40 to an OSS-120B judge** (footnote: not comparable to the official judge), matching the ACL paper and MemBukkit's caveat | `vendor-only` + **`third-party-attributed`** (the paper cites Hindsight's config; it does not measure Hindsight — see "Class refinement" below; supersedes the original `third-party` label) |

**Both runs recorded:** **91.4** (report; OSS-120B judge) and **94.6** (AMB
vendor run; Gemini answerer + Gemini judge). Neither uses the official judge;
the ACL paper's own maximum is 91.4.

**Register handoff:** Alice to update the Hindsight row in
`team/ALICE-VENDOR-DATA-TRANSPARENCY.md` with both runs and these split classes
— I did not edit her file (one writer per tree).

— **Corvid** (`worker-glm-dsh3`), ledger custodian. Number kept, superlative
downgraded, independence stands `contradicted`.

---

## MemOS / OmniMemEval merge (Corvid, ledger owner, 2026-09-12) — Awaiting L1319/L1320

**L-S16-02 — metric pinned, and the first independent measurement of a ledger
system.**
- **Self-report (stays `vendor-only`):** LongMemEval-S **89.20** / LoCoMo **88.83**
  via MemOS's own **OmniMemEval** harness. "Metric unknown" is resolved: answer
  `gpt-4.1-mini-2025-04-14`, judge `gpt-4o-mini-2024-07-18` (LLJ)
  (`ALICE-OMNIMEMEVAL-METRIC.md`, receipts `team/row-omnieval-receipts/`).
- **Third-party measurement (new sub-row L-S16-02b):** TiMem
  (`arXiv:2601.02845`, Table 2) measures MemOS on **LongMemEval-S** under the
  official template at **73.07 (GPT-4o) / 68.68 (GPT-4o-mini)** vs the 89.20
  self-report — a **−16.1 pt** gap. Because MemOS's metric is now pinned as a
  different protocol, the gap is **cross-protocol, not unexplained**. Under the
  ledger's definition ("external party with no stake measured it; we hold the
  reference") this row is **`third-party`** — a measurement of MemOS, **not** a
  verification of MemOS's claim; both numbers are recorded, neither overwrites
  the other.
- **Plausibility flag:** three of six LongMemEval categories (SS-User, SS-Asst,
  SS-Pref) are exactly **100.00** under MemOS's own harness — the shape an
  over-easy judge or retrieval path would produce. Reason to look; not a defect
  claim.

**L-S16-03** (+159% / +38.97% / −60.95%) stays **`unsourced`**.

**OmniMemEval operator COI (new).** OmniMemEval is operated by MemOS and leads
its own table. Its reproduced LongMemEval-S rows — Mem0 **56.00**, Hindsight
**72.20** (SS-Asst **14.29**), Supermemory **66.07**, Zep **79.80** — are
`vendor-only` and must be cited as a **MemOS-operated harness**, never as neutral
measurements. Alice (21:56): the judge is one generic "touches on the same
topic" prompt, not the official task-specific rubric, so they are not
official-protocol numbers; the rivals' lows harden because they are low even
under a lenient judge.

**Zep numbers (add to the collision annotation).** OmniMemEval publishes Zep
LoCoMo **94.7** and LongMemEval **90.2** (split unspecified), bringing Zep to six published numbers
across four benchmarks (DMR 94.8 · LoCoMo 65.99 · LoCoMo 75.14 · LongMemEval
71.2 · LoCoMo 94.7 · LongMemEval 90.2, split unspecified) — the strongest single case for "name the
source or do not cite it."

**Action-row resolution:** L-S16-02's action "obtain MemOS's judge/metric
definition" is **closed** (metric pinned).

— **Corvid** (`worker-glm-dsh3`), ledger custodian.

---

## Class refinement: `third-party` vs attribution (Corvid, 2026-09-12) — answers Awaiting L1351

The Awaiting item asks whether a peer-reviewed outside measurement moves a row
into `third-party`, and flags an "attribution-vs-verification" question on
L-HS-03. Resolution, applied to the ledger:

- **`third-party`** (the four-class label) = an external party **measured or
  verified the system itself**, and we hold the reference.
- **`third-party-attributed`** (carried disposition, like `unsourced`) = an
  external party **cites the vendor's own number/config** without measuring the
  system. It does **not** move the number off `vendor-only`.

**Applied — MemOS gains the LoCoMo half (completes L-S16-02b):**
- **L-S16-02b = `third-party-measured`** (carried disposition). TiMem
  (`arXiv:2601.02845`) ran MemOS on **both** benchmarks: **LoCoMo 69.24**
  (Table 1, GPT-4o-mini, **Mem0 LLJ prompt template** — not the official LoCoMo
  judge) vs self **88.83** (Δ −19.6),
  and **LongMemEval-S 73.07 (GPT-4o) / 68.68 (mini)** vs self **89.20**
  (Δ −16.1). The self-report stays `vendor-only`; the independent measurement is
  recorded and the gap is cross-protocol (OmniMemEval uses a generic
  "touches the same topic" judge, not the official task-specific rubric).

**Applied — L-HS-03 corrected to `vendor-only` + `third-party-attributed`:**
The Chronos paper (`arXiv:2603.16862`, Table 2) **reports** Hindsight 91.40 with
an OSS-120B judge; it does not measure Hindsight. This **supersedes** the 22:50
L-HS split, which had labelled L-HS-03 `third-party` — an over-classification.

**Answer to the Awaiting question:** a peer-reviewed outside **measurement of
the system** (TiMem → MemOS) qualifies as `third-party`; a peer-reviewed outside
**citation of the vendor's own number** (Chronos → Hindsight) does not.

— **Corvid** (`worker-glm-dsh3`), ledger custodian.
