# muse-drafter: LongMemEval-V2 PDF/body pass (spark pulse 2026-09-14)

Closes card 7's "Next step 1" (`CANDIDATE-CARD-LONGMEMEVAL-V2.md`): one PDF pass
for methods + gotcha/premise item shapes + license/code link. Body read of
`arXiv:2605.12493v1`. Grounding only — **all scores vendor-run, not citable, no
score import.**

## License (closes the card field)

- **Paper text: CC BY 4.0** (arXiv HTML header) — card previously said
  "license NOT verified".
- Code/harness `xiaowu0162/LongMemEval-V2`: **Apache-2.0**; HF data
  `xiaowu0162/longmemeval-v2`: **Apache-2.0** (prior data-lane pass). So the
  three lanes are CC-BY-4.0 (prose) + Apache-2.0 (code, data).

## Construction (body-level)

Trajectories from **WebArena** (OneStopShop, CMS, Reddit) and
**WorkArena/WorkArena++** (ServiceNow) via the AgentLab harness, ReAct base
agent + Codex, rejection sampling with GPT-5.2 / GPT-5-mini: **599 WebArena +
941 WorkArena** trajectories, 52.0% success, 28.1 states avg. All 451 questions
**manually annotated** and screened so ≥2 of 4 frontier models (Gemini-3-Pro,
GPT-5.2, Grok-4.1-thinking, Claude-Opus-4.6) answer wrong from parametric
knowledge alone. Tiers: **Small** = 100-trajectory shared haystack (~25M tokens,
one per environment family), **Medium** = ~500 per question (~115M tokens);
haystacks balance successful and failed trajectories, and **many questions are
answerable only from failed trajectories**.

## Evaluation formulation (useful for our delivered-level rule)

Context-gathering: memory implements `Insert(h)` / `Query(q)`; the returned
context is truncated to **200k tokens** and a **fixed Qwen3.5-9B reader**
answers (normalized string match for structured answers, LLM judge for
free-form). Controller = Qwen3.5-9B (RAG) or GPT-5.4-mini/Codex (coding-agent);
retrieval = Qwen3-Embedding-8B. This cleanly separates formation from use.

## Gotcha / premise item shapes (card next-step 2 input)

- **Gotchas** are framed as a **scenario where an inexperienced worker sends a
  message with a screenshot** (multimodal); other questions are text
  true/false, multiple-choice, or short-answer.
- **Premise awareness / abstention** questions are built by giving a **wrong
  premise** the model must identify (curated from the static/dynamic/workflow
  items).
- Body finding worth carrying: **gotchas are the hardest ability even with
  oracle trajectory files** (~0.52 ceiling in-paper) — i.e. the failure mode our
  stale-path probe targets is where evidence is weakest. Design hint, not a
  result.

## Limits

Numbers are one-study vendor runs (reader/controller pinned); card's "not
citable" verdict **stands**. Attribution rule unchanged: **LME-V2 ≠ LongMemEval
v1** — cite by ID + date. Second seat: Alice.

$0, one arXiv HTML read, no Muse batching. — muse-drafter (Spark)
