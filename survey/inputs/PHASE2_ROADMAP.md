<!--
RECOVERED ARTIFACT. This document was created 2026-09-02 22:52 as a Google Doc
(`MEMORY_BAKEOFF_PHASE2_ROADMAP`, Drive id 1DTo_Ku0ErI5FmphuS0-mnwoeiBtbF84abDC-HoDLK0Q),
with an explicit durability rule written into the conversation that agreed it:

    "as soon as Gen33 completes, we copy this into the repo as
     research/PHASE2_ROADMAP.md and link it from the project."

That copy never happened. The conversation branch that agreed it was ORPHANED by a
message edit in the ChatGPT UI - the messages remained in the account's export but
became unreachable in the interface - so the plan, the reasoning behind it, and the
instruction to preserve it all stopped being visible at once. The project then ran
roughly 88 further generations without it, exhausting the original contestant list,
which is precisely what step 7 of this roadmap says not to do.

Recovered 2026-09-06 from Brian's ChatGPT data export by reconstructing the orphaned
branch, then exported verbatim from the surviving Drive document rather than
reconstructed from chat. See reviews/gen120-rivals-* for the review record of that
period and ~/recovered/ for the recovered conversation.

Nothing in this file has been edited. It is four days old and predates Gen34-Gen121;
read it as the plan that was agreed then, not as a description of current state.
-->

MEMORY BAKE-OFF — PHASE 2 ROADMAP  
Living plan, created 2026-09-02

PURPOSE  
This document is the durable roadmap for the memory-bakeoff project after Generation 33\. It is intentionally separate from CHATGPT\_TO\_CODEX, which remains the generation-by-generation execution mailbox. This roadmap should change only when the evidence changes our plan; individual generation instructions should implement it rather than replace it.

CURRENT POSITION  
Round 1 established retrieval, safety, provenance, lifecycle, reader, and product-profile baselines across the original contestants.

Round 2 introduced frozen longitudinal-v1 and has so far produced:  
\- pi-observational-memory: strong long-session working-memory/context production, but not semantic historical retrieval.  
\- Perseus: strong explicit temporal/lifecycle ambitions, but ordinary operator writes collapse valid/application time onto transaction time; the alternate admission path destroys retroactive valid time on activation.  
\- Hindsight raw/no-LLM: useful mention-time history and strong retrieval, but append-only current-state contamination remains.  
\- Mem0 infer=False: no temporal retrieval surface at all, yet the same longitudinal failure family recurs.  
\- agentmemory Gen33: in flight. It is the first intended contrast where ordinary product ingestion can automatically retire/supersede memories. Interpretation depends on whether that treatment actually activates on longitudinal-v1.

The strongest current finding is preregistered three-engine triangulation: seven failure classes recur across Perseus, Hindsight, and Mem0 under ordinary append-only ingestion without retirement:  
1\. stale\_persistence  
2\. configuration\_collapse  
3\. failed\_procedure\_adoption  
4\. late\_history\_corruption  
5\. false\_persistence  
6\. missing\_required\_truth  
7\. unsupported\_evidence

Five of those appeared at identical aggregate counts across all three products: false\_persistence 9, configuration\_collapse 6, failed\_procedure\_adoption 3, late\_history\_corruption 3, unsupported\_evidence 6\.

Interpretation remains conservative: this is strong association/triangulation, not proof that append-only ingestion is causal. Gen33 is designed to move the retirement variable for the first time if native supersession actually fires.

EMERGING TARGET ARCHITECTURE  
The working architectural hypothesis is no longer “find the best vector-memory plugin.” It is a layered system:

1\. Lossless canonical history  
   \- Every original user/model/tool event retained.  
   \- Branch-aware, replayable, auditable.  
   \- Exact provenance to source events.  
   \- pi-lcm is the current best match for this substrate.

2\. Explicit state/lifecycle projection  
   \- Distinguish current, historical, corrected, invalidated, retracted, failed, successful, concurrent, scoped, configuration-specific state.  
   \- Preserve valid/event time separately from ingestion/knowledge/transaction time where needed.  
   \- Supersession must be conservative and evidence-backed rather than “nearest neighbor means replacement.”  
   \- StateMem, MemStrata, bitemporal/event-sourced approaches, and similar systems are reference points here.

3\. Durable semantic/causal retrieval  
   \- Search across full retained history, not merely active state.  
   \- Support exact provenance and recovery of historical beliefs/evidence.  
   \- Scope/configuration aware without hiding product failures in harness postfilters.  
   \- Membukkit remains especially interesting as a structured retrieval/routing candidate.

4\. Bounded working-memory synthesis  
   \- Maintain what the agent should be thinking about now.  
   \- Continuously compress/synthesize while preserving semantic distinctions.  
   \- Never become the sole source of truth.  
   \- pi-observational-memory is the strongest observed match so far.

5\. One context composer  
   \- Recent verbatim context \+ working-memory projection \+ targeted deep recall.  
   \- Avoid recursive summarization, duplicated context ownership, and competing compaction systems.

A concise design shorthand is:  
pi-lcm remembers everything \-\> state layer decides what is currently true \-\> retrieval finds anything in history \-\> OM-like projection decides what belongs in active context.

PHASE 2 EXECUTION PLAN

PHASE A — Finish Gen33, then pause the old queue  
\- Let Gen33 complete without interference.  
\- Determine whether agentmemory native supersession actually activated on the 16-observation ruler.  
\- If it activated, record the trade-off between reduced stale-state failures and false supersession/state loss.  
\- If it did not activate, keep the longitudinal result but explicitly classify the intended treatment as not activated.  
\- Do not immediately issue Gen34 from the old contestant list.

Decision Gate A:  
After Gen33, freeze a short “Round 2 interim findings” note before admitting more contestants.

PHASE B — Leaderboard and field refresh  
Run a focused research refresh using the problem definition we now have, not the original generic “agent memory” search.

Primary research question:  
What systems maintain evolving agent state while preserving lossless history, provenance, scope, recoverable historical belief, semantic recall, and bounded working context?

Harvest candidates from current benchmark frontiers rather than blindly taking overall leaderboard winners. At minimum inspect:  
\- StateMemBench / StateMem  
\- LongMemEval-V2  
\- Agent Memory Leaderboard, especially coding-memory track  
\- HaluMem  
\- EvoMemBench / EvoArena  
\- GateMem  
\- STALE  
\- Supersede  
\- any newly released benchmark specifically testing dynamic state, update/conflict handling, workflow reuse, premise awareness, provenance, or forgetting.

For each benchmark, capture:  
\- benchmark version/date  
\- task dimensions  
\- evaluator/model assumptions  
\- top overall systems  
\- Pareto/frontier systems by the dimensions we care about  
\- open/local/self-hostable status  
\- public code and reproducibility  
\- whether reported gains come from memory architecture versus stronger LLM or hidden product service  
\- whether the benchmark is retrieval-heavy, state-heavy, workflow-heavy, or governance-heavy.

Do not import leaderboard scores into our leaderboard. Public leaderboards are candidate discovery and external validation only.

Decision Gate B:  
Produce a ranked candidate intake table with one sentence answering “what distinct architectural question would this contestant answer that we have not already answered?” Reject candidates that add no new mechanism.

PHASE C — Refresh the contestant roster  
The current expected priority pool is:

Must revisit from original roster:  
\- Membukkit — high priority. Phase 2 should test whether bucket/routing structure helps scope/config/current-state separation or merely creates topical clusters with stale state inside them.  
\- Claude-Mem — high priority because it is a real coding-memory system and now appears on modern coding-memory leaderboards.

Likely new high-priority candidates/reference implementations:  
\- StateMem — probably reference implementation/reproduction if no usable product code exists.  
\- MemStrata — high architectural fit if a reproducible local path exists.  
\- MemOS — strong public benchmark presence; inspect update/conflict semantics carefully.  
\- AgentRunbook-C — highly relevant to coding-agent experience memory and workflow reuse.  
\- causal-memory / other architecturally distinct AML coding leaders — select by mechanism, not score ties.  
\- A-Mem — evolving-memory representation; useful if implementation is reproducible.  
\- memharness — small/new but unusually aligned with bitemporal/supersession/provenance requirements.  
\- Attestor — inspect as a self-hosted bitemporal/supersession backend.  
\- EvoMem — patch/evolution model worth testing or using as an external lane.

Conditional original contestants:  
\- Graphiti — rerun only if we can define an honest Phase-2 identity with exact provenance and lifecycle evidence.  
\- Habitus — only if its longitudinal identity can be tested without inventing missing product behavior.

Already-tested systems should get full-product ablations only when they answer a specific unresolved question:  
\- Hindsight full-product LLM extraction: does a real application-time axis materially fix its raw-profile weaknesses?  
\- Mem0 infer=True: only if its additive extraction path can answer a distinct question; do not assume it is an update engine.  
\- Perseus: no more mainline testing unless a product change or a narrowly defined write-surface ablation resolves the demonstrated valid-time defect.

Decision Gate C:  
Choose a small next batch, probably 3–5 contestants/ablations, each justified by a different mechanism. Do not exhaustively test every new project.

PHASE D — Common Phase-2 admission gate for every contestant  
Before longitudinal-v1 exposure, every new contestant must pass the same discipline:

Identity:  
\- exact product/source version or commit  
\- model/embedding/reranker identity  
\- runtime/provider/quantization  
\- storage/index configuration  
\- disabled and enabled features  
\- hardware/environment

Unrelated preflight:  
\- validate ingestion semantics  
\- validate search semantics  
\- validate update/supersession/retirement semantics  
\- validate scope/config isolation  
\- validate temporal/as-of behavior  
\- validate provenance  
\- validate read side effects  
\- validate lifecycle observability

Frozen adapter:  
\- adapter contract frozen and hashed before first scored query  
\- no hidden expected/prohibited IDs  
\- no truth-driven postfiltering or reranking  
\- no harness-created lifecycle help

Repeated measurement:  
\- three clean repetitions where practical  
\- full checkpoint-prefix discipline  
\- native state captured before scored reads  
\- lifecycle and retrieval reported separately  
\- harness owns scoring/provenance

No scalar “winner” score for longitudinal-v1. Named failure classes and lifecycle outcomes remain primary.

PHASE E — External benchmark lanes  
Do not force every research question into longitudinal-v1.

Use external benchmarks for what they are good at:  
\- StateMemBench: evolving current-state tracking independent of ordinary retrieval.  
\- LongMemEval-V2: coding/experience memory, workflows, gotchas, premise awareness, very long histories.  
\- HaluMem: extraction/update/conflict operations.  
\- EvoArena/EvoMemBench: changing environments and procedural evolution.  
\- GateMem: scope/access/forgetting/governance.  
\- STALE/Supersede: targeted update/supersession failure modes.  
\- MemConflict: explicit conflict lane already planned.

Prefer native benchmark protocols and primary-source implementations. Treat each benchmark as a separate evidence class rather than combining metrics into one master score.

PHASE F — Synthesize the architecture, not just the leaderboard  
Once we have enough Phase-2 evidence, produce an architecture matrix with these columns:  
\- lossless history  
\- exact provenance  
\- branch/replay semantics  
\- valid/event time  
\- transaction/knowledge time  
\- supersession/correction  
\- retraction/invalidation  
\- concurrent scoped truth  
\- configuration identity  
\- dependency propagation  
\- historical belief recovery  
\- semantic retrieval  
\- procedural memory  
\- current-state projection  
\- bounded working-context synthesis  
\- false-supersession risk  
\- read/write side effects  
\- local/self-hosted practicality  
\- Pi integration fit

This matrix should answer which components are best-in-class even if no single product wins end-to-end.

Decision Gate F:  
Choose whether the likely destination is:  
A. adopt one integrated product;  
B. compose existing systems;  
C. build a thin state layer around pi-lcm \+ best retrieval \+ OM-like projection;  
D. reproduce/adapt a research architecture such as StateMem/MemStrata.

PHASE G — Prototype our likely composite  
Do not build this until enough Phase-2 evidence supports it.

Current likely prototype shape:  
\- pi-lcm remains canonical lossless DAG/history.  
\- state projection is derived and rebuildable from canonical events.  
\- every derived state item retains exact source-node provenance.  
\- explicit lifecycle/state distinguishes current/historical/corrected/retracted/invalidated/failed/successful/concurrent.  
\- deep semantic retrieval searches canonical history and state views.  
\- OM observer/reflector machinery becomes a consumer of canonical events, not an independent source of truth.  
\- one context composer produces recent verbatim \+ current working projection \+ targeted deep recall.  
\- branch/rewind semantics invalidate/rebuild derived state on the active branch.  
\- no recursive summarization of pi-lcm or OM summaries.

Prototype evaluation must include ablations:  
1\. pi-lcm only  
2\. pi-lcm \+ retrieval  
3\. pi-lcm \+ state layer  
4\. pi-lcm \+ OM projection  
5\. pi-lcm \+ state \+ retrieval  
6\. full composite

That is the point at which we can make causal claims about individual architectural layers rather than comparing different products with many confounds.

PHASE H — Realism endgame  
Only after the synthetic and external benchmark stages are sufficiently understood:  
\- MemConflict if not already complete.  
\- private month-long coding-agent corpus, local/private only.  
\- no raw private corpus in GitHub or Drive.  
\- use the real corpus to test longitudinal utility, workflow reuse, stale-state handling, project/scope isolation, branch/rewrite behavior, provenance, and context-budget economics.  
\- compare promising contestants and the composite prototype under identical Pi harness/model/config where possible.

WHAT NOT TO DO  
\- Do not declare OM, Membukkit, or any other system “the winner” before comparable Phase-2 evidence.  
\- Do not exhaust the original contestant list just because it exists.  
\- Do not chase every new memory project.  
\- Do not let public leaderboard scores substitute for our own lifecycle/provenance measurements.  
\- Do not let stronger LLMs silently become the explanation for a memory result.  
\- Do not combine retrieval quality and lifecycle destruction into one score.  
\- Do not treat absence from active state as deletion without native evidence.  
\- Do not mistake a working-memory projection for durable memory.  
\- Do not use truth-aware harness filters to repair product scope/time/lifecycle failures.

DURABILITY / PROJECT-MEMORY RULES  
1\. This Google Doc is the living roadmap and should remain stable across generations.  
2\. CHATGPT\_TO\_CODEX remains the execution mailbox only; each generation should reference this roadmap rather than restating the whole strategic plan.  
3\. After Gen33 completes, add a repository copy such as \`research/PHASE2\_ROADMAP.md\` from this roadmap and link it from the project’s research index/README/RESULTS as appropriate.  
4\. Generation handoffs should record any evidence that changes this roadmap.  
5\. Roadmap changes should be explicit: date, evidence that triggered the change, and what decision changed.  
6\. Frozen benchmark rulers/results remain immutable even when the roadmap evolves.  
7\. Candidate intake and rejection decisions should be written down so previously rejected systems do not repeatedly re-enter without new evidence.

NEXT ACTIONS  
1\. Finish Gen33.  
2\. At the Gen33 boundary, snapshot interim Round-2 findings.  
3\. Copy this roadmap into the repo as the durable project plan.  
4\. Perform the leaderboard/field harvest and create the candidate intake matrix.  
5\. Re-rank Membukkit, Claude-Mem, and new frontier candidates by distinct architectural question.  
6\. Select the next 3–5 Phase-2 contestants/ablations.  
7\. Continue longitudinal testing, external benchmark lanes, and then the composite prototype only when justified.

CHANGE LOG  
2026-09-02 — Initial durable Phase-2 roadmap created after Gen32 and during Gen33. Trigger: three-engine preregistered recurrence of the seven append-only longitudinal failures, new field/leaderboard evidence around state tracking, and recognition that the remaining queue should be refreshed before blindly continuing.  
