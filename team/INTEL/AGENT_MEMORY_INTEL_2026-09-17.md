<!-- intake: drive id 1uKp4qY53R1bjJAuDhqmrkCOFpMg_HtoZzR9FFb8r9EY, name 'RAIMEMORY_DAILY_2026-09-17', modified 2026-09-17T22:31:29.283Z, fetched 2026-09-17T22:49:42Z, 21514 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: rAIMemory_daily_intelligence
report_date: 2026-09-17
generated_at: 2026-09-17T15:17:00-07:00
lookback: initial_backfill_2026-09-11_through_2026-09-17; primary_daily_window_previous_24_hours
status: complete
priority_change: yes
agent_action_recommended: yes


BACKFILL NOTE


This is the first run of the r/AIMemory intelligence pipeline. The primary daily window was approximately the previous 24 hours, but because no earlier daily reports exist, this run also performed a catch-up scan covering September 11–17, 2026. Older items below are explicitly treated as catch-up context rather than as events from the latest 24-hour window.


The latest-24-hour surface itself was quiet. One r/AIMemory post dated September 16 was indexed but had been removed; its surviving comments were insufficient to establish the underlying claim, so it is not used as evidence in this report.


# r/AIMemory Daily Intelligence — 2026-09-17


## Executive signal


- The strongest discovery is KnowledgeDrift. A September 14 r/AIMemory post introduced KnowledgeDrift v1; following the primary repository now reveals KnowledgeDrift v2, an offline, judge-free benchmark for software-development memory with 1,883 notes, 1,500 tested facts, 9,008 tasks, a twelve-operation mutation protocol, eight scored families, and explicit signal/token-efficiency scoring. This is unusually well aligned with the bake-off's interest in supersession, temporal state, contradiction, deletion, rationale, and non-recall failure modes.
- KnowledgeDrift v2 is worth evaluating as a benchmark and fixture source, but its headline reference system is Engram Alpha, from the same project author. The results are reproducible and receipt-backed, but comparative conclusions should be treated as first-party until independently reproduced.
- Engram Alpha is itself a potentially interesting candidate system: local-first graph memory with explicit replaces/conflicts-with edges, Tombstones, confidence-aware retrieval, append-only audit history, and mutation-oriented evaluation. Its architecture overlaps several bake-off concerns strongly enough to warrant inspection.
- adebench contributes a different evaluation idea: score what the client/model actually receives after ordering, composition, and truncation, rather than scoring retrieval hits in isolation. That is a useful orthogonal measurement layer for an agentic memory bake-off.
- KnowledgeDrift v2 explicitly incorporates design ideas from ForgetEval, a previously released judge-free benchmark of the memory control plane. The convergence of KnowledgeDrift, ForgetEval, and adebench suggests an emerging evaluation direction beyond simple recall: mutation correctness plus delivered-context quality and efficiency.


## Agent Handoff


PRIORITY CHANGES


- Add KnowledgeDrift v2 to the benchmark-evaluation queue. Compare its task families and mutation protocol against the bake-off's existing continuity, temporal, supersession, scope, and contradiction tests. Prefer importing useful fixtures or dimensions before adopting its aggregate score wholesale.
- Add a delivered-context evaluation layer inspired by adebench to the experiment backlog: measure the memory text that actually reaches the agent under a fixed context budget and realistic competing tool-output pressure.


SYSTEMS TO INVESTIGATE


- Engram Alpha
  Primary source: https://github.com/techtheist/engram
  Reason: explicit supersession, conflict edges, tombstones, confidence-aware recall, audit history, local operation, and a benchmark-driven development process make it unusually aligned with the bake-off's harder memory dimensions.


BENCHMARKS TO INVESTIGATE


- KnowledgeDrift v2
  Primary source: https://github.com/techtheist/knowledgedrift
  Reason: judge-free 9,008-task benchmark that exercises mutation/control-plane behavior, rationale, temporal queries, contradictions, deletion, lineage and delivered-token efficiency rather than recall alone.


- adebench
  Primary source: https://github.com/adecubed/adebench
  Reason: evaluates what the client actually receives after ordering and truncation; useful for detecting a class of failure that retrieval-only metrics miss.


- ForgetEval / Control-Plane Placement Shapes Forgetting
  Primary source: https://arxiv.org/abs/2606.15903
  Reason: 1,000 templated plus 385 adversarial cases centered on supersede/release/purge and control-plane placement; directly relevant benchmark lineage for mutation correctness.


EXPERIMENTS TO CONSIDER


- KD-MUTATION-SUBSET
  Capability/failure mode: supersession, contradiction, deletion/resurrection, rationale, temporal state.
  Source: KnowledgeDrift v2.
  Proposed adaptation: map a small deterministic subset of KnowledgeDrift operations into the existing bake-off runner and compare failure signatures, not just aggregate score.


- DELIVERED-CONTEXT-DOOR
  Capability/failure mode: retrieved evidence is lost during memory composition or context-budget truncation.
  Source: adebench.
  Proposed adaptation: score the exact text presented to the agent after the memory system's final composition step, under both normal and high competing-tool-output pressure.


- BENCHMARK-OWNER-BIAS CHECK
  Capability/failure mode: benchmark taxonomy or scoring inadvertently favors the author's own architecture.
  Source: KnowledgeDrift/Engram relationship.
  Proposed adaptation: run multiple deliberately simple baselines and at least one independently designed system; inspect per-family failures before accepting the headline score.


- HONEST-CAPABILITY-N/A
  Capability/failure mode: systems are penalized opaquely for operations their APIs do not expose, making heterogeneous comparisons misleading.
  Source: KnowledgeDrift v2 and ForgetEval.
  Proposed adaptation: have each adapter declare supported mutation capabilities and distinguish unsupported/N/A from attempted-and-failed.


RESEARCH LEADS


- Audit whether KnowledgeDrift v2 now covers authority, provenance, scope and disposition explicitly. The original r/AIMemory v1 discussion identified these as important gaps because a newer or semantically closer record is not necessarily the governing record.
- Compare KnowledgeDrift's deterministic grading with the bake-off's current judge/critic mechanisms. Its judge-free design may offer useful tests that are cheaper and easier to reproduce.
- Examine whether delivered-context quality should become a first-class bake-off metric distinct from retrieval quality.
- Revisit forgetting/resurrection tests: ForgetEval measures mutation taking effect, while a harder production case is whether a deleted fact stays deleted after later consolidation or source re-ingestion.


## High-value findings


### KnowledgeDrift progressed from a Reddit benchmark proposal to a materially broader v2


Signal: Research lead / potentially new evaluation insight


What happened:
On September 14, an r/AIMemory post introduced KnowledgeDrift v1 as an attempt to move beyond "did the fact come back?" evaluation. Its categories included retrieval, signal-to-noise, abstention, currency, contradiction, drift, deletion, rationale and temporal behavior. The post reported first-party comparisons against Mem0 and LangMem and linked an open repository.


Following that repository now shows KnowledgeDrift v2 rather than merely the v1 described in the Reddit post. The current README describes an offline, judge-free software-development-memory benchmark using a seeded invented world, a twelve-operation protocol and deterministic pass/fail rules. At the 1,500-fact rung it reports 1,883 notes and 9,008 tasks. Its score combines eight family scores with capped signal and token-efficiency bonuses.


Evidence:
- Reddit discussion and original v1 results:
  https://www.reddit.com/r/AIMemory/comments/1wg074z/creating_a_new_ai_memory_benchmark_knowledgedrift/
- Current primary repository:
  https://github.com/techtheist/knowledgedrift


Why it matters to the bake-off:
The benchmark exercises several dimensions the bake-off has already found difficult and important: changed decisions, stale facts, contradiction, mutation, deletion/tombstone behavior, temporal questions, rationale/lineage, and the amount of irrelevant material delivered with the answer. It is therefore useful both as an external comparator and as a source of adversarial fixtures.


Recommended action:
Evaluate benchmark. Do not adopt the aggregate ranking blindly. First map its families and operations onto our existing taxonomy and inspect overlap, missing dimensions, and scoring assumptions.


Methodological caution:
The reference system in the v2 ladder is the author's Engram system. That does not invalidate the benchmark, especially because the artifacts and receipts are public, but independent reproduction is important. Also, v2's software-project world is deliberately synthetic; production validity still needs separate evidence.


### KnowledgeDrift's current ladder exposes why aggregate recall is insufficient


Signal: Interesting extension


The v2 primary repository reports, at the 1,500-fact rung, a reference-system score of 801 with 69% raw success, while a whole-file-in-context baseline reports 71% raw success but only a 390 score because it delivers roughly 404,000 tokens per answer. A TF-IDF title/snippet baseline reports lower success (43%) but a 580 score because it is extremely token-efficient. Vector top-k and LangMem are both reported at 48% success / 359 score; Mem0 at 44% / 348; MemContinuum at 44% / 380.


The important observation is not the exact ordering. It is the decomposition: presence of the right information, support for mutation-specific families, and the cost/noise of delivering it are treated as separate phenomena.


Why it matters:
The bake-off should be careful not to reward a system simply for making the answer technically retrievable if the agent must consume a large noisy payload or if the system cannot represent the operation under test.


Recommended action:
Borrow the decomposition, not necessarily the scoring weights.


### adebench measures the memory "door," not just retrieval


Signal: Potentially new insight


What happened:
A September 13 r/AIMemory post described adebench, a benchmark built around the text a client actually receives from memory after composition, ordering and truncation. In the reported comparison, both systems were cut to a 2,400-character door and also tested under simulated pressure from large MCP tool responses.


The author reports that changing retrieval can improve recall while worsening repeated chunks in the delivered context, and that a two-step retrieval path can perform differently from a one-call composed path under the same final context budget.


Evidence:
- r/AIMemory discussion:
  https://www.reddit.com/r/AIMemory/comments/1wffx8s/i_benchmarked_my_assistants_memory_against_garry/
- Repository:
  https://github.com/adecubed/adebench


Why it matters to the bake-off:
This separates "the store found it" from "the agent actually saw it." For an agentic memory system, the latter is often the operational truth. A benchmark that stops at retrieval may miss failures introduced by ranking, composition, summaries, entity cards, truncation, tool traffic, or context packing.


Recommended action:
Add evaluation case. Implement a minimal delivered-context metric around existing bake-off systems before considering a larger adebench integration.


Caveat:
The published comparison uses the author's own golden set and memory system, with gbrain consuming already-distilled facts in that run. Treat the method as the important contribution, not the reported winner.


### Engram Alpha surfaced as a system worth inspecting


Signal: Research lead


System:
Engram Alpha


Primary source:
https://github.com/techtheist/engram


Architecture / key idea:
A local-first graph memory for software-development agents. The current primary source describes explicit "replaces" and "conflicts-with" relationships, Tombstones for deliberately removed knowledge, a local NLI conflict checker, confidence-aware retrieval with strong/weak/none verdicts, code-reference drift tracking, an append-only audit journal, and MCP access shared across coding assistants.


Evidence:
The claims and benchmarks are first-party but unusually inspectable: code, evaluation harnesses and benchmark outputs are published in the repository. The repository also reports LongMemEval-related retrieval tests and supersession ablations.


Why we care:
Even if Engram never becomes a bake-off entrant, it is a useful architecture specimen because it represents several memory behaviors explicitly rather than delegating them to vector similarity or prompt reasoning.


Recommended action:
Investigate further. A researcher should inspect the mutation model and adapter surface before deciding whether it merits a full bake-off run.


### ForgetEval provides relevant control-plane benchmark lineage


Signal: Known/reinforcing / research resource


Primary source:
https://arxiv.org/abs/2606.15903


The June 2026 paper "Control-Plane Placement Shapes Forgetting" introduces ForgetEval: a 1,000-case templated suite plus a 385-case adversarial layer, with deterministic substring scoring and an adapter protocol for heterogeneous memory systems. It compares thirteen configurations and focuses on where LLM reasoning is placed around supersede, release and purge operations.


This is not a new item from the latest Reddit window, but KnowledgeDrift v2 explicitly cites ForgetEval design rules, making it relevant benchmark lineage discovered during the backfill.


Why it matters:
It reinforces the idea that the memory control plane deserves separate evaluation from recall and provides a source of adversarial forgetting/mutation cases.


Recommended action:
Add to research library and compare its mutation taxonomy against existing bake-off temporal/deletion tests.


## Benchmark & leaderboard watch


### KnowledgeDrift v2


What it measures:
- retrieval in a changing software-project world
- changed/current decisions
- contradictions and suspect discovery
- deletion / release / purge behavior
- rationale / lineage
- temporal recall
- path-oriented recall
- signal-to-noise and delivered-token efficiency


What's new relative to the Reddit v1 post:
The live repository now identifies the benchmark as v2, expands the protocol to twelve operations and reports 9,008 tasks at the 1,500-fact rung. It also explicitly credits ForgetEval design rules and provides capability-aware N/A handling.


New/unfamiliar systems discovered:
- Engram Alpha / reference system
- MemContinuum appears in the current comparison set alongside Mem0, LangMem and cognee


Bake-off implication:
High. This should be compared directly against our current test taxonomy. The benchmark appears closest to our interest in state transitions and memory correctness rather than pure retrieval.


### adebench


What it measures:
The final "door" presented to the client: exact delivered text after retrieval, ordering, composition and cut, optionally under competing context pressure.


What's new:
The measurement unit is downstream of retrieval.


Bake-off implication:
Medium-high. This is likely best adopted as a cross-cutting measurement layer rather than a replacement benchmark.


## New memory systems discovered


### Engram Alpha


Primary source:
https://github.com/techtheist/engram


Key idea:
Make memory mutations and relationships explicit in an inspectable graph, including supersession, conflict, tombstones, trust and provenance-like audit history.


Evidence:
Open repository plus first-party deterministic evaluation. The same project is the current KnowledgeDrift reference system, so independent bake-off testing would be valuable.


Why we care:
Architecture strongly overlaps the dimensions where simple RAG-style memory systems often fail.


### ADE Brain


Primary evaluation source:
https://github.com/adecubed/adebench


Key idea:
A three-level personal-assistant memory described by its author: working state, episodic task memory, semantic distilled facts, plus a knowledge graph and entity cards.


Evidence:
First-party benchmark runs and adapter examples; the system is primarily relevant here because it motivated adebench's delivered-context evaluation methodology.


Why we care:
Not necessarily a priority entrant, but useful as an example of a memory stack that treats client-facing composition as a measurable system component.


## Emerging patterns


Three independent-looking threads now converge on a broader evaluation model:


1. Recall is only one plane.
2. Memory mutation/control-plane behavior must be tested directly.
3. Retrieval success is not equivalent to useful agent context.
4. Noise, token budget, ordering and truncation are measurable parts of memory quality.
5. Heterogeneous systems need capability-aware comparisons so unsupported operations are not confused with failed implementations.


This convergence is more significant than any single leaderboard position.


## New resources


- KnowledgeDrift v2 — judge-free software-project memory benchmark:
  https://github.com/techtheist/knowledgedrift


- Engram Alpha — inspectable local graph memory:
  https://github.com/techtheist/engram


- adebench — client-delivered memory benchmark:
  https://github.com/adecubed/adebench


- ForgetEval paper / control-plane placement study:
  https://arxiv.org/abs/2606.15903


- r/AIMemory KnowledgeDrift discussion:
  https://www.reddit.com/r/AIMemory/comments/1wg074z/creating_a_new_ai_memory_benchmark_knowledgedrift/


- r/AIMemory adebench/gbrain comparison:
  https://www.reddit.com/r/AIMemory/comments/1wffx8s/i_benchmarked_my_assistants_memory_against_garry/


## Experiments worth stealing


### Mutation protocol replay


Experiment:
Feed a fixed invented project world into each memory system, then apply explicit operations such as supersede, release, purge, endorse and settle before probing current state, lineage and contradiction behavior.


What it tests:
Whether the memory system represents state changes rather than merely accumulating retrievable text.


Why it is interesting:
This attacks the gap between retrieval benchmarks and actual long-running agent memory.


How we could adapt it:
Create a compact bake-off-native protocol using our existing temporal/supersession fixtures, then compare results with KnowledgeDrift's task-family definitions.


### Delivered-context pressure


Experiment:
Measure the exact memory text delivered to the model under a fixed memory budget, then repeat while injecting realistic competing tool-response volume.


What it tests:
Whether useful memories survive ranking, composition and truncation.


Why it is interesting:
A system can retrieve the right fact and still operationally fail if the composition layer removes it.


How we could adapt it:
Instrument each bake-off adapter at the last boundary before model context and score both evidence presence and irrelevant delivered bytes/tokens.


### Resurrection after deletion


Experiment:
Delete or tombstone a fact, then later re-ingest source material or run background consolidation before asking again.


What it tests:
Whether deletion persists through subsequent maintenance rather than succeeding only immediately after the mutation.


Why it is interesting:
ForgetEval measures important control-plane operations but this harder resurrection case is closer to production background-memory behavior.


How we could adapt it:
Add a multi-phase delete → maintenance/re-ingestion → recall sequence to the temporal mutation suite.


### Authority versus recency


Experiment:
Give the system a newer but less-authoritative record that conflicts with an older governing decision.


What it tests:
Whether "newer" is incorrectly treated as "current."


Why it is interesting:
The original KnowledgeDrift Reddit discussion explicitly surfaced authority, scope, provenance and disposition as dimensions beyond semantic contradiction.


How we could adapt it:
Use our continuity fixtures to separate effective time, authority, scope and supersession and require reasoned abstention when no governing record can be established.


## Bottom line


Today's strict 24-hour r/AIMemory window did not produce a verified development that should interrupt ongoing work. The initial backfill nevertheless found a high-value research path: KnowledgeDrift has already evolved beyond the v1 Reddit announcement into a v2 benchmark that is unusually close to the bake-off's difficult dimensions.


Recommended change to current priorities:
Yes, but modestly. Assign a research task to evaluate KnowledgeDrift v2 and its relationship to Engram, then identify fixtures/metrics worth importing. Separately, prototype an adebench-style delivered-context measurement at the final memory-to-agent boundary.


Nothing found warrants stopping current experimental work. The best action is to feed these into the research and test-design queues.