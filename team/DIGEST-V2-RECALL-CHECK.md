# DIGEST-V2 recall check — did the classifier bury facts in probe? (spark pulse)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local
**Companion:** the self-audit covered seed *precision*; this covers probe-side
*recall* (facts misfiled as probe → lost to vault seeding).

## Method

Heuristic sweep over the 193 probe rows for fact-shaped text: no shell/log/
dispatch markers in the head, 80–600 chars, no early `?`. 92 rows surfaced;
read the top candidates in full.

## Result: recall essentially clean (negative result)

The 92 collapse on inspection into three non-fact piles:

- **Shell sessions with prose heads** (the bulk, e.g. #33–#70 MLX-server
  block): a sentence of context followed by `%`/`bmosher@` command output.
  Correctly probe — they are invocation material, not standalone facts.
- **Log/diagnostic dumps** (e.g. #31 model-load failure + journalctl).
  Correctly probe.
- **Session-local pastes/narratives** (e.g. #13 shared chat reply,
  #17 model-search narrative): human-readable but irreducibly
  session-bound — no timeless predicate survives extraction. At best
  fuzzy, never seed. Correctly out of seed.

No crisp, timeless, standalone declarative found in the probe bucket on this
pass. Combined with the self-audit: the classifier's error is **one-sided**
(seed over-inclusion, ~22/32) with **no detected fact loss** on the probe
side. Vault-seeding completeness is not threatened by the probe filing;
seed *quality* remains the gate (Cairn's spot-check + the 22 proposed
demotions).
