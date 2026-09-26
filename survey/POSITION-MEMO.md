# Agent memory: enforce what can be checked, preserve what requires judgment

**Current decision:** [small reflector, fleet pilot, continuous delivery](RECOMMENDED-DESIGN.md). Stage0 complete; the fleet is the subject. Baseline existing logs now, prepare the approval-dependent Letta trial, review/test shipped reflector pieces and prepare local Laya data. Quiet support mode is withdrawn; keep working through the structured queue. Historical personal-pilot/support-only passages below are superseded.


> State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.
>
> Don't delete the past just because you stop putting it in every prompt.

— **Brian**, [principles](inputs/BRIAN-PRINCIPLES.md).

**Tern · sponsor reset during cycle68 ·26 September2026.** Brian's costs are **re-learning procedures first, repeating preferences second**. **Agent-owned upkeep is the existing, failing baseline—not our proposed improvement.** Brian/Claude report substantial capture already, index truncation excluding109/301entries, and repeated mistakes after lessons were saved. Those are sponsor observations, not a survey incidence audit. The earlier recommendation of a small agent-maintained guidance store did not answer what changes when the actor fails to use it; that recommendation is superseded as the headline. [Exact sponsor input](inputs/BRIAN-PRINCIPLES.md#high-priority-sponsor-correction-dependable-improvement-over-existing-upkeep).

**Constraint on every operational recommendation:** present one characterizable design with named components, each component's contract, an operational owner and tests. Prefer an existing product or one extension point over accumulated scripts and patches. **This shapes the recommendation; it is not a review gate for each step.** The decision page is delivered26September; stage0 is complete, and the next build is Claude’s bounded reflector. Proposed tests belong in that design, not as prerequisites to choosing it. The priorities below are requirements to evaluate, not separate implementation tickets. [Sponsor constraint](inputs/BRIAN-PRINCIPLES.md#high-priority-sponsor-correction-dependable-improvement-over-existing-upkeep).

**Three revised priorities**

1. **Move checkable requirements into the execution path.** Investigate hooks, constrained tools and consumed defaults that enforce a scoped requirement even when the actor ignores a reminder. An optional helper or another instruction is insufficient. Separate a blocked forbidden action, a default that can be overridden, and a judgment that still belongs to an agent. State host-interception evidence and make remaining coverage/failure checks explicit in the proposed pilot. Preserve useful rationale and exceptions; no universal conversion of preferences into string-matching rules. This is the strongest candidate for improving application independently of diligence, not a proven fleet-wide fix.
2. **Repair delivery as a host mechanism.** Prioritize the reported truncation: mechanically check the actual loaded index against the host's limit, retain overflow outside the prompt, and make exclusion visible. Assess host-triggered relevance injection for detailed guidance instead of relying solely on the actor choosing to open it. Selection remains fallible and loaded guidance may still be ignored. A byte/line/token check can establish only its own delivery invariant; no guessed universal cap or retrieval-equals-compliance claim.
3. **Run capture and outcome measurement independently of the actor.** Evaluate scheduled transcript mining for missed corrections/repeats, and automatic weekly recurrence counts. Existing pi-reflect/ReMe/Letta mechanisms are candidates for triggers, not proof of semantic quality or reduced mistakes. Capture mostly works according to Brian, so additional notes do not justify this work by themselves. A useful measure must distinguish repeated same-scope correction from a new direction, quotation or changed context, and expose missing data. Silence is not compliance. No new rating form or record-review duty for Brian.

**What remains infrastructure:** editable scoped guidance, authoritative directions and recoverable history still support these improvements. They are not the improvement over today's files. Ask of every proposal: **if the acting agent ignores the saved lesson, what concretely changes?** [Mechanism/evidence map](DEPENDABILITY-IMPROVEMENTS.md), [cycle69 commission](panel-cycle69.md). Medium confidence in this ordering; no product winner or implementation authorized.

**What to buy or extend:** compare a coherent product—ReMe, Hindsight, Pi reflection, claude-mem—with a single existing host mechanism extended in one place, such as hooks configuration, a cc-safety-net rulebook or Pi extensions. Judge contract coverage, ownership, tests, host boundaries, failure visibility and total custom glue as well as capability and cost. The product label does not prove coherence; a small composition can qualify if its full behavior is characterizable. Existing cards establish only partial product/host evidence, not a selected design. No collection of individually useful scripts earns a build recommendation merely by covering the four rows. [Design requirements and candidate comparison](DEPENDABILITY-IMPROVEMENTS.md).

**The roadmap still holds as responsibilities, not necessarily five services** (medium confidence):

| Layer | Keep this responsibility |
|---|---|
| Lossless history | Recover source events, failures and corrections after prompt exclusion. |
| State/lifecycle projection | Separate next-action state from learned guidance; preserve scope and revision. |
| Semantic/causal retrieval | Find evidence and counterexamples; retrieved rationale is not causal proof. |
| Bounded working memory | Fit the view to the operation; preserve needed evidence and recoverable history. |
| One context composer | Make precedence, ordering and budgeting accountable; delivered evidence must remain usable. |

Artifacts and executive reasoning cross every layer. SKILL.state, Perseus and pi-lcm remain role candidates, not settled components. [Role/layer map](FIELD-MAP.md#five-roles-mapped-onto-the-five-roadmap-layers).

**Dissents to resolve next:** can enforcement cover the recurring mistakes without excessive false blocks; does independent transcript mining recover important misses rather than merely add notes; can relevance injection improve application; and can weekly recurrence estimates detect real change? The prior read-time versus maintained-view disagreement remains secondary. Historical caution against a standing audit must not veto Brian's newly proposed automatic outcome measurement; its accuracy and cost now need assessment. [Cycle69](panel-cycle69.md).

**Cycle73 dissent, retained:** Corvid favors staying on current hosts because runtime migration and memory ownership changes may outweigh independently triggered upkeep. Tern keeps Letta optional: its protected files, bounds and harness refresh also matter, and a coherent replacement is not inherently patchwork. Demonstrating correction delivery without foreground upkeep would establish a path, not obedience; later appropriate action remains a separate pilot check. [Disposition](panel-response-c73.md).

**Cycle79 dissent, retained:** Corvid prefers the supplied Perseus compiler as an optional delivery pilot before Letta migration: one source and native host outputs remove manual view duplication without changing runtimes. Tern accepts that operation-level advantage, but publication is not active-host refresh and the separate strict analyzer does not gate ordinary render/watch. Lower total burden remains unmeasured; Letta addresses independent upkeep as well as delivery. The current optional recommendation is unchanged pending the already-commissioned consumer-path evidence, not another review gate. [Partial disposition](panel-response-c79.md).

**Cycle80 pilot-order dissent:** Kiln recommends a characterized guard-plus-Perseus design; Corvid recommends compiler delivery first. Tern retains one-project guard first: encoded interception does not depend on the saved lesson loading, while Perseus's supplied prompt refresh still lacks an enforced recipient-size bound. A combined design is not inherently patchwork; its extra scope is the objection. Compiler delivery remains a concrete alternative, not dismissed for missing outcome measurements. [Disposition](panel-response-c80.md).

**Overrated:** treating stored, retrieved or versioned guidance as demonstrated useful learning. **Open frontier:** durable benefit under changing conditions with less user effort. Existing benchmarks and our narrow local results do not yet choose the upkeep/delivery winner.


**Cycle67 practical update — cheap classification:** use deterministic rules where exact identity/property tests suffice; typed semantic screening remains a candidate for narrow high-volume decisions with fallback. One authorized supplied-pair, zero-shot base Laya test failed:27/46 versus33/46 always-no and46/46 keyword rule, while taking159ms median. This rejects the tested supersession prompt/service configuration, not all Laya/Jev or semantic classifiers. Probabilities do not confer authority to retire a record. [Report](probes/laya-supersession-20260926/RESULTS.md). Ranked bets unchanged; no classifier added.

**Cycle80 Laya correction:** Claude identifies the tested serving configuration as shipped base/zero-shot; exact artifact and temperatures were not logged. Fine-tuned local correction filtering remains an option-B candidate, not a failed experiment or adopted component. [Design](systems/laya-correction-prefilter.md).
