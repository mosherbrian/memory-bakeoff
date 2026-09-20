# SmartSearch cluster verified — and a de facto LongMemEval protocol plus a 14-point framework swing

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-CHRONOS-956-CHECK.md` /
`ALICE-TIMEM-SOURCE-CHECK.md`; AMB sources three more rows to the SmartSearch
paper · **Cost:** $0 (two arXiv fetches), one turn.

**Receipts:** `team/row-smartsearch-receipts/` (`MANIFEST.md` with sha256):
`arXiv:2603.15599` ("SmartSearch: How Ranking Beats Structure for Conversational
Memory Retrieval") abs + HTML + text.

## Finding 1 — AMB's cluster is faithfully sourced

The SmartSearch paper's Table 7 (LongMemEval-S) contains, verbatim:

| System | Overall | KU | MS | SA | SP | SU | TR |
|---|---|---|---|---|---|---|---|
| SmartSearch (index-free) | **88.4** | 93.6 | 84.2 | 85.7 | 96.7 | 100.0 | 82.7 |
| Memora | **87.4** | 97.4 | 78.2 | 78.6 | 83.3 | 98.6 | 89.5 |
| EverMemOS | **83.0** | 89.7 | 73.7 | 85.7 | 93.3 | 97.1 | 77.4 |
| MemOS | **77.8** | 74.3 | 70.7 | 67.9 | 96.7 | 95.7 | 77.4 |
| Nemori | 74.6 | 79.5 | 55.6 | 92.9 | 86.7 | 90.0 | 72.2 |
| Mem0 | 66.4 | 66.7 | 63.2 | 26.8 | 90.0 | 82.9 | 72.2 |
| Full-context | 65.6 | 76.9 | … | | | | |

AMB's external rows SmartSearch 0.884, Memora 0.874, EverMemOS 0.830 are exact.
**No sourcing error** in this cluster either; AMB's external registry is holding
up under every spot-check (Chronos, TiMem, SmartSearch).

## Finding 2 — a de facto LongMemEval protocol is emerging

Table 7 states: *"All systems use `gpt-4.1-mini` as answer LLM and `gpt-4o-mini`
as judge."* That is **the same answer/judge pair as OmniMemEval's setup**
(`ALICE-OMNIMEMEVAL-METRIC.md`), and TiMem likewise uses a `gpt-4o-mini`-class
answerer with an LLM judge. So several independent 2026 papers converge on
**LongMemEval-S with a gpt-4.1-mini/gpt-4o-mini judge pair**, which is a far
better comparability anchor than any vendor's self-run (Hindsight's Gemini
answer+judge; MemBukkit's gpt-5.4 reader; agentmemory's judge-free recall).

**Portfolio implication:** when the charter compares LongMemEval-family numbers,
name this protocol as the reference and treat vendor self-runs as a different
instrument.

## Finding 3 — MemOS now has three independent measurements, all below self

| Source | Protocol | LongMemEval-S |
|---|---|---|
| MemOS self (OmniMemEval) | gpt-4.1-mini / gpt-4o-mini | **89.20** |
| SmartSearch paper | gpt-4.1-mini / gpt-4o-mini | **77.8** |
| TiMem paper | GPT-4o | **73.07** |
| TiMem paper | gpt-4o-mini | **68.68** |

The three independent values cluster **~69–78**, i.e. **11–20 points below** the
vendor's self-report, and the SmartSearch run uses the *same* protocol as
OmniMemEval — which weakens "OmniMemEval's protocol is just more generous" as an
explanation. This strengthens the `cross-vendor-measured` flag on L-S16-02.

## Finding 4 — the strongest protocol-sensitivity statement we have

The paper's limits section: *"The full-context baseline alone shifts from 77.1%
to 91.2% across frameworks — a **14 pp swing with no retrieval change**."* It
therefore reports under two protocols separately and *"never compare[s] numbers
across them."* That is (a) the clearest evidence yet for the portfolio's "pin the
harness" rule, (b) a direct warning that the E-1 long-context null is
**framework-dependent**, and (c) an independent endorsement of the collision
register's "name the grader or don't cite it."

## Consequence for the ledger

- AMB's external registry: **verified faithful** for a third cluster.
- **L-S16-02 (MemOS)**: add SmartSearch 77.8 (same protocol) to the
  cross-vendor cluster; the self-vs-independent gap is now three-for-three.
- Add to the P2 rules: the **gpt-4.1-mini/gpt-4o-mini LongMemEval-S** protocol is
  the current de facto reference; and quote the 14 pp framework swing whenever a
  long-context null is presented.

## Method and limits

- Read the paper's HTML full text; extracted Table 7 and the quoted statements
  verbatim. No benchmark, engine, or LLM run.
- I did not verify SmartSearch's own 88.4 beyond its report, nor open the
  Memora/EverMemOS source papers; they are recorded as this paper's measurements.
