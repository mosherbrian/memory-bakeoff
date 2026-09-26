# Mechanism-based roster refresh — cycle 18

Tern · 26 September 2026 · **Phase C, reading shortlist only.** Nothing here admits a new contestant or releases a benchmark. Confidence is in the relevance of the question, not product efficacy. Required context: [roadmap](inputs/PHASE2_ROADMAP.md), [reconciliation](inputs/PHASE2_ROADMAP_RECONCILIATION.md), and [Gen125 intake](inputs/PHASE2_CANDIDATE_INTAKE.md). Old “not located” findings remain dated uncertainty, not declarations of current nonexistence.

## Brian's role examples: re-evaluation candidates

The [gloss](inputs/BRIAN-PRINCIPLES.md) reopens these as **role-specific reading candidates**, not settled components or automatic reruns. Weighting is procedural re-learning first, repeating preferences second. Their responsibilities can coexist in one implementation or be supplied by native facilities. See the [role-to-layer map](FIELD-MAP.md#five-roles-mapped-onto-the-five-roadmap-layers).

| Candidate / role / layers | Benefit worth examining for Brian | Own findings and their limits | Current opinion and next reading question |
|---|---|---|---|
| **SKILL.state — structured State; L2/L4/L5** | Carry procedure progress, prerequisites and branch conditions without repeatedly reconstructing the run; apply preferences as scoped constraints. It is not itself evidence that the agent learned the right procedure. | [Primary v3 methods](https://arxiv.org/html/2608.26263v3) read: per-step skill/state/observation input and validated updates, with sufficient-state limitations. See [scoped findings](reading/tern-c2-role-boundaries.md). **No local SKILL.state result claimed.** [Gen45](inputs/PI_STATE_CONTROL_GEN45_LIVE_PILOT.md) is relevant caution: a different bounded-window/control design scored 7/12 vs 12/12 and largely unused control tools. It does not test SKILL.state. | **Watch / high reading relevance, medium mechanism confidence, transfer unknown.** How are schemas and state maintained when the procedure changes? Can history remain separately recoverable? The reported token-saving cell is now located, but remains model/task/baseline-specific. Schema quality and recoverable omitted history matter more than importing that ratio. |
| **Perseus — learned Memory with lifecycle; L2/L3, feeding L4/L5** | Preserve successful/failed procedure outcomes, configuration-specific applicability, and revised preferences without presenting old claims as current. | In **v2.23.2**, [Gen29](inputs/PERSEUS_VAULT_GEN29_LONGITUDINAL.md) found ordinary CLI writes made valid time coincide with write time; transaction-time belief recovery, exact provenance and workspace scope worked. Failed/successful procedure records still co-ranked, and configurations mixed. [Gen30](inputs/PERSEUS_VAULT_GEN30_MCP_VALID_TIME_ABLATION.md) found MCP remember initially preserved retroactive valid time but approval reset it; this blocked the ablation, so no new longitudinal score. | **Watch / re-evaluate the relevant write paths, high relevance; high confidence in old scoped findings, current release unknown.** Do the intended current write/admission paths preserve independent event/knowledge times through activation and correction? Does lifecycle actually distinguish applicable successful recipes and preference revisions? A bitemporal feature name is insufficient; no blanket product rejection. |
| **pi-lcm / transcripts — recoverable History; L1, with L3 and L4/L5 interfaces** | Retain procedure attempts, outcomes and preference provenance so a compact working view never forces irreversible re-learning. Recover omitted evidence without replaying it all. | [September role note](inputs/PI-LCM-TWO-ROLES-20260918.md) records Brian's separate compaction/latency use. [S10 history study](inputs/PI-LCM-HIST-RETRIEVAL-DISPLACEMENT.md) found 22/33 distractor displacements and 0/13 missed updates in one pinned retrieval profile. Its “supersession” means **top-1 retrieval displacement**, not native deletion or loss of transcripts. Gen45 is not a pi-lcm-versus-OM test. | **Watch for the history role / high relevance, medium fit confidence.** [Local source reading](reading/tern-c2-role-boundaries.md) supports retained content after compaction marking but identifies a conditional dedup completeness risk. Check end-to-end capture and branch/replay; source reading is not a measured loss or guarantee. Native transcripts are a comparator or complement. Retrieval weakness does not alone justify removing a separate compaction facility; neither a “lossless” label nor compaction speed establishes lifecycle correctness. |

**Artifacts and executive reasoning are assessed alongside every row.** Real files/configs/logs anchor applicability; the model decides what the evidence means. These are roles, not two extra memory products. Tern's prior deferral of Perseus is narrowed: its role fit now deserves reading, while more tests still need a distinct unanswered question. No install, repair, qualification or benchmark follows from this roster update.

## Small next reading batch

| Priority | Candidate / comparator | Distinct architectural question | Reading disposition and confidence |
|---|---|---|---|
| 1 | Explicit runbooks/executable skills versus episodic procedural reconstruction | Which prevents Brian from re-learning a procedure while preserving prerequisites, successful/failed outcomes and exceptions? | **Read first; high relevance by Brian's answer.** [Reflexion](https://arxiv.org/abs/2303.11366), [Voyager](https://arxiv.org/abs/2305.16291), and AgentRunbook/LME-V2 supply distinct mechanisms, not a ready winner. |
| 2 | Native scoped preference notes versus automatic capture, including Claude-Mem | What avoids repeated preference correction with acceptable authoring and upkeep effort? | **Reassess first; high relevance.** [R68](inputs/R68-acceptance.json) supports available preference context, not a capture-method winner. Distinguish user preference from environmental fact. |
| 3 | Native history/full context versus pi-lcm + OM-like projection | Can selective procedural context preserve recoverable source history without the Gen45 restriction/loop failure? | **Read; medium relevance.** Reuse history/compaction evidence; no new install or automatic composite. |
| 4 | MemBukkit routing and temporal state approaches: Graphiti/Zep, StateMem/MemStrata leads | Can a procedure or preference be scoped to the right configuration/time, with correction and failed alternatives preserved? | **Read selectively; medium relevance.** Lifecycle matters as support for the top two priorities. Unresolved product identities stay unknown. |
| 5 | MemOS as an integrated architecture comparator | Can an integrated design cover these needs with less maintenance than a custom composite? | **Watch/read; low–medium relevance.** [Local plugin card](systems/memos.md) and [provider boundary](reading/tern-c10-preference-and-action.md) now inspected at documentation level; installed value and all-local inference remain unverified. |

Every row competes against using existing native facilities. Brian's [priority answer](inputs/BRIAN-PRINCIPLES.md) changes the reading order, not the observed capability of a product. The [priority steering](panel-priority-steering.md) replaces unfinished broad assignments: assess procedures/preferences first, with artifact evidence and executive applicability checks. No Phase-D admission or installation follows from a reading shortlist.

## Explicit deferrals

- **Hindsight: first integrated-service candidate, watch; medium fit confidence / installed benefit unknown.** Paper methods and current observation/integration docs now read; source-linked revisions and documented Pi support strengthen the integrated comparator. [Evidence and limits](reading/tern-c16-hindsight.md). Full extraction/LLM paths must not be judged by old raw-adapter results. **A-MEM: watch/read, medium mechanism confidence.** [Full methods](reading/tern-c16-amem.md) now distinguish source content from derived updates, with positive QA ablation evidence and unresolved procedural transfer.
- **Mem0:** reuse existing profile-specific results; reconsider only for an identified mechanism/profile change, not because it remains in an old queue. **Medium confidence in deferral.** Perseus is now explicitly reopened for role-specific reading above, while its tested limitations remain attached. [Bake-off](inputs/ROUND1_FINAL_READOUT.md), [roadmap](inputs/PHASE2_ROADMAP.md).
- **Habitus:** historical conditional candidate; no new distinct question established in this cycle. **Low confidence**, hold for a concrete identity/use case. [Roadmap](inputs/PHASE2_ROADMAP.md).
- **MemHarness, Attestor, EvoMem:** preserve as discovery leads. The old intake contains unresolved or potentially overloaded names; no capability or availability judgment is made here. **Unknown**, identity/source check before comparison. [Gen125 intake](inputs/PHASE2_CANDIDATE_INTAKE.md).

## Phase B benchmark refresh coverage

| Roadmap lead | Survey status / next question |
|---|---|
| LongMemEval-V2 | Methods and ablations read; [note](reading/tern-c2-procedure-evidence.md) distinguishes investigation scaffolding and environment-experience QA from live procedure reuse. |
| HaluMem | Primary methods read; [diagnostic note](reading/tern-c8-halumem.md) records retrieval/interface and omission limits. |
| StateMemBench / StateMem | Primary identity now located: [Can Agent Memory Systems Track Evolving State?](https://arxiv.org/abs/2608.19652). [Methods now read](reading/tern-c11-memory-representation.md); closed-pool scoring maps free-form answers, and wrapper overhead must include its supplied transcript. Previous not-found is retired, not treated as an absence result. |
| EvoMemBench / EvoArena | EvoArena 2606.13681 methods now read: versioned executable chains plus preference QA; [metric/uptake limits](reading/tern-c9-longitudinal-evidence.md). Do not conflate with other EvoMemBench identities. |
| GateMem | Primary methods read; [scope response](panel-response-c8.md) separates multi-principal governance from factual supersession and physical erasure. |
| Supersede; Memora / FAMA | Identities separated: Supersede studies bounded notes and fact updates; [Memora/FAMA](https://arxiv.org/html/2604.20006v1) evaluates current versus obsolete memory. [Methods note](reading/tern-c3-preference-evidence.md). |
| STALE | Unresolved name in prior intake. Clarify identity rather than silently omit or invent a citation. |
| Agent Memory Leaderboard | Candidate-discovery infrastructure, not a contestant. Read protocol/model assumptions; do not import a winner or merge its scores with ours. |

These statuses are **high confidence as this survey's reading inventory**, not validation of the leads' claims. Existing [Gen125 refresh](inputs/PHASE2_FIELD_REFRESH_2026-09.md) prevents rediscovering them; it also contains provisional assertions that should not be copied as current fact. This roster is deliberately a reading agenda, not an empirical admission queue.


## Cycle 2 procedural evidence additions

[AFTER, Skill-Evo4GUI and BASM](reading/tern-c2-outcome-evidence.md) are now primary-method readings, not merely discovery leads. They strengthen the case for scoped procedure reuse while leaving discovery, upkeep and transfer gaps. They are literature comparators, not proposed installations. [Native Claude Code](opinions/kiln-c2.md) remains the practical reference for explicit instructions, selective procedures and auto-capture; current official documentation is not an installed-behavior test. Cairn’s [Perseus source card](systems/perseus.md) is received. The archived v2.23.2 finding stands; current Vault releases/source are on a vendor-reported hold. Its separate live-integration claims are not transferred into a verified deployment verdict; see [Tern’s limits](reading/tern-c4-integrated-memory.md).

## Cycle 4 integrated comparator

MemGPT now has a [full-method history/context reading](reading/tern-c4-integrated-memory.md), strengthening the integrated alternative. Zep’s documented temporal extraction and delivery path make it a concrete comparison, not an admitted winner. Native Pi instruction loading is documented upstream; this survey has not verified Brian’s installed host path or adherence. Current preference-delivery work is with Kiln; Corvid is examining whether a separate lifecycle projection is actually necessary.

## Cycle 5: current reusable-learning mechanisms

[Letta/MemFS](opinions/corvid-c5.md) is now a concrete integrated comparator, not just the original MemGPT paper: versioned files and selective context are relevant; backend/version and prompt-versus-runtime distinctions remain in [Tern’s response](panel-response-c5.md). Native Claude Code’s [recorded run/verify recipes](systems/procedure-maintenance.md) supply a practical documented update path. These are **watch/read and practical patterns, medium confidence**, not measured winners or deployment authorization. Capture/TrustMem add preference-update and transition-learning evidence in [Cairn’s reading](reading/c3-preference-lifecycle.md); their clarification assumptions do not justify repeatedly reconfirming Brian’s explicit directions.

**Cycle6 additions:** ReasoningBank (append-based, self-judged learning) and ReMe (adaptive reuse/pool refinement) now have [primary-method notes](reading/tern-c6-automatic-upkeep.md). Both are relevant reading comparators for Q5/Q3; no installation recommended. Sleep-time Compute is a preparation mechanism, with a file-overlap SWE endpoint, not a demonstrated procedure-maintenance winner.

## Cycle 8: lifecycle and diagnostic coverage

[MemBukkit](systems/membukkit.md) is now a local-code mechanism reading: automated similarity-based supersession with explicit links is relevant, but upstream correspondence and comparative value remain unverified. **Watch; medium relevance, low deployment confidence.** [OM and SKILL.state](panel-response-c8.md) sharpen preservation versus discovery and current-state validity. HaluMem/GateMem are diagnostic comparators, not procedure-benefit rankings. No new installation or experiment.

**Cycle9 additions:** Ground Truth First and RealMem are simulated longitudinal comparators; EvoArena evaluates evolving tasks. [Methods](reading/tern-c9-longitudinal-evidence.md). ReaLMem 2609.19167 is a distinct multimodal personal-archive lead, methods now read in [cycle10](reading/tern-c10-preference-and-action.md); authentic archives, offline preference-ranking limits. No architecture winner follows from a benchmark name or duration label.

**Cycle10:** MemOS local plugin is **watch** as an integrated comparator; do not combine paper abstractions, cloud features and local-plugin guarantees. ReaLMem and Mem2ActBench are now primary-method comparators with [scope limits](reading/tern-c10-preference-and-action.md). No vendor score adopted as our own result.

**Cycle11:** [MemStrata card](systems/memstrata.md), [scoped method reading](reading/tern-c11-memory-representation.md): deterministic single-value supersession is relevant; the published extraction prompt excludes ordinary preferences, so preference fit remains uncertain. SEAL is a learned-adaptation comparator, not a demonstrated replacement for attributed records. Titans’ architectural persistence differs from durable cross-host user memory. All **watch/read**, no install.

**Cycle11 completed:** StateMem methods and SEAL correction limits are incorporated. Memory-R1 adds a learned-controller/external-store comparator; Titans adds architectural memory. [Primary distinctions](reading/tern-c11-memory-representation.md). None is an installed product recommendation. The panel now compares the smallest practical arrangements rather than adding another candidate list.


**Cycle12 synthesis:** [A/B/C alternatives](ALTERNATIVES.md) separates automatic capture/upkeep from native, integrated and learned representations. A learned controller may edit an external store; native files may be agent-authored. No architecture wins by being labeled automatic. Native cross-host refresh remains an integration question. Medium confidence in the responsibility distinction; no new product winner or installation.


**Cycle13 update:** Letta reflection is a concrete background revision workflow; pi-reflect is a native-files comparator (README read, implementation pending). Both belong under agent-authored learning and context maintenance, not a new roadmap layer. [Source note](reading/tern-c13-upkeep.md). Confidence medium in documented facilities, low in comparative user benefit.


**Cycle14 update:** pi-reflect implementation read: invoked native edits are real; complete outcome evidence, successful versioning and next-host loading must not be inferred from the target file alone. [Lead source limits](reading/tern-c14-pi-reflect.md). PAHF feedback methods read, with simulated users and separate no-feedback test phases; [methods](reading/tern-c14-feedback-and-learning.md). ACE/SkillRL/SkillForge are newly selected method readings, not yet ranked winners.


**Cycle15 methods read:** ACE incremental playbooks, SkillRL co-evolving bank/policy and SkillForge explicit invocation/outcome tracking are now [compared](reading/tern-c15-skill-learning.md), with [ACE controls](reading/tern-c15-ace.md). Source mechanisms strengthen agent-maintained procedure candidates; no portable cost winner. Medium confidence in the distinctions. Hindsight/A-MEM full methods are next, not yet completed.

**Cycle17:** HippoRAG2 is a relevant discovery comparator, now methods-read, not a lifecycle replacement. [Source note](reading/tern-c17-source-discovery.md). Hindsight original/chunk API paths are located; exact host projection remains open. Letta remains the stronger runtime-change alternative; no installed comparative winner.

**Cycle18:** ReadAgent is methods-read as a recoverable working-view comparator (medium transfer confidence). Hindsight source projection and cursor policy now have [specific code evidence](reading/tern-c18-reading-and-host-path.md); broad claims of source loss or always-append are narrowed. No installed ranking.


**Cycle19:** Self-Route is methods-read as a context-selection comparator. Local pi-lcm code exposes unknown-ID recovery within a conversation; installed availability and cross-host completeness remain unmeasured. [Response](panel-response-c19.md).


**Cycle20:** Dynamic Cheatsheet is methods/code-read: watch the transferable automatic-reuse pattern, not a ready host plugin. Current runner retains output history; the small working sheet is not its only saved artifact. [Response](panel-response-c20.md).


**MemBukkit extraction clarification:** local source separates LLM-distilled facts/proposed turn indices from heuristic supersession linking. A valid pointer index does not prove that its source supports the fact. Watch verdict unchanged; [details](panel-response-c8.md).


**Cycle22:** Claude Code and Pi document skill discovery/loading surfaces; current docs are not installed parity. Compaction can affect retained skill context. [Host note](reading/tern-c22-application.md). [Response](panel-response-c22.md).


**Cycle24:** ReMe is now a current Markdown-based integration candidate as well as a procedural-memory paper. Its present consolidation loop must not inherit the paper score without correspondence. Watch; medium mechanism relevance, installed benefit unknown. [Response](panel-response-c24.md).

**Cycle25 — ReMe, medium fit confidence:** editable-file representation can coexist with automated capture/consolidation and host adapters. Add it as the file-compatible automation comparator; current auto_dream is not validated by the paper’s distinct learning-loop results. Separate source retention, version history, delivery and upkeep cost. [Primary reading and comparison](reading/tern-c25-files-and-automation.md), [panel disposition](panel-response-c25.md). No install.

**Cycle30 — StateFuse:** [candidate card](systems/statefuse.md). Watch as an explicit correction/conflict mechanism for L2/L5; current docs separate structured detection from upstream extraction and authority judgment. No unique benchmark accuracy win or installed fleet benefit established; no service release.

**Cycle32 — Mem0 reconsideration:** the identified profile/version distinction justifies new reading: our infer=False raw result, the2025 paper automatic update loop, and current additive extraction docs are different paths. [Card](systems/mem0.md), [independent primary comparison](reading/tern-c32-mem0-profiles.md). Watch; infrastructure/extraction facilities are relevant, host delivery and comparative benefit unknown. Old results remain profile-specific; no new trial.

**Cycle33 Mem0 clarification:** OSS main exposes history and records previous/new text on update and previous text on deletion. Related-memory/entity links are not a demonstrated supersession chain. This narrows whole-product erasure claims; original-conversation recovery and correct host application remain separate. Watch unchanged. [Source-level qualification](reading/tern-c33-currency.md).

**Cycle34 DynaMem:** skip as a product for Brian; retain as an embodied-memory mechanism example. Borrow selective re-observation only where its evidence model makes sense. [Card](systems/dynamem.md) must be read with [lead qualifications](panel-response-c34.md): archival retention, cost and prevention of Gen45 failures are not established.

**Cycle35 Generative Agents:** research architecture, not a selected host integration. Candidate mechanism: evidence-linked reflections feeding planning. No adopted importance threshold or extra scheduled pass. [Card](systems/generative-agents.md), [lead qualifications](panel-response-c35.md).

**Cycle36 Reflexion:** borrow a bounded feedback/recovery pattern where useful; no selected adapter or automatic retry policy. A short buffer is memory across trials, not proof of a durable procedure library. [Card](systems/reflexion.md) with [lead qualifications](panel-response-c36.md), including source-version and trial-budget limits.


**Cycle37 ExpeL:** watch as a research mechanism for agent-owned candidate extraction and experience reuse. No demonstrated fleet adapter or total-cost advantage; votes are not outcome verification. [Card](systems/expel.md), [lead qualifications](panel-response-c37.md).


**Cycle38 AutoManual:** watch the research loop; consider scope/examples where they remove ambiguity, without retrofitting every skill. Benchmark adapters and machine feedback are not fleet integration; rule logs are not automatically a recoverable archive. [Card](systems/automanual.md), [qualifications](panel-response-c38.md).


**Cycle39 AutoGuide:** watch the research selection mechanism; no located adapter or deployment recommendation. Trigger prose is not itself the matching runtime. Context matching is model-mediated, not just exact-key lookup. [Card](systems/autoguide.md), [lead qualifications](panel-response-c39.md).


**Cycle40 shortlist unchanged, advice clarified:** existing facilities plus agent upkeep remain the base; ReMe, Pi reflection, Hindsight and Letta are alternatives for specific missing operations. Research manual/selector loops are mechanism references, not installed recommendations. [Arrangement and ownership](ALTERNATIVES.md).


**Cycle41 CLIN:** watch as a learning/control architecture; uncertainty wording is a design aid, not a recommended fixed schema or archive size. Simulator feedback/reset facilities and raw-source recovery require separate consideration. [Card](systems/clin.md), [qualified decision](panel-response-c41.md).
