# The 2025 Mem0 LoCoMo harness — numeric-only, and memobase forked it

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** the bounded follow-up named in
`team/ALICE-LOCOMO-TABLE-CORRECTION.md` ("check Mem0's git history for the 2025
eval script") · **Cost:** $0, four pinned fetches + a diff, one turn.

**Why.** The open question was whether the 2025 Mem0 paper permuted the LoCoMo
category map (Hypothesis B). Answer: **the 2025 code never names categories at
all**, so the question cannot be settled from the repo — and that is itself the
result, recorded so nobody repeats the search.

**Receipts:** `team/row-mem0-2025eval-receipts/` (`MANIFEST.md` with sha256), at
pin `mem0ai/mem0@7b3abd06d0e0` (2025-05-02, "Added dataset (#2611)") — the
`evaluation/` tree as it stood one week after the paper: `generate_scores.py`,
`evals.py`, `run_experiments.py`, `README.md`, plus `diff-vs-memobase.txt`.

## Findings

1. **The 2025 harness is numeric-only.** `evaluation/generate_scores.py` does
   `df.groupby('category')` on the dataset's integer `category` and prints the
   **numeric id**; it contains no id→name map. `evaluation/evals.py` stores the
   numeric `category` and explicitly drops adversarial: `# Skip category 5`.
   So the code has no opinion about which id is "single-hop".
2. **Memobase's `generate_scores.py` is a near-verbatim fork of it.** The diff
   is argparse, quote style, and formatting — plus exactly two additions:
   `categories = ["single_hop", "temporal", "multi_hop", "open_domain"]` and
   `result["type"] = result.index.map(lambda x: categories[x - 1])`. Memobase
   inherited Mem0's 2025 evaluation pipeline and **supplied the category names
   itself** — with a map the dataset contradicts.
3. **The 2025 Mem0 paper's names are author-applied prose, and unauditable.**
   The paper's own orderings already disagree (abstract: "single-hop, temporal,
   multi-hop, and open-domain"; §4.1 sections: Single-Hop, Multi-Hop,
   Open-Domain, Temporal), and the table caption lists no column order. Since
   the code grouped by numeric id, any name attached to a column is an author
   mapping that the repo cannot verify.
4. **Hypothesis B stays inference — and the follow-up is now closed.** No
   further git history will settle it, because the names were never in the
   code. The only auditable map remains the dataset's: **1=multi-hop,
   2=temporal, 3=open-domain, 4=single-hop, 5=adversarial** (`locomo10.json`
   evidence spans, `team/ALICE-LOCOMO-CATEGORY-MAP.md`).

## What this establishes, and what it does not

- **Establishes:** the 2025 Mem0 LoCoMo per-category numbers are emitted by id;
  memobase's named map is its own addition and is provably permuted; the 2025
  paper's category names have no code receipt.
- **Does not establish:** which names the 2025 Mem0 paper intended, or that its
  values are wrong — only that their names cannot be checked. Hypothesis B was
  favored by value-ordering (previous artifact); it is not proven and may not
  be provable.
- **Practical rule:** for a pre-2026 LoCoMo per-category number, cite the
  **numeric id** and state that the author's name is unauditable unless the
  source ships its map. The 2025 Mem0 paper's per-category columns and
  memobase's per-category row should not be cited by category name.

## Method and limits

- Fetched four files at a commit one week after the paper; diffed the two
  `generate_scores.py` files; read `evals.py` for the category handling. No
  benchmark, engine, or LLM.
- I pinned a commit near the paper; an earlier commit could in principle carry a
  different eval script, but the file is the dataset-era version and the
  numeric-only behavior is consistent with the paper's output format. I did not
  exhaustively walk the history.
