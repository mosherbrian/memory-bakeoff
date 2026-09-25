<!-- intake: drive id 1eoMJNX5gVPa7_c41Ze9gS-S7WrD_Tqsd-rsH83D_vTM, name 'AGENT_MEMORY_INTEL_2026-09-24', modified 2026-09-24T14:05:10.874Z, fetched 2026-09-24T14:15:02Z, 19257 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-24
generated_at: 2026-09-24T06:59:28-07:00
lookback: approximately_previous_24_hours
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Daily Intelligence — 2026-09-24


## Executive Signal


- The strongest fresh primary-source development is Total Agent Memory (TAM) v14.5.0, released September 23. Its authors cross-graded TAM and Mem0 Platform answers on the same held-out LoCoMo and LongMemEval-S questions using matched judge configurations and report no statistically significant same-answer-model difference on that subset. This is useful evidence, but not a neutral leaderboard or demonstrated equivalence: the comparison is self-authored, the split was not scored blind, and the repository discloses tuning history.
- The more consequential finding is benchmark instrumentation. TAM’s published three-seed LoCoMo analysis reports that the generator answer changed across seeds on 12.5% of questions, the judge verdict changed on 5.1%, and the judge flipped on an identical answer 2.7% of the time. Two deterministic guard fixes moved the reported overall score from 0.645 to 0.579. This is directly relevant to the bake-off: evaluator stability should be measured as a first-class property rather than inferred from a stable aggregate.
- TAM’s releases over the preceding 48 hours expose two concrete write-side memory hazards that are excellent adversarial fixtures. A simple opt-in supersession heuristic would have falsely retired 138 records in a real 5,128-record store; an earlier near-duplicate dedup rule dropped 36 of 455 legitimate FactConsolidation updates because only one critical value changed.
- A fresh r/ClaudeCode handoff pattern adds a useful continuity test: the writer verifies that the handoff actually persisted, marks verified facts separately from hypotheses, and the receiving session re-checks mutable state such as PIDs, logs and exit codes instead of blindly trusting a stale “done.”
- No new benchmark launch or leaderboard today is strong enough to interrupt ongoing implementation. The actionable change is to harden the bake-off evaluator and add mutation/control-plane adversarials.


## Agent Handoff


### PRIORITY CHANGES


- Add a judge/evaluator stability audit to the bake-off. Persist model answers, grade the exact same answer set repeatedly, measure identical-answer verdict flip rate, and use deterministic guards for cases that are rules rather than judgments.
- Add explicit write-side mutation adversarials for false supersession and update-killing deduplication. Score false retirement separately from missed retirement.


### SYSTEMS TO INVESTIGATE


- Total Agent Memory (TAM) v14.5.0
  Primary source: https://github.com/vbcherepanov/total-agent-memory
  Reason: fresh September 23 release with reproducible cross-grading tooling, local retrieval/write path, temporal knowledge graph and unusually transparent failure reports around evaluator noise, supersession and deduplication.


### BENCHMARKS TO INVESTIGATE


NONE — no wholly new benchmark or leaderboard surfaced today with stronger evidence than the benchmark-methodology findings below. Continue existing surveillance of Glasshouse, AML Cycle 2, KnowledgeDrift, ForgetEval and related benchmarks without elevating a new one today.


### EXPERIMENTS TO CONSIDER


- JUDGE-INSTRUMENT-STABILITY
  Capability/failure mode: evaluator nondeterminism and false-positive judging.
  Source: TAM LoCoMo three-seed analysis.
  Proposed adaptation: store one fixed answer corpus, re-grade it across repeated seeds/runs, report identical-answer verdict flip rate and score shifts before accepting small benchmark deltas.


- SUPERSESSION-OVERREACH
  Capability/failure mode: an update detector retires independent facts that share a subject or opening phrase.
  Source: TAM v14.4.0 supersession analysis.
  Proposed adaptation: pair true single-valued replacements with simultaneously valid sibling attributes such as “likes jazz” and “likes rock”; measure false retirement separately from failure to supersede.


- DEDUP-KILLS-UPDATE
  Capability/failure mode: near-duplicate suppression discards a legitimate state change.
  Source: TAM v14.3.1 regression report.
  Proposed adaptation: create nearly identical records differing in exactly one governing value; require the system to retain the update semantics rather than treating the new record as a duplicate.


- HANDOFF-MUTABLE-REVALIDATION
  Capability/failure mode: cross-session handoff treats mutable operational state as durable fact.
  Source: fresh r/ClaudeCode handoff-skills discussion.
  Proposed adaptation: persist a handoff containing both stable facts and mutable claims, change the mutable state between sessions, and require the receiving agent to trust stable verified facts while revalidating mutable ones. Also require the producing agent to read back storage before declaring the handoff complete.


### RESEARCH LEADS


- Measure the bake-off’s current evaluator flip rate on identical answers before trusting small score differences between memory systems.
- Cross-grade competing systems under exactly the same question subset, answer model, judge model, prompt, retry policy and deterministic guards; report any remaining non-equivalent protocol details explicitly.
- Treat supersession as a typed semantic operation, not merely similarity plus recency. Explore how systems distinguish replacement from multiple simultaneously true values.
- Consider typed handoff claims: stable verified fact, hypothesis, unresolved item, and mutable operational state that expires or demands revalidation.


## High-Value Findings


### Total Agent Memory v14.5.0 publishes a same-question cross-grade against Mem0


Signal: Research lead / useful comparative methodology


What happened:
Total Agent Memory’s primary repository marks v14.5.0 as released September 23, 2026. It grades Mem0 Platform’s published per-question answers and TAM’s answers on the same held-out LoCoMo and LongMemEval-S questions under two grading configurations each. The repository reports no statistically significant TAM-versus-Mem0 difference when the answering model is matched on those questions.


The reported headline figures include Mem0 Platform at 88.46% on 1,144 LoCoMo questions under the published judge and 91.00% on 400 LongMemEval-S questions under the official judge. TAM with GPT-5 answering is reported at 86.54% and 92.25%, respectively; alternative judge configurations produce different absolute values.


Evidence:
Primary repository with protocol and artifacts:
https://github.com/vbcherepanov/total-agent-memory


The repository is unusually explicit about limitations: it says the result is not demonstrated equivalence, the split was not scored blind, and tuning history is disclosed. It also notes that Mem0’s published setup differs from an earlier public protocol in judge, reruns and answer-prompt hints.


Why it matters to the bake-off:
The most useful lesson is methodological rather than competitive. Cross-system comparisons should preserve the answer corpus and normalize the evaluator before interpreting rank differences. A memory benchmark result is a product of the memory system, answer model, prompt, judge, question subset and retry/rerun policy.


Recommended action:
Read primary source and consider TAM as a candidate bake-off entrant or architecture specimen, but independently reproduce any comparative claim before using it to rank systems.


### Judge instability is large enough to swamp small benchmark deltas


Signal: Potentially new evaluation insight


What happened:
TAM’s repository reports a three-seed LoCoMo end-to-end run where retrieval was byte-identical and only generation/judging varied. Across 1,986 aligned questions, the generated answer differed on 12.5%, the judge verdict differed on 5.1%, and the judge flipped on an identical answer on 2.7%.


The same analysis found two deterministic failure modes in the judge. Refusals were sometimes accepted as correct answers to ordinary factual questions, while fluent hallucinations were accepted as correct abstentions when the adversarial gold was empty. Replacing those cases with deterministic guards changed the reported overall score from 0.645 to 0.579.


Evidence:
Primary reproducible benchmark artifacts and runner are linked from:
https://github.com/vbcherepanov/total-agent-memory


Why it matters to the bake-off:
A stable aggregate can hide unstable individual verdicts because errors cancel. Reporting a benchmark to three decimals does not establish evaluator precision. This is especially important in our bake-off, where small changes can otherwise look like architecture wins.


Recommended action:
Add JUDGE-INSTRUMENT-STABILITY to the evaluation harness. Keep answer generation and grading separable, preserve answer-level artifacts, re-grade identical answers, and report flip rates and confidence intervals alongside aggregate scores.


### Supersession heuristics can silently delete valid parallel facts


Signal: Potentially new insight / adversarial fixture


What happened:
TAM v14.4.0 added opt-in fact supersession using a simple heuristic: active records in the same project/type with shared opening words but a changed ending can be retired as replaced. The feature is off by default because, on a real 5,128-record store, that rule would have retired 138 records that were not updates. The repository gives “likes jazz” alongside “likes rock” as an example of independent facts that would be damaged by an over-eager replacement rule.


Evidence:
Primary release notes:
https://github.com/vbcherepanov/total-agent-memory


Why it matters:
This is exactly the precision/recall tradeoff hidden behind “supports supersession.” A memory system can score well on obvious updates while corrupting valid multi-valued state.


Recommended action:
Add a separate false-supersession metric. Do not count only whether old values disappear after a true update.


### Deduplication can erase legitimate updates before retrieval ever sees them


Signal: Potentially new insight / regression fixture


What happened:
TAM v14.3.1 reports that a prior near-identical-text deduplication rule treated updates that changed one value as repeats. On MemoryAgentBench FactConsolidation, the older rule dropped 36 of 455 facts. Examples include a citizenship value or PostgreSQL version changing while the surrounding sentence remains almost identical.


Evidence:
Primary release notes:
https://github.com/vbcherepanov/total-agent-memory


Why it matters:
This is a write-path failure, not a retrieval failure. If the new state never enters memory, no retrieval or reasoning improvement can recover it. The bake-off should localize failure stage rather than collapsing everything into answer correctness.


Recommended action:
Add DEDUP-KILLS-UPDATE and label failures as capture/write, storage/mutation, retrieval/composition or answer/reasoning when possible.


### A fresh Claude Code handoff pattern treats “done” as a claim that needs evidence


Signal: Interesting extension


What happened:
A r/ClaudeCode comment posted roughly 23 hours before this report describes three MIT-licensed handoff skills. The contract separates verified facts from hypotheses, completed from unresolved work, and records one next action. The writer reads the handoff back and refuses to claim persistence in an ephemeral sandbox; the pickup step re-checks mutable state such as PIDs, logs and exit codes before continuing.


Evidence:
Reddit discussion:
https://www.reddit.com/r/ClaudeCode/comments/1wma6ma/comment/pbjcagm/
Repository:
https://github.com/0mandrock1/handoff-skills


Why it matters to the bake-off:
This is memory provenance and temporal validity expressed at the handoff boundary. A stored statement can be true when written yet unsafe to reuse later if it describes mutable external state.


Recommended action:
Add HANDOFF-MUTABLE-REVALIDATION as a compact coding-agent continuity test.


## Benchmark & Leaderboard Watch


No credible new benchmark or leaderboard launched in the strict daily window that should displace existing benchmark work.


The useful benchmark development today is methodological: TAM’s cross-grade shows why comparisons must control question subsets, answering model, judge model, judge prompt and rerun policy. Its own three-seed analysis also demonstrates that judge-level noise can remain substantial even when aggregate scores look stable.


Implication for the bake-off:
- Preserve answer-level artifacts.
- Re-grade the same outputs when evaluating judge reliability.
- Add deterministic rules around factual refusals and abstention where the ground truth makes the decision mechanical.
- Treat small cross-system deltas as provisional until evaluator noise is below the claimed effect size.


## New Memory Systems Discovered


### Total Agent Memory — material new release, not a newly born project


Primary source:
https://github.com/vbcherepanov/total-agent-memory


Architecture / key idea:
Persistent local memory for coding agents built around a temporal knowledge graph, procedural memory, codebase/AST ingestion and hybrid retrieval. The v14.5.0 release adds neighboring-turn context to cross-encoder reranking, relative-date resolution, rank-aware context budgeting and head-to-head benchmark tooling. Its writes/searches can operate locally without an LLM call.


Evidence:
Open-source repository, benchmark runners and result artifacts are available. Competitive claims remain first-party and should be independently reproduced.


Why we care:
TAM is valuable less because of a single headline score than because its release history documents concrete memory-control failures and fixes in a production-oriented system.


No other newly surfaced system in today’s scan had evidence strong enough to outrank this release for immediate attention.


## Research Leads


- How often does our current judge flip on identical answers? Run this before interpreting narrow score changes.
- Can deterministic policy checks remove obvious false-positive evaluator cases without accidentally encoding benchmark-specific answers?
- What representation best distinguishes a superseding single-valued fact from a valid multi-valued attribute?
- Should bake-off adapters expose mutation capability declarations so unsupported supersession/deletion is distinguished from attempted-but-failed behavior?
- Can coding-agent handoffs carry an explicit validity class or revalidation policy for mutable external state?


## Emerging Patterns


Three patterns are becoming clearer across the recent daily reports:


1. Evaluation itself is part of the memory system. Judge instability, context composition and benchmark protocol can move results enough to obscure architectural differences.
2. Memory mutation is a first-class failure surface. Deduplication and supersession can corrupt state before retrieval begins, so “recall quality” alone cannot diagnose the system.
3. Durable continuity needs validity semantics, not just persistence. A handoff or memory should communicate whether a claim is stable, historical, hypothetical, governing, superseded or mutable and due for revalidation.


## New Resources


- Total Agent Memory v14.5.0 and benchmark artifacts:
  https://github.com/vbcherepanov/total-agent-memory


- Claude Code handoff-skills discussion:
  https://www.reddit.com/r/ClaudeCode/comments/1wma6ma/comment/pbjcagm/


- handoff-skills repository:
  https://github.com/0mandrock1/handoff-skills


## Experiments Worth Stealing


### JUDGE-INSTRUMENT-STABILITY


Experiment:
Generate or freeze one answer corpus, then run the evaluator repeatedly over exactly the same answers. Track per-item verdict changes and cases where identical answers receive different labels.


What it tests:
Whether the benchmark instrument is stable enough to resolve the performance differences being claimed.


Why it is interesting:
Aggregate scores can remain stable even while individual verdicts flip because errors cancel.


How we could adapt it:
For every evaluation family that uses an LLM judge, persist the raw answer, run multiple judge passes, report identical-answer flip rate, and compare the confidence interval with the delta between systems.


### SUPERSESSION-OVERREACH


Experiment:
Mix true replacements with same-subject facts that are simultaneously true. Example structure: a service changes from PostgreSQL 16 to 18 versus a person liking both jazz and rock.


What it tests:
Whether the system knows when to retire a prior value and when not to.


Why it is interesting:
A system can look strong on replacement benchmarks while silently destroying multi-valued state.


How we could adapt it:
Score true-positive supersession, false retirement and unresolved contradictions separately.


### DEDUP-KILLS-UPDATE


Experiment:
Store a fact, then issue a nearly identical statement where exactly one critical field changes.


What it tests:
Whether deduplication prevents a legitimate update from entering memory.


Why it is interesting:
It isolates a write-path bug that downstream retrieval cannot fix.


How we could adapt it:
Run the same fixture through capture/write inspection before querying, and classify failures by stage.


### HANDOFF-MUTABLE-REVALIDATION


Experiment:
Have session A persist a handoff containing stable verified facts plus mutable operational state. Change only the mutable state before session B begins.


What it tests:
Whether cross-session memory preserves useful continuity without treating stale operational facts as timeless truth.


Why it is interesting:
It combines provenance, transaction time, external-state validity and coding-agent continuity in a small deterministic fixture.


How we could adapt it:
Require the writer to verify persistence, mark mutable claims, and require the reader to revalidate only those claims before acting.


## Bottom Line


Modest change to current research priorities.


Do not interrupt current implementation work for a new architecture. Instead, harden the evaluation layer now: measure judge stability on identical answers and add the false-supersession / dedup-kills-update fixtures to the mutation suite. These are cheap, high-information tests and directly address failure modes documented in a fresh production-oriented memory-system release.


Total Agent Memory v14.5.0 is worth a focused inspection and possible bake-off entry, but its Mem0 comparison should be treated as first-party evidence until independently reproduced under our own fixed protocol.


The Claude Code handoff pattern is a smaller but useful continuity lead: persistence should be verified, and mutable state should be explicitly revalidated rather than silently trusted across sessions.