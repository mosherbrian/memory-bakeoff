# OmniMemEval's LongMemEval judge is not the official rubric — it is a generic "be generous" prompt

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-OMNIMEMEVAL-METRIC.md`;
the perfect MemOS categories made the judge load-bearing · **Cost:** $0 (two
pinned fetches), one turn.

**Receipts:** `team/row-omnieval-judge-receipts/` (`MANIFEST.md` with sha256):
OmniMemEval `scripts/longmemeval/lme_eval.py` and the official LongMemEval
`src/evaluation/evaluate_qa.py` (repo `xiaowu0162/LongMemEval`).

## Finding 1 — the rubric is materially looser than the benchmark's

| | Official LongMemEval | OmniMemEval |
|---|---|---|
| Prompt structure | **task-specific**: separate prompts for single-session-user/assistant/multi-session, temporal-reasoning, knowledge-update, single-session-preference, and abstention | **one generic prompt** for all categories |
| Rubric | "answer yes if the response contains the correct answer. … If the response only contains a **subset** of the information required by the answer, answer **no**" | "you should be **generous** with your grading — as long as it **touches on the same topic** as the gold answer, it should be counted as CORRECT" |
| Label extraction | `'yes' in eval_response.lower()` | parse JSON `{"label": …}`; `label.lower() == "correct"`; **raises** if no label |

So OmniMemEval's LongMemEval score is a **topic-match judgment**, not the
official correctness rubric. Its numbers are internally consistent across the 14
backends (one prompt, one judge model), but they are **not official-protocol
LongMemEval** and are not directly comparable to official-judge figures.

## Finding 2 — mechanically sound, lenient by design

The instrumentation is not broken: the judge requires a JSON label, raises on
extraction failure (no default-to-correct), uses `temperature=0`, and compares
strictly to `"correct"`. The looseness is in the **rubric text**, not the
plumbing. (`lme_eval.py`: `raise ValueError("could not extract judge label…")`;
`lme_metric.py`: `score = 1 if v else 0`.)

## Finding 3 — what this changes

1. **The perfect MemOS row has a mechanism.** 100.00 on single-session-user,
   single-session-assistant, and single-session-preference under a "same topic
   is CORRECT" rubric judged by `gpt-4o-mini` is exactly the shape a generous
   judge produces. This moves my earlier plausibility flag from "look at this"
   to "the judge is the likely cause."
2. **The "rivals undercut their self-reports" finding survives and hardens.**
   Mem0 56.00 and Hindsight 72.20 (SS-Asst 14.29) are low *despite* a lenient
   judge — a stricter official rubric would push them lower, not higher.
3. **The MemOS-vs-TiMem gap is partly a judge-rubric difference.** TiMem uses
   the official LongMemEval QA/LLJ template; OmniMemEval uses its generic
   generous prompt. So the ~16-point gap reflects **model + rubric**, not one
   protocol. A strict comparison must use the official judge on both sides.
4. **Citation rule:** do not write "MemOS 89.20 on LongMemEval" without "under
   OmniMemEval's non-official generous judge." The OmniMemEval docs themselves
   warn that published scores "may use different … judge implementations, and
   should not be treated as directly comparable" — the same caveat applies in
   the other direction.

## Correction to my previous artifact

`ALICE-OMNIMEMEVAL-METRIC.md` called OmniMemEval "a one-harness reproduction";
the accurate phrase is **"one non-official harness with a generic generous
judge."** The one-harness property (identical data, prompts, answerer, judge
across backends) still holds and is still useful for *relative* comparison; the
absolute numbers carry the rubric caveat.

## Method and limits

- Read both judge implementations and prompts verbatim; no benchmark, engine, or
  LLM run. I did not verify whether OmniMemEval's LoCoMo/HaluMem prompts match
  their official counterparts (LoCoMo's own judge is similarly generous, so the
  gap is likely smaller there) — a bounded next step if needed.
- I did not compare the answer-generation prompts, only the judge.
