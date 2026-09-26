# Agent memory: preserve learned procedures, not yesterday's assumptions

> State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.
>
> Don't delete the past just because you stop putting it in every prompt.

— **Brian**, [principles and priorities](inputs/BRIAN-PRINCIPLES.md).

**Tern · cycle 2 · 26 September 2026 · Explore.** Brian's costs are **re-learning procedures first, repeating preferences second**. My recommendation is a small collection of reusable procedures, a clear preference surface, and recoverable source history. **Medium confidence** in this combination; no universal product winner. This is ready as a working position now, not held until September 29.

**Ranked bets for Brian:**

1. **Save the hard-won part of a procedure.** Keep non-obvious ordering, gotchas, failed alternatives and outcome evidence; state when the recipe applies and when to stop. Use a textual skill/runbook for conditional reasoning and an executable helper for stable mechanical steps. Reuse investigation methods as well as task solutions: a reliable way to find the right configuration can outlive a particular configuration. Favor reuse when avoided rediscovery and mistakes exceed authoring, checking, upkeep and misapplication costs. **Medium confidence.** Change my mind if maintained procedures cost more than reconstructing episodes. [Methods note](reading/tern-c2-procedure-evidence.md), [outcome evidence](reading/tern-c2-outcome-evidence.md).
2. **Promote repeated preferences into explicit scoped instructions.** Separate what Brian wants from what a past environment allowed. Record source, scope and supersession; automatic notes can capture candidates, but important recurring directions should not depend solely on incidental recall. Check preference authority/currency, not “truth” against a file. Keep detailed procedures selectively loaded. **Medium confidence**; capture quality and adherence on this stack remain unmeasured. Change my mind if promotion/upkeep causes more correction than it avoids. [Official memory mechanisms](https://code.claude.com/docs/en/memory), [R68's narrow positive result](inputs/R68-acceptance.json).
3. **Keep history recoverable and the working prompt selective.** Preserve failed attempts and old preferences as evidence, without presenting them as current recommendations. Use history for exceptions and changing conditions; a past success is not a present result. **Medium confidence.** Change the implementation if native history already supplies adequate recovery cheaply. Do not equate retrieval ranking failures with deleted history.

**Does the five-layer roadmap still hold?** Yes as responsibilities, **medium confidence**; separate services must earn their cost. Brian's SKILL.state, Perseus and pi-lcm examples are role candidates, not chosen components. [Mapping](FIELD-MAP.md#five-roles-mapped-onto-the-five-roadmap-layers), [roster](ROSTER.md#brians-role-examples-re-evaluation-candidates).

| Layer | Current position |
|---|---|
| **Lossless history** | Keep source events, failed attempts and corrections recoverable. Prompt exclusion must not silently erase them. |
| **State/lifecycle projection** | Separate next-action state from learned procedures/preferences. Track scope, revision and status; “current” is not simply “most recently written.” |
| **Semantic/causal retrieval** | Retrieve procedures, counterexamples and supporting evidence. Lexical search, embeddings and agent-led investigation compete; a retrieved rationale is not causal proof. |
| **Bounded working memory** | Keep as a recoverable view. Structured state can help where relevant variables are known; unknown future relevance argues for retained history. |
| **One context composer** | Keep accountable precedence and budgeting across instructions, state, learned memory and evidence. It supplies the executive rather than replacing reasoning. |

**Artifacts and executive reasoning cross these layers.** A check establishes only its tested outcome and conditions. Recheck what could invalidate the next action; do not rebuild the whole environment merely to certify a remembered recipe. Version equality alone proves too little; unconditional recertification costs too much. This selective-checking policy is **my medium-confidence judgment**, not a measured optimum.

**Overrated:** treating a retrieved skill, a passing schema check, or an accepted revision as proof of useful learning. New procedural studies supply outcome evidence but retain discovery, transfer and upkeep gaps. Gen45's negative composed-window result cautions against that implementation; it does not falsify SKILL.state or the whole architecture. [Evidence and limits](reading/tern-c2-outcome-evidence.md), [Gen45](inputs/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md).

**Dissents:** [Corvid](opinions/corvid-c2.md) prices checking and favors reconstruction. **Accept the cost challenge; reject** costless or timeless reconstruction. Keep his rival for unfamiliar conditions. [Kiln](opinions/kiln-c2.md) favors executable skills. **Accept selectively**, not for every procedure. [Cairn](reading/c1-procedural-memory.md) adds outcome checks and environment identity. **Accept**, with limited scope and nonzero cost. Mechanism choice remains open; [responses](panel-response-c2.md) preserve disagreements.
