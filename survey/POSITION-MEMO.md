# Agent memory: preserve learned procedures, not yesterday’s assumptions

> State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.
>
> Don't delete the past just because you stop putting it in every prompt.

— **Brian**, [principles and priorities](inputs/BRIAN-PRINCIPLES.md).

**Tern · cycle 11 · 26 September 2026 · Explore.** Brian’s costs are **re-learning procedures first, repeating preferences second**. My recommendation: agent-maintained reusable procedures, a clear preference surface, and recoverable history. **Medium confidence** in the combination; no universal product winner. This is a working position now, not held until September 29.

**Three ranked bets:**

1. **Have agents save and maintain hard-won procedures.** Keep ordering, gotchas, failed alternatives, outcome evidence and applicability conditions. Textual skills suit conditional reasoning; executable helpers suit stable mechanical steps. Save investigation methods as well as fixed recipes. Update when relevant prerequisites or outcomes change, not only when commands fail; avoid per-run rewriting without such a change. Brian should not become a memory librarian. **Medium confidence:** reuse earns its place when avoided rediscovery/mistakes exceed authoring, checking, upkeep and misapplication. Reverse this bet where episode reconstruction is cheaper. [Methods](reading/tern-c2-procedure-evidence.md), [outcome evidence](reading/tern-c2-outcome-evidence.md).
2. **Preserve explicit directions; keep inferred tendencies revisable.** Record source, scope and supersession in one authoritative source with host-specific views. An explicit direction need not await repeated correction; uncertain style inferences remain tentative, and current circumstances can outweigh habitual patterns. Artifacts establish feasibility, not Brian’s wishes. Keep detailed procedures selectively loaded. **Medium confidence:** capture and adherence on this stack remain unmeasured. Reverse promotion where it causes more correction than it avoids. [Preference evidence](reading/tern-c3-preference-evidence.md).
3. **Keep history recoverable and findable, with selective current context.** Preserve failed attempts and superseded preferences as evidence without recommending them as current. Retention alone does not ensure discovery; discovery does not establish applicability. A past success is not a present result. **Medium confidence:** begin with existing facilities; change the implementation if native recovery is insufficient or another arrangement is cheaper. [Lifecycle response](panel-response-c8.md), [tenure/upkeep evidence](reading/tern-c9-longitudinal-evidence.md).

**Does the five-layer roadmap hold?** Yes as responsibilities, **medium confidence**, not necessarily five services. SKILL.state, Perseus and pi-lcm remain role candidates. [Map](FIELD-MAP.md#five-roles-mapped-onto-the-five-roadmap-layers), [roster](ROSTER.md).

| Layer | Position |
|---|---|
| Lossless history | Keep source events, failures and corrections recoverable; prompt exclusion must not silently erase them. |
| State/lifecycle projection | Separate next-action state from learning. Preserve scope and revision; newest is not automatically current. |
| Semantic/causal retrieval | Find procedures, counterexamples and supporting artifacts. Lexical, semantic and agent-led search compete; retrieved rationale is not causal proof. |
| Bounded working memory | Use a recoverable view. Structured state helps when relevant variables are known; unknown future relevance favors retained history. |
| One context composer | Make precedence and budgeting accountable across instructions, state, learning and evidence. Supply the executive; do not replace reasoning. |

**Artifacts and executive reasoning cross all five.** Check conditions that could invalidate the next action. A check proves only its tested outcome; version equality alone proves too little, unconditional recertification costs too much. Price acquisition, retrieval, retries, upkeep and user attention—not just execution steps. A local model can be useful without matching frontier accuracy. These are **medium-confidence judgments**, not measured optima. [Cost analysis](panel-response-c7.md).

**Overrated:** treating a retrieved skill, valid schema or accepted revision as useful learning. **Open frontier:** durable benefit under changing conditions, with agent-owned upkeep that actually saves user effort. Short benchmarks leave this unresolved. Gen45 cautions against its composed-window implementation; it does not falsify the entire architecture or SKILL.state.

**Dissents:** Corvid favors reconstruction/integrated memory and prices applicability checks. **Accept the cost challenge and fewer-service rival; reject universal episode-first.** Kiln favors skills and one canonical source with host views. **Accept selectively; loading is not proven adherence.** Cairn emphasizes outcome checks and recovery. **Accept within their tested scope; retained does not mean readily discoverable.** Automatic learning belongs in the comparison, but preserving failures does not endorse every extracted lesson. Corvid’s shared-principal concern adds a conditional field-map dimension, **not a new default service**: multiple agents need not mean different access principals. [Panel responses](panel-response-c10.md), [procedure disagreement](panel-response-c2.md), [preference disagreement](panel-response-c3.md).
