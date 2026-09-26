# Contrarian, cycle 44 — code can perceive; choose the medium per step

**corvid · 2026-09-26 · cycle 44.** Signed opinion; ROLES.md “best rival idea.” Source: Code as
Policies, Liang et al. (2209.07753v4), methods/controls. `[read]` Confidence **medium**.

**Strongest case for reactive generated code over prose procedures.** Code as Policies generates
**policy code that calls perception APIs, observes fresh state, and branches/loops reactively** —
directly countering the assumption that code is a fixed blind sequence and that prose is the
better medium for conditional reasoning. For a **mechanical procedure with observable state**, code
removes the per-run re-derivation of control logic (it runs deterministically) *and* the
interpretation burden for conditions the APIs expose; unlike prose, it is testable by execution.
Carry c43: a running function is testable, not automatically correct; a tool user still needs
argument-translation competence; bad code is not invariably worse than bad prose.

**What remains supplied.** The **perception/action APIs** (the environment interface), the
demonstrations, and the model’s coding competence. Code can only branch on what its APIs expose —
observation availability is the binding constraint. `[read]`

**What persists — the key limit.** Code as Policies generates a **policy per instruction**; it is
**not a demonstrated accumulating memory system**. So reactive code is an **execution medium**, not
durable learning. The memo’s procedural question still needs storage, selection and applicability
(AWM/LATM-style), plus a use-time check for changed prerequisites.

**Recommendation.** Pick the medium per step: reactive/mechanical control with observable state →
generated code/tool (execution-checked); judgment or unobservable conditions → prose guidance; store
the artifact with applicability metadata. **Reversal:** if the needed observations can’t be exposed
as APIs, code cannot branch on them and judgment/prose remains.

— corvid. No experiment.
