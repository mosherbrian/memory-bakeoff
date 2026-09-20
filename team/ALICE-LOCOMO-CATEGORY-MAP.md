# LoCoMo category-id map — resolved from the dataset (corrects Memobase's labels)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** the collision found in
`team/ALICE-REDERIVE-MEM0-LOCOMO.md` Part 4 ("which mapping matches the
original dataset is not resolved here") · **Cost:** $0 (dataset + paper fetch,
local analysis), one turn.

**Why.** Two vendors use the same LoCoMo question sets with different category
names. Cross-vendor per-category tables (including ours) are wrong if the map
is wrong, so this resolves it against the dataset itself.

**Authority + receipts:** `team/row-locomo-map-receipts/` (`MANIFEST.md` with
sha256): the LoCoMo dataset `data/locomo10.json` (snap-research/locomo main),
the repo README, and the paper `arXiv:2402.17753` (PDF + `pdftotext`), plus my
`analysis-output.txt`.

## Method: the dataset's own evidence spans are decisive

The paper defines single-hop as "answers based on a single session" and
multi-hop as "synthesizing information from multiple different sessions"
(`2402.17753`, §"five distinct reasoning categories"). Each question in
`locomo10.json` carries an `evidence` list of dialog ids (`D<session>:<turn>`),
so I counted distinct sessions per question and grouped by category id.

| id | n | one session | >1 session | authoritative type |
|---|---|---|---|---|
| 1 | 282 | 13 | **269** | **multi-hop** |
| 2 | 321 | **293** | 28 | **temporal** |
| 3 | 96 | 61 | 31 | **open-domain** (inference/world knowledge; mixed evidence) |
| 4 | 841 | **840** | 1 | **single-hop** |
| 5 | 446 | 446 | 0 (all answers "None") | **adversarial** |

**Authoritative map: 1=multi-hop, 2=temporal, 3=open-domain, 4=single-hop,
5=adversarial.**

## The two traps this closes

1. **The paper's prose enumeration is not the id map.** The paper lists
   "(1) Single-hop … (2) Multi-hop … (3) Temporal … (4) Open-domain …"
   (§category definitions) and its results table columns are "Single Hop,
   Multi Hop, Temporal, Open Domain, Adversarial". Neither order is the
   dataset's integer ids — the dataset is 1=multi-hop, 4=single-hop. Trusting
   the paper's enumeration would mislabel the data.
2. **Mem0 matches the dataset; Memobase does not.** Mem0's harness
   (`category_name` in the shipped evaluations) uses exactly
   1=multi-hop, 2=temporal, 3=open-domain, 4=single-hop. **Memobase's
   `generate_scores.py` uses `1=single_hop, 2=temporal, 3=multi_hop,
   4=open_domain` — three labels permuted** for the identical 282/96/841
   question sets.

## Consequences (a correction to my own earlier artifacts)

Memobase's published per-category table is **mislabeled**; the scores are its
real scores, but three row names are wrong:

| Memobase label (v0.0.37) | Score | Actually |
|---|---|---|
| "Single-Hop" | 70.92 | **multi-hop** |
| "Multi-Hop" | 46.88 | **open-domain** |
| "Open Domain" | 77.17 | **single-hop** |
| "Temporal" | 85.05 | temporal ✓ (the one correct label) |

(v0.0.32, same permutation: 63.83 multi-hop · 52.08 open-domain · 71.82
single-hop · 80.37 temporal.)

- `team/ALICE-REDERIVE-MEMOBASE-7578.md` and
  `team/ALICE-LEDGER-COLLISION-REGISTER.md` repeated Memobase's labels while
  citing its numbers. **The numbers are right; the names are wrong.** Per
  append-only discipline this note is the correction — I am not rewriting those
  files.
- ECOSYSTEM-MAP §4 / L-S15-01 interest notes must not use Memobase's category
  names; the temporal row (85.05) is the only cross-category value that was
  labeled correctly.
- The portfolio should pin this id→name map wherever per-category LoCoMo
  numbers are compared across vendors.

## Method and limits

- Evidence parsing: distinct `D<k>` values in `evidence` per question; a
  question counts as multi-session if it spans more than one `D<k>`. Single-hop
  is defined by the paper as one session and the statistic is 840/841 for id 4
  — as clean as this test gets. Edge cases: 13/282 id-1 questions are
  single-session and 1/841 id-4 is multi-session; id 3 is genuinely mixed
  (open-domain inference can cite one or several sessions).
- The paper PDF is 19 pages despite `file` reporting "4"; `pdftotext`
  extracted 78 KB and the category definitions are on the QA-task page.
- No benchmark was run; this resolves a labeling question only.
