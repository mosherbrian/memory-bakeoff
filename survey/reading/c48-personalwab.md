# Reading note — PersonalWAB / PUMA: personalized web agents — actions executed, feedback simulated, correction burden?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 48.**
One primary methods read (Tern, identity): **PersonalWAB / PUMA — "Large Language Models
Empowered Personalized Web Agents," arXiv 2410.17236v2.** Moves the panel from persona-response
scoring to **preference-conditioned web actions**. Questions at source: **real or synthetic**
user histories and tasks; **online vs offline paradigms** (does the agent act in a live simulated
web with feedback, or predict from a frozen log?); **actual action execution versus predicted
API calls** as the endpoint; **reward / judge / feedback provenance** (who says an action was
right — ground truth, simulator, LLM?); **user and temporal train/test splits** (disjoint users?
future interactions held out?); **memory, SFT, and DPO ablations with executor controls** (which
component carries the gain at fixed executor?); **costs**; and the recurring commissioned
question: **any real correction-burden measure**.

C47 qualifications carried: train/benchmark personas **disjoint**; the **16× is final-context
arithmetic, not total work**; a **coupled same-model training bundle is still valid system
evidence** — my "not a memory effect" was too categorical; hardware/steps were reported even
without a full ledger; and **"Brian cannot train" is not a supplied constraint** — I will not
use it as one.

**Frame held before the read (minimal):** the panel's sharpest test yet of the action endpoint —
if preferences are scored by executed web behavior with environment feedback, this is closer to
Brian's lane than MCQ; the risk to watch is simulated feedback standing in for real user benefit.
Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Real behaviors, executed functions, programmatic scoring — but the preference ground truth is LLM-inferred (2410.17236v2, §3–§6, A.4) `[read]`

**History real, profile and instructions synthetic.** 1,000 users sampled from Amazon Review
(5 categories); purchases/ratings/reviews are **real, time-ordered**; the **profile is LLM-inferred**
from behavior and **instructions are LLM-generated** from profile+behavior (search /
recommendation / review). **Temporal split per user: 80% history / 10% train / 10% test** — future
interactions held out; test targets are products the user *actually* bought later. Good grounding;
but the preference signal is circular at the top: instructions encode what the inferred profile said.

**Endpoint: executed actions, not predicted calls.** Web abstracted as functions (BM25 search,
SASRec recommender, add_review, respond, stop); the agent invokes them. **Single-turn scoring is
programmatic — no LLM judge**: function accuracy (right function + format) and **result accuracy =
rank of the actual target product** in the returned list (review: sentence-transformer cosine).
**Multi-turn feedback comes from an LLM user simulator handed the profile and ground truth** —
useful, but simulated benefit with oracle access, not real user benefit.

**PUMA = SFT function selector + task-specific memory retrieval + DPO on heuristic pseudo-labels,
all in a fine-tuned LLaMA-2-7b.** Ablations (Table 5) run **at fixed executor**: remove memory →
result accuracy drops significantly; remove SFT → drops dramatically; remove DPO → slight drop.
That is a genuine component decomposition — memory and supervised function-learning carry it,
preference-alignment marginally. Baselines share one prompt template, memory component varied
(no/random/last/relevant, ReAct, Reflexion, RecMind, InteRecAgent). **Sharpest result: every
baseline's result accuracy ≈ No-Memory** — generic retrieval and reasoning fail to improve
*personalized execution*; only task-specific retrieval + training moves it. PUMA wins accuracy
with shorter memory and a smaller model, and latency 2.8s vs 6.5–6.9s for GPT-based methods.

**Costs:** completion time measured; no dollar ledger; training cost unreported.
**Correction burden: not measured** — multi-turn adjustment from simulator feedback exists, but no
turns/cost for a *real* user to repair a wrong-preference action.

**Verdict: the strongest action endpoint read this far — executed calls, programmatic result
scoring, temporal holdout, fixed-executor ablations — on top of an LLM-inferred preference layer
and an oracle-fed simulator for feedback.** For Brian: the ≈No-Memory baseline failure is the
counter-evidence to "just retrieve history"; a small local executor with task-specific retrieval
beat frontier latency AND accuracy, which fits his lane's capacity shape. Confidence: high on
endpoints/ablations (explicit), medium on review-similarity metric, high on correction-burden
absence (searched).

— cairn. Source `[read]`: arXiv HTML 2410.17236v2, opened 2026-09-26; c47 qualifications carried
(disjoint-persona boundary noted — here users recur, TIME is the split; 16×-style arithmetic
treated as context-only; coupled bundle read as system evidence; no "Brian cannot train" constraint).

— cairn. Source: arXiv 2410.17236v2, opened today.