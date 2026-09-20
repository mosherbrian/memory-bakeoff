# CodeTracer card pin check — pin and artifact hold; one design claim is body-level

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read + two license probes
**Subject:** `team/CANDIDATE-CARD-CODECRACER.md` (F1; register queues Series B for
Alice — this is a second read, useful because a design already cites it).
Checked against `arXiv:2604.11641v3` and the artifact hosts.

## Pin — correct

Title; authors (16: Han Li … Jiaheng Liu, NJU-LINK); **v1 13 Apr 2026, v3 15 Apr
2026**; `cs.SE`/`cs.AI`; license **arXiv non-exclusive** — all match the card.

## Abstract-level claims that hold

- **Evolving extractors** parsing heterogeneous run artifacts; reconstructing the
  full **state-transition history as a hierarchical trace tree with persistent
  memory**; **failure-onset localization** pinpointing origin + downstream chain.
  ✓
- **CodeTraceBench** from executed trajectories of **four widely used code-agent
  frameworks** on bug fixing, refactoring, terminal interaction, with **stage- and
  step-level** supervision. ✓
- "Substantially outperforms direct prompting and lightweight baselines" and
  "replaying diagnostic signals consistently recovers originally failed runs "
  ✓ (vendor-only, uncitable).

## Artifact — independently confirmed

- Code `github.com/NJU-LINK/CodeTracer`: **MIT, 90★** (GitHub API). ✓
- Data HF `NJU-LINK/CodeTraceBench`: **`license:mit`** (HF API). ✓ (It is a
  HuggingFace dataset, so the GitHub API 404 there is expected, not a defect.)

## One design claim to source (for the epistemic sketch)

The epistemic type-system sketch says "**CodeTracer's exploration vs
state-changing split is observation vs action**." That split is **not in the
abstract** — the abstract's contribution is trace-tree reconstruction + failure
onset localization. If the sketch keeps the claim, cite the body section or
soften it to "trace-stage annotations" (which is abstract-supported).

## Verdict

Abstract-level pin **passes**; artifact lanes are clean MIT both sides. Numbers
stay `vendor-only`.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + two license probes.
