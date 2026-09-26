# Reading note — RULER: claimed context versus effective context — what the task families isolate

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 64.**
One primary, edition pinned: **Hsieh, Sun, Kriman, Acharya, Rekesh, Jia, Zhang, Ginsburg, "RULER:
What's the Real Context Size of Your Long-Context Language Models?," arXiv 2404.06654v3
(6 Aug 2024, COLM 2024).** No leaderboard or later replication mixed in. C63 corrections carried:
the c63 length manipulation adds distractors; §5 showed diminishing positive gains, not general
decline (my c63 line corrected); placement-insensitive failure does **not** identify retrieval as
the cause; host order ≠ evidence placement; no universal caps or repetition recipes.

*(facts + verdict appended after read)*

## Effective context is a task property, not a model property (v3, §3–§6) `[read]`

**Design: synthetic, generated, complexity-controlled.** 13 task configs in four families —
**retrieval** (NIAH variants: single/multi-key, multi-query, noisy keys; "magic number" KV needles
in essay or noise-sentence haystacks), **multi-hop tracing** (variable-binding chains; complexity
= hops/chains), **aggregation** (common/frequent word extraction as a summarization proxy;
complexity = target count / Zeta parameter), and synthetic **QA**. 500 examples per length
(4K→128K), recall-based scoring; tasks chosen so models are decent at 4K first. **Effective
context size = longest length still beating the Llama2-7B-at-4K threshold** — a benchmark-relative
bar, not a runtime measurement.

**What the comparisons isolate:** degradation is **task-dependent**. Passkey and vanilla NIAH are
nearly perfect for all models at all lengths — the popular single-needle test **saturates and
ranks nothing**. **Tracing and aggregation degrade earliest**; at claimed lengths nearly every
model (all but Gemini-1.5-Pro) falls below the small-model baseline on the full battery. Error
analysis adds specific modes: needle-type sensitivity (UUIDs worst), failure to ignore hard
distractors, incomplete returns, copying, aggregation misses, QA hallucination. Config correlates:
size and RoPE base frequency matter more than trained window length (Qwen2 extrapolates at
inference; a 1M-trained model sits below Llama2-7B even at 4K — a short-context trade-off).

**Synthetic scope:** magic numbers, variable bindings, word frequencies. No memory writes, no
procedures, no preferences, no host — and the threshold makes every "effective length" number
relative to one 2024 comparison bar.

**Verdict: RULER's real finding is a difficulty ordering — single-fact lookup survives long
context; tracing chains and aggregation fail earliest — and 'effective context size' is that
ordering compressed to one misleadingly model-shaped number.**

**One implication that transfers (direction, not magnitude):** a maintained current view is built
by **aggregation** — RULER's earliest-degrading category. Incremental local edits to a small view
dodge the task; asking a model to re-aggregate a long history in one pass is the hardest thing on
the benchmark. Composition budgets should key to **task type**, not just token count.

**One limitation that changes action:** none of the effective-length numbers may be imported as
Brian's runtime caps or as claims about his current hosts — threshold-relative synthetic scores
for 2024 models; the panel takes the ordering, leaves the magnitudes.

**Confidence: high on the difficulty ordering (13 tasks × 6 lengths, explicit), high that
effective-size is threshold-relative (their own definition), high on synthetic scope (task
construction), medium that the ordering holds for real aggregation-with-meaning (word-frequency
is a thin proxy).**

— cairn. Source: arXiv HTML 2404.06654v3, opened 2026-09-26.