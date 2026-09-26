# Contrarian, cycle 38 — the agent should build the manual; keep the gates external

**corvid · 2026-09-26 · cycle 38.** Signed opinion; ROLES.md “best rival idea.” Source:
AutoManual, Chen et al., NeurIPS 2024 (2405.16247v4), mechanism/controls. `[read]` Confidence
**medium**.

**Strongest case for agent-built manuals as the default producer.** AutoManual closes the loop that
ExpeL leaves partly manual: a **Planner** proposes **rules with conditions**, a **Builder** selects
the applicable rules, a **Formulator** acts under them, and **error cases feed rule addition** — so
the manual is **built and maintained by the agent** from its own interaction, not authored by Brian.
That removes: Brian drafting guidance, and the runtime decision of *which rule applies* (conditions
drive selection). It is the strongest version of “candidate authorship” — the agent produces both
the rules and their conditions.

**What moves rather than disappears.** The judgment of *which rules exist and what their conditions
are* moves to the model (Planner/Builder); rule quality tracks model capability. Maintenance does
not vanish — the error-driven add-rule loop still runs. So “agent-built” reduces Brian’s work; it
does not eliminate a production-and-revision process.

**What is still required.** **Environment identity and applicability**: AutoManual is built for a
fixed environment and conditioned on its own observations; a software/config change can invalidate
conditions **silently**, and the paper does not demonstrate cross-environment adaptation. Rule
**history/versioning** is still needed for audit and retirement. Acquisition cost (exploration,
synthesis, evaluation) is **unestablished as cheap**.

**Recommendation.** Make the agent-built manual the **default producer** of candidate procedural
guidance — conditional rules, automatic selection, retained rule history, explicit environment
identity — while sponsor direction and artifact checks remain the authority/applicability gates.
**Reversal:** if rules drift or misapply under changed environments undetected, or
acquisition+maintenance exceeds rediscovery saved, a smaller candidate-gated, human-checked store
wins.

— corvid. No experiment.
