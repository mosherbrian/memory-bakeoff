# Decision note c60 — when acquisition earns its upkeep: what c56–59 actually discriminates

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 60.**
Existing c56–c59 reads only; no new source. Skeleton first. C59 corrections carried: CRAFT's
validation re-checks the **original** case, not extra held-out cases; VQA used generated
references/model judging, unlike tabular/math labels; dedup ≠ semantic non-overlap; **GPT-4
benefits from its own tools too** (smaller gain, not none); poor open-source pilots are not
local transfer; the ~$14 build estimate is **AutoManual's, not LATM's** (my c59 misattribution —
fixed in-file); no universal registry, per-record check, or "strictest admission" ranking;
FRIDAY's bundle is useful without a universal interface-discovery moderator.

**Question:** among reconstruct-at-answer-time, create-on-demand, bounded practice, and batch
construction — which comparisons in c56–59 actually discriminate, what can none of them
establish, and what do I recommend?

*(decision appended below)*

## What discriminates

**1. Same toolset, different executors (CRAFT §4.3, c59)** `[read]` — the sharpest control for
Brian: identical stored tools, GPT-3.5 gains much, GPT-4 gains less (still gains). Acquisition
value tracks the **author-to-executor capacity gap**. Brian's shape — strong authoring pass,
local models executing — sits on the high-gain side, though no source tests a local executor.

**2. Same framework, with-vs-without acquired tools (FRIDAY, c58)** `[read]` — GAIA +4.3/+2.5/
0.0 but Excel 0→60. Discriminates **where**: acquisition pays where the executor lacks the
interface, and little where it already improvises. The moderator is inferred from two endpoints,
not varied — directional, not a law.

**3. Stored-form ablations (CRAFT §4.1–4.2, c59)** `[read]` — abstraction beats raw solutions
with retrieval held fair; dropping function names costs >6.6 SAcc. Discriminates **how to
store**: generalized, deliberately-named entries over episodic dumps.

**Non-discriminating: Cradle (c57)** `[read]` — module-bundle ablations only; no library
on/off; contributes architecture plausibility, zero acquisition economics.

## What none can establish

No source runs a stored procedure **after environment drift** (c56 gap, unbroken by c57–59); no
break-even exists anywhere — CRAFT's ~$2,500 batch, FRIDAY's unpriced practice, on-demand
reconstruction's answer-time cost are never on one ledger; **local-model transfer is untested**
(GPT-3.5 is not local; failed open-source pilots show author quality, not transfer); selection
accuracy is never directly measured.

## Recommendation (one)

**Acquire on bounded practice, not batch, not pure on-demand:** when the local executor visibly
lacks an interface or workflow (FRIDAY's Excel shape), run a short strong-author pass and retain
generalized, named entries — each re-checked on its originating case (CRAFT order) and deduped
by name+arity. Where the local model already muddles through (GAIA shape), reconstruct at answer
time and store nothing. Batch construction is reserved for domains with **answer labels** to
gate admission — Brian's preferences have none, so his entries keep the weaker gate: explicit
directions bind, inferred ones stay revisable. No registry mandate, no per-record check beyond
the originating-case re-check.

**Confidence: high that controls 1–3 are the discriminating ones in c56–59; medium that the
bounded-practice recommendation survives untested drift and local transfer; high that no
break-even evidence exists (searched across four sources).**

— cairn. Built from reading/c56–c59.