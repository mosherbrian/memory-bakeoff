# Keep-warm economics — second driver on the break-even

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, arithmetic from already-measured values
**Consumer:** the keep-warm proxy trial in `SPRINT-OPS-PROPOSAL.md`.
**Checks:** `BILLING-CACHE-FINDINGS-20260915.md` §4 ("warming wins, by roughly
2–4×").

## Inputs (all measured earlier in the thread)

| quantity | value | source |
|---|---|---|
| median context per call | 210,153 tok | `FLEET-SPEND-20260914.md` |
| fresh input rate | $0.10/M | rate table |
| cache read rate | $0.002/M | rate table |
| cold-miss cache-write | not separately billed | `cache-retention-probe.md` prime row: 24,360 tok cost $0.00245 = 24,360 × $0.10/M |
| per-lane miss rate | ~1.5–3.7 /h (7–17 per 4.6 h) | `FLEET-SPEND-20260914.md` |
| refresh interval proposed | ~100 s ⇒ 36 /h | `BILLING-CACHE-FINDINGS` §4 |

## Re-derivation

- **One cold miss** = 210,153 × $0.10/M = **$0.0210**.
- **One refresh** = same context as cache read = 210,153 × $0.002/M = **$0.00042**,
  plus output. If the proxy replays the *real* body the model still generates a
  response; at ~200–800 output tok × $0.20/M that is $0.00004–0.00016. Total
  ≈ **$0.00046–0.00058**.
- **Warming cost/hour/lane** = 36 × $0.0005 ≈ **$0.018**.
- **Marginal lane (1.5 misses/h)**: avoided cost $0.0315/h vs $0.018 cost → net
  **+$0.013/h** (~1.8×).
- **Busy lane (3.7 misses/h)**: $0.0777 vs $0.018 → net **+$0.060/h** (~4.3×).

So the "2–4×" claim **reproduces**, and the break-even is
**misses ≳ 0.86/h** — i.e. "about once an hour", as stated.

## Caveat the range hides

Warming is paid **per hour of wall time**, not per miss. A lane that is idle for
hours (dispatch is currently stopped) accrues $0.018/h/lane for nothing. So the
proxy should **pause warming for a lane with no activity in the last N minutes**
(N ≈ 2× the cache lifetime), and resume on the next real request — otherwise
idle lanes flip the sign. With that guard, the economics above hold for active
lanes only, which is the population the claim is about.

## Limits

Arithmetic from others' measured inputs; no new measurement. Output-token size of
a replay is assumed, not measured — it is the only soft term, and at $0.20/M it
cannot change the sign for an active lane.

— **Corvid** (`worker-glm-dsh3`). $0, local.
