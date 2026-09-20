# EvoMemBench card pin check — pin passes; no-license claim independently confirmed

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read + one repo license probe
**Subject:** `team/CANDIDATE-CARD-EVOMEMBENCH.md` (muse-drafter). Card 8's
verifier is open; this is that second read. Checked against
`arXiv:2605.18421v2` and the code repo.

## Pin — correct

Title; authors (10: Yuyao Wang … Jia Li); **v1 18 May 2026, v2 15 Jun 2026**;
`cs.CL`; license **arXiv non-exclusive** — all match. Code link in the abstract
is exactly `github.com/DSAIL-Memory/EvoMemBench`. ✓

## Abstract-level claims that hold

- Two axes: **memory scope (in-episode vs cross-episode) × memory content
  (knowledge-oriented vs execution-oriented)**, i.e. the four settings. ✓
- **15 representative memory methods** vs strong long-context baselines under one
  protocol. ✓
- Findings: long-context baselines "remain highly competitive"; memory helps when
  context is insufficient / tasks difficult; **no single memory form works
  consistently**; retrieval strong for knowledge settings, procedural/long-term
  for execution. ✓ (all `vendor-only`, uncitable)

## Code license — "no license" confirmed independently

`DSAIL-Memory/EvoMemBench`: GitHub API `license: None`, `LICENSE`/`.txt`/`.md`
all **404**, 13 stars — exactly the card's read. Treat as **all-rights-reserved**;
do not vendor or adapt without a license.

## Body-only (not verified, not refuted)

The per-source dataset counts (2,800 / 800 / 884 / 800+270+200) and the model
substrates (DeepSeek-V3.2; Gemini-3-Flash / GPT-5-mini baselines) are not in the
abstract — HTML/repo-level claims.

## Endorsed

The card's **name-collision flag** (EvoMemBench `2605.18421` vs Evo-Memory
`2511.20857` vs EvolveMem `2605.13941`) is important and correct; cite by ID.

## Verdict

Abstract-level pin **passes**. With this, **all Series A named cards (1–8) have a
verification pass** — cards 1–4 by Alice, cards 5–8 (`HaluMem`, `StateMemBench`,
`LME-V2`, `EvoMemBench`) by this seat, at abstract level. Numbers stay
`vendor-only`.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + one license probe.
