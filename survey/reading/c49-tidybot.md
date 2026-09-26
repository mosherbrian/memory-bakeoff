# Reading note — TidyBot: personalized tidy-up from few examples — who supplies them, and what survives contact with the robot

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 49.**
One primary methods read (Tern, identity): **TidyBot, arXiv 2305.05658v2 — personalized mobile
manipulation where the user's preferences are induced from a handful of examples and applied to
unseen objects.** Questions at source: **who supplies the examples, the preferences, and the
ground truth** — is this actual user teaching or researcher-constructed "preferences"?;
**example→summary controls at the same executor** (does the natural-language preference summary
beat raw examples, and is the summarizer ever varied independently of the actor?); the
**unseen-object split** (how is generalization to never-taught items measured?); **language
benchmark versus physical trials** — how much of the headline is GPT answering text scenarios vs
the robot succeeding, and is there a **failure decomposition** (perception vs planning vs
preference error)?; **actual preference revisions or correction burden** (does the user ever
correct the learned rule, and is that measured?); **costs**.

C48 qualifications carried: **removing SFT/DPO changes the executor — component ablation is not
unchanged-policy**; memory-removal protocol was partly unspecified; **near-flat retrieval was a
single-turn observation**, not universal; **keep the GPT-4o vs GPT-4o-mini table/implementation
discrepancy** rather than choosing an identity; small-model timing is not a deployment comparison;
**outcome proxies do not establish user satisfaction**.

**Frame held before the read (minimal):** TidyBot is this panel's oldest teach-by-example claim;
the decisive question is provenance — if the "user examples" are authored by the researchers to
match intended rules, the personalization is staged. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Few examples → rule summary → unseen objects: generalization measured, but the "user" is the authors (2305.05658v2, §3.1, §4.1–4.6) `[read]`

**Provenance: researcher-constructed.** The 96-scenario benchmark (4 room types; 672 "seen"
example placements + 672 unseen evaluation placements) was **created by the authors as text**;
real-world runs use preferences "provided as a set of textual examples" — no user-teaching
sessions, no real principal anywhere. The human study (40 participants, author-institution
affiliates) judges preference-alignment of placements against given text — third-party raters,
not owners of the preferences.

**Mechanism and controls, same executor (text-davinci-003 for both steps):** examples → LLM
writes a **rule summary** (as a code comment) → summary (not raw examples) places **novel
objects**. The decisive numbers: **commonsense without preferences 45.0% seen / 45.6% unseen**
— sensible placements, wrong user; **summarization 91.8 / 91.2**; **human-written "oracle"
summary 97.1 / 97.5** (+6 points, the summarizer is the improvable link). **Seen ≈ unseen
accuracy is the generalization result**: the rule transfers, it isn't memorization. The stated
failure modes are exactly derived-layer rot: summaries that **list objects instead of
categories**, and summaries that **merge receptacles**.

**Language vs physical kept honest.** Human study: method preferred 46.9% vs CLIP 19.1% (34.1%
tie). Real robot: 8 scenarios × 10 objects × 3 runs = 240 objects, **85% placed correctly**,
with a **failure decomposition**: localize 92.5% × classify 95.5% × **LLM choice 100%** ×
execute 96.2%. Read that 100% carefully — it is **conditional on the predicted category** in
author-authored scenarios; the honest preference-accuracy estimate remains the benchmark's 91.2.
15–20 s per object.

**Corrections and costs: neither measured.** Preferences are static example sets; nothing records
a user revising a learned rule or the cost of doing so. No dollar costs; LLM comparison
(davinci-003 > 002/code-002, PaLM-540B worse on summarization) is accuracy-only.

**Verdict: the cleanest few-shot personalization generalization result read this far — separate
seen/unseen scoring, an oracle-summary ceiling, and a real failure decomposition — but the
personalizer is benchmarked against the experimenters' own staged preferences.** For Brian: the
architecture is his files (few examples → written rule → apply to new cases); the +6 oracle gap
says invest in the summary step, and the two named failure modes are concrete review checks.
Confidence: high on benchmark numbers and decomposition (explicit), high on provenance reading,
high on correction/cost absence (searched).

— cairn. Source `[read]`: arXiv HTML 2305.05658v2, opened 2026-09-26; c48 qualifications carried
(component ablation ≠ unchanged-policy; single-turn flatness not universal; keep source
identity discrepancies; timing ≠ deployment comparison; outcome proxy ≠ satisfaction).

— cairn. Source: arXiv 2305.05658v2, opened today.