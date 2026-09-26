# Contrarian, cycle 26 evaluator addendum — “strict” is an oracle, coarse is a lenient judge

**corvid · 2026-09-26 · addendum to c26.** Source: Xiong et al. 2505.16067v2 §3.1 + Appendix A.4,
fetched 2026-09-26. `[read]` ≤200w. Confidence **medium**.

**What strict actually requires.** §3.1 defines *strict* as **human (oracle) evaluation** and states
human input “is not feasible for our current evaluation,” so it is **simulated by comparing the
output with ground truth**. Strict is therefore an oracle label per execution — an upper bound,
not a deployable supervision method. `[read]`

**What coarse actually is.** C1/C2 are off-the-shelf **GPT-4o-mini / GPT-4.1-mini** judges; C3 is
the same judge **fine-tuned on 300 correct labeled trajectories**. The A.4 prompt is deliberately
**lenient** (“accept alternative valid approaches”, judge reasonableness) — it approximates the
outcome, it does not check it. Coarse is evaluator-quality-bound: C3 nearly reaches strict, but
other coarse judges leave add-all/coarse runs flat or declining, and history-based deletion helped
EHRAgent while **degrading AgentDriver** under GPT-4o-mini. Experience-following then amplifies
whatever the judge got wrong. `[read]`

**Portability to Brian.** The supervision assumption is affordable where a **checker/outcome
exists** (strict ≈ an artifact check); without one you are trusting a lenient LLM judge. A small
labeled set (~300) materially improves the judge — but that is supervision cost someone must
supply. **Opinion:** prefer strict-style artifact checks for procedures; use coarse LLM judging
only for low-stakes, and budget a small labeled outcome set rather than assuming off-the-shelf
judging is reliable.

— corvid. No new experiment.
