# Hindsight's "independently reproduced" claim, resolved — it is co-authorship

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** the `third-party` class is the only empty one
in the ledger; `ALICE-HINDSIGHT-CLAIM-CHECK.md` flagged the claim as uncited and
this is the follow-up hunt · **Cost:** $0 (arXiv + marketing-site fetches), one
turn.

**Receipts:** `team/row-hindsight-thirdparty-receipts/` (`MANIFEST.md` with
sha256): Hindsight Technical Report `arXiv:2512.12818v1` (PDF + first-page
text), the abs page, `vectorize.io/benchmarks`, and the AMB leaderboard app
bundle.

## Finding 1 — the reproducing institutions are authors of the vendor's report

The Hindsight Technical Report (`arXiv:2512.12818v1`, 2025-12-14, "Hindsight is
20/20: Building Agent Memory that Retains, Recalls, and Reflects") lists:

| Affiliation | Authors |
|---|---|
| **Vectorize.io** | Chris Latimer, Nicoló Boschi, Chris Bartholomew |
| **The Washington Post** | Andrew Neeser |
| **Virginia Tech** | Gaurav Srivastava, Xuan Wang, Naren Ramakrishnan |

The README's *"independently reproduced by research collaborators at Virginia
Tech [Sanghani Center] and The Washington Post"* refers to **co-authors of the
vendor's own report** — not an external party that verified the result. That is
a vendor-led collaboration, which is weaker than independent verification.

**Consequence:** the ledger's `third-party` class ("an external party verified
it; we hold the reference") **stays empty**. To earn it, we would need a
reproduction by a party with no authorship or employment tie to Vectorize; none
is located. (This also corrects my earlier note: the claim is not *uncited* —
the artifact exists, and it is a co-authored vendor report.)

## Finding 2 — the report's own number is 91.4, not the marketed 94.6

| Source | LongMemEval | LoCoMo |
|---|---|---|
| Hindsight Technical Report abstract (2025-12-14) | **91.4%** | **89.61%** |
| `vectorize.io/benchmarks` + blog (2026) | **94.6%** | **92.0%** |
| MemBukkit's competitor table | **91.4** (judge swapped) | — |

The report also states its baseline framing: *"up to 89.61% on LoCoMo (vs.
**75.78%** for the strongest prior open system)"* — i.e., it cites **Memobase's
75.78** (our row L-S15-01) as the prior open best.

So the current marketing headline (94.6) is **not** the number in the
vendor's own technical report (91.4), and the ecosystem is already citing the
report's 91.4. The marketing page contains no "91.4" at all.

## Finding 3 — two smaller provenance defects

- **Mislabeled benchmark link.** `vectorize.io/benchmarks` says "All scores …
  come from [LongMemEval](https://arxiv.org/abs/2512.12818)" — but 2512.12818 is
  **Hindsight's own paper**, not the LongMemEval benchmark (arXiv `2410.10813`).
- **The vendor's own leaderboard is candid about the distinction.** AMB
  (`agentmemorybenchmark.ai`) labels externally-sourced rows *"Unverified —
  sourced from external papers, not independently reproduced"* and *"Scores are
  not directly comparable."* That is good hygiene; it also confirms the
  headline category is not independent verification.

## Classification consequence

- **Hindsight row: unchanged `vendor-only`.** The "independent reproduction"
  assertion is resolved to co-authorship; the report number is 91.4 (not 94.6);
  the marketing number is a later, unverifiable-in-our-hands figure.
- **`third-party` remains empty** — Hindsight was its only candidate, and it
  does not qualify.
- For the collision register: Hindsight now has **three** LongMemEval-family
  numbers — 91.4 (report; also MemBukkit's table), 94.6 (marketing/blog), and
  the dashboard's 3-conversation 86–90.02% — plus LoCoMo 89.61 (report) vs 92.0
  (marketing).

## Method and limits

- Read-only: fetched the report (PDF + text), the abs page, the marketing
  benchmarks page, and the AMB app bundle; extracted affiliations from the
  report's first page and numbers by text search. No benchmark, engine, or LLM.
- The report is `arXiv:2512.12818v1` (a "Technical Report", v1, 2025-12-14);
  the marketing page is mutable and was fetched today. I did not search for any
  *other* VT/WaPo publication beyond the report the claim points at.
