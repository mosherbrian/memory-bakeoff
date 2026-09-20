# Keep-warm proxy trial — measurement pre-registration (design seat)

**Author:** Corvid (`worker-glm-dsh3`)
**Date:** 2026-09-15 · **Cost:** $0, design only, no runs
**Consumer:** the approved keep-warm trial in `SPRINT-OPS-PROPOSAL.md` (and its
success bar, "5–6 min Muse bin toward ~97% without idle pulses").
**Freeze rule:** freeze this before the first proxied minute; the metric below is
the only pre-specified one.

## Unit, cohort, control

- **Unit:** per-lane per-hour. **Cohort:** Muse (`muse-spark-1.3-contributor`)
  lanes only — the cliff is Muse-specific (DeepSeek ≥99.8% at all ≤30 min gaps).
- **Control:** at least one Muse lane **without** the proxy in the same window;
  the proxy cohorts's change is read against it, not against history.

## Primary metric (pre-specified)

**Muse 5–6 min inter-turn bin cache-hit%**, from

```
scripts/probe_cache_ttl_by_model.py --since-hours N
```

- **Baseline (measured 2026-09-14/15):** 14.8–18.3% in the 5–6 min bin; 96.9% in
  0–1 min.
- **Success bar (from the ops proposal):** the 5–6 min bin **≥ 90%** with no
  idle-pulse injections into any lane's context.
- **Secondary:** total Muse fresh-input tokens per hour and total Muse $ per
  hour vs the control lane; output tokens per hour (must not rise materially).

## Pre-specified checks (the ones that can invalidate the run)

1. **Fail-open:** take the proxy down mid-window; the lane must keep working
   (requests succeed, no hang). Record a boolean.
2. **Prefix fidelity across the date boundary** (`CORVID-KEEPWARM-PREFIX-FIDELITY.md`):
   run across local midnight with (A) verbatim replay and (B) date-regenerated
   replay; A is expected to fail to keep the lane warm after the boundary, B to
   hold. Without this arm the trial can silently leak a daily miss class.
3. **No double-billing:** a lane that hits should not also show a fresh prime in
   the same gap; check the DB for paired (prime then miss) per gap.

## Decision rule

- **Adopt** if the 5–6 min bin clears 90% on the proxied cohort, the control does
  not, fail-open passes, and output tokens are flat.
- **Reject / revise** if the bin does not clear, or the date arm A/B shows the
  proxy writing a second entry (paying twice).
- **Report either way** with the lane-qualified numbers; a null result is a
  result — it closes the last lever that avoids misses without shedding context.

## Limits

The metric bins by inter-turn gap, not by "pulse vs real work"; the ops trial
changes the pulse policy at the same time, so hold the pulse policy fixed for the
window (this is the clean-day recommendation). One representative day, per the
spend author's recommendation.

— **Corvid** (`worker-glm-dsh3`). $0, design only.
