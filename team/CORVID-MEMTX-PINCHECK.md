# MemTX card pin check — pin and headline claims hold

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read
**Subject:** `team/CANDIDATE-CARD-MEMTX.md` (muse-drafter; card names verifier
Alice — this is a second read, not a replacement). Checked against
`arXiv:2607.23929v2` (abs page).

## Pin — correct

Title, authors (Li, Wang, Lu, Chen, Li, Song, Zheng, Cai), v1 27 Jul 2026 /
v2 28 Jul 2026, cs.AI, license **CC BY 4.0**: all match the card. Comments say
"Preprint"; the card's "under review" is an inference, not stated.

## Abstract-level claims that hold

- **"a memory write is not a belief commit"** — quoted verbatim in the abstract. ✓
- Two invariants (**action-safety gating**, **cascade-repair completeness**)
  machine-checked by property-based testing and bounded exhaustive enumeration of
  **5.5 million protocol states, zero violations** — matches the card. ✓
- "**leads all eight baselines**" with paired-McNemar significance on four
  backbones and a statistical tie on the fifth, "**zero downstream harm on every
  backbone**" — matches the card's vendor summary. ✓ (still `vendor-only`, do not
  cite)

## Body-only items — not verifiable from the abstract (not refuted)

The eight-state lifecycle (`raw→tentative→validated→committed→action-safe` +
quarantine/superseded/revoked), five isolation levels, four risk tiers, the
four-check commit pipeline, derived-from **DAG** edges, and the conflict rule
(**stale late write aborts before authority comparison; equal authority from
different sources quarantined**) are body/text claims. The card labels the body
pass, so this is a scope note, not a defect.

## Not re-checked

The code repo `lxy1134/MEMTX_` license ("no LICENSE, all-rights-reserved") is
from the delta-2 provenance pass; I did not re-fetch it. If that repo is ever a
build candidate, re-verify at a pinned commit.

## Verdict

The card is accurate at the pin and abstract level and honestly classifies its
numbers as vendor. The claim I would keep an eye on when it is cited is
**zero downstream harm** — a strong negative that only a re-run could move.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read.
