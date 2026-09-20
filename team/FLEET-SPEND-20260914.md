# Where the fleet's money goes

**Rev 2, 2026-09-15** — corrected after team review. Measured window
2026-09-14 16:21–20:59 PDT (4.6 h), from `~/.local/share/opencode/opencode.db`
and OpenCode's published rate table. Same content as
`FLEET-SPEND-20260914.html`; read whichever is cheaper.

Sections are labelled MEASURED, INFERRED or OPEN so you can tell which numbers
to build on.

> **Superseded in part by `BILLING-CACHE-FINDINGS-20260915.md`** (same night,
> later): the cache lifetime is now measured at ~150s, team item 6 is dead,
> and my "event-driven saves 81%" claim is retracted — the real figure at the
> measured threshold is ~6%. Read that document before acting on this one.

---

## Corrections to Rev 1

Three claims in Rev 1 were wrong. All three came from team review, and all
three are confirmed here by independent re-measurement.

| Rev 1 said | Rev 2 says | who caught it |
|---|---|---|
| misses are **94.6% of the bill** | misses are **66.7% of dollars**. 94.1% was the share of *fresh-input dollars*, not of the bill — cache reads and output are 29% of spend and sit with the hits | fsync |
| one gap curve for the fleet; the bend at 5–6 min is unexplained | the curve is **per model**, and the bend was my aggregation artefact — see below | Corvid |
| weekly $30 wall (stated flat) | the wall is a **projection**. There are no budget rows in the database; it is rate × time. Ruled real by GiLMore, but it is a judgement, not a measurement | Ledger |

**A fourth caveat, self-reported.** Reconstructing the bill from per-token
rates gives **$8.18** against OpenCode's recorded **$5.90** — about 39% over,
most likely the DeepSeek cache rate or peak/off-peak hours applying to part of
the window. The *ratios* in this document are internally consistent and hold.
The absolute dollars should be taken from the recorded figure, not from my
arithmetic.

---

## MEASURED — spend so far

| | |
|---|---|
| Spend since 16:21 | **$5.90** (recorded) over 4.6 h, 2,970 billed calls |
| Muse burn rate | **$0.97/hour** |
| DeepSeek burn rate | $0.31/hour |
| Turn completion | 2,967 / 2,970 = **99.9%** |

Composition of the bill: fresh input **70.7%**, cache reads **23.5%**,
output **5.8%**.

## INFERRED — rolling-window position

A rolling bucket does not accumulate; at a constant rate it plateaus.

| bucket | Muse | DeepSeek | verdict |
|---|---|---|---|
| 5-hour ($12) | $4.86 (41%) | $1.55 (13%) | sustainable indefinitely |
| weekly ($30) | projected **Tue 23:27** | Fri 18 Sep | the binding constraint |
| monthly ($60) | projected Thu 17 Sep 06:18 | Tue 22 Sep | — |

Projections assume continuous running, which overstates them since lanes idle.
No budget counter was read — see Corrections.

## MEASURED — the rates

Cache-read rate cross-checked against a real billed row: 8,490 fresh input +
11 output billed $0.00085, matching $0.10/M exactly.

| model | input /M | output /M | cache read /M | monthly | note |
|---|---|---|---|---|---|
| muse-spark-1.3-contributor | $0.10 | $0.20 | $0.002 | $60 | current, 10 lanes |
| muse-spark-1.2-contributor | $0.10 | $0.20 | $0.002 | $60 | same price, **separate budget** |
| mimo-v2.5 | $0.14 | $0.28 | $0.0028 | $60 | next cheapest on our mix |
| deepseek-v4.1-flash | $0.15 / $0.30 | $0.60 / $1.20 | $0.003 / $0.006 | $60 → **$15** | off-peak / peak. 3 dsh seats. See correction below |
| glm-5.3-flash | $0.15 | $0.50 | **$0.03** | $60 | cache read 15× Muse — costly here |
| longcat-2.0 | $0.30 | $1.20 | $0.006 | $60 | — |
| kimi-k2.6 | $0.95 | $4.00 | $0.16 | $60 | ~4 h runway on our mix |

**[WRONG — see the correction immediately below. Left in place as history.]**
~~**Limits are per model, not pooled** — the published table carries a different
monthly figure per row ($60 GLM-5.3-Flash, $15 GLM-5.3), which one shared pool
could not.~~ Within each model: 5-hour = 20%, weekly = 50%, monthly = 100%.

**CORRECTION 2026-09-17 — THE DASHBOARD CANNOT SETTLE THIS, AND NEVER COULD.**
An earlier version of this block claimed the shares summing to the total *proved*
one pool. It proves nothing, because `sum(x_i / C) == (sum x_i) / C` whenever the
per-model ceilings are equal — and they are ($60 monthly, $30 weekly, on every
row we have seen). **Every percentage the Go page displays is identical under
both readings.** Measured 2026-09-17: $20.1262 + $6.8379 + $0.006 = $26.9701
gives 89.9% of the week and 45.0% of the month under the pooled reading, and
89.9% / 45.0% under the per-model reading too. That identity is why this rule has
been "settled" in both directions from the same screen, twice each. Looking
harder at the page is not a method.

**SETTLED AS ONE POOL, 2026-09-17**, on four NON-arithmetic grounds. Ranked by
strength, because the weakest is the one that reads most convincingly:

1. **The "Total" row carries a reset timer and is the headline.** Under
   per-model quotas that figure is an aggregate that can pass 100% with nothing
   exhausted. Nobody builds that number and gates on it.
2. **The docs are singular** — "5-hour — 20% of **the** monthly limit; weekly —
   50%; monthly — 100%." One limit, whose fractions define the windows; each
   model is *subject to* it. Read here twice as ambiguous; it is not.
3. **The referral credit applies "toward your Go usage limits"** — one thing.
4. **27 models × $60 independent would be $1,620/month of allowance for $10.**
   Weakest of the four, and worth stating why: contributor pricing is paid in
   *training data*. Zen's retail row for the same Muse model is $1.25/M against
   our $0.10/M, so the notional allowance is not the vendor's cost, and a loose
   per-model ceiling would be cheap for them to offer. Vendors do publish limits
   that look absurd on paper and rely on users concentrating on one model.

Still not a vendor statement. Ask support, so the rule is citable rather than
inferred.

**The confirming probe was DECLINED 2026-09-17.** It would have pushed ~$6 of
GLM before the weekly reset — refused after $3.03 under the pool, fine under
per-model. Declined because the evidence is four-deep while the probe spends the
week's only Go **fallback**, two days before the free GLM window expires. It also
has a precondition that was never checked: if "Use your available balance after
reaching the usage limits" is enabled, the wall is not a stop but a switch to
real prepaid spend at 1:1. Confirmation arrives free in normal operation — the
first refusal of a model whose own row sits well under its ceiling is the pool.

**The deciding experiment, which is cheap only while we sit near a wall
(2026-09-17: week 89.9% used, $3.03 left, resets in 2 d 18 h).** The readings
disagree about headroom: pooled says $3.03 for everything, per-model says GLM
5.3 Flash alone has $29.99. So push ~$6 of GLM traffic before the weekly reset.
Pooled ⇒ refused after $3.03 or falls back to free/balance. Per-model ⇒ fine.
Unused weekly allowance expires at the reset, so the test costs nothing we would
otherwise keep. `go-budget --plan` prints this, with the numbers of the day.

Under the pooled reading, which the rest of this document assumes:

- The plan allowance is **ONE $60/month equivalent**, $30/week, $12 per 5 hours,
  shared by every model. Weekly quota reads **$30.00 per model** on the page,
  exactly half the monthly $60 — so the window fractions (20% / 50% / 100%) are
  confirmed even though the pooling is not.
- The per-row "monthly limit" in the published table is a **ceiling on how much
  of that one pool a single model may take**, not an allowance of its own. No
  model may exceed its row; the sum may not exceed $60 either way.
- **Spreading seats across models buys no extra budget.** Two seats on two models
  produce two bills that ADD against the same $60. It buys concurrency and
  reviewer independence — both real — but zero dollars.

The reasoning in the struck sentence was an inference from the table's differing
row values. The dashboard is a direct reading of the counter and it wins. This
error survived because the per-model reading was never checked against a total.

**What the plan is actually worth, and what a cap really costs (2026-09-17).**
Go is **$10/month for $60 of contributor-rate allowance — a 6x multiplier.** The
per-model row is a ceiling on that model's share of the $60, and the "4x" on
deepseek-v4.1-flash is a ceiling multiplier: $15 x 4 = $60, the whole pool. It
does NOT discount the rate. Proof: on 2026-09-16 the dashboard showed DeepSeek's
$6.24 as **20.8%** of the $30 week. A rate discount would have shown ~5%.

**Reaching a cap is not a wall.** Two documented outcomes: free models stay
available, and an opt-in "Use balance" setting continues on prepaid Zen credit
instead of blocking. The contributor tier is still available on Zen, so the
fallback bills **the same $0.10/$0.20/$0.002**, only at 1:1 instead of 6:1.

Consequence for sizing: the caps are a leverage question, not a research
constraint. Our measured pairing (kiln on Muse 1.3, corvid on deepseek-v4.1,
2026-09-17 volumes, doubled for parallel seats) is **$22.48/month of
contributor-rate usage**. Go covers it for $10. Run the identical work entirely
on Zen balance and it is ~$22. **The plan saves about $12/month; it does not
gate the work.** Size against the cache hit rate, which swings the same bill 9x,
and treat a cap breach as a downgrade to free models, not a stop.

**CORRECTION 2026-09-17, from `opencode.ai/docs/go` — the DeepSeek "4×" is a
LIMIT promotion, not a price promotion.** This table recorded it as a price cut
ending 20 Sep, which made the post-promo projection four times too expensive and
the post-promo *allowance* four times too large. The page's own notation is
`$15 $60 4x · Ends Sep 20` in the **Monthly Limit** column. So on 20 Sep:

- deepseek-v4.1-flash **prices do not change**; its ceiling inside the shared
  pool falls **$60 → $15** — i.e. after the 20th it may supply at most a quarter
  of the plan's month, where before it could supply all of it.
- Its two-number prices are **off-peak / peak**, not a promo. DeepSeek's off-peak
  hours are 16:30–00:30 UTC = **09:30–17:30 local**, so our 08:00–18:00 window is
  off-peak except the first 90 min and last 30 min.
- deepseek-**v4**-flash keeps $0.15/$0.60/$0.003 at a **$30** cap and is untouched
  by the promo — at our cache profile it is the cheaper seat after the 20th.

**Which cap actually binds.** Weekly is 50% of monthly, so 4.3 weeks of
weekly-cap spending is 215% of the monthly cap. **For a SUSTAINED rate the
monthly pool binds first.** That is a statement about sustained rates and not
about any given moment: on 2026-09-17 the week read 89.9% against the month's
45%, because the monthly window had opened more recently than the weekly one
(26 d 17 h to the monthly reset, 2 d 18 h to the weekly), so this month sat
entirely inside this week. Read both; the live constraint was the week. Sizing against the weekly $30 wall (this document's original framing)
permits about twice the sustained rate the month allows. A per-model row can
bind earlier only for a model whose ceiling is below the pool — today that is
GLM-5.3 ($15), deepseek-v4-flash ($30), and deepseek-v4.1-flash ($15 after the
20th).

Runway on our measured mix: Muse 1.3 alone 62 h; adding 1.2 and MiMo ≈ 168 h.

## MEASURED — what was used

| engine | calls | fresh input | cache reads | output | billed |
|---|---|---|---|---|---|
| muse-spark-1.3-contributor | 1,498 | 40,479,165 | 186,286,598 | 269,185 | $4.47 |
| deepseek-v4.1-flash | 1,165 | **853,457** | 324,999,552 | 545,345 | $1.43 |
| glm-5.3-flash (probes) | 4 | 36,417 | 6,272 | — | $0.01 |

The dsh seats did **more calls on 2% of the fresh input** and produced 3× the
output per call.

## MEASURED — where the dollars sit

| call type | calls | share of calls | fresh $ | cache $ | output $ | share of bill |
|---|---|---|---|---|---|---|
| cache miss (>50% fresh) | 333 | ~10% | $5.44 | $0.00 | $0.01 | **66.7%** |
| cache hit | 3,107 | ~90% | $0.34 | $1.92 | $0.46 | 33.3% |

Median context per call: **210,153 tokens**. One full miss re-bills about
$0.021 of fresh input.

| lane | misses | fresh tokens | cost |
|---|---|---|---|
| conductor-glm | 66 | 13,354,921 | $1.34 |
| kiln (implementer) | 51 | 10,523,698 | $1.05 |
| ledger (proposal-drafter) | 52 | 7,791,208 | $0.78 |
| verity (reviewer) | 49 | 5,611,318 | $0.56 |
| builder (conductor-chat) | 45 | 2,652,712 | $0.27 |
| fsync (memory-bake-off) | 26 | 5,313,506 | $0.53 |
| the three dsh seats, combined | 3 | 40,465 | $0.00 |

## MEASURED — cache decay is per model, not fleet-wide

Cache **hit rate** by how long the lane had been quiet before the call. This
replaces Rev 1's single blended curve, and it is the finding that governs what
to do.

| model | 0–1m | 1–2m | 2–3m | 3–4m | 4–5m | 5–6m | 6–7m |
|---|---|---|---|---|---|---|---|
| muse-spark-1.3-contributor | 96.3% | 66.5% | 56.0% | 33.0% | 25.0% | **18.6%** | 41.9% |
| deepseek-v4.1-flash | 99.4% | 99.9% | 100.0% | 99.9% | — | **99.9%** | 99.9% |

Call counts, Muse: 1481 / 132 / 112 / 32 / 4 / 172 / 53. DeepSeek: 1288 / 2 /
1 / 1 / 0 / 153 / 6.

- **Muse's cache decays over minutes. DeepSeek's does not move.** There is no
  single fleet cadence; only the Muse seats need tightening.
- Rev 1's unexplained bend at 5–6 min was an aggregation artefact — averaging a
  collapsing curve with a flat one. Corvid's diagnosis, confirmed.
- The 6–7 min bounce to 41.9% rests on 53 calls and may be noise.
- Agrees with Corvid's direction; tails differ slightly (they measured
  96.9% → 14.8%), likely different binning or window.

## OPEN — what we still don't know

1. **Why the two models differ.** An outside extension documents the gateway
   prefix-cache TTL at ~5 min, but neither of our models matches it — Muse
   drops from 1–2 min, DeepSeek persists past 30. TTL is not the whole story.
2. **This sample is contaminated.** Every lane was stopped and started roughly
   a dozen times during the migration; a restart always begins a cold session,
   so some share of the misses is self-inflicted. A clean 24 h would settle it.
3. **Whether cache retention is settable.** If `prompt_cache_retention` or a
   stable per-session cache key lets the cache survive the pulse, that beats
   pulsing faster. Untested.
4. **Whether a plan-wide ceiling sits above the per-model limits.** Nothing in
   the docs mentions one. Absence of evidence.

## The conductor's position

> "It would backfire — compaction raises the bill instead of cutting it… Compacting
> throws away the cheap cached context and replaces it with freshly written summary
> that bills at full price."
>
> "The disruption is real too: each compaction sheds detail the lanes are working
> from, so verification chains and half-done comparisons would come back thinner
> or broken."

- **Right on the pricing.** Cache reads are $0.002/M against $0.10/M fresh.
- **Right on the disruption**, and no measurement settles it. The conductor
  knows which lanes are mid-verification.
- **The arithmetic still does not support "raises the bill"** — a compaction
  costs ~$0.003 once and cuts later misses from $0.021 to $0.002 — but the case
  is weaker at 66% than it looked at 95%, and compaction is declined.
- **Declined on cost grounds:** the cool-pulse position. For Muse seats slower
  means more misses. **Adopted:** serialization — one pulse per seat,
  no-trigger bumps off.
- One correction: the claim this has "kept tonight's spend near zero". Tonight
  is $5.90.

## DECISION — team recommendation (Ledger synthesis)

Apply 1+2+3 now; test 6 in parallel and prefer it if it holds; hold 4 in
reserve. Sized against **sustained full pace** (~$1.28/h → ~$215/week).
Re-size after 20 Sep, when the free GLM window and the DeepSeek promo both end.

| # | change | status |
|---|---|---|
| 1 | **Muse pulse ≤60 s**, time-boxed, revert ready. Drops Muse misses ~90%: $5.90 → ~$2.40 per 4.6 h ($0.52/h, ~$87/week). Halves burn, keeps context. **Insufficient alone** — does not clear $30 | apply |
| 2 | **GLM-5.3-Flash Lite free window** 08:00–18:00 daily to 20 Sep, **1 in flight**. Background seats only (license checks, release watches, grounding passes). Single queue, never critical path; breach risks the account | apply |
| 3 | **Spread background seats** to 1.2 / MiMo budgets nights and weekends. Headroom 62 h → ~168 h. Conductors stay on 1.3 (quality 48.2 vs 39.8) | apply |
| 4 | **Claude Max / Codex Plus** as sparing reserve — overflow and strongest-model jobs only | hold |
| 5 | **No compaction** — conductor's quality objection stands; savings weaker at 66% | declined |
| 6 | **Test cache retention before committing to faster pulses.** If retention settings let the cache survive the pulse, that beats item 1 — no extra calls, no dependence on an inferred TTL. Fall back to item 1 | test first |

---

Fleet state at time of writing: 13 lanes on OpenCode Go, dispatch live, 99.9%
turn completion. Commits `f8247ab`, `591b687`.
