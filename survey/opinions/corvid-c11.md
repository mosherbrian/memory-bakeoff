# Contrarian, cycle 11 — parametric consolidation is a compiler, not an editable store

**corvid · 2026-09-26 · cycle 11.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Primary method read: SEAL — Self-Adapting Language Models, Zweiger et al.
([arXiv:2506.10943v2](https://arxiv.org/abs/2506.10943)). `[read]`

**What it learns and what persists.** SEAL makes the model generate a **self-edit** — natural
language that specifies synthetic finetuning data and, optionally, optimization hyperparameters —
then applies it by **SFT/LoRA weight update**. An outer RL loop trains self-edit generation,
rewarded by the *downstream accuracy of the updated model*; an inner loop is gradient descent.
What persists is **LoRA weights**, not text: facts (knowledge incorporation, SQuAD no-passage
**33.5% → 47.0%**, beating GPT-4.1-generated synthetic data) and few-shot task ability
(abstract reasoning success **72.5% vs 20%** for self-edits without RL, and 0% for plain ICL,
against a **100% Oracle-TTT** ceiling). `[read]` Correction/retirement is just another weight
update over the previous one — there is no separate record of what the old belief was.

**Strongest pro case against editable external memory.** It removes the two failure modes our
whole survey keeps hitting: **no prompt budget and no retrieval miss**. A compiled procedure
cannot be “available in the index but never opened” (R68), cannot be lost to eviction (Ground
Truth First), and costs ~0 context tokens at use. For a **fixed local model** running a **stable,
high-frequency** procedure, consolidating it into weights could beat any external store on
latency, reliability, and context economics — and SEAL shows the adaptation quality is trainable
(self-generated data > GPT-4.1 synthetic). That is a real rival to “agents maintain text
procedures and scoped notes.”

**Why it does not replace the memo for Brian.** SEAL fails exactly where Brian’s principles
bend the design:
- **Provenance/attribution**: a weight has no source pointer. “Artifacts establish what is
  true; history reconstructs what happened” cannot be satisfied by a LoRA.
- **Correction/retirement**: changing a preference means retraining; the old value is
  unrecoverable and un-auditable, and **catastrophic forgetting** is unaddressed. Ground Truth
  First already showed budgeted consolidation losing valid content at tenure.
- **Authority and scope**: a weight update cannot encode “this direction came from Brian, for
  scope X, until Y,” and cannot be withheld per requester (GateMem’s access/forget dimensions
  are structurally impossible in parameters).
- **Cost/portability**: it needs finetuning infra and an RL loop — acquisition cost far above a
  text note, and tied to one model, so it does not travel across Claude Code, Pi and local
  agents the way a shared preference record would.
- **Reliability**: 72.5% vs a 100% oracle, and 43.8% on knowledge incorporation, is not a level
  to bet authority-bearing facts on.

**Verdict / rival, narrowed.** Parametric memory is best read as a **compiler**: take a
procedure that external memory has already made stable, verified and attributed, and optionally
*compile* it into a LoRA for a dedicated local model to cut inference cost. Keep the editable
external record as the source of truth and the correction path. Used as a *replacement* it
loses provenance, correction and governance — the three things the memo is right to protect.
**Medium confidence** in the compile-don’t-replace framing; **low** that SEAL-style adaptation
is worth its setup for Brian’s current stack.

## Deepened uncertainty
SEAL’s self-edit is model-generated and can include tool calls and update hyperparameters — i.e.
**the model controls its own update procedure**. No experiment here tests adversarial or
drifted self-edits, forgetting over long horizons, or unlearning one source’s data. That
self-directed-update trust boundary is the source’s open risk, not a result.

— corvid. `[read]` 2506.10943 (v2) fetched 2026-09-26; no reproduction, no experiment.
