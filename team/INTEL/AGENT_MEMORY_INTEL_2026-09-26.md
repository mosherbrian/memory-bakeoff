<!-- intake: drive id 1qaJjsYsths6opeCwXSOAO47UAttexsBn0-XfPDb-pC0, name 'AGENT_MEMORY_INTEL_2026-09-26', modified 2026-09-26T14:06:01.297Z, fetched 2026-09-26T14:15:02Z, 20924 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-26
generated_at: 2026-09-26T07:03:00-07:00
lookback: approximately_previous_24_hours_plus_freshness_catchup
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Intelligence — 2026-09-26


## Executive Signal


Today’s strongest fresh signal is an evaluation-boundary problem: memory quality should be measured at the text that actually reaches the agent, not merely at the retrieval layer. A fresh r/AIMemory post introduced adebench and compared memory systems through a “door” — the client-facing memory path after ordering, composition, character cuts, and real tool-response pressure. Its primary repository formalizes this distinction. A fact that is present in raw search but cut out of the delivered context does not help the agent.


That sounds obvious, but it changes what we should measure. The bake-off already separates some retrieval and answer behavior; today’s finding suggests making the delivery boundary first-class and stress-testing it under realistic competing context pressure. adebench also includes a particularly relevant report-only write-back probe: deliberately degrade retrieval, let the assistant produce “no record,” then test whether the normal memory writer stores that degraded answer and causes it to outrank the real fact later. That is a clean self-poisoning mechanism we should steal.


The second major finding is benchmark integrity. A fresh discussion around SAGE surfaced a February 2026 systematic audit of LoCoMo that had not made it into our daily intelligence stream. The audit reports 99 score-corrupting ground-truth errors among 1,540 non-adversarial questions (6.4%), plus 57 citation-only errors. It estimates a theoretical ceiling of roughly 93.6% for a perfectly correct system on the uncorrected answer keys, with worse noise in multi-hop, temporal, and open-domain categories. This does not make LoCoMo useless, but it materially weakens claims based on small score differences unless results are also checked against the corrected/error-flagged set.


SAGE itself is an interesting newly surfaced write-path optimization rather than a new benchmark release. It uses embedding-space novelty to route clearly novel inputs to ADD, clearly redundant inputs to NOOP, and only ambiguous cases to an LLM merge/update path. The project reports large write-cost and ingestion-time reductions, but its own paper also shows quality tradeoffs on some configurations and explicitly notes that embedding geometry can drop semantically distinct facts. The most important bake-off question is therefore not “does SAGE save calls?” but “what is its false-NOOP rate on temporally, operationally, or authoritatively different updates that happen to be embedding-near?”


A catch-up sweep also found DolphinBench, a recent task-oriented agent-memory benchmark with 600 tasks across three personas. It grades tool actions rather than recall answers, uses years of conversation history, and reports accuracy together with cost and latency. This belongs on active benchmark surveillance because it measures whether remembered information actually changes future behavior, not merely whether an agent can recite it.


No verified official leaderboard change in the strict daily window warrants interrupting current implementation work.


## Agent Handoff


### PRIORITY CHANGES


1. Make the delivered-context boundary a first-class evaluation layer.
   Track at least:
   - whether the gold memory exists in storage,
   - whether retrieval returns it,
   - its rank,
   - whether it survives composition/order/cut into the actual agent-visible context,
   - whether the final answer/action uses it correctly.
   Do not treat “retrieval hit” as equivalent to “memory reached the model.”


2. Add a memory self-poisoning fixture.
   Force retrieval to miss or truncate a known fact, induce a plausible “no record” or wrong answer, allow the normal write-back path to run, then restore retrieval and check whether the degraded answer now competes with or outranks the original truth.


3. Add LoCoMo benchmark-integrity handling.
   If LoCoMo is used anywhere in the bake-off, preserve:
   - raw score on the canonical dataset,
   - score with the audit-flagged 99 score-corrupting items removed or corrected,
   - per-category results,
   - judge/model/run variance.
   Do not describe small uncorrected LoCoMo deltas as decisive without acknowledging the reported 6.4% label-noise floor.


4. Evaluate SAGE-style novelty gating only as a prefilter until it survives adversarial update tests.
   The key metric is false NOOP / lost update, especially when new and old facts are semantically close but differ in:
   - effective time,
   - authority,
   - scope,
   - negation,
   - supersession,
   - operational consequence.


5. Add DolphinBench to benchmark surveillance and architecture-method comparison. Do not adopt it wholesale yet; first compare its action-grading, history construction, causal-history validation, cost accounting, and harness assumptions against the bake-off.


### DO NOT INTERRUPT CURRENT IMPLEMENTATION


These findings strengthen the evaluation harness and research queue. None currently demonstrates that the active implementation path is wrong enough to justify stopping in-flight work.


## High-Value Findings


### 1. adebench: evaluate the memory “door,” not just retrieval


Freshness:
Fresh r/AIMemory post in the daily window; primary repository inspected today.


Reddit:
https://www.reddit.com/r/AIMemory/comments/1wffx8s/i_benchmarked_my_assistants_memory_against_garry/


Primary repository:
https://github.com/adecubed/adebench


What is demonstrated in the repository:
- The benchmark defines a “door” as the client-facing path and text actually delivered to the model.
- Its scored door section checks that expected content survives into delivered text, not merely raw search hits.
- It separately tests cards, fact updates, time metadata, live state, abstention, file search, and graph structure.
- It measures injected text size on every run.
- It can evaluate one-call and two-step delivery paths under the same declared budget.
- It can inject measured tool-response pressure and report context margins.
- It contains a write-back self-poisoning probe.


Author-reported comparison, not independent evidence:
On the author’s own 25-question golden set, the ADE memory reportedly delivered 23/25 door answers versus 18/25 for gbrain under a 2,400-character cut; under measured p95 MCP response pressure, 19/25 versus 14/25. The author explicitly discloses that this is their own golden set and that gbrain received already-distilled facts, so this is not a neutral architecture leaderboard.


Why it matters:
This is a useful distinction the bake-off can operationalize without adopting the benchmark itself. A system can have excellent recall in isolation and still fail as an agent memory because the orchestration layer truncates, reorders, previews, or crowds out the useful evidence.


### 2. LoCoMo ground-truth audit: a benchmark can have a larger error floor than the model delta


Newly surfaced today; audit itself is dated February 2026.


Primary audit:
https://github.com/dial481/locomo-audit/blob/main/AUDIT_REPORT.md


Reported audit results:
- 1,540 non-adversarial LoCoMo questions audited.
- 156 total ground-truth issues.
- 99 score-corrupting errors: 6.4%.
- 57 wrong-citation-only errors that do not change standard answer-text scoring.
- Score-corrupting breakdown: 33 hallucinated facts, 26 temporal errors, 24 wrong-speaker attributions, 13 ambiguous/debatable cases, 3 incomplete answers.
- Reported theoretical ceiling on the uncorrected keys: about 93.6%.
- Category error rates are uneven: multi-hop 9.9%, temporal 8.1%, open-domain 9.4%, single-hop 4.3%.


Evidence caveat:
The audit says it was performed by Claude Opus 4.6 with human review. It is not an official LoCoMo correction release, so its error file should itself be inspected and sampled before treating every flagged item as ground truth.


Bake-off implication:
Benchmark labels are part of the measurement instrument. The bake-off should version and audit the evaluator data with the same seriousness applied to memory-system code. This also reinforces yesterday’s evaluator-stability work: score movement can come from the memory, the judge, or the benchmark itself.


### 3. SAGE: cheap novelty gating is promising, but false NOOP is the dangerous failure mode


Fresh r/AIMemory discussion:
https://www.reddit.com/r/AIMemory/comments/1wb8rxw/do_we_really_need_an_llm_to_decide_whether_every/


Primary repository:
https://github.com/swang1024/SAGE


Paper:
https://arxiv.org/pdf/2605.30711


Mechanism:
SAGE L2-normalizes memory embeddings and uses a vMF-inspired density/novelty signal to classify incoming information as:
- clearly novel → ADD,
- clearly redundant → NOOP,
- ambiguous → invoke the LLM merge/update path.


Claims from the fresh post:
- 3.4× lower add-phase API cost and 2.5× faster ingestion with GPT-4o-mini on LoCoMo.
- 16–18% of A-Mem write/evolution calls can be skipped as a drop-in gate.
- strong token-F1 results across seven open-weight backbones.


Important qualification from the paper:
The paper’s full LoCoMo table shows that the efficiency gain is not a universal quality win. In the reported GPT-4o-mini comparison, SAGE substantially reduces prompt/completion volume, wall-clock ingestion time, and API cost, but Mem0 leads some quality categories and overall average judge score. The paper also explicitly lists embedding-geometry errors, lack of DELETE/compaction, and broader benchmark generality as limitations.


Most revealing question raised by the community:
“Use endpoint X” and “stop using endpoint X after Friday” can be embedding-near while operationally opposite. That is exactly the update type a write-side novelty gate must not silently discard.


### 4. Fresh production anecdote: “what’s new?” can fail because query semantics do not encode recency


Fresh r/AI_Agents discussion:
https://www.reddit.com/r/AI_Agents/comments/1wpscrw/in_midaugust_my_agents_memory_answered_whats_new/


The author reports a graph that contained the needed recent facts, but a semantic+keyword retriever with no temporal intent produced old July facts when asked “what’s new?” because most of the stored graph was from July. The same post reports other silent issues such as a result cap retaining the oldest end of a window.


Evidence status:
Anecdotal, not independently reproduced.


Why it matters:
It is a useful adversarial query form. Temporal intent can exist in the user request without sharing lexical/semantic features with the facts themselves. Retrieval systems should not rely on embedding similarity alone to infer “latest,” “current,” or “new.”


## Benchmark & Leaderboard Watch


### DolphinBench — catch-up, high priority


Primary site:
https://dolphinbench.ai/


Paper linked from benchmark site:
https://arxiv.org/abs/2609.24971


Current site summary:
- 3 personas.
- 600 total tasks, 200 per persona.
- histories up to 5,128 messages spanning nearly five years.
- tasks use simulated real tools such as email, Slack, Discord, calendar, and CRM.
- grading checks tool call, target, and content rather than recall text.
- cost includes memory ingestion and testing.
- leaderboard is designed around accuracy, cost, and latency rather than a single accuracy number.


Why this is unusually relevant:
DolphinBench pushes evaluation toward causal task utility. A remembered rule is only useful if it changes the agent’s action correctly years later. That is closer to the bake-off’s agentic purpose than QA-only benchmarks.


Status:
Add to surveillance and perform a fixture/harness audit before importing any scores.


### LoCoMo


No leaderboard update identified today, but the newly surfaced audit materially changes confidence calibration for LoCoMo-based comparisons. Treat uncorrected scores as noisy measurements, especially for multi-hop and temporal categories.


### Agent Memory Challenge / other watched leaderboards


No verified official result change in the strict daily window that merits a priority shift.


## New Memory Systems / Techniques


### SAGE novelty gate


Classification:
Newly surfaced technique in today’s community scan; primary paper predates this daily window.


Potential role:
Cheap first-pass write router ahead of an LLM-based ADD/UPDATE/NOOP decision.


Recommendation:
Prototype only behind an adversarial false-NOOP suite. Do not allow embedding novelty alone to make irreversible supersession or deletion decisions.


### MEX


A fresh r/AIMemory post again describes MEX as if v0.8.0 were newly released. This is a duplicate freshness issue already identified yesterday: primary release history places v0.8.0 earlier in September and v0.8.2 later. Do not count this as a new system release. Keep watching for independent evaluation of its code-grounding/staleness mechanism.


## Research Leads


### Delivery composition as a distinct memory subsystem


The “door” concept suggests the memory system boundary should include:
retrieval → composition → ordering → budget cut → tool/context coexistence → delivered context.


This creates a useful decomposition for failures that currently get blamed on retrieval even when retrieval was correct.


### Write-path optimization should be judged by catastrophic false negatives, not average savings


A write gate that saves 30–70% of routing cost but occasionally discards a governing update can be worse than no optimization. Evaluate the tail: “which updates get silently erased?”


### Benchmark integrity needs a versioned data contract


For every imported benchmark:
- pin dataset hash/version,
- preserve known-issue manifests,
- run evaluator canaries,
- report raw and corrected/filtered variants where justified,
- separate benchmark-label uncertainty from model/system variance.


### Action-based evaluation is becoming more important


DolphinBench adds another strong signal that agent-memory evaluation is moving beyond “answer a question about history” toward “take the correct future action because of history.” This direction is highly aligned with the bake-off and should inform new fixtures even if the benchmark itself is not adopted.


## Emerging Patterns


1. Retrieval success is necessary but not sufficient. The useful unit is increasingly “evidence that survives all the way to action.”
2. Memory write optimization is dangerous when semantic similarity hides temporal, authority, or negation changes.
3. Evaluation infrastructure is itself an attack surface: judge instability, leaked benchmark artifacts, stale references, and now ground-truth label noise can all create false progress.
4. Context budget is a systems property, not a memory-only property. Tool schemas, previews, agent scaffolding, and other runtime text compete directly with memory.
5. Temporal intent deserves explicit routing. “Latest/current/new” should influence filtering/ranking independently of semantic similarity.


## New Resources


adebench:
https://github.com/adecubed/adebench


SAGE:
https://github.com/swang1024/SAGE
https://arxiv.org/pdf/2605.30711


LoCoMo audit:
https://github.com/dial481/locomo-audit/blob/main/AUDIT_REPORT.md


DolphinBench:
https://dolphinbench.ai/
https://arxiv.org/abs/2609.24971


Fresh Reddit discovery threads:
https://www.reddit.com/r/AIMemory/comments/1wffx8s/i_benchmarked_my_assistants_memory_against_garry/
https://www.reddit.com/r/AIMemory/comments/1wb8rxw/do_we_really_need_an_llm_to_decide_whether_every/
https://www.reddit.com/r/AI_Agents/comments/1wpscrw/in_midaugust_my_agents_memory_answered_whats_new/


## Experiments Worth Stealing


### DELIVERED-CONTEXT-vs-RETRIEVAL


Failure mode:
The correct memory is retrieved but disappears before the model sees it.


Fixture:
1. Seed a governing fact and multiple plausible distractors.
2. Query through the system’s real agent-facing memory path.
3. Record raw hits and ranks.
4. Capture the exact context bytes/tokens delivered to the agent.
5. Repeat under increasing non-memory context pressure.
6. Score storage presence, retrieval presence, delivered-context presence, and final behavior separately.
7. Vary composition strategies: one-call, preview+detail, card-first, facts-first.


Success criterion:
A retrieval hit cannot earn a memory-correctness point if the agent never receives the evidence.


### MEMORY-WRITEBACK-SELF-POISON


Failure mode:
A transient retrieval failure creates a wrong assistant answer, which the memory system then stores as new evidence and uses to override the original truth.


Fixture:
1. Store canonical fact F.
2. Verify F is normally retrievable.
3. Artificially constrain/degrade the read path so F is absent.
4. Ask a question whose safe answer should be “unknown” or whose wrong fallback is predictable.
5. Allow the ordinary conversation/write-back pipeline to persist the exchange.
6. Restore normal retrieval.
7. Query for F with multiple paraphrases.
8. Fail if the degraded answer now outranks, supersedes, or contaminates F.


### WRITE-GATE-FALSE-NOOP


Failure mode:
A novelty/dedup gate treats a materially new update as redundant because its embedding is close to the old fact.


Adversarial pairs:
- “Use endpoint X” → “Stop using endpoint X after Friday.”
- “Alice owns service A” → “Bob is now authoritative owner for service A.”
- “Deploy region us-west” → “For tenant B only, deploy eu-central.”
- “Medication dose 10” → “Dose 10 was discontinued; use 5.”
- “Feature enabled” → “Feature disabled pending incident review.”


Metrics:
false NOOP, false merge, lost temporal boundary, lost authority boundary, inappropriate deletion/supersession, downstream answer/action error.


### LOCOMO-GOLDEN-INTEGRITY


Purpose:
Ensure benchmark label defects do not masquerade as memory-system regressions.


Procedure:
1. Pin the exact LoCoMo dataset hash.
2. Import the audit issue manifest as an overlay, not as destructive edits.
3. Run canonical scoring unchanged.
4. Run a second score excluding or correcting audited score-corrupting cases.
5. Report both, plus category deltas.
6. Sample disputed flags manually before using corrected results for formal claims.


### RECENCY-INTENT-ROUTING


Failure mode:
The store has current facts, but a query such as “what’s new?” or “what changed?” has weak lexical similarity to them and returns older, more semantically similar material.


Fixture:
Populate a history where older material dominates volume but newer facts exist. Ask:
- “What’s new?”
- “What changed recently?”
- “What is current now?”
- a control query without recency intent.


Measure whether temporal intent changes candidate generation/ranking and whether old-but-semantic matches are suppressed appropriately.


### ACTION-CAUSAL-MEMORY


Inspired by DolphinBench.


Fixture:
Create a long history containing a single governing rule. Later issue a plausible tool task whose default action is wrong unless that rule is remembered. Grade the actual tool/action parameters, not an explanation.


Add an ablation:
Run the same task with the governing history removed. The task is valid only if the memory-containing run can succeed while the ablated run predictably cannot. This helps establish that memory, rather than generic model knowledge, caused the success.


## Bottom Line


Today’s most actionable contribution is not another memory architecture. It is a tighter definition of where memory should be measured.


First, follow the fact all the way from storage to retrieval to delivered context to action. Second, test whether degraded reads can poison future writes. Third, treat write-side novelty optimization as a high-risk classifier whose false negatives matter more than average savings. Fourth, stop treating benchmark answer keys as unquestioned ground truth: the newly surfaced LoCoMo audit is large enough that small uncorrected score gaps should not drive architectural decisions.


Recommended bake-off actions: add DELIVERED-CONTEXT-vs-RETRIEVAL and MEMORY-WRITEBACK-SELF-POISON to the near-term fixture queue; add a false-NOOP adversarial for any novelty/dedup gate; annotate LoCoMo with benchmark-integrity handling; and place DolphinBench on active benchmark surveillance.


No finding today justifies interrupting current implementation work.