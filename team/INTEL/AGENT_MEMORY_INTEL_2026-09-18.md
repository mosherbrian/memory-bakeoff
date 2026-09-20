<!-- intake: drive id 1XFRoZpyQmUpR8-XkDK8TXaDB0hf66qnnX5ye1OXIGUE, name 'AGENT_MEMORY_INTEL_2026-09-18', modified 2026-09-18T14:00:34.954Z, fetched 2026-09-18T14:15:02Z, 12152 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-18
generated_at: 2026-09-18T07:00:00-07:00
lookback: approximately_previous_24_hours
status: complete
priority_change: no
agent_action_recommended: yes


# Agent Memory Daily Intelligence — 2026-09-18


## Executive Signal


- The strict September 17–18 scan was quiet for new memory benchmarks or systems in the designated communities. No verified new benchmark release or leaderboard change warrants changing the bake-off's current priorities today.
- The most useful fresh signal came from an active r/RAG technical thread: commenters independently highlighted two evaluation-integrity failures—stale gold-set identifiers after re-indexing, and bugs/drift in the evaluator itself. Both can produce clean-looking but false benchmark results.
- That thread also reinforced that recall@k alone is insufficient: rank-sensitive metrics such as MRR/nDCG and explicit unanswerable/false-premise cases expose failures that hit-rate can hide.
- A long-horizon multi-agent simulation discussion outside the core feeds produced one adjacent research lead: agents reportedly maintain a never-compressed, self-editable “soul” memory layer. The underlying post was removed and discussion contains contested framing, so this is a weak lead rather than evidence—but the architecture suggests a useful immutable-vs-mutable-core-memory experiment.
- No reason to interrupt current bake-off work. Add two cheap evaluation-harness guardrails and keep monitoring.


## Agent Handoff


PRIORITY CHANGES


NONE


SYSTEMS TO INVESTIGATE


NONE


BENCHMARKS TO INVESTIGATE


NONE newly verified in the strict daily window.


EXPERIMENTS TO CONSIDER


- EVAL-CANARY
  Capability/failure mode: evaluator/checker corruption or drift silently invalidates benchmark scores.
  Source: r/RAG discussion on September 17, 2026.
  Proposed adaptation: before every bake-off sweep, run a tiny immutable set of hand-verified pass/fail cases through the evaluator; abort or flag the sweep if the checker fails any canary.


- GOLD-ID-DRIFT
  Capability/failure mode: re-indexing/re-ingestion changes internal identifiers and makes a frozen gold set point at stale records, falsely lowering retrieval scores.
  Source: r/RAG offline-RAG evaluation thread.
  Proposed adaptation: add an integrity check that resolves every expected gold reference against the current corpus/index before scoring; distinguish corpus/eval-key drift from retrieval failure.


- RANK-AWARE-RETRIEVAL
  Capability/failure mode: correct memory appears somewhere in top-k but too low to be operationally useful.
  Source: r/RAG discussion.
  Proposed adaptation: report MRR or another rank-sensitive measure alongside hit/recall, and nDCG where multiple memories are legitimately relevant.


- CORE-MEMORY-MUTABILITY
  Capability/failure mode: a persistent never-compressed identity/core-memory layer accumulates stale or self-reinforcing state.
  Source: September 17 long-horizon simulation discussion; weak evidence.
  Proposed adaptation: compare immutable, append-only, and self-editable core-memory policies under long-horizon contradictory experience and deliberate poisoning/supersession.


RESEARCH LEADS


- Determine whether the bake-off evaluator already has immutable hand-verified canaries independent of system fixtures. If not, add them before expanding benchmark breadth.
- Audit whether any current bake-off gold references depend on unstable store/index IDs rather than source-stable semantic identifiers.
- Consider separating retrieval presence from retrieval rank and from final delivered-context presence; yesterday's adebench lead and today's rank-metric discussion point in the same direction.
- Long-horizon “core identity” memory deserves a small architecture probe, but do not infer behavioral conclusions from the removed simulation post without primary artifacts.


## High-value findings


### Evaluation harnesses need their own regression tests


Signal: Interesting extension


What happened:
A technically detailed r/RAG thread about an offline RAG system received fresh September 17 comments focused on evaluation reliability. The original author reported that an apparent 47% recall result for one book jumped to 97.6% after discovering that the frozen gold set referenced stale chunk keys from before a re-index. A commenter separately described keeping a small immutable hand-verified set that runs before every evaluation sweep so checker bugs are detected before trusting aggregate numbers.


Evidence:
This is practitioner evidence from a concrete evaluation workflow, not a formal paper. The thread includes measured retrieval numbers and a specific diagnosed failure mechanism.


Why it matters to the bake-off:
Memory-system research can spend enormous effort interpreting apparent model/system failures that are actually evaluator failures. As the bake-off accumulates adapters, generations, sealing logic, fixture transformations and benchmark imports, the evaluator itself becomes part of the experimental apparatus and needs an independent reference standard.


Recommended action:
Add evaluation case / harness guardrail. A tiny immutable canary suite is cheap and should fail closed before expensive runs proceed.


Source:
https://www.reddit.com/r/Rag/comments/1wfzp1a/fully_offline_rag_over_27_technical_books_11k/


### Gold-set identity drift can masquerade as retrieval failure


Signal: Potentially new insight for evaluation operations


What happened:
The same r/RAG experiment exposed a concrete provenance problem: after re-indexing, the evaluator's stored chunk keys no longer matched the current index. The retriever was finding the correct book/content neighborhood, but the scorer treated it as failure because expected IDs were stale.


Evidence:
First-person debugging report with before/after numbers in the thread. It is not independently reproduced, but the mechanism is straightforward and testable.


Why it matters:
This is especially relevant to a bake-off that repeatedly transforms corpora and adapters. A benchmark should ideally bind expected evidence to stable source identity/content semantics, not ephemeral vector-store IDs.


Recommended action:
Audit evaluator. Before scoring, validate all gold references against the current corpus and emit a distinct integrity error rather than a system failure when references cannot resolve.


### Rank-sensitive metrics are a useful bridge between retrieval and delivered context


Signal: Known/reinforcing


Fresh comments in the r/RAG thread argued that recall@k only establishes that relevant evidence appears somewhere in a retrieval window. MRR captures how early the first useful result appears; nDCG is more appropriate when several results have graded relevance. This reinforces yesterday's adebench discovery: retrieval presence, retrieval ordering, and final delivered context are separate planes.


Bake-off implication:
Do not replace existing capability tests with IR metrics, but use rank-sensitive metrics as diagnostics for systems with retrieval APIs. Then separately measure whether the relevant evidence survives composition/truncation into the model's context.


Recommended action:
Add diagnostic metrics where adapters expose ranked retrieval.


## Benchmark & Leaderboard Watch


No newly verified agent-memory benchmark release, material leaderboard update, or unfamiliar high-confidence benchmark entrant was found in the designated communities during the strict daily window.


Carry-forward items from the September 17 backfill remain active research leads rather than today's discoveries:
- KnowledgeDrift v2
- adebench
- ForgetEval


No new evidence today changes their priority or interpretation.


## New Memory Systems Discovered


No new system met the evidence threshold for inclusion today.


A removed long-horizon simulation discussion described each simulated agent as having a never-compressed, self-editable “soul” memory layer. Because the source post was removed and the discussion's behavioral claims were contested, the implementation is retained only as an architectural research lead, not promoted as a discovered system.


## Research Leads


### Core memory as a separate mutation regime


Question:
Should an agent's highest-priority persistent memory obey different write, compression, provenance, and supersession rules from ordinary episodic/semantic memory?


Why interesting:
A never-compressed layer protects continuity from summarization loss, but self-editability can create stale identity state, lock-in, poisoning, or self-reinforcing beliefs. Conversely, making it immutable can prevent legitimate evolution.


Proposed bake-off probe:
Hold retrieval constant and compare three core-memory policies: immutable, append-only with explicit supersession, and free self-editing. Subject each to contradictory experience, adversarial injected memories, long delays, and later corrections.


## Emerging Patterns


The last two daily investigations now point toward a useful three-plane evaluation model:


1. Store/control-plane correctness — was memory formed, mutated, superseded, deleted and scoped correctly?
2. Retrieval quality — was the right evidence retrieved, and how highly was it ranked?
3. Delivered-context quality — after composition, ordering and truncation, did the agent actually receive the evidence without excessive noise?


Today's additional lesson is that a fourth concern sits underneath all three: evaluator integrity. A broken gold mapping or checker can make every higher-level conclusion wrong.


## New Resources


- Fresh r/RAG evaluation-integrity discussion:
  https://www.reddit.com/r/Rag/comments/1wfzp1a/fully_offline_rag_over_27_technical_books_11k/


- Removed long-horizon multi-agent simulation discussion retained only as a weak architectural lead:
  https://www.reddit.com/r/AgentsOfAI/comments/1whx5cj/removed/


## Experiments Worth Stealing


### Immutable evaluator canaries


Experiment:
Maintain a very small set of manually verified inputs with known evaluator outputs. Run these before every benchmark sweep.


What it tests:
The measurement apparatus itself.


Why it is interesting:
It prevents time being wasted interpreting system regressions that were caused by scoring code, parsing changes, fixture drift or judge changes.


How we could adapt it:
Make the canary set independent of any memory-system adapter and require 100% pass before accepting a sealed generation.


### Stable-evidence identity check


Experiment:
After any re-ingestion, re-index or fixture regeneration, resolve all expected evidence references before running systems.


What it tests:
Whether the benchmark's gold set still describes the corpus being evaluated.


How we could adapt it:
Prefer source-stable IDs derived from corpus identity/location/content over vector-store row IDs; fail with BENCHMARK_INTEGRITY rather than SYSTEM_FAIL when gold evidence is missing.


### Four-layer outcome trace


Experiment:
For selected failures, preserve a trace of: stored state → ranked retrieval → composed/delivered context → final answer.


What it tests:
Where memory information was actually lost.


How we could adapt it:
Use the trace diagnostically on a small representative subset rather than adding expensive instrumentation to every case initially.


## Bottom Line


No change to current research priorities.


The strict daily scan was quiet for genuinely new systems and benchmarks. The useful result is methodological: add an evaluator canary and a gold-reference integrity check if the bake-off does not already have them. These are cheap safeguards against false experimental conclusions.


Continue the previously identified KnowledgeDrift v2 and delivered-context investigations; nothing found today warrants interrupting ongoing experimental work.