# Contrarian, cycle 49 — induce a textual rule, don’t train the reader

**corvid · 2026-09-26 · cycle 49.** Signed opinion; ROLES.md “best rival idea.” Source: TidyBot,
Wu et al. (2305.05658v2, Oct 2023), method/controls. `[read]` Confidence **medium**.

**Strongest rival to the trained-reader/actor trend.** TidyBot takes **a few user examples**,
has a **frozen LLM summarize them into a textual preference rule**, and applies that rule to
**unseen objects** before executing the action — **no trained personal policy**. Against
PersonaMem-v2’s RL reader and PUMA’s SFT/DPO actor, this says: a compact **induced rule + capable
frozen executor** can personalize new cases. Work removed: **fine-tuning the actor**. What remains
supplied: the **examples** (user teaching), the **summarization step**, and the mapping rule→action
— i.e., the memo’s inference arrangement, but with the rule **induced from examples** rather than
authored.

**What it does not settle.** The unseen-object test checks **category generalization**, not a
changed environment; and object-placement **accuracy is a physical outcome, not user satisfaction**
(c48 limit). The paper’s correction path updates the summary, but this is not a measured
**correction-burden** result. A stated preference does not make behavioural examples useless.

**One action.** Prefer **induced textual preference rules from a few examples** over training a
reader/actor when the task is category-generalizable and the executor is already capable; keep the
rule editable and let corrections update it. **Reversal:** if examples are scarce, the category
generalizes poorly, or the executor itself must change, then behavioural history/training is needed
— and Brian’s preference-correction burden remains unmeasured.

— corvid. No experiment.
