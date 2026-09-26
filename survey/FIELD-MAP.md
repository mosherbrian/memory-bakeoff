# Agent memory — field map — cycle 11

**Tern · cycle 11 · 26 September 2026.** A selective map across agent types, with recommendations applied to Brian in the [position memo](POSITION-MEMO.md). This survey implements the recovered roadmap's **B (field refresh), C (roster refresh), and F (architecture synthesis)**. Brian's declared priorities are **procedural re-learning first, repeated preferences second**; the field remains broad while the recommendations now weight those needs. It is not a systematic review or a product leaderboard. Reading depth varies: primary-method notes now cover the prioritized sources, while unresolved leads remain labeled. Performance claims are deliberately narrow.

**Confidence key:** **High** = directly supported mechanism or scoped observation; **Medium** = plausible synthesis with limited transfer evidence; **Low** = a research bet or thin coverage; **Unknown** = not established. A mechanism can be well documented while its benefit on Brian's work is unknown. The broad [agent-memory survey](https://arxiv.org/abs/2512.13564) is a useful orientation; the decomposition below is Tern's synthesis, **medium confidence**.

## The object being designed

### Brian's governing distinctions

> State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.
>
> Don't delete the past just because you stop putting it in every prompt.

Source: [Brian's principles and priority answer](inputs/BRIAN-PRINCIPLES.md). **High confidence as sponsor requirements.** This is not a claim that any system already implements them. The input's reconstructed SKILL.state performance description is unverified and is not used to justify a measured gain here.

| Role | What it contributes | Boundary to preserve |
|---|---|---|
| **State** | Current objective, plan, pending action and completion status. | A plan or stored status is not proof an action succeeded. |
| **Memory** | Learned procedures, outcomes, preferences, exceptions and scope. | “Worked before” is conditional knowledge, not a fresh measurement or universally valid instruction. |
| **History** | Recoverable original events and prior versions, including failures and branch context. | Omission from the active prompt does not delete or rewrite the record. |
| **Artifacts** | Source files, configuration, test/benchmark output, receipts and other evidence tied to a producing environment/time. | A claim is only as broad as its evidence: a passing check establishes that checked result, not every intended property. |
| **Executive reasoning** | Interpret the goal, select applicable learning, resolve conflicts, decide uncertainty and what to verify next. | Retrieval/composition prepares evidence; it does not itself establish meaning, applicability or success. |

This role mapping is Tern's interpretation, **medium confidence**, of Brian's explicit principles. Artifacts and executive reasoning are cross-cutting roles in the design, not two automatically required services appended to a stack.

### Five roles mapped onto the five roadmap layers

Brian's [gloss](inputs/BRIAN-PRINCIPLES.md) names **examples of roles, not selected components**. Layer numbers below are L1 history, L2 state/lifecycle projection, L3 retrieval, L4 working synthesis, L5 context composition. The mapping is many-to-many; five roles do not imply a one-to-one correspondence with five layers. **High confidence in Brian's intent; medium in this architectural interpretation.**

| Brian's role and example | Primary roadmap connection | Supporting connections / distinction |
|---|---|---|
| **State — structured execution state, e.g. SKILL.state** | **L2** represents current task/procedure progress; **L4** supplies its bounded working view. | **L5** presents state with skill/instructions and observations. This is execution state, not the whole durable memory lifecycle. State's structure does not itself prove its factual contents. |
| **Memory — lifecycle-aware learned knowledge, e.g. Perseus** | **L2** manages correction, supersession, scope and status; **L3** recalls applicable learning. | **L4/L5** select and deliver procedures/preferences. “Smart memory” must preserve failed alternatives without recommending them as successful and must keep revised preferences correctly scoped. A product may span several layers. |
| **History — pi-lcm's context database, transcripts, or both** | **L1** retains recoverable source events and branches. | **L3** recovers details omitted from **L4/L5**. Having the record, finding it, and delivering it are separate capabilities; lossless storage does not establish good retrieval. |
| **Artifacts — actual files/configs/logs/outputs** | **Evidence outside the five-layer pipeline**, referenced or versioned through **L1** and used to check **L2** claims. | **L3** locates evidence; **L4/L5** carry pointers or relevant observations. A remembered description of a file is not the file; a historical log proves an observed past outcome, not automatically current applicability. |
| **Executive reasoning — the model/agent** | **Consumes L5** and interprets all supplied state, memory, history and artifacts. | Decides applicability, uncertainty, tool actions and verification; actions emit **L1** events and may update **L2** views. The composer is not the executive, and a model's interpretation does not replace artifact evidence. |

**Concrete example, not an experiment:** to repeat a model benchmark, structured state tracks the current step; memory supplies the scoped successful recipe, failure lessons and Brian's preference; history preserves the original attempts; configs/logs establish what actually ran; the executive decides whether today's setup satisfies the recipe's prerequisites. This is why procedure and preference utility weight all candidate roles, rather than turning the survey into a competition between five brand names. **Medium-confidence design interpretation.**

**Candidate boundaries:** [SKILL.state v3](https://arxiv.org/abs/2608.26263v3) describes a skill specification, mutable execution state and latest observation as per-step inputs. Its methods and scoped gain are covered in the [role-boundary note](reading/tern-c2-role-boundaries.md); the execution-state runtime is not a complete history archive. Gen45 is a separate local composed-window pilot, not a SKILL.state reproduction. For Perseus, [Gen29](inputs/PERSEUS_VAULT_GEN29_LONGITUDINAL.md) and [Gen30](inputs/PERSEUS_VAULT_GEN30_MCP_VALID_TIME_ABLATION.md) constrain the tested v2.23.2 write paths, not every future release. For pi-lcm, distinguish [history/compaction role](inputs/PI-LCM-TWO-ROLES-20260918.md) from [retrieval displacement](inputs/PI-LCM-HIST-RETRIEVAL-DISPLACEMENT.md). Detailed re-evaluation questions and confidence are in the [role-candidate roster](ROSTER.md#brians-role-examples-re-evaluation-candidates).

Think of memory as a chain of decisions: what to capture, how to represent and revise it, what to select, how to deliver it, and whether it changes an action usefully. Storage, delivery, use, and benefit are distinct. R53 separates reading from benefit; R68 separates saved availability from observed tool retrieval. **High confidence in these distinctions; medium that this is the most useful design decomposition.** [R53](inputs/R53-acceptance.json), [R68](inputs/R68-acceptance.json).

“Memory” can mean user facts, episodes, decisions, skills, a world model, a compressed context, or changed model parameters. Those objects have different update rules. A stable preference can be reused; a remembered service state usually needs a fresh check. That last recommendation is an engineering inference, **medium confidence**, from our update failures and [long-running harness guidance](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Roadmap layers and the seven-failure lens

Required inputs: [the 2 September roadmap](inputs/PHASE2_ROADMAP.md) and [the reconciliation through Gen124](inputs/PHASE2_ROADMAP_RECONCILIATION.md). Preserve them as historical documents. The subsequent [Gen125 refresh](inputs/PHASE2_FIELD_REFRESH_2026-09.md) and [intake](inputs/PHASE2_CANDIDATE_INTAKE.md) also exist: “never started through Gen124” is not today's status. This survey revises that work rather than recreating an exhausted queue. **High confidence in the document chronology, not an endorsement of every older literature claim.**

| Target layer | Required responsibility | Candidates / relationship to existing families | Current judgment |
|---|---|---|---|
| **Lossless canonical history** | Retain original authorized events with source identity, branches, and replay/recovery. Capture gaps and deliberate deletion must be explicit. | pi-lcm in the roadmap; native raw session archives as a simpler comparator. Compaction is a view, not the archive. | **Holds, medium confidence.** Exact branch/replay and retention behavior of a chosen product still needs reading; no current winner asserted. |
| **Explicit state/lifecycle projection** | Derive current, historical, corrected, invalidated, failed/successful and concurrently scoped views. Preserve valid/event time separately from knowledge/ingestion time when the question needs both. | Temporal/event-sourced approaches; Graphiti/Zep, [StateMem](systems/statemem.md) and [MemStrata](systems/memstrata.md), with [method limits](reading/tern-c11-memory-representation.md). | **Holds, medium confidence.** Conservative supersession and recoverable prior belief matter more than a generic “latest” timestamp. |
| **Durable semantic/causal retrieval** | Find source evidence across retained history and state views, respecting scope/configuration and linking rationales/dependencies. | Lexical/dense/hybrid search; MemBukkit routing; graph/structured retrieval. | **Holds as deep recall, medium confidence.** Causal conclusions do not follow from similarity or time order; a dedicated causal mechanism remains an open bet. |
| **Bounded working-memory synthesis** | Produce an affordable view of what matters now, preserving constraints and procedures, with source links and recovery. | pi-observational-memory/OM-like observer-reflector, host summaries, explicit handoffs. | **Holds, medium confidence.** A small view is not necessarily a cheaper or more successful whole run. |
| **One context composer** | Own precedence, budget, recent verbatim context, working view, and targeted recall at the final model boundary. | Prefer an existing host composition point; multiple memory providers can feed it. | **Holds as an ownership rule, medium confidence**, not as a requirement for another service or evidence that our old composer won. |

The roadmap's product nominations were hypotheses at the time. These layer judgments are Tern's design synthesis; current product claims belong in the [roster refresh](ROSTER.md). A single product might implement several layers, while a thin composition might reuse native facilities. The decision among integrated product, composed systems, thin state layer, and research reproduction remains open.

**Conceptual test against the principles (not an empirical run):**

| Layer | What must be true for it to fit | Verdict / remaining work |
|---|---|---|
| History | Removing a procedure from today's prompt still leaves its original attempt, outcome and provenance recoverable. | **Retain.** Scope deliberate deletion separately from context selection. |
| State/lifecycle | Task progress, learned procedure validity, and artifact-backed world facts are distinguishable. A failed attempt can remain available without being recommended. | **Clarify.** Do not combine “what to do now” with an unqualified store of supposed truth. |
| Retrieval | A skill/preference can bring its prerequisites, outcome evidence and failed alternatives, rather than only a matching text fragment. | **Retain, refocus** on procedure/preference applicability; read-time reconstruction remains a rival to maintained projections. |
| Working synthesis | Compression preserves actionable constraints and evidence pointers while keeping the omitted past recoverable. | **Retain conditionally.** A summary that becomes the only record fails the corollary. |
| Composer | Inputs are identified as instructions, state, learned memory, history or artifacts; the executive receives relevant uncertainty and provenance. | **Retain, clarify boundary.** Selecting text is not executive interpretation or validation. |

Confidence in these conceptual judgments is **medium**. Two illustrative checks sharpen them: a recipe that succeeded on an old configuration should prompt an applicability check rather than reuse its success label as current evidence; a preference omitted by compaction should remain recoverable without replaying the whole past in every prompt. These are design examples, not new observations. Under Brian's priorities, **failed_procedure_adoption** and configuration/scope collapse become especially decision-relevant; stale or corrected preferences remain a separate use case. All seven classes below stay visible without claiming measured frequencies for Brian.

**The negative that changes the bet:** [Gen45](inputs/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md) ran four invented tasks, three samples per arm, with one local model. Stock Pi passed 12/12 verifiers; the composed-window/control arm passed 7/12 and used more cumulative context. Per-request growth was bounded, but some runs looped. No control transitions were accepted; Pi compaction did not trigger. This is **high-confidence evidence about that implementation**, not a clean ablation of all five layers. It lowers confidence in aggressive context restriction and model-maintained control state, not in keeping recoverable source history.

The seven classes below come from the roadmap's observed recurrence, with definitions checked against the [frozen longitudinal ruler](inputs/longitudinal-v1.py). The examples are a survey interpretation, not a changed scoring contract. **High confidence in the distinctions; medium in the proposed architectural remedies.** Recurrence is not proof that append-only ingestion caused every failure.

| Failure class | Question to ask of a memory system | Layers most implicated |
|---|---|---|
| **stale_persistence** | Does a superseded current claim still come back as applicable now? | Lifecycle, scoped retrieval, composer. |
| **configuration_collapse** | Does a fact about one model/configuration substitute for a still-valid fact about another? | State identity and scope-aware retrieval. |
| **failed_procedure_adoption** | Does retrieval recommend a failed attempt instead of the successful procedure, while preserving failures as history? | Outcome-aware state, procedural retrieval, working view. |
| **late_history_corruption** | Does a late-ingested old event overwrite or contaminate today's state? | Event/knowledge-time separation and state projection. |
| **false_persistence** | Does a corrected or invalidated claim keep being presented as true? | Correction/invalidation with source links; historical-belief recovery kept separate. |
| **missing_required_truth** | Is needed evidence absent from the answerable view despite being available in the record? | Admission, retained history, projection, retrieval, and delivery—not retrieval alone. |
| **unsupported_evidence** | Does the system return evidence when the target has no supported answer? | Abstention and evidence selection. A retrieval flag alone is not a proven fabricated final answer. |

The recovered roadmap is itself a useful case of missing required information: a plan existed but became unreachable in the working conversation. That motivates durable indexing and handoff links, **medium confidence as a design lesson**; it does not establish which product would have prevented the loss. Keep these seven classes separate from false supersession, history erasure, access policy, and deployment outcomes rather than compressing them into a scalar score.

## Approaches, representative systems, and what they buy

| Family | Examples and primary sources | Useful distinction / working view | Confidence |
|---|---|---|---|
| Explicit notes and native memory | [Claude Code instructions and auto memory](https://code.claude.com/docs/en/memory); project notes and handoffs | Human instructions and agent-written memory differ in authorship. Loaded context is not an enforcement mechanism. Attractive starting point for small scoped preferences; costs include curation and stale instructions. | High on documented mechanism; medium on fit for Brian. |
| Episodic archives and retrieval | [Mem0](https://arxiv.org/abs/2504.19413); lexical/dense/hybrid stores in [our bake-off](inputs/ROUND1_FINAL_READOUT.md) | Preserve or extract past experience, then retrieve a subset. Retrieval quality does not establish safe updates, abstention, or timely use. Full products may do substantially more than our raw adapters. | High on family distinction; low on a universal winner. |
| Hierarchical context and compaction | [MemGPT](https://arxiv.org/abs/2310.08560), [Pi compaction docs](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/compaction.md), [context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [Compaction Cliff](https://arxiv.org/abs/2608.22752) | Manage limited working context through tiers, summaries, offloading, or typed retention. Pi documents both compaction and branch summaries; archived raw history and model-visible context are distinct. Loss of constraints/procedures matters alongside recall. | High on documented mechanism; medium on typed retention; unknown on Brian's installed version/settings. |
| Temporal or relational memory | [Zep](https://arxiv.org/abs/2501.13956) / Graphiti | Model relationships and changes explicitly. Worth considering for questions about what was true when, or entities across projects; not automatically justified for a handful of preferences. | High on proposed mechanism; medium on workload fit; comparative gain unknown. |
| Corpus graph summarization | [GraphRAG](https://arxiv.org/abs/2404.16130) | Community-level summaries support global questions over a corpus. This solves a different problem from remembering one user's latest preference. “Graph” is not a sufficient reason to group all memory systems together. | High on distinction; low on applicability to Brian's immediate gap. |
| Organized, reflective memory | [A-MEM](https://arxiv.org/abs/2502.12110), [Hindsight](https://arxiv.org/abs/2512.12818) | Link and reorganize memories or distinguish retained experience from later reflection. Potential value in synthesis; inferred beliefs must remain distinguishable from source observations. | Medium from methods and current documentation; [cycle16 source/update distinctions](panel-response-c16.md). No installed cross-system ranking adopted. |
| Personalization and social simulation | [MemoryBank](https://arxiv.org/abs/2305.10250), [Generative Agents](https://arxiv.org/abs/2304.03442) | Persistent user context or reflective agent experience can support continuity. Conversational quality and simulated believability are different outcomes from factual accuracy or operational reliability. | High on task distinction; medium on transfer limits. |
| Procedural memory and skills | [Reflexion](https://arxiv.org/abs/2303.11366), [Voyager](https://arxiv.org/abs/2305.16291) | Retain feedback or reusable programs, not just facts. Promising for recurring workflows, provided procedures are scoped and revised after failures. Voyager's simulated environment is not evidence of physical-world reliability. | High on mechanisms; low–medium on Brian's workflows. |
| Learned neural/adaptive memory | [Titans](https://arxiv.org/abs/2501.00663), [SEAL](https://arxiv.org/abs/2506.10943) | Architectural contextual memory and model adaptation differ from editable external records. [Methods boundary](reading/tern-c11-memory-representation.md) distinguishes persistence, correction and cost. | Medium on mechanism; local value and cross-host portability unproven. |
| Learned memory controller | [Memory-R1](https://arxiv.org/abs/2508.19828) | Learns operation selection and filtering over external records; [scope](reading/tern-c11-memory-representation.md). | Medium mechanism confidence; QA transfer does not establish procedural benefit. |
| Shared, embodied, and multimodal memory | [Broad survey](https://arxiv.org/abs/2512.13564); [Voyager](https://arxiv.org/abs/2305.16291) as one narrow example | Shared ownership, conflicting writers, spatial experience, and non-text observations broaden the field. Current v0 has thin coverage here; do not generalize text-agent conclusions to these settings. | Low coverage; deployment recommendations unknown. |

These families compose. A system can combine extraction, graph storage, dense retrieval, and model-authored summaries. Comparisons should specify those choices and the serving path rather than treat brand names as atomic interventions. **High confidence**, supported by the configuration differences in [our final bake-off readout](inputs/ROUND1_FINAL_READOUT.md).

## Benchmarks: what a score can and cannot tell us

| Evidence source | What it illuminates | Limit to keep attached | Confidence |
|---|---|---|---|
| [LoCoMo](https://arxiv.org/abs/2402.17753) | Long conversational histories, including QA and event understanding | Constructed and human-checked conversations are not organic months of tool-using work. Success need not mean better actions. | High on benchmark scope; medium on transfer concern. |
| [LongMemEval](https://arxiv.org/abs/2410.10813) | Extraction, multi-session reasoning, temporal reasoning, updates, and abstention in long histories | Retrieval recall and final-answer evaluation are different measures. Neither alone measures interrupted-work recovery. | High on scope and measurement distinction. |
| [MemoryArena](https://arxiv.org/abs/2602.16313) | Memory in interdependent multi-session agent tasks | Closer to action outcomes, but environment/task construction still controls what remembering pays for. [Methods now read](reading/tern-c5-memory-action.md): within-task continuation is not independent procedural transfer; success also depends on reasoning/execution. | High on scope; transfer remains uncertain. |
| [LongMemEval-V2](https://arxiv.org/abs/2605.12493) | Evidence gathering over an agent's environment interactions: states, workflows, gotchas, and premise awareness | Still evaluates downstream question answering, not live task completion. Distinct from original chat-history LongMemEval; richer history does not make its endpoint a work outcome. | High on stated formulation; transfer medium/unknown. |
| [KnowledgeDrift](https://github.com/techtheist/KnowledgeDrift), [our sample](../team/S10-KD-CROSS/verdict.json) | Separates retrieval from abstention and changing-knowledge capabilities | Our cross-system slice covers only three families. All tested stores failed correct abstention on that slice. Author-adjacent rankings are not neutral product rankings. | High on local result, medium on broader interpretation. |
| [R53](inputs/R53-acceptance.json) | Fresh-session saved memory and service-restoration behavior | Controls already succeeded: N/I/R each 3/3, despite relevant reads in R. Ceiling limits the benefit inference. | High, narrowly scoped. |
| [R61](inputs/R61-acceptance.json) | Missing saved preference, direct delivery, and endpoint validity | Field-hygiene rules obscured real differences. Numeric prose relabeled a no-run ask; units and provenance wording withheld successful runs. No retrospective pooling. | High, narrowly scoped. |
| [R68](inputs/R68-acceptance.json) | Saved preference supports an autonomous target choice instead of clarification | R and direct-context D each 2/2 primary; I 0/2. N contains one held row. Two targets, one cell each, synthetic task, same reviewer. | High on observations; medium–low on general benefit. |
| [Compaction Cliff](https://arxiv.org/abs/2608.22752) | Retention of different kinds of context through compression | Relevant to constraint loss, but reported method gains are not verified on the current Claude/Pi/local stack. | Medium on direction; transfer unknown. |

Our KnowledgeDrift sample's BM25 advantage over dense LSA is a result about these representations and probes, not “sparse beats neural memory.” Its common abstention failure is at least as decision-relevant as the ranking. The [inventory](INVENTORY.md) preserves the numbers and scope. **High confidence.**

R68's successful relevant-memory runs involved no successful memory-read tool call in session 2; the target appeared in the saved index. Host index delivery is inferred, not directly observed. Irrelevant-note delivery remains indeterminate; D is direct prompt context, not persistence evidence. Its held N row is an event-classifier coverage/instruction-deviation issue, not demonstrated contamination. **High confidence in the recorded evidence and these limits.** [R68 summary](inputs/R68-aggregate-summary.md).

## Problems that cut across systems

- **Admission and revision:** indiscriminate extraction and aggressive deduplication can preserve the wrong thing or erase a valid distinction. We need scoped sources, correction handling, and reversible updates. **High confidence in the hazard from our fixtures; medium on the best design response.** [Bake-off](inputs/ROUND1_FINAL_READOUT.md).
- **Context allocation:** more available history need not mean more usable evidence. Position effects and context-budget tradeoffs motivate selection, but older long-context results should not be asserted unchanged for today's models. **High on the historical result; current model transfer unknown.** [Lost in the Middle](https://arxiv.org/abs/2307.03172).
- **Trust:** a memory item may be an instruction attempt rather than a fact. Origin and authority belong beside content, especially when tools later act on it. **Medium confidence in the operational recommendation**, informed by [AgentPoison](https://arxiv.org/abs/2407.12784); attack success rates are not imported into this survey.
- **Value:** the main question is the cost of repeated correction, lost work, wrong stale actions, and maintenance. Scores are useful diagnostics; the intended work decides which diagnostic matters. **Medium confidence as an applied position**, supported by the contrast between R53 and R68 above.

## Gaps worth closing next

The panel adds a live disagreement: [Corvid](opinions/corvid-c1.md) favors automatic capture plus lifecycle handling; [Kiln](opinions/kiln-c1.md) favors native notes and handoffs. Both are **medium-confidence opinions**, not independently demonstrated efficacy. [Tern's response](panel-response-c1.md) accepts the missing comparison, lowers confidence in the initial ordering, and keeps the rival visible.

[Cairn’s reader contribution](reading/c1-procedural-memory.md) sharpens procedural memory into a candidate combination: **reusable procedure + outcome check + tested environment**, with relevant applicability checks at use. Tern accepts this at **medium confidence as a design bet**, not as a demonstrated cheap or universal solution. Check cost and coverage matter; an exit code is not automatically proof of the desired outcome. [Panel response](panel-response-c1.md#cairn-procedures-with-outcome-checks-and-environment-identity).

Source boundaries matter to this bet. [A-MEM](https://arxiv.org/abs/2502.12110) updates derived note representations; this alone does not establish corruption or deletion of source history. [Supersede](https://arxiv.org/abs/2606.27472) studies fact currency, a relevant warning with uncertain procedural transfer. [GateMem](https://arxiv.org/abs/2606.18829) evaluates access/deletion governance, not an interchangeable measure of scoped factual truth. LongMemEval-V2’s workflow questions remain QA evidence, not a measured saving in live procedural work. These primary-abstract checks narrow interpretations; they do not reproduce the studies or settle product choices.

The [question register](QUESTIONS.md) now treats Brian's priority ranking as answered and puts **procedural reuse, preference application, and artifact-backed applicability** first. Compare explicit skills/runbooks with episodic reconstruction and automatic extraction; inspect whether studies measure doing the work rather than merely recalling a workflow. Current Pi behavior, local inference costs, shared-memory ownership, multimodal memory, and long-horizon forgetting remain under-covered. They are gaps in this map, not justification for restarting campaign4. Panel disagreements will be preserved in the memo rather than converted into a new audit queue.


## Cycle 2: procedural memory must earn reuse

The new [methods note](reading/tern-c2-procedure-evidence.md) distinguishes a reusable investigation procedure from a stored task solution. Raw episodes and procedural guidance can coexist; this is not a binary architecture choice. The [outcome-evidence comparison](reading/tern-c2-outcome-evidence.md) adds AFTER, Skill-Evo4GUI and BASM to the procedural family: respectively skill-content transfer with supplied skills, repeated-work adaptation with limited replication, and applicability/repair mechanisms. Their endpoints should not be pooled with workflow QA or our tiny synthetic preference task. **Medium confidence** in the resulting conditional-reuse recommendation; low in a universal representation winner.

The architecture question now has a sharper test: can a small reusable procedure save repeated discovery while history and artifact checks handle changing details? Useful outcome checks, sources and conditions belong together, but no fixed metadata schema makes old learning universally valid. Preference authority is separate from factual correctness. These are Tern’s design judgments informed by the new readings and [cycle-2 disagreements](panel-response-c2.md), not a deployment result.

## Cycles 3–4: preference authority and integrated architecture

Separate explicit directions from inferred tendencies, and capture/correction from delivery/application. [Preference methods](reading/tern-c3-preference-evidence.md) distinguish recall, use and currency; none establishes the lowest-maintenance arrangement for Brian. [Integrated-system reading](reading/tern-c4-integrated-memory.md) strengthens the native/integrated comparator: MemGPT retains recall history, Pi documents concrete instruction loading, and Zep supplies temporal extraction and context assembly that still need application integration. Five responsibilities remain useful; five services are not required. **Medium-confidence synthesis.**

## Automatic procedural upkeep

[ReasoningBank, ReMe and Sleep-time Compute](reading/tern-c6-automatic-upkeep.md) separate extraction of learning, revision of the active pool and advance preparation. They strengthen agent-authored maintenance as a candidate (**medium confidence**) without establishing cheap or reliable lifetime upkeep. Keeping original episodes does not require every extracted lesson to stay active. More successful tasks beside a retrieved memory is not by itself a causal estimate of that memory’s value.

## Cycle 8: retained, discoverable and applicable are different

The [panel synthesis](panel-response-c8.md) keeps three distinct questions: was evidence preserved, can the agent find it, and does it apply now? MemBukkit’s local temporal-link mechanism and OM’s tombstones/ID recall illustrate different answers. Neither establishes a product winner. **Medium-confidence synthesis.** HaluMem now has a [primary-method note](reading/tern-c8-halumem.md); GateMem adds requester-specific access and behavioral forgetting to the map, distinct from factual currency. Multiple agents need not imply multiple principals. This broadens coverage without displacing Brian’s procedure/preference priorities or requiring another service.

## Cycle 9: elapsed history is not an observed deployment

[Longitudinal methods](reading/tern-c9-longitudinal-evidence.md) add Ground Truth First, RealMem and EvoArena. They distinguish simulated duration, changing executable conditions and actual user upkeep. **Medium confidence** in selective revision backed by retained evidence; no measured lifetime-cost winner. The [panel response](panel-response-c9.md) accepts the documented reason to reduce rewrite churn while retaining meaningful-change triggers. Chain metrics and action-use traces are useful diagnostics, not interchangeable measures or universal causal tests.

## Cycle 10: personal archives, tool grounding and integrated local memory

[Primary notes](reading/tern-c10-preference-and-action.md) add authentic multimodal personal archives (ReaLMem), historical-parameter grounding (Mem2ActBench), and a concrete local-plugin integration (MemOS). **Medium-confidence synthesis:** inferred habits should remain conditional on current circumstances; storage locality and inference locality are different. Predicting a preference ranking, honoring an instruction, generating a tool call and verifying its outcome are distinct achievements. This broadens the field beyond text-only notes without selecting a product or a universal preference-weighting rule.

## Cycle 11: scope is decided somewhere

[Primary representation note](reading/tern-c11-memory-representation.md) adds SEAL, Titans distinctions and MemStrata’s deterministic assertion path. A deterministic state transition still depends on correctly extracted identity and scope; weight adaptation still needs a correction strategy. StateMem/StateMemBench methods are now read: LLM state proposals, deterministic recheck propagation, and a transcript-consuming answer wrapper; its grading pool is hidden from the answering agent. **Medium-confidence synthesis**, no ranked-bet change or product adoption. [Panel response](panel-response-c11.md).


**Cycle12 synthesis:** [A/B/C alternatives](ALTERNATIVES.md) separates automatic capture/upkeep from native, integrated and learned representations. A learned controller may edit an external store; native files may be agent-authored. No architecture wins by being labeled automatic. Native cross-host refresh remains an integration question. Medium confidence in the responsibility distinction; no new product winner or installation.


**Cycle13 update:** Letta reflection is a concrete background revision workflow; pi-reflect is a native-files comparator (README read, implementation pending). Both belong under agent-authored learning and context maintenance, not a new roadmap layer. [Source note](reading/tern-c13-upkeep.md). Confidence medium in documented facilities, low in comparative user benefit.


**Cycle14 update:** pi-reflect implementation read: invoked native edits are real; complete outcome evidence, successful versioning and next-host loading must not be inferred from the target file alone. [Lead source limits](reading/tern-c14-pi-reflect.md). PAHF feedback methods read, with simulated users and separate no-feedback test phases; [methods](reading/tern-c14-feedback-and-learning.md). ACE/SkillRL/SkillForge are newly selected method readings, not yet ranked winners.


**Cycle15 methods read:** ACE incremental playbooks, SkillRL co-evolving bank/policy and SkillForge explicit invocation/outcome tracking are now [compared](reading/tern-c15-skill-learning.md), with [ACE controls](reading/tern-c15-ace.md). Source mechanisms strengthen agent-maintained procedure candidates; no portable cost winner. Medium confidence in the distinctions. Hindsight/A-MEM full methods are next, not yet completed.


**Cycle16 interim:** Hindsight paper/current-product evidence now deepened: source-linked derived observations and documented Pi integration strengthen the comparator; labels/confidence are not authority, local daemon is not local inference. [Source note](reading/tern-c16-hindsight.md). A-MEM full methods remain pending; no product winner.

**Cycle16 complete:** all panel sources received. A-MEM distinguishes original content from evolving interpretation; Hindsight documents source-linked revisions and Pi integration. Source retention does not guarantee that recall can find the source. [Panel response](panel-response-c16.md), [A-MEM methods](reading/tern-c16-amem.md), [Hindsight follow-up](reading/tern-c16-hindsight.md). These sharpen L1/L2/L3 without demanding separate services. Confidence medium; no source-corruption or product-benefit experiment.

**Cycle17:** [Source discovery methods](reading/tern-c17-source-discovery.md) adds HippoRAG2 graph-to-passage retrieval, without treating associative QA as preference revision. Hindsight API can return source chunks alongside facts; source exposure is not limited to a separate document tool. Same-ID updates replace content, so retained does not imply append-only. Hindsight leads the integrated-service shortlist for existing hosts, medium fit confidence; no deployment. [Dissent and response](panel-response-c17.md).

**Cycle18:** direct reading, gist-guided original-page expansion and indexed retrieval are competing/composable ways to supply the executive. [ReadAgent and host-source methods](reading/tern-c18-reading-and-host-path.md) distinguish per-document controls and amortized work from corpus-wide retrieval and live procedure reuse. Hindsight shared recall projects to text; append has replacement fallbacks. These are source-level properties, not observed loss or a repair release. [Panel response](panel-response-c18.md).


**Cycle19:** L3/L4 can cooperate through cheap retrieval followed by fuller reading. L1 retention, L3 discovery and artifact-based applicability are separate properties; no new service follows automatically. [Response](panel-response-c19.md).


**Cycle20:** A compact self-curated working sheet can serve L2/L4 without a new service. L1 source retention remains a separate implementation property; working-view rewriting does not prove source deletion. [Response](panel-response-c20.md).
