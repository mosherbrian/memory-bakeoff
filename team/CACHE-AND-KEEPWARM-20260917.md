# Cache TTL and keep-warm, measured 2026-09-17

Split out of `QUEUE.md` the same day it was written, because the tables below
were being parsed as QUEUE ROWS. The poller treats any line beginning with `|`
as a row and read column 4 as the eligible seats, so these tables produced rows
seeking seats named `1-2m`, `83%` and `100%` - and its `unroutable` alarm paged
Brian, correctly. Tables belong here; the board gets a pointer.

## Effective cache TTL per provider

Hit rate of the call FOLLOWING a gap, binned by gap length, from live traffic.

| model | <1m | 1-2m | 2-2.5m | 2.5-3m | 3-5m | 5-10m | 10-25m | >25m |
|---|---|---|---|---|---|---|---|---|
| muse-spark-1.3-contributor | 97% | 83% | 63% | 52% | 37% | 17% | 25% | 10% |
| deepseek-v4.1-flash | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 76% |
| glm-5.3-flash | 99% | 100% | 100% | 100% | 100% | 100% | 0%* | 0%* |

*2-3 calls, noise rather than a reading.

Muse decays from ONE MINUTE, so the controlled ladder's "150-160 s cliff" is
generous against live traffic. deepseek holds 100% to 25 minutes - an order of
magnitude longer. There is no fleet-wide cache cadence, and a 150 s constant
applied to every provider (as the first version of this analysis did) is wrong
in both directions at once.

## Where keep-warm would have paid, under the OLD sporadic fleet

7 days to 2026-09-17, gaps in the 150 s-25 min band. Superseded by the section
below; kept because it is the number the earlier design rested on.

| provider | gaps | fresh tok after | keep-warm cost | net |
|---|---|---|---|---|
| muse-spark-1.3-contributor | 748 | 113.25M | 34.20M | +79.05M |
| muse-spark-1.3-contributor-free | 127 | 11.19M | 2.57M | +8.62M |
| deepseek-v4.1-flash | 319 | 0.06M | 30.01M | -29.95M |
| glm-5.3-flash | 14 | 0.38M | 0.35M | +0.03M |
| glm-5.3 | 22 | 0.10M | 1.44M | -1.34M |

## Why that table no longer decides anything

Those gaps belong to the 13-seat sporadic fleet. Since the 2026-09-16 change to
a few steady long-running workers, the band keep-warm exists to fill is nearly
empty - per provider per day, roughly 100-275 calls under 1 minute, **0-3
between 2 and 25 minutes**, 3-4 beyond. The steady-worker change did not make
the proxy more worthwhile; it removed most of the need for it, because a working
worker keeps its own cache warm.

## Per-provider cache hit rate

Each from that provider's own accounting, 7 days. `fleet-discipline` reports
these separately since 2026-09-17; before that it read only the ZCode logs and
reported a GLM number as if it were fleet-wide.

| provider | hit rate | fresh / cached |
|---|---|---|
| deepseek-v4.1-flash | 99.7% | 4.2M / 1,355M |
| zcode glm-5.3-flash | 96.7% | 0.75M / 22.28M (24 h) |
| muse-spark-1.3-contributor | 85.2% | 174.6M / 1,003M |

Muse's 85.2% and the ~$22/month projection resting on it are SPORADIC-FLEET
numbers. Re-derive both after a day of steady work on Muse.

## The decision, pre-committed

Do not build the proxy yet. Re-run the TTL table after one day of the steady
pattern running on Muse, and build only if the 1 min-25 min band carries real
volume. For deepseek it is already settled: its cache outlives every gap this
fleet produces.

If it is ever built: fail open; `baseURL` override with no credential
relocation; regenerate the `<env>` date rather than replaying it (see
`CORVID-KEEPWARM-PREFIX-FIDELITY.md`); per provider, never fleet-wide; an UPPER
idle bound as well as a lower one; and the gate written by plumb-fable rather
than by whoever builds it.
