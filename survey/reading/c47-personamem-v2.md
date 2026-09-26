# Reading note — PersonaMem-v2: implicit preferences, trained readers — does the memory effect survive a frozen executor?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 47.**
One methods read (Tern, identity-verified): **PersonaMem-v2, arXiv 2512.06688v1 — a different
paper from the original PersonaMem (2504.14225v2, read in c46; not re-read here).** Questions at
source: **synthetic or real profiles**; how **implicit** preferences are constructed (stated
directly vs. revealed while talking about something else); **evaluation response form and judge**
(free generation? LLM judge? candidate ranking?); **train/test splits** — this edition is said to
involve training, so which splits, and what was trained; **writer/reader controls** (is the
memory-writer separated from the answer-reader, and are they varied independently?); the
commissioned core: **does a memory-method gain survive a frozen executor, or is the headline
carried by policy training?**; **token and total-cost boundaries**; and **any actual
correction-burden evidence** (the c46 gap — does this edition measure it?).

C46 qualifications carried: **taxonomy separates questions, not abilities experimentally**;
**old states are also queried by the evolution/reasons tasks**, not only as distractors; topic
partition alone does not establish absence of all scoped exceptions; the original "generative"
metric still ranks supplied candidates; cost rankings must carry asymmetric preparation
boundaries.

**Frame held before the read (minimal):** if v2 trains a reader on preference-tracking, the
panel's question sharpens: a trained policy is not a memory design, and Brian's lane cannot
train — so the load-bearing comparison is memory-on vs memory-off **at fixed policy**. Written
skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Implicit personas, RL-trained memory — and the frozen-executor control is absent
(2512.06688v1, §2.1–2.5, §3.1–3.2, §4.1–4.3) `[read]`

**Construction: synthetic, but the traps are new.** 1,000 PersonaHub-expanded personas; 20k+
preferences typed **stereotypical / anti-stereotypical / neutral** plus health/therapy; preferences
revealed **implicitly inside task conversations** (email writing, translation, photo queries), not
stated. Three genuinely novel scenario classes: **ambiguous attribution** (hypothetical tests,
third-person-written messages the model must NOT absorb as user persona), **privacy** (leaked
addresses/API keys must not feed personalization), and **explicit user requests to forget prior
preferences**, ordered topologically with updates. History ≤32k tokens (+code/math filler to
128k). Only ~30% of generated Q&As survive filtering (GPT-5 generation, multi-judge votes);
no-context-answerable questions excluded. Splits: **5k benchmark / 18k train / 2k validation**.

**Endpoint:** MCQ (all four options reasonable; one personalized) **plus open-ended scored by
LLM-as-judge against annotated ground-truth preference** — unlike the original's judge-free
scoring, the judge is now in the loop, and it doubles as the RL reward.

**Training is the headline:** GRPO RL on Qwen3-4B (cold-start SFT first), two arms — long-context
reasoning over full history, and **agentic memory**: chunked history, **capped 2k-token
human-readable memory**, causality (no future peeking), Markovian updates; **one model writes
memory and answers** — so **no writer/reader separation, no independent variation of either**.
Agentic-memory 4B: 55.2% MCQ / 60.7% open-ended, beating the same-size long-context-trained model
and the GPT-5 series; **16× efficiency vs processing full 32k histories** (2k memory).

**Commissioned core — does memory survive a frozen executor? The test does not exist.** The
comparison set is trained-memory vs trained-long-context vs frontier models; **nothing runs
memory-on/off at fixed policy**, so the gain is a **bundle of RL training + memory mechanism**,
not a memory effect. The 16× is token arithmetic against full-history processing, valid as such;
no dollar ledger, training cost unreported. **Correction burden: still unmeasured** — forget-
requests are *tested* (a control-respect endpoint), but no turns/cost to repair a wrong
preference.

**Verdict: the richest preference-pain construction read this far — implicit signals,
misattribution traps, privacy, forget-requests — attached to a result that cannot separate
policy training from memory design.** For Brian: the trap taxonomy (hypothetical / third-person /
leaked-secret / forget-request) is directly his preference-lifecycle checklist, and a capped,
human-readable memory mirrors his files; the 55.2% headline is a trained-policy number his lane
cannot inherit. Confidence: high on construction and the missing-control reading (explicit
single-model pipeline), medium on benchmark difficulty comparisons, high on correction-burden
absence (searched).

— cairn. Source `[read]`: arXiv HTML 2512.06688v1, opened 2026-09-26; c46 qualifications carried
(taxonomy ≠ isolation; old states queried beyond distractors; topic partition ≠ no scope
exceptions; candidate-ranking endpoint; asymmetric preparation boundary).

— cairn. Source: arXiv 2512.06688v1, opened today.