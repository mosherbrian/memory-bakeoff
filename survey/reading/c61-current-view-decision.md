# Decision note c61 — read-time resolution versus a maintained current view: three results, one default

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 61.**
Skeleton first; own prior reads only (c30/c33/c34/c46/c54), at most **three discriminating
results**. C60 corrections carried: source-scoped controls, no blanket transfer claims, no fixed
reuse thresholds or automatic demotion; **verification, authorization and applicability are
different judgments**; **a scoped direction is not simply the newest sentence**.

Three objects kept distinct throughout: an **explicit direction** (authority), an **inferred
tendency** (revisable), a **procedure whose environment changed** (candidate for re-observation).

*(decision appended below)*

## Three results that discriminate

**1. LongMemEval's winning recipe (c33)** `[read]` — read-time currency over timestamped raw
sessions, **no write-time supersession**, topped the benchmark. A maintained current view is
**not universally required**. But the recipe leaned on **time as an index key** — read-time
resolution won with structure, not by asking the model to sniff recency.

**2. PersonaMem's failure profile (c46)** `[read]` — the same read-time operation, done
**without** structure, is a measured weak point: acknowledging the latest preference degrades
with sessions elapsed; distractors are exactly the outdated states. Together, 1+2 discriminate
not the mechanism but the **requirement: currency must be explicit** — as a time index or a
projection — because implicit recency resolution fails.

**3. DynaMem (c34)** `[read]` — for **world-observable** state, invalidation required
**re-observation**: neither the record read at question time nor the maintained one is
authoritative when the world can change silently. This draws the boundary where **both**
candidates lose to fresh eyes.

(c54 as qualifier, not discriminator: PAIR's maintained 150-word view **lost corrections** —
reported — so a projection without a correction path becomes a stale authority, plausibly worse
than raw.)

## Recommendation, reversal, untested assumption

**Default:** timestamped raw kept recoverable **plus** a small maintained current view per
recurring domain — scoped directions held as authority (not "newest sentence"), active
procedures marked with their environment, each line pointing at supporting evidence. Read time
resolves **against the view first**, never against implicit recency guesses; world-observable
facts get re-observed, not remembered.

**Reversal:** when the view cannot be kept trustworthy — corrections demonstrably not landing
(c54's reports) or upkeep starved — **drop the projection** and fall back to c33's shape:
time-indexed raw plus read-time resolution. A stale current view is worse than none, because it
claims authority it no longer holds.

**Untested assumption:** that a maintained current view actually improves appropriate later use
over time-indexed raw. No source ran that comparison — c33 won **without** a view, c54 had a
view **without** a raw-only arm. The default rests on the currency-failure evidence (2), not on
a demonstrated projection win.

**Confidence: high that currency must be explicit (two independent failure/success profiles);
medium on the default itself (the head-to-head is missing); high that re-observation beats both
for world state (explicit protocol in c34).**

— cairn. Built from reading/c33, c34, c46, c54 (c30 where decisive).