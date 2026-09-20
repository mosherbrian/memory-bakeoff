# DIGEST-V2 classifier determinism re-derive (spark pulse)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local, no LLM

Re-ran the full 4-stage classification chain from the v1 digest into a
scratch file and compared against the rows behind the filed `team/DIGEST-V2.md`:

- stage counts reproduce exactly at every pass (170/71/60/17 → 189/73/39/17
  → final 193 probe / 75 fuzzy / 32 fact / 18 question)
- **row-level identical: all 318 rows** (shape + verdict + rewrite + why)

Classification is deterministic from digest + script; the filed counts are
not a one-off accident. (This does not bless seed *quality* — the
self-audit's 22 proposed demotions stand separately for Cairn.)
