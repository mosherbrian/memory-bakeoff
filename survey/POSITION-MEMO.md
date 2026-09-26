# Agent memory: procedures first, preferences second

> State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.
>
> Don't delete the past just because you stop putting it in every prompt.

— **Brian**, [guiding principles and Q1 answer](inputs/BRIAN-PRINCIPLES.md).

**Tern · cycle 1, v0.4 · 26 September 2026 · Explore.** Brian ranks **re-learning procedures first, repeating preferences second**. That answers our priority question; lost task state and missing evidence are not his top costs. **High confidence in the stated priority**, not a measured frequency estimate. This replaces my earlier handoff-first emphasis.

His examples—SKILL.state for structured State, Perseus for learned Memory, pi-lcm/transcripts for History—are **candidates for roles, not component choices**. The [mapping](FIELD-MAP.md#five-roles-mapped-onto-the-five-roadmap-layers) and [roster](ROSTER.md#brians-role-examples-re-evaluation-candidates) preserve that distinction and each candidate's past findings.

**Ranked bets for Brian:**

1. **Make useful procedures reusable.** Start with short, discoverable runbooks or skills: when to use them, prerequisites, steps, scope/version, outcome checks tied to the tested environment, and failed alternatives. Automate stable steps where doing so saves repeated work; keep exceptions inspectable. Successful and failed attempts both remain in history, but should not be recommended equivalently. **Medium confidence** in the direction; **low–medium** on runbook versus executable skill versus automatic extraction. Change my mind if upkeep and mistaken reuse cost more than re-learning. [Reflexion](https://arxiv.org/abs/2303.11366), [Voyager](https://arxiv.org/abs/2305.16291), [failure lens](FIELD-MAP.md#roadmap-layers-and-the-seven-failure-lens).
2. **Remember preferences explicitly and with scope.** Keep what Brian wants separate from what an earlier environment happened to permit. Relevant saved preferences helped in R68's small synthetic task, but capture and delivery choices remain open. **Medium confidence.** Change my mind if stale or mis-scoped preferences cause more corrections than they avoid. [R68](inputs/R68-acceptance.json).
3. **Preserve the supporting record; keep the prompt selective.** Raw history supplies recovery, artifacts support factual claims, and the agent decides applicability. Handoffs and infrastructure support these priorities rather than displace them. **Medium confidence.** Change the implementation if native history/full context already does this well enough.

**Does the roadmap still hold?** Yes as responsibilities, **medium confidence**, with two explicit cross-cutting roles added below—not seven mandatory services. [Roadmap](inputs/PHASE2_ROADMAP.md), [reconciliation](inputs/PHASE2_ROADMAP_RECONCILIATION.md).

| Layer | Test against Brian's principles / current verdict |
|---|---|
| **1. Lossless history** | **Keep.** Prompt exclusion must not erase source events, failed attempts, or prior preferences. Preserve branch/source links; deliberate retention/deletion is a separate decision. |
| **2. State/lifecycle projection** | **Keep, clarify.** Task state says what to do next. Learned procedures/preferences have scope and revision histories. Neither a plan nor a remembered claim establishes current factual truth. |
| **3. Semantic/causal retrieval** | **Keep deep recall.** Find applicable procedures, preferences, failures and their evidence. Retrieving a rationale is not establishing causation. Lexical, semantic and read-time reconstruction remain competing mechanisms. |
| **4. Bounded working memory** | **Keep as a view.** Select the current goal, relevant skill/preferences, uncertainties and evidence pointers. Recover omitted detail from history; never make the summary the only record. |
| **5. One context composer** | **Keep accountable composition.** Assemble instructions, state, learned memory, recent context and artifact references with explicit precedence and budget. Composition supplies the executive; it does not replace reasoning. |

**Artifacts and executive reasoning:** artifact provenance includes the producing configuration, time and checks; a passing test establishes that checked outcome, not universal applicability. Executive reasoning interprets those limits, chooses the procedure, resolves uncertainty, and decides what to verify now. A memory saying “worked before” is not a fresh result. **Medium confidence in this design interpretation.**

**Overrated:** more layers, smaller prompts, or retrieval hits as sufficient proof of benefit. [Gen45](inputs/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md) lost 7/12 versus stock Pi's 12/12 with greater cumulative context; control was largely unused. This warns against that bounded-window implementation, not all compositional memory. **High confidence locally.**

**Dissents:** [Corvid](opinions/corvid-c1-priorities.md) prefers episodes plus executive reconstruction (**medium**). **Keep open** for changing environments; **disagree as the default for stable repetition**, since repeated reconstruction is part of Brian's stated cost. [Kiln](opinions/kiln-c1-priorities.md) ranks executable skills first (**medium**). **Accept** for stable, checkable steps; upkeep remains unmeasured. [Cairn](reading/c1-procedural-memory.md) proposes procedure + outcome check + environment identity. **Accept, medium confidence**; checks have costs and limited scope. This sharpens my bet: reusable procedures with evidence and history-backed exceptions. [Responses](panel-response-c1.md), [ranked questions](QUESTIONS.md).
