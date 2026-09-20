<!-- intake: drive id 1WS2vYz1fQt3lNXW8LcCi7bOvVXjfQ6g77Zyq7tRrmnI, name 'AGENT_MEMORY_INTEL_2026-09-20', modified 2026-09-20T14:03:06.979Z, fetched 2026-09-20T14:15:05Z, 15723 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-20
generated_at: 2026-09-20T07:01:54-07:00
lookback: approximately_previous_24_hours
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Daily Intelligence — 2026-09-20


## Executive Signal


- Agent Memory Challenge Cycle 2 is now OPEN. This is the highest-signal development today: AML has moved from an announced benchmark to an active standardized evaluation with separate Textual, Coding, and Multimodal tracks, common Add/Search interfaces, platform-controlled Answer/Eval, private evaluation data, version traceability, and independent review.
- The Cycle 2 benchmark contract is unusually relevant to the bake-off. Textual memory explicitly groups capabilities around Memory Cognition, Memory Evolution, and Memory Alignment; the published scope includes temporal reasoning, knowledge update, continual learning, personalization, abstention, and evidence governance. Coding Memory uses 150 software-engineering tasks under relevant-history and noisy-history conditions. Multimodal Memory approaches roughly 5,000 instances across seven data sources and nearly 800M tokens.
- AML’s first-cycle public leaderboard is itself a useful system-discovery surface. Current textual ranking shows MemoraX first (58.02), followed by MemOS (45.89), NTES-MEMORY-SMART (44.21), AML-Eval-FLASH (43.65), Cognee (42.61), NTES-MEMORY-MQ-LAYER (42.11), TencentDB (41.48), Mem0 (41.40), MemPalace (39.48), Vectorize Hindsight Cloud (38.54), and others. The large gap between MemoraX and the field merits inspection, but leaderboard rank is not general memory quality.
- A recent r/AI_Agents post reports a separate 12-system / 1,800-task comparison where Cognee and Karpathy’s Wiki tie at 97.1 accuracy, with Cognee roughly half the token cost but over five times slower. This conflicts sharply with AML’s first-cycle ordering, where Cognee is fifth and far below MemoraX. The discrepancy is valuable evidence that benchmark/task design dominates apparent “best memory system” claims.
- No equally strong new Reddit-native benchmark or memory architecture surfaced in the strict 24-hour scan. Today’s priority change is therefore benchmark surveillance and evaluation-contract comparison, not an immediate architecture change.


## Agent Handoff


PRIORITY CHANGES


- Evaluate Agent Memory Challenge Cycle 2 as an external benchmark/comparator for the memory-bake-off. Map its capability taxonomy and evaluation contract against our existing tests before considering participation or importing fixtures.
- Inspect the Cycle 1 leaderboard per-dimension results, especially MemoraX’s unusually large lead, and identify systems not already represented in our bake-off research inventory.
- Compare the 12-system r/AI_Agents benchmark methodology with AML. The contradictory Cognee placement is a useful natural experiment in benchmark sensitivity.


SYSTEMS TO INVESTIGATE


- MemoraX — primary source/discovery surface: https://agentmemories.ai/zh-cn/docs — Reason: 58.02 overall on AML Cycle 1, substantially ahead of the next system, with particularly strong explicit recall and broad capability scores.
- MemPalace — primary discovery surface: https://agentmemories.ai/zh-cn/docs — Reason: unfamiliar system in the top ten with a different capability profile, including relatively stronger epistemic-safety/privacy than several higher-ranked systems.
- NTES-MEMORY-SMART / NTES-MEMORY-MQ-LAYER / NTES-MEMORY-TDAM — primary discovery surface: https://agentmemories.ai/zh-cn/docs — Reason: multiple related entries suggest a family of memory approaches worth tracing to architecture/source material.


BENCHMARKS TO INVESTIGATE


- Agent Memory Challenge Cycle 2 / Agent Memory Leaderboard — https://agentmemoryleaderboard.ai/competition/ and https://agentmemories.ai/ — Reason: active standardized evaluation across textual, coding, and multimodal memory with a controlled Add/Search boundary and platform-owned downstream answer/eval.
- Independent 12-system Claude Code memory comparison — Reddit lead: https://www.reddit.com/r/AI_Agents/comments/1wjq4vh/i_tested_12_ai_memory_systems_across_1800_tasks_a/ — Reason: produces a radically different ordering from AML and exposes cost/latency tradeoffs alongside accuracy.


EXPERIMENTS TO CONSIDER


- AML-CONTRACT-MAP — Capability/failure mode: benchmark coverage and blind spots. Source: AML Cycle 2. Proposed adaptation: map each AML subcategory to bake-off cases and mark covered/partial/missing dimensions, especially transaction-time/effective-time, scope isolation, provenance, deletion/resurrection, and multi-agent boundaries.
- NOISY-HISTORY-CODING — Capability/failure mode: whether retrieved engineering experience helps under realistic distractor history. Source: AML Coding Memory. Proposed adaptation: run matched coding tasks with relevant history alone versus relevant+noise and measure both task outcome and memory evidence used.
- BENCHMARK-RANK-INVERSION — Capability/failure mode: overgeneralization from a single benchmark. Sources: AML Cycle 1 versus the 12-system r/AI_Agents comparison. Proposed adaptation: choose overlapping systems (at least Cognee and Mem0 if available) and compare rank under multiple benchmark families; record which capability assumptions cause reversals.
- PLATFORM-BOUNDARY-ISOLATION — Capability/failure mode: generation-model confounding. Source: AML’s standardized Add/Search candidate boundary. Proposed adaptation: where feasible, hold answer generation fixed across bake-off systems and separately score retrieval/memory evidence versus final task performance.


RESEARCH LEADS


- Determine exactly what changed in AML Cycle 2 versus Cycle 1, including any Streaming Memory protocol and whether event-time availability is enforced strongly enough to test temporal leakage.
- Trace MemoraX, MemPalace, and the NTES memory variants to papers/repos/product documentation and identify architectural novelty rather than leaderboard-only names.
- Investigate whether AML’s evidence-governance and memory-evolution dimensions can supply external validation for the bake-off’s harder temporal and provenance findings.
- Examine why Cognee ranks near the top in the 1,800-task Claude Code benchmark but fifth at 42.61 in AML textual evaluation. Candidate explanations include task type, agent autonomy in memory writes, answer model, memory-operation contract, latency/token budgets, and scoring definition.


## High-value findings


### Agent Memory Challenge Cycle 2 opened September 20


Signal: Research lead / high-value external evaluation development


What happened:
The Agent Memory Leaderboard’s second public challenge cycle is now open. The official platform fixes the evaluation boundary: participant systems own Add and Search, while AML controls Answer and Eval. Formal results bind to fixed system versions and combine public/private evaluation, with anomaly review and independent result review.


Evidence:
Primary official challenge pages and repository. The official site reports the cycle open September 20, 2026 and describes separate Textual, Coding, and Multimodal tracks. Participation is free, while entrants pay their own API/database/compute costs. Full evaluation closes in early November with official leaderboards planned for mid-November.


Why it matters to the bake-off:
AML is attempting exactly the cross-system comparability problem the bake-off repeatedly encounters. Its standardized downstream answer/evaluation pipeline reduces one important confound: different generation models and judges surrounding the memory layer. Its scope is broader than pure recall and includes temporal/evolution and evidence-governance concepts.


Recommended action:
Evaluate benchmark. Treat it as a complementary external benchmark, not a replacement for the bake-off’s deeper temporal, scope, and lineage tests.


Sources:
https://agentmemoryleaderboard.ai/competition/
https://agentmemories.ai/
https://github.com/AML-memory/agent-memory-leaderboard


### Cycle 1 leaderboard exposes unfamiliar systems and a large leader gap


Signal: Research lead


What happened:
The current first-cycle textual leaderboard places MemoraX at 58.02 overall, versus MemOS at 45.89 and a cluster around 41–44 including Cognee, TencentDB and Mem0. The leaderboard reports separate capability columns rather than only an aggregate score.


Evidence:
Official AML leaderboard.


Why it matters:
The leaderboard is now a practical discovery surface for systems the bake-off may not have examined. More importantly, capability-level columns allow comparison of where systems win rather than treating aggregate rank as architecture quality.


Recommended action:
Investigate unfamiliar top systems and capture their architecture, availability, licensing, and reproducibility status before deciding whether any deserve bake-off inclusion.


### Cognee’s rank inversion across two evaluations is itself useful evidence


Signal: Potentially new evaluation insight


What happened:
A September 18 r/AI_Agents post reports 1,800 tests across 12 memory systems using Claude Code/Opus 5, with Cognee and a Markdown wiki tied at 97.1 accuracy. Cognee reportedly used roughly half the wiki’s token cost but was over five times slower. In AML Cycle 1, Cognee ranks fifth at 42.61 overall, behind MemoraX, MemOS, NTES-MEMORY-SMART and AML-Eval-FLASH.


Evidence:
The Reddit benchmark is first-party/community evidence and needs methodology inspection. AML is a standardized public evaluation platform. The numerical scores are not directly comparable because the tasks and metrics differ.


Why it matters:
This is a concrete demonstration that “best memory system” is benchmark-dependent. Rank reversals should be studied rather than averaged away.


Recommended action:
Investigate further. Extract the 12-system benchmark methodology and compare dimensions, memory-write policy, agent model, context budget, and scoring with AML.


Reddit source:
https://www.reddit.com/r/AI_Agents/comments/1wjq4vh/i_tested_12_ai_memory_systems_across_1800_tasks_a/


## Benchmark & Leaderboard Watch


### Agent Memory Challenge Cycle 2


What it measures:
Three independent tracks: Textual Memory, Coding Memory, and Multimodal Memory. The official site describes capability groupings spanning retrieval/relational reasoning, temporal reasoning/knowledge update/continual learning, personalization/abstention/evidence governance. Coding Memory evaluates 150 software-engineering tasks under relevant and noisy history conditions. Multimodal evaluation spans seven data sources and approximately 5,000 instances.


What’s new:
Cycle 2 is now active rather than announced. It expands the shared evaluation arena across text, code, and multimodal memory and formalizes a fixed Add/Search participant boundary with platform-run Answer/Eval.


New/unfamiliar systems discovered from Cycle 1:
MemoraX, MemPalace, multiple NTES memory variants, AML-Eval-FLASH, memory-dense, memory-8000, and others.


Bake-off implication:
High. The evaluation contract and capability decomposition are worth mapping against our test matrix. Participation itself is secondary to understanding what AML measures well and what it omits.


## New Memory Systems Discovered


### MemoraX


Evidence:
Official AML Cycle 1 leaderboard; currently the top textual system by a substantial margin.


Why we care:
The gap is large enough to warrant architecture/source investigation, but no architectural superiority should be inferred from leaderboard position alone.


### MemPalace and NTES memory variants


Evidence:
Official AML Cycle 1 leaderboard.


Why we care:
These are unfamiliar entries that broaden the system inventory. They should be traced to primary sources before any evaluation decision.


## Emerging Patterns


The strongest pattern today is evaluation maturation rather than a new storage primitive. Multiple current sources are moving toward controlled comparisons that separate the memory layer from downstream generation and expose multiple dimensions: recall, temporal evolution, governance, task execution, token cost, latency, and robustness to noisy history.


At the same time, the Cognee rank inversion shows why this maturation matters: systems can look dominant under one workload and middling under another. A useful bake-off should therefore preserve per-capability failure signatures and avoid collapsing conclusions into a single universal leaderboard.


## New Resources


- Agent Memory Challenge Cycle 2: https://agentmemoryleaderboard.ai/competition/
- Agent Memory Leaderboard / participation material: https://agentmemories.ai/
- AML repository: https://github.com/AML-memory/agent-memory-leaderboard
- AML Cycle 1 leaderboard: https://agentmemories.ai/zh-cn/docs
- r/AI_Agents 12-system comparison: https://www.reddit.com/r/AI_Agents/comments/1wjq4vh/i_tested_12_ai_memory_systems_across_1800_tasks_a/


## Experiments Worth Stealing


### Relevant history vs noisy history


Experiment:
Run identical coding tasks with curated useful prior experience and with the same useful experience embedded in distracting history.


What it tests:
Whether memory retrieval selects actionable prior engineering experience rather than merely finding semantically similar history.


Why it is interesting:
It makes memory utility causal at the task level rather than measuring retrieval in isolation.


How we could adapt it:
Pair existing coding transcripts with controlled distractor episodes and compare success, retrieval payload, and evidence attribution.


### Fixed downstream answer model


Experiment:
Force all candidate memory systems to return evidence through a common interface, then use the same downstream answer model and evaluation procedure.


What it tests:
Memory-layer contribution independently of generation-model variation.


Why it is interesting:
Many published memory comparisons mix memory architecture with answer-model differences.


How we could adapt it:
Add a retrieval/evidence-only arm to selected bake-off tests alongside the existing end-to-end agent arm.


### Rank inversion audit


Experiment:
Take systems appearing in multiple benchmarks and explicitly compare rank order by benchmark family and capability.


What it tests:
Benchmark sensitivity and hidden assumptions.


Why it is interesting:
Cognee’s very different apparent standing across AML and the 12-system community benchmark provides a live example.


How we could adapt it:
Maintain a cross-benchmark matrix rather than a single score and identify which task families predict each reversal.


## Bottom Line


There is a meaningful priority change today: Agent Memory Challenge Cycle 2 is now live and should enter the research arm’s benchmark watch immediately. Its controlled Add/Search boundary, capability decomposition, noisy-history coding tests, and text/code/multimodal scope make it a useful external reference point for the bake-off.


The immediate action is not to stop current experiments or rush to submit. First map AML’s evaluation dimensions against our existing test matrix, inspect the unfamiliar top Cycle 1 systems, and use the Cognee rank inversion as a concrete case study in benchmark sensitivity.


Nothing found today warrants interrupting current implementation work, but AML Cycle 2 is important enough to add to active research priorities.