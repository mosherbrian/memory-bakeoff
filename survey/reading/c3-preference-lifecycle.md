# Reading sweep — preference lifecycle: change, scope, correction

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 3.**
Signed opinion, not an audit. Questions (Tern): **what is stored, how is update authority
decided, and what does the evaluation actually measure** — plus the contrast that decides
Brian's Q9: **explicit reversal** (the user says "not anymore") versus **latent-style
inference** (the system notices and adapts). Cycle-2 finding carried in: no located lifecycle
design represents "applicable now" as a first-class object; this cycle asks the same of
preferences — is a *changed* preference a new fact, a rewritten profile, or a scoped overlay?

Provenance key: `[read]` = full text at source today; `[card]` = our cards; `[ours]` = our
measurement.

**PARTIAL — written before reading, per commission.**

## Provisional opinion (before source reads)

From what we already hold: R68 showed relevant saved preferences *helped* a small synthetic
task `[ours:R68]`, and cycle 2's Supersede read showed a *rewritten* store loses currency even
on a frontier model `[read:c2]`. That predicts the safe preference shape is
**append-with-scope-and-date + reversal as an explicit event**, not profile rewriting. The open
risk is the opposite failure: preferences that never die because nothing is authorized to
reverse them. The question for this cycle is whether any primary source actually *decides*
update authority — user-only, agent-inferred, or hybrid — and measures the two error directions
(obeying a stale preference vs. obeying a poisoned "new" one) separately.

## Source slots (being filled now)

**1. CAPTURE: Disentangling Preference Drift from Memory Poisoning in Personalized LLM Agents**
(arXiv:2609.02265). The title is our exact question: when a stored preference changes, was that
a legitimate drift or a corrupt write? Update authority is the mechanism under test.

**2. TRUSTMEM: Learning Trustworthy Memory Consolidation for LLM Agents** (arXiv:2606.25161).
Consolidation = who/what decides which memories survive an update. Read for the authority
mechanism and the eval surface.

## Gaps kept as unknown

- Whether either benchmark measures *scope* (preference true for project X, not host Y) or only
  global user state.
- Whether "explicit reversal" is scored separately from "inferred change" in either eval.
- Original PersonaMem-line sources not located on today's search surface; not needed if the two
  slots above carry the mechanism.

— cairn. Verdicts per source appended as reads land.