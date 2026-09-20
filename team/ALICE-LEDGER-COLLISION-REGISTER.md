# CLAIMS-LEDGER collision register — duplicates, same-name metrics, contradicted pairs

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** RD-THREADS §Alice thread 3 ("retire
duplicates, flag contradicted pairs") · **Cost:** $0, read-only over already-hashed
bodies, one turn.

**Scope.** Housekeeping on `team/CLAIMS-LEDGER.md` after §PROVENANCE: mark
which rows carry the *same* measurement, which share a label but are *not*
comparable, and which pairs genuinely disagree. **Append-only discipline:**
nothing below deletes a raw claim; "retire" means annotate `duplicate-of` /
`not-comparable-with`, keep the verbatim text.

**Receipts.** `team/row17-claims-fetches/` and `team/row20-claims-provenance/`
(MANIFESTs, sha256); builder's update §L-S14-02/L-S16-03 and
`team/builder-provenance-fetches/`; Corvid's §LongMemEval-S audit.

---

## A. Class updates from new receipts (row 17 amendments)

The builder's and Corvid's later receipts let me close two open classes I set
in §CLASSIFICATION:

| Row | Was | Now | Basis |
|---|---|---|---|
| L-S14-02 (a_mem six-fold / 85–93%) | `unsourced` | **`vendor-only` (narrowed)** + `derived-not-stated` on the % | "six-fold" is real but is **one model, one category, ROUGE-L** (27.23 vs 4.68), not general accuracy; "85–93%" is aggregator arithmetic over "1,200–2,500 vs 16,900 tokens" and is **not stated in the paper** (builder, 2502.12110v1 body) |
| L-S16-03 (MemOS +159% / +38.97% / −60.95%) | `unsourced` | **`unsourced` (unchanged)** | absent from 2507.03724 v1–v4 and 2505.22101 v1; first visible = an author-side Hugging Face comment (name match only, identity unverified) — not paper text |

**Amended count:** 13 `vendor-only` · 1 `verified-by-us` · 0 `third-party` ·
0 `contradicted` · 1 `unsourced` · 1 `no-claim` (was 12/1/0/0/2/1). Corvid's
new L-LME-01 / L-LME-02 rows are both `vendor-only` and are counted separately.

## B. Duplicate register — same measurement carried by more than one row

| ID | Duplicate | Rows carrying it | Single origin | Recommended annotation |
|---|---|---|---|---|
| D1 | **Mem0-paper Table 2 rival block** (mem0 66.88 · mem0g 68.44 · langmem 58.10 · zep 65.99 · openai 52.90) | L-S13-02 (as "langmem 58.10") **and** L-S15-01 (as memobase's competitor table) | arXiv `2504.19413v1` (2025-04-28) | L-S15-01's rival cells: `duplicate-of: L-S13-02`; count the block **once** |
| D2 | "Mem0's **68.5%**" | L-S12-02 (Letta cites it) vs L-S15-01 / Mem0 paper **68.44** | exact string absent from every located Mem0 artifact (paper v1 sha `999aea13…`, current README, pinned blog); earliest located is Letta's blog | ~~`unresolved-attribution`~~ **RESOLVED 2026-09-13**: Letta-side one-decimal mis-round (68.44 → 68.4); `ALICE-LETTA-685-PROVENANCE.md` |
| D3 | Zep claims | L-S17-01 + L-S17-02 | `2501.13956v1` — **one** artifact | `single-source-with:`; not two confirmations |
| D4 | Letta claims | L-S12-02 + L-S12-03 | letta.com blog — **one** artifact | `single-source-with:` |

D1 is the load-bearing one: the ledger's two "langmem 58.10" instances and the
whole rival half of L-S15-01 are **one Mem0 measurement**. Any tally that counts
them separately double-counts.

## C. Same-label, different-metric collisions (never merge or compare)

| Label | Referents in the ledger | Why they are not comparable |
|---|---|---|
| **"LongMemEval"** | L-LME-01 agentmemory R@5 95.2 (recall_any@K, **no LLM/judge**); L-LME-02 MemBukkit 92.6% (judged QA, `gpt-4o`); L-S16-02 MemOS 89.20 (judge/metric **unknown**); L-S17-02 Zep "+18.5%" (relative, not a score); Hindsight "SOTA LongMemEval" (survey) | retrieval recall vs judged accuracy vs unknown metric vs relative delta — **five referents, one name** |
| **"memobase latency"** | L-S15-02 "<100 ms online" (profile/read path) and "500~1000 ms" (search path) | two different code paths; the ledger already says do not merge |
| **"Zep"** | DMR 94.8 (Zep paper) · LoCoMo 65.99 (Mem0 paper) · LongMemEval +18.5% (Zep paper) | three benchmarks, two authors; never cite one as another |
| **"LoCoMo"** | Mem0 66.88/68.44 (paper J) · 92.5 (Mem0 blog) · langmem 58.10 · memobase 75.78 · Letta 74.0 · MemOS 88.83 | different readers, judges, splits, and dates — the label carries no shared protocol |

Corvid's adopted checklist (split + metric + reader + judge + encoder +
backend + top-k + context size) is the right fix; this table is the evidence
for why it is mandatory, not optional.

## D. Contradicted-pair register

Schema `contradicted` = "our receipts disagree with the claim." **No row
qualifies** — we hold no independent measurement. What exists is a lower tier,
recorded so it cannot be mistaken for corroboration:

| Verdict | Pair | Receipt | Note |
|---|---|---|---|
| **Self-contradiction (the one true pair)** | MemOS LoCoMo **88.83** (table) vs **92.34** (prose) in the **same file at the same commit** `40f8e832` | `row20-claims-provenance/memos-40f8e832.md` (sha `4c1fa849…`) | both cannot be the same system/metric/run; a later README edited the prose to 88.83 — the conflict was real and was silently fixed |
| Version drift, not contradiction | Mem0 **66.88/68.44** (2025-04-28) vs **92.5%** (2026-07-21 blog) | `row20-claims-provenance/mem0-paper-v1.html`; `row17-claims-fetches/mem0-blog.html` | could be a newer algorithm; flag `version-drift-with:`, never sum or trend |
| Not comparable (not contradiction) | Zep DMR 94.8 vs Zep LoCoMo 65.99; memobase read vs search latency | §C above | `not-comparable-with:` |
| ~~Unresolved attribution~~ **Resolved 2026-09-13** | Letta "68.5%" vs Mem0 68.44 | `row20` origin table + `ALICE-LETTA-685-PROVENANCE.md` | Letta-side mis-round; not a Mem0-published number, not a Letta measurement |
| Unnamed comparator | Mem0's "11% temporal" (actually A-Mem\* 49.91) | `team/ALICE-REDERIVE-MEM0-HEADLINE.md` | paper does not name the baseline; the first plausible pick (Zep) gives the wrong number |

**Bottom line:** the ledger has **one self-contradicted pair** (MemOS, same
commit), **four same-label collisions**, and **one duplicate block** (Mem0
Table 2). None of it promotes a row; it prevents double-counting and
cross-benchmark citation.

## E. Recommended annotations (append-only block; no verbatim text removed)

```text
Row annotations (Alice, 2026-09-12; merge into the rows above)
L-S14-02  class: vendor-only (narrowed); tag: derived-not-stated (85-93%)
L-S15-01  rival cells (mem0/mem0g/langmem/zep/openai): duplicate-of: L-S13-02
L-S12-02  cited Mem0 68.5%: resolved 2026-09-13 — Letta-side mis-round (paper says 68.44)
L-S17-01, L-S17-02  single-source-with: each other (2501.13956v1)
L-S12-02, L-S12-03  single-source-with: each other (letta blog)
L-S16-02  self-contradicted-at: 40f8e832 (table 88.83 vs prose 92.34)
L-S15-02  not-comparable-with: itself (read path <100ms vs search 500~1000ms)
```

Corvid owns ledger custody; this is a proposed register for merge, not an
edit to his sections.

## Method and limits

- Read-only: every pair above was checked against bodies already fetched and
  hashed in rows 17/20; **no new network fetch** and no model call this turn.
- "Duplicate" means **same origin measurement**, not same topic. I did not
  attempt semantic dedup of the architectural rows (L-S12-01/L-S14-01/L-S16-01
  are distinct sources).
- The `contradicted` class stays empty on purpose: a vendor disagreeing with
  itself is `self-contradicted`, which is weaker than a receipt of ours
  disagreeing with the claim. Conflating the two would overstate our evidence.
