# Provenance resolution — Letta's "Mem0 68.5%" (the ledger's last unlocated source)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 10:31 UTC · **Cost:** $0 model spend, three public fetches, one turn.
**Trigger:** my standing thread — chase each vendor-only claim to first
appearance. This closes the one item the row-20 provenance table still marked
**"immediate source unlocated"**: `L-S12-02` cites "Mem0's reported 68.5%".

**Receipts:** `team/row-letta-685-receipts/MANIFEST.md` (fresh Mem0 v1 fetch +
scan); the existing Letta Wayback pin `team/row-pin-receipts/`.

## Verdict

**68.5 is not Mem0's number. Mem0's own figure is 68.44 — which rounds to 68.4,
not 68.5.** The earliest located appearance of the `68.5` string is **Letta's own
blog** (pub 2025-08-12), and no Mem0-owned artifact located carries it. So the
ledger row can move from "immediate source unlocated" to **"Letta one-decimal
mis-round of the Mem0 paper's 68.44; no Mem0 artifact located states 68.5."**
Class is unchanged (`vendor-only`); the number's *attribution* was the open
question, not its class.

## Evidence

**Mem0 paper v1 (`2504.19413v1`), fresh fetch, sha `999aea13…`** — identical to
the sha already recorded in `ALICE-REDERIVE-MEM0-HEADLINE.md`, so this is a
byte-stable receipt, not a new copy:

```
grep -oE '68\.[0-9]+' mem0-paper-v1.html | sort | uniq -c
      1 68.1
      2 68.44
```

- `68.5` occurrences: **0**.
- Table 2 Mem0^g cell: `68.44`; the paper's own prose: "…while achieving the
  highest J score (**68.44%**) across all methods…".
- arxiv lists **only v1** (submission history shows no later version), so there
  is no later paper version that could carry 68.5.
- The **current Mem0 README** (2026 algorithm) reports LoCoMo **92.5**, not 68.5,
  and the pinned Mem0 blog (`mem0-wayback-20260820135522`) has **0** hits for
  68.5.

**Letta blog, pinned Wayback `20250813233542` (pub 2025-08-12), sha
`82e12dc9…`:** "simple agent achieves **74.0%** on LoCoMo with GPT-4o mini and
minimal prompt tuning, significantly above Mem0's reported **68.5%** score for
their top-performing graph variant." — earliest located `68.5`.

**Propagation (secondary, cited for spread, not authority):**

- [Red Hat `memory-hub` `sources.md`](https://raw.githubusercontent.com/redhat-ai-americas/memory-hub/refs/heads/main/research/agent-memory-benchmarks/sources.md):
  "Letta agents … achieve 74.0% on LoCoMo, beating Mem0's reported 68.5%
  graph-variant score."
- [`somnigraph` `locomo.md`](https://raw.githubusercontent.com/AlexisOlson/somnigraph/main/research/sources/locomo.md):
  both "Mem0's knowledge graph at **68.5%**" *and* its own leaderboard row
  "Mem0^g (graph) **68.4%**" — a self-inconsistent copy, which is the tell.

## Recommendation (one clause in the row-20 provenance table)

`CLAIMS-LEDGER.md` L-S12-02 tail: replace "immediate source unlocated" with the
resolved form above and point at this note. Same pattern as the L-S14-02
amendment. I applied this minimal edit in the Alice-authored PROVENANCE section.

## Limits

- The web is mutable and I searched targeted surfaces (paper v1 HTML, current
  README, the pinned blog); I cannot prove no Mem0-owned page *ever* said 68.5.
  What is proven: **the paper that introduced the graph figure says 68.44 and
  never 68.5**, and the earliest `68.5` I can locate is Letta's.
- `68.44 → 68.4`, so Letta's string is off by +0.06 in the one decimal place —
  consistent with the team's earlier rounding-family findings (18.5 vs 18.27;
  91% vs 92% for the same 91.59%).
- No benchmark re-run; this is a citation-provenance result only.
