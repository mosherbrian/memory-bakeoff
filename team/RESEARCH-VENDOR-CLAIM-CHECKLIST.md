# Vendor-claim integrity checklist — from the Hindsight audit to P2

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-12 · **Cost:** $0, synthesis over existing ledger/survey
receipts (no new fetches; provenance already on file)
**Why:** the Hindsight audit (`team/RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md`)
caught four distinct defects in one claim. The portfolio's P4 close report will
cite these vendors again, so the checks that caught it should be a standing
gate, not a one-off.

**Plain English (for Brian):** a vendor's benchmark number can be wrong in ways
a citation does not reveal. The Hindsight case exposed six checks, each cheap,
each with a receipt. This note lists them and maps the portfolio's engines
against them so P2/P4 can run the gate before any number is repeated.

## The six checks

1. **Trace social proof to authorship.** "Independently reproduced" often means
   the reproducers are co-authors. Check the paper's author/affiliation list.
   *Hindsight:* the README's "independent" parties (Virginia Tech, The
   Washington Post) are paper **co-authors** — the acknowledgement is the
   README sentence.
2. **Compare the marketing number to the peer-reviewed number.** If the live
   headline exceeds the paper, flag it. *Hindsight:* live **94.6** vs paper
   **91.4** (Gemini-3) / **83.6** (20B OSS).
3. **Identify who operates the benchmark/leaderboard.** A vendor-run benchmark
   is not independent. *Hindsight:* the 94.6 came from **AMB**
   (`vectorize-io/agent-memory-benchmark`), built by the vendor.
4. **Pin split + metric + reader + judge.** "LongMemEval", "accuracy", and
   "SOTA" are not comparable without them. *Hindsight:* paper is LongMemEval-S
   (Wu et al. 2024); page cites a different arXiv (`2512.12818`); the vendor
   page names no generation/judge.
5. **Check citation identity.** The cited paper must be the one used.
   *Hindsight:* `2512.12818` ≠ the paper's Wu et al. 2024.
6. **Check for multi-attribution of one number.** *Hindsight:* **91.4** is
   attributed to Gemini-3 Pro (ACL paper) and to a swapped GPT-OSS-120B judge
   (MemBukkit's competitor guide), and to no model (README).

## Portfolio status against the checks (existing receipts only)

| Engine | Peer-reviewed paper located? | Marketing vs paper | Benchmark operator | Split / judge named? | Flag |
|---|---|---|---|---|---|
| **Hindsight** | ACL 2026 demo, **co-authored by the "independent" parties** | 94.6 (live) > 91.4 (paper) | **vendor (AMB)** | page: no; paper: LongMemEval-S | **3 fails** (§Addendum, ledger L-HS-01..03) |
| **Zep / Graphiti** | arXiv 2501.13956 (vendor) | "+18.5%" re-derived as **18.27%** from Table 2 | vendor paper | judge unstated | arithmetic flag (Alice, ledger L-S17-02) |
| **Mem0** | arXiv 2504.19413 | live 92.5 vs paper 66.88 vs Letta-cited 68.5 | vendor + rivals' tables | judge varies | number unstable (Alice flag 3) |
| **MemOS** | arXiv 2507.03724 | README 89.20/88.83 via own OmniMemEval | vendor harness | metric/judge absent | metric undefined; 159% unsourced (L-S16-02/03) |
| **MemBukkit** | paper **"under review"** (no peer-reviewed version located) | 92.6 vendor-only | vendor recipe, **official gpt-4o judge** | reader gpt-5.4 + judge named | vendor-only; best-documented claim in the set |
| **agentmemory** | none located | 95.2 = retrieval-only (no judge) | own harness | explicitly disclaims "LongMemEval score" | honest scope; vendor-only (L-LME-01) |
| **Memobase** | vendor table only | 75.78 self-run | vendor | judge gpt-4o named | rivals' rows pasted from Mem0's paper (Alice flag 1) |
| **Letta** | vendor blog | 74.0 | vendor | gpt-4o-mini, files-only | no independent reproduction |
| **Habitus** | none located | no vendor Hit@5 at pin | our own receipts only | n/a | vendor claim corrected in survey (flag 4) |

## The gate for P2/P4

Any headline number entering the P4 close report must carry, in-line:
**paper-or-none · operator · split · metric · reader · judge · reproduction
command**. A number that fails checks 1–3 is reported as vendor-marketing, not
evidence. This is the same "receipts claim; state is" rule applied to external
claims.

— **Corvid** (`worker-glm-dsh3`). One audit became a checklist; the portfolio
should not re-learn it system by system.
