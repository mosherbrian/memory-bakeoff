# S3-1 verifier checklist — standard-tier firing run (pre-registered)

**Author/verifier:** Corvid (`worker-glm-dsh3`) · **Date:** 2026-09-15 · **Cost:** $0
**Consumer:** the S3-1 producer (worker-glm-2) and this seat's verification pass.
**Why now:** QUEUE S3-1 names this seat as verifier; this freezes what the receipt
must carry **before** the run, so the check is mechanical and the definitions
cannot drift after the numbers exist.

## What must be true in the receipt

1. **Tier and corpus.** Standard tier (per `DESIGN-INVOCATION-BENCHMARK.md` §2.5)
   with the corpus hash; the binding reachability guard
   (`check_invocation_corpus_reachability.py`) exits **0** and the corpus selftest
   is green — i.e. every labeled `topic` moment is reachable under the binding
   trigger (summaries-only, len ≥ 4, trigger STOPWORDS). An S09-class unfireable
   moment counted as labeled is a **reject**.
2. **Shipping metric definitions.**
   - `FalseFire = fired(topic)` on `filler_plain` **only** — fresh/gap excluded,
     reported as `fresh_rate`/`gap_rate` beside it (the 2026-09-14 ruling).
   - `NearMissFire` on `filler_near_miss`, **never folded into `FalseFire`**;
     denominator stated (`|filler_near_miss|`).
   - `FirePrecision` with its denominator (all fired turns); near-miss fires
     lower it, by design (F2).
   - `FBMR_topic` over labeled topic moments, denominator = |labeled topic
     moments| after any exclusions, exclusions named.
3. **Controls separate.** `fire-never` (FBMR 0 / FalseFire 0) and `fire-always`
   (FBMR 1 / FalseFire 1) on the same corpus; if they do not separate, no system
   number is publishable (design §5 instrument-failure condition).
4. **Determinism.** A re-run against a frozen input snapshot yields a
   byte-identical summary (or the receipt explains the volatile fields).
5. **Provenance.** Run receipt records corpus/harness hashes, host/runtime, seed,
   and the exact invocation.
6. **No score import.** Vendor/system headline numbers are not imported; if the
   tier is below `standard`, the result is descriptive only.

## Reject conditions (one representative bad input each)

- a `topic` moment that cannot fire counted as labeled;
- a near-miss fire folded into `FalseFire`;
- a `fresh`/`gap` fire counted in `FalseFire`;
- a system number with no fire-never/fire-always separation;
- a rate without its denominator/exclusions.

## Note

This is verifier-side pre-registration, not a run and not a score. It tightens
`CORVID-STANDARD-TIER-PREREG.md` into a checklist keyed to the S3-1 deliverable.

— **Corvid** (`worker-glm-dsh3`). $0, design only.
