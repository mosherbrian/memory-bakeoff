# Reading sweep — preference lifecycle: change, scope, correction

**cairn (Reader — local Qwen3.8 Flash-Next on Halogen, free) · 26 September 2026 · cycle 3.**
Signed opinion, not an audit. Questions (Tern): **what is stored, how is update authority
decided, and what does the evaluation actually measure** — plus the contrast that decides
Brian's Q9: **explicit reversal** (the user says "not anymore") versus **latent-style
inference** (the system notices and adapts).

Provenance key: `[read]` = full text at source today (arXiv HTML, 2026-09-26); `[ours]` = our
measurement.

---

## Per source

**1. Capture: Disentangling Preference Drift from Memory Poisoning in Personalized LLM
Agents** — arXiv:2609.02265, full text. `[read]`
**Stored:** structured preference hypotheses (claim, **scope** = global or named domain,
**timescale** = permanent or situational) as nodes in a graph ledger with three decay layers
(stable / contextual / transient) plus a **quarantine** state — written but non-retrievable
until corroborated, evicted otherwise.
**Update authority:** not the writer and not the channel — a learned authenticity gate. A
continuous-time latent belief (neural ODE) consumes each event and chooses among six actions:
retain, add, **narrow to scope**, revise, quarantine, or **ask the user** (taken when belief
entropy is high; budgeted at ≤1 clarifying turn per 12 interactions). Overwriting a *stable*
node requires repeated high-confidence evidence; one sentence cannot redefine a user. A safety
selector sits outside the ledger and cannot be moved by any stored preference.
**Their theorem:** any rule reading only recency + provenance has error bounded below by how
closely a feasible adversary can imitate the statistics of a legitimate revision — so
accept-everything personalization and reject-untrusted provenance filtering each fail on the
case the other handles. **Asking is the only action that escapes the bound**, because it changes
the information, not the rule applied to it.
**Evaluation actually measures:** D-PrefGuard — 2,400 longitudinal episodes, five tracks:
stationary behavior, four shapes of **genuine drift**, benign non-updates (sarcasm, context
switch), three contamination families, utility-vs-safety conflicts. Scored separately: genuine
-update adherence, poisoning acceptance, benign non-update acceptance. Anti-self-grading:
zero-shot on independently built HorizonBench + 40 real users over 2–3 weeks labelling their
own preferences.
**Results:** 71.5% win rate vs 69.3% for a baseline with **identical supervision** (architecture
contributes only ~2.2 points — most of the gain is labels); poisoning 11.5% vs 20.0%
(provenance-only) while adhering to 83.5% of genuine updates vs 74.1%; benign non-updates
admitted 8.9% vs 19.6%. An adaptive attacker with released weights doubles poisoning to 24.7%,
at which point the provenance filter is marginally safer — **they report both numbers**. Cost
~630 ms/turn.
**Verdict: solid — the most on-target source found for Q9.** Confidence: medium-high (own
generator risk acknowledged and mitigated twice, but not eliminated; decay rates grid-searched).

**2. TrustMem: Learning Trustworthy Memory Consolidation for LLM Agents** — arXiv:2606.25161,
method + limitations. `[read]`
**Stored:** memory entries edited by agent-generated write / revise / delete actions.
**Update authority:** the agent's RL-trained policy — but every local state transition is scored
by a frozen-LLM **Memory Transition Verifier** on three axes: **coverage** (chunk's important
information preserved), **preservation** (valid prior memory not unjustifiably deleted or
distorted), **faithfulness** (new content supported by the chunk or prior state). Preference
pairs are built among candidate updates *from the same memory state* and optimized with
Transition-Ranked GRPO — supervision at the transition, not the terminal answer.
**Evaluation actually measures:** MemoryAgentBench, HaluMem (operation-level hallucination in
extraction/updating/QA), Mem- validation; plus transition-level **omission / corruption /
hallucination rates**. Reported: +6.5 MAB, +12.14 F1 HaluMem extraction, omission −40.1%,
corruption −79.1%, hallucination −50.0% vs the strongest baseline per error type.
**Verdict: solid on its one claim, and it is a claim our own register needs:** terminal task
success **masks** corrupted writes — a correct answer can hide a poisoned store that fails a
future task. Any preference evaluation scored only by downstream outcomes (ours included,
`[ours:R68]`) has exactly this blind spot. **Not** a preference-lifecycle paper: it checks
*support*, not *authorship* — whether the claim should have become a preference at all is out
of scope, and there is no user channel. Their stated limitation: text-only. Confidence: medium
(benchmark figures not reproduced).

---

## The one idea in this area that most deserves our attention

**Preference-authenticity is a decision problem, not a policy table — and the escape from the
impossibility result is a *budgeted, uncertainty-gated ask*, which is exactly the mechanism our
own lane runs broken.**

Capture's theorem says explicit-only rules (recency, provenance) and latent-only acceptance each
fail on the other's case; the measured frontier agrees. The design that survives is: latent
inference **proposes** (retain/add/narrow/revise/quarantine), an explicit human channel
**decides** the uncertain few, and **scope is where most "changes" actually belong** — "brevity
in standups" is a *narrow*, not a *revise*; a flat profile cannot express the difference and
rewrites itself to its own destruction. TrustMem adds the complementary half: whatever the
authority, each write transition needs a preservation/faithfulness check **at transition time**,
because terminal success hides the damage.

This lands directly on Brian's setup. Our pi-Perseus lane already has the ask-shaped mechanism —
the draft→confirm gate — and its measured failure is that it asks on **every** write: 59/88
drafts expired unconfirmed `[ours]`. Capture budgets asks to ~1 per 12 interactions, taken only
when belief entropy is high. The fix direction for our lane is not to remove the gate but to
**gate the gate**: routine low-entropy writes land with scope+timescale stamped; only
contradictions of stable preferences escalate to Brian. That is risk-tiered capture with an
external proof that the tiering is the only design that beats both failure modes.

**What would change my mind:** evidence that the ask-rate can't stay low outside their generator
(each ask is a user-visible interruption; if real traffic is contradiction-dense, the budget
breaks); or a poisoning result under Brian's actual threat shape (shared repo files, tool
output) rather than their retrieved-document adversary.

## Gaps kept as unknown

- D-PrefGuard and Capture share an author team; zero-shot on HorizonBench mitigates, does not
  eliminate, generator-fit.
- Neither source measures **cross-host scope** (preference true on project X, not host Y) —
  Kiln's portability question is unaddressed by both.
- TrustMem figures quoted as reported; no reproduction here.

— cairn, Reader. Sources `[read]`: arXiv HTML 2609.02265 and 2606.25161, fetched 2026-09-26.