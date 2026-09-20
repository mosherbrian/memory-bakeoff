# DMR attribution check — is Zep's "MemGPT 93.4%" the MemGPT paper's own number?

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** the open question in
`team/ALICE-REDERIVE-ZEP-HEADLINE.md` §Method limits ("worth a separate probe:
the MemGPT paper itself reports no DMR score in its abstract") · **Cost:** $0,
two fetches + local grep, one turn.

**Why it is load-bearing.** L-S17-01 is entirely a comparison to MemGPT:
"Zep demonstrates superior performance (94.8% vs 93.4%)." If the 93.4% were
Zep's own measurement of a rival rather than the rival's published number, the
comparison would be a different (and worse) kind of claim. This settles it.

**Receipts:** `team/row-dmr-receipts/` — `memgpt-2310.08560v2.html`
(sha `030ddb6f…`) and an independent ar5iv render (sha `0b4467a4…`); Zep's
reference [3] confirmed as "Charles Packer, … MemGPT: Towards llms as operating
systems, 2024" from `team/row20-claims-provenance/zep-paper-v1.html`.

## Verdict: the attribution is CORRECT

MemGPT paper (arXiv `2310.08560v2`, **Table 2 "Deep memory retrieval (DMR)
performance"**), verbatim rows:

| Model | Accuracy | ROUGE-L |
|---|---|---|
| GPT-3.5 Turbo | 38.7% | 0.394 |
| **+ MemGPT** | 66.9% | 0.629 |
| GPT-4 | 32.1% | 0.296 |
| **+ MemGPT** | 92.5% | 0.814 |
| GPT-4 Turbo | 35.3% | 0.359 |
| **+ MemGPT** | **93.4%** | 0.827 |

Zep's "MemGPT … 93.4%" is the MemGPT paper's own **GPT-4 Turbo + MemGPT** row,
not a Zep re-measurement. Zep's Table 1 also reproduces the MemGPT paper's
**fixed-context GPT-4 Turbo baseline (35.3%)** under the label "Recursive
Summarization." Both agree across the two renders. So L-S17-01's number is
correctly cited.

## What the check sharpens

1. **The comparison is memory-vs-memory, not memory-vs-null.** The MemGPT
   paper's own fixed-context baseline is **35.3%** (GPT-4 Turbo); both MemGPT
   (93.4%) and Zep (94.8%) sit far above it. Zep's headline gap is **+1.4 pts
   over MemGPT**, and — the point my Zep re-derivation already flagged — only
   **+0.4 pts over Zep's own full-conversation baseline (94.4%)**, which is the
   E-1 null the portfolio actually runs.
2. **"Primary evaluation metric" is Zep's characterization.** The MemGPT paper
   introduces DMR as one of three evaluations — DMR (§3.1), multi-document QA
   (§3.2.1), nested key-value retrieval (§3.2.2) — and its abstract does not
   single DMR out as primary. Zep's phrasing is defensible but is not the
   MemGPT team's own priority statement.
3. **Cross-paper comparability depends on the judge, which the abstract
   omits.** The MemGPT paper scores DMR with an LLM judge *and* reports ROUGE-L;
   Zep also uses an "LLM judge." Same metric family, but neither abstract fixes
   judge model/prompt, so the 94.8-vs-93.4 gap is not strictly reproducible
   across papers from the text alone.
4. **Version note:** the table is verified in **v2** (Feb 2024; the version
   Zep's 2025 reference points at). The v1 HTML render I fetched does not
   expose the table (0 hits for "93.4", 4 for "DMR"), so I do not claim v1.

## What this does and does not establish

- **Establishes:** the 93.4% is MemGPT's own published DMR accuracy (GPT-4
  Turbo), correctly attributed by Zep; and that the MemGPT fixed-context
  baseline is 35.3%.
- **Does not establish:** the correctness of either measurement. No benchmark
  was run. L-S17-01/L-S17-02 remain `vendor-only`; this is attribution
  verification, not reproduction.

## Method and limits

- Fetched `arxiv.org/html/2310.08560v2` and the independent ar5iv render;
  grepped the stripped text for `93.4`, `92.5`, `DMR`; read Table 2 in both.
- Confirmed Zep's reference [3] is the Packer et al. MemGPT paper from the
  already-hashed Zep paper body. No model, no benchmark, no engine.
