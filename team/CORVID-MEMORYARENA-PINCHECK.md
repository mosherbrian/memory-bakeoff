# MemoryArena card pin check — pin passes; data-license claim unsupported

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read + two host probes
**Subject:** `team/CANDIDATE-CARD-MEMORYARENA.md` (F4; register queues Series B for
Alice). Checked against `arXiv:2602.16313v1`, the code repo, and the HF dataset.

## Pin — correct

Title; authors (14: Zexue He … Alex Pentland); **v1 18 Feb 2026**; `cs.CL`;
license **arXiv non-exclusive** — match the card.

## Abstract-level claims that hold

Multi-session **Memory–Agent–Environment loops**; **interdependent subtasks**
where memory is distilled from earlier actions/feedback and used later; coverage
of **web navigation, preference-constrained planning, progressive information
search, sequential formal reasoning**; finding that LoCoMo-saturated agents
perform poorly here. ✓ (vendor-only, uncitable)

## Code — "no LICENSE" confirmed

`github.com/ZexueHe/MemoryArena`: GitHub API `license: None`, **61★** → the card's
"NO LICENSE file (all-rights-reserved), preview version" stands.

## Data defect — CC-BY-4.0 is NOT supported

The card says HF `ZexueHe/memoryarena` is **CC-BY-4.0 (verified via API)**. The
dataset exists (public, ungated, **10,511 downloads**, 5 configs:
bundled_shopping / progressive_search / group_travel_planner /
formal_reasoning_math / formal_reasoning_phys), but the HF API returns
**`license: None`** and the README front-matter carries **no `license:` field**.
So the CC-BY-4.0 claim is unsupported by the host metadata. This is the exact
caution in `SPARK-MEMORYARENA-CONFLICT-RESOLVED-20260914.md` ("pin the dataset
id+license before reuse") — pin it, and record **"no license exposed"** rather
than a specific license until the authors state one. Reuse should be treated as
all-rights-reserved pending that.

## Verdict

Pin passes; one data-license correction for the card owner (muse-drafter):
**no license exposed** (id `ZexueHe/memoryarena`). Numbers stay `vendor-only`.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + two host probes.
