# Reading note — RAG or Long-Context: the routing controls, and what the cost sheet omits

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 19.**
One source (Tern): **arXiv:2407.16833 — "Retrieval Augmented Generation or Long-Context LLMs?
A Comprehensive Study and Hybrid Approach"** (Jin et al., Google/UMass; EMNLP 2024). Verify
identity first. Questions: matched models/budgets; the **routing signal**; cost accounting; when
full-context actually wins; is routing by **self-assessed answerability** dependable in their
measured setting; what does their cost omit. Distinguish passage/document QA from live procedure
or preference application. No cross-paper leaderboard, no extra sources.

**Provisional frame (before the read).** Expected shape: benchmark comparison across QA suites
→ a hybrid (RAG first; if the retriever's evidence is judged insufficient, fall back to full
context) → claim ~same accuracy at a fraction of tokens. The two questions that matter for our
lane: (1) the fallback trigger is a **self-assessment of answerability** — the same
uncertainty-detection dependency as Capture's ask channel (oracle-replayed), PAHF's
confidence-silencing (simulated), and ReadAgent's gap-noticing (measured only indirectly via
compression trade-off). If this paper *measures* the trigger's precision/recall against ground
truth, it is the best evidence in the family; if it only reports end-to-end accuracy, the
trigger's failure mode stays invisible again. (2) Their cost is token/API cost on QA tasks —
almost certainly omits: index construction, per-query latency of the two-pass path, and any
human-side cost. Written skeleton first; verdict after the read.

*(facts + verdict appended after read)*

## Matched controls and headline (identity verified: Jin et al., Google/UMass, EMNLP 2024) `[read]`

Three LLMs (Gemini-1.5-Pro/1M, GPT-4O/128k, GPT-3.5-Turbo/16k), nine real English query-based
datasets (LongBench ×7 + Bench ×2), two retrievers (Contriever, Dragon), 300-word chunks, top-k,
same prompts; leakage handled by "based only on the provided passage" (validated: avg 50.57 →
45.53 when applied). **LC beats RAG everywhere when it can hold the context** (+7.6 / +13.1 /
+3.6 avg); RAG wins only when the text grossly exceeds the window (147k-word Bench docs vs 16k
window).

**The finding that funds everything (§4.1):** RAG and LC predictions are **identical for 63% of
queries — including identical errors** (70% within score-diff 10). The cheap path and the
expensive path mostly *know the same things and miss the same things*.

**Self-Route (§4.2–4.3):** answer from retrieved chunks first, with an explicit decline option
(*"Write unanswerable if the query can not be answered based on the provided text"*);
declines escalate to full context. Measured: 81.7% judged answerable (Gemini), token use 38.6%
(Gemini) / 61% (GPT-4O), cost −65% / −39%; performance vs LC: −2.2 / −0.2 / +1.7 (the last where
LC was truncated). Routing rides in the same call as answering — no extra pass.

## Is self-assessed answerability dependable *in their measured setting*?

**Only in aggregate — never at the decision level.** The calibration premise is stated as an
*assumption* ("under the assumption that LLMs are well-calibrated", §4.2) and never tested: no
confusion matrix of route decisions against "would LC have answered correctly". The −0.2/−2.2%
end-to-end deltas are the sole evidence, and they conflate the two error directions — false
*answerable* (silently accepts a wrong retrieved answer; costs accuracy) and false
*unanswerable* (costs tokens only). The dangerous direction is invisible by construction, and
the paper itself shows the decline threshold is **alignment-dependent, not stable**: OpenAI
models "are more likely to reject answering using RAG, leading to a lower answerable percentage
but higher accuracy" (§4.3) — same task, different trigger, different trade-off. The k-ablation
adds: cost is non-monotone in k, optimum is dataset-dependent — the operating point needs
per-task tuning.

**What the cost sheet omits:** index construction and upkeep (chunking + embedding priced
nowhere; "hosted on customer side" is a footnote, not a number); **escalation latency** (the
declined path is two sequential LLM calls); reranking; and all human-side cost. Token-ratio
accounting itself is honest — escalated queries pay both passes.

**QA vs live application:** all static query-based QA/summarisation over fixed documents — no
writes, drift, or preference scope. The *structure*, however, is the first **measured** evidence
in this sweep for the c12 A+C hybrid's cost shape: memory-first attempt + explicit decline +
escalation to full record, no oracle needed — ahead of Capture (oracle-replayed asks) and PAHF
(simulated users), short of a decision-level calibration study (none exists here).

**Strongest idea for Brian:** the 63%-identical result is the economic engine — attempt from the
memory record first; if it cannot ground the action, *say so in-band* and escalate to raw
history. Two measured caveats: tune the decline threshold per model, and expect the residual
loss to sit in false acceptances — the escalation trigger goes silent exactly when it is most
needed, the same confidence-silencing shape as PAHF §5, this time with a price tag.

**Verdict: solid on the hybrid cost claim (matched models, two retrievers, measured savings);
oversold on routing dependability (premise assumed, aggregate-only evidence); cost omits index
upkeep + escalation latency.** Confidence: high on numbers and on the gap (explicit assumption
sentence + absent confusion analysis).

— cairn. Source `[read]`: arXiv HTML 2407.16833 (v1 rendering) §3.1–3.3, §4.1–4.3, §5.1–5.3, §5.5, opened 2026-09-26.