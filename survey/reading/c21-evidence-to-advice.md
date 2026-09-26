# Evidence-to-advice — the three sources that most change our advice

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 21.**
Already-read evidence only; no new sources. Corrections from Tern applied: code can silently
return a wrong answer; FH-vs-DC is not a lifecycle/currentness experiment; A-MEM drift is a
risk, not a reproduced fact; DC-RS retains raw past IO-pairs.

## 1. Self-Route (2407.16833) — the economics of the default loop — confidence: high on numbers, medium on transfer

**Outcome:** answer from retrieved memory first, with an explicit *decline* option; declines
escalate to full context. −65% cost (Gemini) at −2.2% performance; 63% of queries give
identical answers (right **and wrong**) on both paths.
**Transfer limit:** static QA; no drift, no writes; the decline threshold is alignment-dependent
and never tested at decision level.
**Supports:** the default arrangement for Brian's lane: **record-first attempt, in-band decline,
escalation to raw history** (grep/logs). This is the c12 A+C hybrid with a measured price tag —
no oracle needed.

## 2. Dynamic Cheatsheet v2 (2504.07952) — how to capture procedures — confidence: high on controls, medium on transfer

**Outcome:** with a recurring task family, the model discovered a Python solver, stored it, and
reused it: 10%→99% (Game of 24); the DC-∅ control (same prompts, empty sheet) shows the memory
carries the win. Smaller models stall — curation needs competence.
**Transfer limit:** self-curated, label-blind; **code is not self-verifying — a stored script
can run green and be semantically wrong**; 3–5× per-query cost; no shuffled-order control.
**Supports:** for repeated procedures, store the **ran-and-worked artifact** (script/command
with its last successful invocation and the check that made it "worked"), not prose heuristics —
and re-run the recorded check at reuse, since the artifact alone proves only that it ran.

## 3. Capture (2609.02265) — the ask budget for preferences — confidence: high on mechanism, low on the human number

**Outcome:** bounded clarifying questions (≤1 per 12) provably enlarge the achievable error
region when features are limited; D-PrefGuard shows adherence without asking-everything.
**Transfer limit:** the 40-user study is oracle-assisted replay — the human is absent exactly
where attention cost lands. Our lane's only measured attention number remains our own confirm
ledger: **59/88 drafts expired unconfirmed**.
**Supports:** external scoped preference record + learned proposer + **ask budget enforced
against Brian's observed response rate**, not a design-time constant; preference changes are
mostly scopings, so record scope before asking.

**Honourable mentions:** PAHF measured confidence-silencing (keep a reactive channel; never
clarification-only); FH worse than baseline (never ship "append everything").

## One open question to retire

*"Is memory-first-with-decline worth it versus always reading full history?"* — **retired as
sufficiently answered for the present decision**: yes, ~38% of tokens for ~2 points, provided
the decline option is explicit and per-model tuned (Self-Route, measured). The remaining
unknowns (decision-level calibration, drift behaviour) change *tuning*, not *whether*.

— cairn. All three sources `[read]` this session (c19, c20, c3/c13); limits per those notes.