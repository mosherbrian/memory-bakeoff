# StreamMemBench card pin check — pin passes; repo + EgoLife data license recorded

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one abs read + web/HF probes
**Subject:** `team/CANDIDATE-CARD-STREAMMEMBENCH.md` (A2). Closes the card's
next-step 1 ("Locate the repo and the EgoLife data license; record both (owner
Corvid)") and the last missing in-file verifier line
(`CORVID-CARD-VERIFIER-CENSUS.md`). Checked against `arXiv:2606.14571v2`.

## Pin — correct

Title; authors (8: Guanming Liu … Tun Lu); **v1 12 Jun 2026, v2 26 Aug 2026**;
`cs.AI`; **Findings of EMNLP 2026** (comments) — match. The abs carries a license
link; the card states **CC BY 4.0**.

## Abstract-level claims that hold

Streaming benchmark building a **two-step task sequence around each evidence
anchor from EgoLife egocentric streams**; initial task = **evidence use**,
follow-up = **feedback/interaction reuse**; **four metrics** (evidence recall,
initial use, feedback incorporation, follow-up reuse); **eight memory systems ×
two backbones**; "publicly available". ✓ (vendor-only numbers; the paired
ablation 160 / FUR 27.5%→40.6% / +13.1 figures are body-level, Alice-verified
from the PDF and not in the abstract.)

## Artifacts — recorded

- **Code:** `github.com/landian60/StreamMemBench` → **MIT, 23★**, pushed
  2026-07-17. ✓ (register row agrees.)
- **EgoLife data license:** the LMMs-Lab official release
  `huggingface.co/datasets/lmms-lab/EgoLife` carries **MIT** in its dataset card
  (`cardData.license: mit`; the top-level `license` field is `null` — the same
  metadata nuance as GateMem). The EgoLife *paper* (`2503.03803`) is arXiv
  non-exclusive, but that governs the paper, not the data.
- **Caveat for any use:** EgoLife is **egocentric video of real participants**.
  Even under MIT, privacy/consent terms on the underlying footage deserve an
  explicit check before a build; MIT on the card is not the whole story for
  human-subject video.

## Effect

The card's Data row can read **"EgoLife (lmms-lab/EgoLife) — MIT (cardData);
real-participant video, check consent terms before use"**, next-step 1 is
closed, and the owner can add `Verifier: Corvid (abstract pin ✓ 2026-09-15,
this file)` — which would make the verifier-line census **17/17**.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + web/HF probes.
