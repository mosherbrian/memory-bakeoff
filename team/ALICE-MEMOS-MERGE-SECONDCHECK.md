# Second-seat check of the MemOS / L-S16-02b ledger merge

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-13 · **Trigger:** Awaiting item "MemOS: self-reported vs
independently measured — Remaining: second-seat check of the merge" and the
standing duty "second-check new R&D artifacts (CLAIMS-LEDGER additions)" ·
**Cost:** $0, read-only over already-hashed receipts, one turn.

**Receipts re-hashed against their MANIFESTs (all match):**
`team/row-timem-receipts/timem-text.txt` `d68ce685…`,
`team/row-omnieval-receipts/docs_user_memory_results.md` `164d0c85…`,
`team/row-smartsearch-receipts/ss-text.txt` `f19d6fe1…`,
`team/row-chronos-receipts/paper-text.txt` `f732a9ee…`.

## Verdict

**Transcription ACCURATE — every number and class call in the merge reproduces
from the frozen receipts. One label correction, numbers unchanged.**

## Claim-by-claim

| Ledger claim (merge section, `CLAIMS-LEDGER.md` L823–L897) | Receipt | Reproduced |
|---|---|---|
| MemOS self **LongMemEval 89.20** | `results.md` summary table header `LoCoMo \| LongMemEval` → `MemOS 88.83 \| 89.20`; LongMemEval reproduced row `… 84.62 \| 89.20` | ✓ |
| MemOS self **LoCoMo 88.83** | same summary table; LoCoMo table `… \| 88.83` | ✓ |
| Metric: answer `gpt-4.1-mini-2025-04-14`, judge `gpt-4o-mini-2024-07-18` | `results.md` setup table | ✓ |
| Plausibility flag: SS-User / SS-Asst / SS-Pref exactly **100.00** | LongMemEval reproduced row `100.00, 100.00, 100.00, 89.47, 78.95, 84.62` | ✓ |
| TiMem measures MemOS LongMemEval-S **73.07 (GPT-4o) / 68.68 (mini)** | TiMem Table 2, both answer-model blocks | ✓ |
| TiMem measures MemOS LoCoMo **69.24** | TiMem Table 1 `MemOS … 69.24 ± 0.11` | ✓ |
| Gaps **−16.1 / −19.6** | 89.20−73.07 = 16.13; 88.83−69.24 = 19.59 | ✓ |
| SmartSearch same pair (`gpt-4.1-mini` + `gpt-4o-mini`) MemOS **77.8** | Table 7 `MemOS a 77.8 …` | ✓ |
| OmniMemEval rivals: Mem0 **56.00**, Hindsight **72.20** (SS-Asst **14.29**), Supermemory **66.07**, graphiti-zep **79.80** | LongMemEval reproduced table | ✓ |
| L-HS-03: Chronos paper **reports** Hindsight **91.40** with an OSS-120B judge footnote ("not directly comparable to systems evaluated with the official benchmark judge") | `paper-text.txt` | ✓ |

Class calls concur: **L-S16-02b = `third-party-measured`** (TiMem ran MemOS on
both benchmarks), **L-HS-03 = `vendor-only` + `third-party-attributed`**
(Chronos reports Hindsight's number/config; it does not measure Hindsight). The
merge's own line L832 already states the LongMemEval arm correctly ("under the
official template").

## Correction (one label; no number moves)

L884 reads:

> LoCoMo **69.24** (Table 1, GPT-4o-mini, **official LoCoMo protocol**) vs self 88.83

The TiMem paper says the opposite for LoCoMo. Its own two protocol sentences:

- LongMemEval: *"The QA and LLJ protocol follow the official LongMemEval-S
  evaluation template, as shown in Appendix E.2.1 and E.2.2."*
- LoCoMo: *"We compute LLJ using **Mem0's evaluation prompt template**, as shown
  in Appendix E.1.2."*

So the LoCoMo arm is a **Mem0-prompt-template** number, not the official LoCoMo
judge. Recommended replacement: `Mem0 LLJ prompt template (de facto; not the
official LoCoMo judge)`. Numbers, gaps, and class are unaffected. This matters
because the citation rule and Harness Guardrails #1–2 require pinning the judge
**prompt**, not just the benchmark name — an "official" label here would let the
69.24 (and the −19.6 gap) later be cited as official-protocol when the source
paper does not claim that.

**Owner:** ledger custodian (Corvid) applies the phrase fix at L884; I did not
edit a file I do not own.

## Method and limits

- Stored-artifact re-derivation only: I re-read the frozen text the merge cites
  and re-ran the arithmetic; I did not re-run TiMem's or OmniMemEval's harness.
- TiMem is a peer-reviewed external measurement of MemOS, but its harness is not
  audited by us; "official LongMemEval template" is the paper's own prose, not an
  independent diff against the upstream LongMemEval repo (Alice's earlier judge
  check compared OmniMemEval against that repo, not TiMem).
- The OmniMemEval rival rows remain MemOS-operated (COI) and generic-judge, as
  the merge already states; this check confirms transcription, not neutrality.
