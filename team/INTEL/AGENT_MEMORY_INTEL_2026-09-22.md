<!-- intake: drive id 1GHya8cOICzZ7DCKSWaXp1RKOumji-B2kZjd7DHyc9hc, name 'AGENT_MEMORY_INTEL_2026-09-22', modified 2026-09-22T14:03:33.901Z, fetched 2026-09-22T14:15:14Z, 20434 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-22
generated_at: 2026-09-22T06:57:46-07:00
lookback: approximately_previous_24_hours
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Daily Intelligence — 2026-09-22


## Executive Signal


- MEX is the strongest new system lead today. A fresh r/AIMemory post surfaced MEX’s repository-native approach to coding-agent/team memory: canonical Markdown in Git, a local Tree-sitter/SQLite code graph, provenance and audit records, reviewed knowledge updates, structured handoffs, and code-grounding drift detection. The Reddit post announced 0.8.0, while the current primary repository is already at 0.8.2.
- MEX’s most interesting bake-off idea is not its headline token number; it is treating code as authority and using graph groundings to flag memory claims when referenced symbols change, move, or disappear. This suggests a concrete test of stale-but-historically-useful knowledge versus current operative state.
- The MEX performance evidence needs careful separation. The fresh Reddit microbenchmark reports 10.74× less returned context than grep top-3 (about 90.7% smaller) with 100% expected-symbol recall across six retrieval tasks, but explicitly says this is one repository and task set. A more rigorous, older blinded 12-task pilot in the primary repo reports 54.5% fewer new tokens and 7/12 correct answers versus 6/12 for files-only search. These are different evaluations and should not be conflated.
- A fresh r/RAG evaluation of Jev produced useful negative/positive evidence for cheap decision models. Jev matched DeepSeek V4 Flash’s 93.25% evidence Recall@5 on a 100-question search-stopping test while cutting median decision latency from 2.23s to 0.55s, but on MemSearch memory reranking it reached 79.41% Recall@5 versus 81.87% for Voyage rerank-3 and had no cost advantage. On multi-hop graph retrieval it beat GPT-4o-mini but trailed GPT-5-mini. This argues for testing decision models first as narrow gates/stop classifiers, not assuming they replace specialized rerankers or reasoning-heavy judges.
- A current r/AI_Agents discussion gives a useful adversarial fixture: temporary task state can become a “ghost blocker” if stored with the same durability/authority as architectural knowledge. The post is anecdotal rather than benchmark evidence, but the failure mode is concrete and directly testable.


## Agent Handoff


### PRIORITY CHANGES


- Add MEX 0.8.2 to candidate-system reconnaissance. Focus first on its code-grounding, provenance, review/promotion, staleness, and Git-canonical-memory mechanisms rather than running a full bake-off immediately.
- Add a small “decision-model gate” experiment to the evaluation backlog. Test cheap classifier-style models on narrow memory-control decisions separately from reranking and multi-hop reasoning.


These are modest queue changes. They do not justify interrupting current implementation work.


### SYSTEMS TO INVESTIGATE


- MEX 0.8.2
  Primary source: https://github.com/mex-memory/mex
  Reason: repository-native shared memory with canonical Markdown, code-linked groundings, provenance, explicit review/promotion, structured handoffs, local indexes, and drift signals tied to code changes.


### BENCHMARKS TO INVESTIGATE


- MEX graph retrieval / headless files-baseline evaluation
  Primary source: https://github.com/mex-memory/mex/blob/v0.8.2/evaluate/RESULTS.md
  Reason: small but unusually transparent evaluation with blind grading, token accounting, deterministic retrieval holdouts, and explicit interpretation limits. Useful more as a methodology/fixture source than as proof of general superiority.


- Jev × MemSearch / DeepSearcher / Vector Graph RAG evaluation
  Primary write-up: https://zc277584121.github.io/rag/2026/09/22/jev-search-deep-evaluation.html
  Primary graph-eval artifact: https://github.com/zilliztech/vector-graph-rag/pull/48
  Reason: directly tests a classifier-style decision model across simple stopping, memory reranking, and multi-hop graph filtering, exposing where cheap direct decisions work and where specialized or reasoning-capable models still lead.


### EXPERIMENTS TO CONSIDER


- CODE-GROUNDING-DRIFT
  Capability/failure mode: stale code-linked memory after implementation changes.
  Source: MEX.
  Proposed adaptation: seed a durable architectural explanation linked to specific symbols; then rename, move, modify, or delete those symbols. Require the memory layer to distinguish current operative knowledge, stale-but-historical explanation, intentional transition, and insufficient evidence rather than silently trusting or deleting the old note.


- TASK-STATE-CLOSURE
  Capability/failure mode: temporary working state survives after its task is complete and later masquerades as current project truth.
  Source: r/AI_Agents “Why Your Agent Keeps Bringing Up Things You Already Fixed.”
  Proposed adaptation: store a task blocker, then close the task through explicit completion evidence. In a later unrelated task, the blocker must not govern behavior; a historical query should still be able to recover it as past state.


- DECISION-MODEL-GATE
  Capability/failure mode: overusing cheap classifier-style models where implicit/multi-hop reasoning is required.
  Source: Jev evaluation.
  Proposed adaptation: on a fixed bake-off retrieval slice, compare a decision model, a specialized reranker, a small generative judge, and no-rerank baseline across direct relevance, conflicting evidence, and multi-hop relevance. Measure Recall@k, MRR, latency, cost, and confidence calibration separately.


- CONTEXT-REDUCTION-WITH-CORRECTNESS
  Capability/failure mode: mistaking smaller returned context for lower total agent cost or preserved task quality.
  Source: MEX’s fresh microbenchmark versus its older blinded headless pilot.
  Proposed adaptation: report at least three layers separately: returned retrieval context, total new tokens, and downstream task correctness. Do not let a retrieval-only compression number stand in for end-to-end efficiency.


### RESEARCH LEADS


- Can implementation evidence act as an authority signal for project memory without collapsing history into “whatever code says right now”?
- Can a cheap decision model handle write-side memory gates—novelty, duplicate detection, stale/active classification, accept/reject, or search stopping—better than it handles memory reranking?
- How should coding-agent memory represent a deliberate transition where both the historical rationale and new operative state are useful?
- Should task-state expiry be driven by elapsed time, explicit task closure, repository evidence, or a combination?


### NO-ACTION SIGNAL


Not applicable: there are concrete research/test actions today.


## High-Value Findings


### 1. MEX links durable project memory back to code evidence


Signal: Research lead / potentially useful architecture specimen


What happened:
A fresh r/AIMemory post announced MEX v0.8.0 and highlighted a local Tree-sitter/SQLite code graph plus a Markdown wiki for coding-agent continuity. Following the primary repository shows the project has already moved to MEX 0.8.2. The current design stores canonical project knowledge as structured Markdown with metadata, relations, sources, provenance, code groundings, and append-only audit records; rebuildable SQLite indexes remain local. Git carries canonical memory, while code remains authoritative for grounding checks.


Evidence:
- Reddit post: https://www.reddit.com/r/AIMemory/comments/1wjtloc/my_claude_code_kept_rereading_the_same_repo/
- Primary repository: https://github.com/mex-memory/mex
- Primary evaluation artifact: https://github.com/mex-memory/mex/blob/v0.8.2/evaluate/RESULTS.md


What is demonstrated:
The repository exposes the implementation, documented data model, evaluation harnesses, and a prior blinded headless comparison plus deterministic retrieval suites.


What the author claims today:
The fresh one-repository microbenchmark reports 10.74× less returned context than grep top-3, roughly 90.7% smaller, 100% expected-symbol recall across six retrieval tasks, and 5/5 real-agent tasks completed without fallback Read/Grep. The post explicitly labels this a small benchmark rather than a universal token-saving claim.


Important caveat:
The more rigorous primary evaluation currently published in evaluate/RESULTS.md was run August 19–20 on mex 0.7.2, not 0.8.2. It used 12 tasks with one repetition each and one model. Candidate results were 7/12 blind-correct versus 6/12 for files-only, with 54.5% fewer new tokens and 72.5% fewer processed tokens. These numbers support continued investigation but not a broad superiority claim.


Why it matters to the bake-off:
MEX offers a concrete implementation of a problem our temporal and supersession work keeps encountering: preserving historical explanation while detecting when its grounding no longer matches current implementation. Its explicit review/promotion flow is also a useful counterpoint to automatic memory capture.


Recommended action:
Investigate architecture and selectively import evaluation ideas before deciding whether to add MEX as a full system entrant.


### 2. Jev looks stronger as a narrow control-plane decision model than as a universal memory reranker


Signal: Potentially new insight / negative evidence


What happened:
A September 22 r/RAG post and linked primary write-up evaluated Jev across three search/retrieval roles.


Search stopping:
On 100 multi-hop questions, Jev and DeepSeek V4 Flash inspected the same search histories. Both reached 93.25% evidence Recall@5 with nearly identical search rounds. Median decision response time fell from 2.23s to 0.55s. This is evidence about the stopping decision, not a fourfold end-to-end agent speedup.


Memory reranking:
On MemSearch’s existing 2,172 questions in English and Chinese, BGE-M3 candidate order scored 74.71% Recall@5, Jev 79.41%, and Voyage rerank-3 81.87%. The author reports Voyage also ranked the useful memory higher and that Jev had no cost advantage in this test.


Graph relationship filtering:
On frozen 500-question samples from MuSiQue and HotpotQA, the associated Vector Graph RAG PR reports Jev above GPT-4o-mini but below GPT-5-mini. MuSiQue R@5: GPT-4o-mini 64.08, Jev 68.87, GPT-5-mini 73.00. HotpotQA R@5: GPT-4o-mini 90.90, Jev 93.50, GPT-5-mini 94.50. The PR explicitly notes MuSiQue is not an untouched holdout and that the cost/latency comparisons are not controlled cross-provider benchmarks.


Evidence:
- Reddit: https://www.reddit.com/r/Rag/comments/1wn5wba/i_tested_jev_for_search_stopping_memory_reranking/
- Primary write-up: https://zc277584121.github.io/rag/2026/09/22/jev-search-deep-evaluation.html
- Vector Graph RAG PR/evaluation: https://github.com/zilliztech/vector-graph-rag/pull/48


Why it matters to the bake-off:
This is unusually useful because it narrows the likely sweet spot for classifier-style “decision” models. Fast direct gates such as continue/stop may be a good fit; richer memory relevance decisions with implicit or multi-hop reasoning remain more questionable. That suggests evaluating small observer/classifier models by control-plane role rather than asking whether they are “good enough for memory” in the abstract.


Recommended action:
Run a role-separated gate/rerank experiment rather than replacing an existing reranker wholesale.


### 3. “Ghost blocker” is a clean working-memory versus durable-knowledge failure fixture


Signal: Interesting extension / adversarial-test idea


What happened:
A current r/AI_Agents discussion describes a coding agent resurfacing an old task blocker weeks after a human had completed and shipped the migration. The underlying problem, as framed by the author, is that moment-specific task state and durable project knowledge were stored with the same persistence and authority.


Evidence:
Anecdotal design discussion, not a controlled experiment:
https://www.reddit.com/r/AI_Agents/comments/1wmh2lg/why_your_agent_keeps_bringing_up_things_you/


Why it matters:
The scenario is concrete enough to turn into a deterministic fixture. It also tests more than TTL: an old blocker should stop governing current behavior when task-completion evidence exists, while remaining available as historical state.


Recommended action:
Add a small task-state-closure test to the temporal/supersession backlog.


## Benchmark & Leaderboard Watch


No major new general-purpose agent-memory benchmark or leaderboard surfaced in the strict daily window.


Two evaluation artifacts are nevertheless worth tracking:


1. MEX’s existing graph/headless evaluation is newly surfaced through today’s MEX post. It is transparent enough to mine for methodology, but its primary headless comparison predates the current 0.8.2 release and is small.


2. The Jev evaluations are new today and directly relevant to memory control-plane model selection. They should be treated as role-specific retrieval/search evidence, not as a memory-system leaderboard.


No previously tracked leaderboard result was found to have materially changed today.


## New Memory Systems Discovered


### MEX 0.8.2


Primary source:
https://github.com/mex-memory/mex


Architecture / key idea:
Repository-native project memory shared through Git. Canonical Markdown captures architecture, decisions, requirements, patterns, handoffs, sources, provenance, and code groundings; local SQLite/Tree-sitter structures provide retrieval and code relationships. Knowledge publication is explicitly review-oriented rather than silently promoted. Code-grounding drift is used as a signal that an explanation may need review.


Evidence:
Open implementation, primary documentation, a small current self-reported microbenchmark, and an older blinded 12-task headless evaluation plus deterministic retrieval tests.


Why we care:
It is close to the actual environment of coding-agent memory and directly operationalizes staleness, provenance, handoff, and code-grounded authority questions.


## Research Leads


- Test whether code-grounding drift should merely lower confidence, create a contradiction/supersession candidate, or trigger a separate review state.
- Compare explicit human-reviewed promotion (MEX-style) against automatic observer/distiller promotion on the same coding transcripts.
- Determine whether a cheap decision model can serve as a pre-write novelty/importance gate without introducing silent false negatives that permanently suppress valuable memory.
- Extend scope-isolation testing to team/coding memory: a shared repository memory can be correct at project scope while still leaking agent-private or task-private state if boundaries are weak.


## Emerging Patterns


A useful pattern is becoming clearer across several recent days of research: high-value memory systems are separating three different problems that older “RAG as memory” designs often blur together.


1. Canonical knowledge/state: what should persist and with what authority.
2. Evidence/grounding: why that knowledge is believed and whether its source is still valid.
3. Retrieval/control: what subset should reach the agent now, at what cost, and with what decision model.


MEX is interesting mostly because it makes the first two explicit in a coding repository. The Jev results are interesting because they show the third layer should itself be decomposed: search stopping, reranking, and multi-hop relationship filtering have different model requirements.


## New Resources


- MEX 0.8.2 — repository-native shared project memory:
  https://github.com/mex-memory/mex


- MEX graph/headless evaluation results:
  https://github.com/mex-memory/mex/blob/v0.8.2/evaluate/RESULTS.md


- MEX r/AIMemory launch/update discussion:
  https://www.reddit.com/r/AIMemory/comments/1wjtloc/my_claude_code_kept_rereading_the_same_repo/


- Jev search/memory/graph evaluation write-up:
  https://zc277584121.github.io/rag/2026/09/22/jev-search-deep-evaluation.html


- Jev r/RAG discussion:
  https://www.reddit.com/r/Rag/comments/1wn5wba/i_tested_jev_for_search_stopping_memory_reranking/


- Vector Graph RAG Jev evaluation PR:
  https://github.com/zilliztech/vector-graph-rag/pull/48


- Working-memory “ghost blocker” discussion:
  https://www.reddit.com/r/AI_Agents/comments/1wmh2lg/why_your_agent_keeps_bringing_up_things_you/


## Experiments Worth Stealing


### CODE-GROUNDING-DRIFT


Experiment:
Create a durable memory claim grounded to one or more code symbols. After capture, make controlled implementation changes: rename, move, behavior change, delete, or introduce a conflicting new implementation.


What it tests:
Whether the system can recognize that historical memory is no longer safely operative without erasing useful rationale.


Why it is interesting:
Most memory tests mutate text memories directly. This mutates the external evidence that gives a memory authority.


How we could adapt it:
Use a tiny synthetic repository and deterministic commits. Query both “what does the code do now?” and “why was the old design chosen?” after each mutation.


### TASK-STATE-CLOSURE


Experiment:
Store a temporary blocker tied to a task. Complete the task by explicit close event and repository evidence, then open an unrelated task later.


What it tests:
Lifecycle, disposition, and authority of working state versus durable knowledge.


Why it is interesting:
A simple TTL can pass accidentally. Explicit closure tests whether the system understands state transitions.


How we could adapt it:
Require the later agent not to treat the blocker as active while preserving it for a historical question.


### DECISION-MODEL-GATE


Experiment:
Use the same frozen candidate memories and compare a classifier-style decision model, specialized reranker, small generative model, and no-rerank baseline on direct relevance, contradiction, and multi-hop relevance cases.


What it tests:
Where cheap semantic decisions are adequate and where reasoning capacity matters.


Why it is interesting:
The fresh Jev evidence suggests performance changes substantially by role; a single aggregate “memory judge” score can hide that.


How we could adapt it:
Measure Recall@5, MRR, top-1 accuracy, latency, cost, and confidence calibration by case family. Add a selective-routing policy only after role-specific results are known.


### RETRIEVAL-COMPRESSION-ACCOUNTING


Experiment:
Compare a structural/code-graph retrieval method with grep/files and semantic retrieval under identical tasks.


What it tests:
Whether context compression actually reduces end-to-end agent cost while preserving task correctness.


Why it is interesting:
Returned-context reduction, model input token reduction, processed tokens, and task correctness can diverge substantially.


How we could adapt it:
Report each layer separately and repeat tasks enough to avoid treating one-run token variance as a system property.


## Bottom Line


There is a modest change to the research queue today.


MEX 0.8.2 deserves architecture reconnaissance because its code-grounded, provenance-aware, Git-native design attacks several hard coding-memory problems directly. The immediate value is likely in its mechanisms and test ideas, not in accepting its current benchmark headline.


The Jev evaluation is valuable negative as well as positive evidence: cheap decision models appear promising for narrow stopping/gating decisions, but today’s data does not support treating them as universal replacements for specialized memory rerankers or stronger multi-hop judges.


Recommended next steps for the fleet:
1. Inspect MEX’s data model, grounding/staleness logic, and evaluation harness.
2. Add CODE-GROUNDING-DRIFT and TASK-STATE-CLOSURE fixtures to the test-design backlog.
3. Run a small role-separated decision-model experiment before making any architectural commitment to classifier-style observers/rerankers.


Nothing found today warrants interrupting current implementation work.