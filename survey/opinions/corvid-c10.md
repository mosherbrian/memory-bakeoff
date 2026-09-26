# Contrarian, cycle 10 — stability, not authority, predicts the user; and explicit text misses behaviour

**corvid · 2026-09-26 · cycle 10.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Primary source read at methods/results level: ReaLMem + ChronoProfiler, Zhou et al.
([arXiv:2609.19167](https://arxiv.org/abs/2609.19167)) — distinct from the synthetic RealMem
(2601.06966). `[read]`

**What the authentic data actually tests.** Seven participants, 350+ photos/videos each,
**2,508 sessions over 2018–2025**, dual-layer annotation (verified metadata + the owner’s own
first-person context, feelings, implicit preference signals; an LLM only renders narrative and
invents nothing), anonymised, 1,629 QA. Three tiers: T1 factual recall; **T2 persona inference**
(profiling, longitudinal tracking, behavioural reasoning); **T3 predictive personalization** — a
**ranking** task scored by Kendall-τ against the participant-validated preference ordering.
So this is **held-out label prediction**, *not* interactive adaptation: the model never acts and
gets corrected. T2/T3 are contributor-verified. `[read]`

**Strongest challenge to the memo’s preference policy.** ChronoProfiler builds a per-item
profile and scores each attribute by **temporal stability** (support × duration × recency,
entropy-weighted per user, injected as a salience prior), because flat memories cannot arbitrate
“vegan two years ago” vs “BBQ last week.” Results: a ~6k-token temporally-weighted profile
**matches or beats 123k-token full context** on T2 (Δ +0.6/+4.0/+4.3) and T3 (0/+3.5/+1.8), and
swapping only the profile representation lifts T2 by **+6.3** over the memory system’s own
profile. The active ingredient is *which preference is stable*, derived from behaviour — not an
explicitly declared direction. That raises a real rival: **inferred, temporally-stable preference
may predict the user better than an explicitly promoted one**, and a single explicit statement
can be a one-off that stability scoring correctly discounts.

**But it also warns against over-promoting.** The TS ablation shows sharpening recurring
preferences helps profiling (+2.7 T2) and **hurts context-specific assistance (−2.4)**. And the
modality ablation is the sharpest twist: **dialogue-free visual+metadata beats rich dialogue on
T3 (61.4 vs 59.2)** — a text preference record can be *worse* than the behavioural signal
because conflicting text cannot be arbitrated. `[read]`

**What should change in the memo.** Not the authority/inference split — ChronoProfiler never
tests authority or consent, so bet 2’s “explicit directions are policy” still stands. Two
sharpening moves: (1) for *prediction and assistance*, arbitrate inferred tendencies by
**temporal stability over evidence**, not by recency or recall count; (2) do not promote a
recurring preference into an authority rule merely because it recurs — TS says recurrence can
trade away occasion-specific help, and only Brian can decide when a preference binds. Bet 2’s
“clear preference surface” should be temporally weighted and evidence-grounded, which this shows
is cheap (~6k tokens) and effective.

**Missing comparison / what would change the memo.** It never measures correction burden,
upkeep, or adaptation, and 7 participants cannot carry population claims. A reversal would be
real-user evidence that explicit promotion reduces repeated corrections more than stability-based
inference does; no such number exists here. **Medium confidence** that stability-weighting
improves the preference surface; **low** that it substitutes for explicit authority.

— corvid. `[read]` 2609.19167 fetched 2026-09-26; no reproduction, no experiment.
