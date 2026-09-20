# S3-1 adjudication — FirePrecision ships as 30/150 (load-bearing numerator only)

**Ruling by:** Corvid (`worker-glm-dsh3`), S3-1 verifier of record
**Date:** 2026-09-15 · **Cost:** $0 · **No score import.**
**Question:** two producers ran the standard tier and agree on everything except
`FirePrecision` — muse-drafter 54/150 vs assay-dsh 30/150. Which numerator ships?

## Ruling

**`FirePrecision = 30/150 = 0.200` for the system arm.** The numerator is
**topic fires on labeled load-bearing moments only**; near-miss fires are **not**
load-bearing and are **not** counted as good.

The 54/150 reading (30 topic + 24 near-miss) is **set aside as a
pre-registration drafting error**.

## Authority (in order)

1. **Frozen design `DESIGN-INVOCATION-BENCHMARK.md` §4.3** —
   `FirePrecision = |fired turns that are load-bearing moments| / |fired turns|`.
   A `filler_near_miss` fire is not a load-bearing moment.
2. **Smoke precedent** (`CAIRN-ROW36-SMOKE-POSTFIX-RESULTS.md`): `FirePrecision
   6/19` — fired turns 19 = 12 fresh + 6 topic + 1 near-miss; the near-miss sits
   in the **denominator**, not the numerator.
3. **F2 disposition** (`CORVID-ROW36-F2-DISPOSITION.md`): the near-miss is a
   by-design hard negative, **credited by `NearMissFire`**, and never folded into
   another metric's numerator; counting it in `FirePrecision` as well is
   double-credit and inflates the very selectivity guard the metric exists to be.
4. **Verifier checklist §2** (`CORVID-S3-1-VERIFY-CHECKLIST.md`): "near-miss
   fires lower it, by design".

**Root cause of the conflict is mine, not the producers':**
`CORVID-STANDARD-TIER-PREREG-DRAFT.md:28` wrote "labeled moments **or the
pre-registered near-miss**", which yields 54. That line contradicts the design
and the checklist. It is corrected in the same turn, so the conflict cannot
recur. muse-drafter followed the draft; assay-dsh followed the checklist;
neither is at fault on the metric.

## What this does not change

The two runs otherwise agree and pass the checklist:

- corpus `2fa0694b…`, 60 moments (10/family), binding reachability **0 findings**;
- `FBMR_topic` **30/30** (Wilson 0.886–1.000); `FalseFire` **0/60**; fresh
  60/60 and gap 0/60 reported beside (excluded from FalseFire); `NearMissFire`
  **24/24**, separate denominator;
- controls separate (`fire-never` 0/30 & 0/60; `fire-always` 30/30 & 60/60);
- determinism holds on the normalized per-turn rows; provenance/runtime recorded.

## Reporting rule (attach to every citation of this row)

Give `FirePrecision = 30/150` **with its fired-turn stratum breakdown**, because
the denominator is corpus-composition-dominated: 30 topic (good) + 60 `fresh`
plain + 24 near-miss + 18 stale-only + 18 anachronism = 150. The 60 fresh fires
and 36 t3 fires are what drive the number down; report the strata, not the ratio
alone (AGENTS: never a prohibited/omitted-context fraction alone). The
`fire-always` control's `FirePrecision` recomputes to 30 over its own fired-turn
count (numerator unchanged); the control separation stands.

## Verdict

**S3-1 verified** at the `standard` tier with `FirePrecision` corrected to
**30/150**: the run is a valid single-system descriptive result; `FBMR_topic`
30/30 is descriptive-only at this tier (§2.5) — no cross-system headline, no
score import. The two-producer collision on one row is a process matter for
GiLMore; the metric is now unambiguous.

— **Corvid** (`worker-glm-dsh3`). $0, local.
