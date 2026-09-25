<!-- intake: drive id 1A3O-3s4cZJmlsRfaUI0RIY-rADyG2yY213rV6bF5Omk, name 'AGENT_MEMORY_INTEL_2026-09-25', modified 2026-09-25T14:03:45.627Z, fetched 2026-09-25T14:15:02Z, 23510 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-25
generated_at: 2026-09-25T06:57:10-07:00
lookback: approximately_previous_24_hours_plus_freshness_catchup
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Intelligence — 2026-09-25


## Executive Signal


Today's strongest fresh finding is not a new memory system but a missing evaluation dimension: a deletion API can truthfully report success while the supposedly deleted bytes remain in the backend's own persistent files. A fresh r/RAG self-check compared five agent-memory stores using deleted and undeleted marker pairs, then inspected raw persistence after each backend's own cleanup path. The author reports Mem0 and Chroma still retained the deleted marker bytes, while LanceDB, qdrant-local, and inspeximus did not in the tested configurations. The positive control is the important methodological contribution: an "absent" result is only accepted if the undeleted marker is still detectable, so a broken instrument or accidental wipe cannot masquerade as successful erasure.


This should become a separate bake-off dimension. Logical forgetting ("the system no longer retrieves it") and physical erasure ("the underlying persistence no longer contains it") are different capabilities and should be scored separately.


A broad freshness sweep also caught a high-value benchmark that earlier daily reports missed: MemCalib, submitted September 21 and revised September 22. MemCalib evaluates whether the answering model gives each retrieved memory proposition the right amount of influence: Ignore, Bound, or Control. This is a missing-middle benchmark between retrieval and final answer correctness. It is especially relevant to our recent findings around stale-but-retrievable facts, authority, over-personalization, and control-plane poisoning. This is a catch-up finding, not a publication from the last 24 hours.


There is also an important source-integrity correction. A fresh r/AIMemory post says the author "just released mex v0.8.0," but the primary GitHub release history shows v0.8.0 was released September 2 and the current v0.8.2 on September 13. The post's benchmark and code-linked-staleness ideas are useful, but this is renewed discussion of an older release, not a new release. Future daily reports should gate "new release" claims on primary tag/release timestamps.


No verified official agent-memory leaderboard changed in the strict daily window. Agent Memory Challenge Cycle 2 remains open, with official results expected in mid-November.


## Agent Handoff


### PRIORITY CHANGES


1. Add a separate erasure-integrity dimension to the bake-off. Distinguish:
   - logical deletion / non-retrievability,
   - physical residue in the system's own persistence,
   - resurrection after maintenance or re-ingestion.
   Do not collapse these into one "forgetting" score.


2. Add MemCalib to the benchmark-evaluation queue as a catch-up item. Its core idea—atom-level Ignore / Bound / Control—may fill a gap between "retrieval succeeded" and "the model used the retrieved memory appropriately."


3. Harden the existing task-state-closure test. Temporary memories should carry an owner and an explicit close/kill condition, not merely a TTL.


4. Add a multi-agent scope-bleed fixture in which two agents have semantically similar but conflicting local truths. Default retrieval should respect agent/project/task scope; cross-agent access should require an explicit opt-in path.


5. Add a source-freshness gate to this intelligence workflow: social claims of "released," "new," or "just shipped" must be checked against the primary release/tag/paper timestamp before being classified as new.


### SYSTEMS TO INVESTIGATE


No new system merits immediate bake-off entry from today's strict window.


MEX remains worth investigating for code-grounded memory and staleness detection, but today's Reddit post is not evidence of a new release. The current primary release is v0.8.2 from September 13.


### BENCHMARKS TO INVESTIGATE


#### MemCalib — catch-up, high priority


Primary paper:
https://arxiv.org/abs/2609.24259


Code/data:
https://github.com/Quark-Medical/memcalib
https://huggingface.co/datasets/ZiLaotou/MemCalib


Why it matters:
MemCalib asks whether each memory proposition has the appropriate influence on the final response. Its three target levels are:
- Ignore: no answer-specific footprint
- Bound: limited/local support
- Control: materially governs a conclusion, constraint, or recommendation


The benchmark contains 15,000 examples across health, general assistance, and coding, with 13,500 training examples and a disjoint 1,500-example test set. It explicitly measures over-use and under-use rather than treating memory use as binary.


The paper reports that even the strongest evaluated model has low exact calibration, and that most models exhibit a directional bias toward either over-using or under-using memory. The benchmark uses rubric-guided judging at the atomic-proposition level and reports human/judge agreement on a sampled subset.


Bake-off implication:
This provides a vocabulary and possible fixture structure for a failure mode we have repeatedly encountered: the right memory can be retrieved yet wielded with the wrong authority. It should be compared against our authority-vs-recency, stale/operative, control-plane poisoning, and delivered-context tests.


### EXPERIMENTS TO CONSIDER


#### ERASURE-BYTES-vs-RECALL


Capability/failure mode:
A delete operation succeeds at the API/retrieval layer but sensitive memory remains recoverable from the backend's own files or history structures.


Procedure:
1. Store two unique high-entropy markers A and B.
2. Confirm both are retrievable.
3. Delete A through the system's documented API.
4. Confirm A is no longer retrievable while B remains retrievable.
5. Run the system's documented compaction/optimization/vacuum path, if any.
6. Inspect all persistent artifacts owned by the memory system for marker A and marker B.
7. Report four states independently:
   - retrieval deletion passed/failed,
   - physical residue present/absent,
   - positive control passed/failed,
   - cleanup step passed/failed.
8. Repeat after restart and after additional writes/maintenance.


Important:
"Physical residue present" is not automatically the same as an application-level correctness failure. Some systems deliberately preserve history. The test should expose the behavior and capability, not silently reinterpret vendor semantics.


Source:
https://www.reddit.com/r/Rag/comments/1wj4yry/i_deleted_a_record_from_5_agentmemory_stores_and/
https://github.com/DanceNitra/ramr/blob/main/integrity/erasure_selfcheck.py
https://dancenitra.github.io/agora/public/posts/verify-agent-memory-deletion.html
https://github.com/chroma-core/chroma/issues/7659


#### MEMORY-INFLUENCE-CALIBRATION


Capability/failure mode:
The correct evidence is present in context, but the model over-trusts an irrelevant/stale memory or under-uses a governing one.


Procedure:
Construct mixed memory blocks containing:
- one atom that should be ignored,
- one atom that should provide bounded context,
- one atom that should control the answer.


Run the same query under controlled permutations and measure whether the final answer reflects each atom at the intended influence level. Include cases where the same fact should be Control in one query and merely Bound or Ignore in another.


Source:
MemCalib.


#### TASK-STATE-CLOSURE-v2


Capability/failure mode:
A completed task's transient blocker survives as durable project truth and resurfaces in unrelated future work.


Procedure:
Write a temporary state such as "blocked on queue-name decision" attached to a task ID and an explicit kill condition. Resolve the task through a different path (human completion, code change, or task close). In later unrelated sessions, the memory may remain available as history but must not surface as an operative blocker.


Test both:
- time-based expiry,
- event-driven invalidation.


Prefer event-driven close conditions where evidence exists; TTL alone cannot know whether the blocker resolved early or remains valid longer than expected.


Source:
https://www.reddit.com/r/AI_Agents/comments/1wmh2lg/why_your_agent_keeps_bringing_up_things_you/


#### AGENT-ORIGIN-SCOPE-BLEED


Capability/failure mode:
A shared memory store leaks semantically similar but locally valid memories between agents, projects, or tasks.


Procedure:
Agent A and Agent B receive near-identical tasks but conflicting local conventions or decisions. Store both in one physical repository with explicit scope metadata. Query from A, then B, then from an explicitly cross-agent mode.


Pass criteria:
- default A retrieval does not surface B-only governing facts,
- default B retrieval does not surface A-only governing facts,
- explicit cross-agent query can discover both with provenance intact.


Source:
https://www.reddit.com/r/AIMemory/comments/1wj23qt/thoughts_on_commingled_vs_segmented_multi_agent/


#### QUERY-EXPANSION-COMPETITION


Capability/failure mode:
Multi-query expansion increases candidate diversity but imports plausible distractors that outrank the exact evidence.


Procedure:
For a frozen set with known target evidence:
1. Run baseline retrieval repeatedly to establish the noise floor.
2. Run generated query variants.
3. Log candidate sets before fusion, after fusion, after reranking, and final delivered context.
4. Separate failures caused by the target being dropped from failures where the target survives but newly imported distractors outrank it.
5. Test original-query weighting and specificity-preserving rewrites.


Fresh r/RAG evidence:
A 210-question experiment reported a deterministic 206/210 baseline versus 203/210 under four-query expansion, with 2.3x latency. For two of the three lost questions, the correct chunk survived the candidate cutoff but newly introduced wrong chunks outranked it after reranking. This is a small, author-run experiment and should be treated as a method lead rather than a general conclusion.


Source:
https://www.reddit.com/r/Rag/comments/1wikfbe/multiquery_retrieval_cost_us_3_questions_out_of/


### RESEARCH LEADS


- Compare MemCalib's atom-level influence labels with our own concepts of authority, scope, staleness, confidence, and provenance. Determine whether "Bound" is expressive enough for cases where memory may inform explanation but not govern current state.


- Investigate whether physical-erasure verification belongs in the core bake-off score, a separate security/compliance profile, or both. Avoid penalizing systems whose documented product contract intentionally retains immutable audit history unless the benchmark explicitly requests purge.


- Extend deletion/resurrection testing to include hidden persistence layers: histories, WALs, append-only journals, indexes, backups, caches, and derived embeddings.


- Test whether task-state lifecycle metadata can be represented generically as:
  owner + created_at + effective interval + close condition + supersession target + disposition.


- Add provenance to scope tests so a cross-agent memory, when intentionally retrieved, cannot silently masquerade as the active agent's own prior state.


## High-value findings


### 1. Delete success and erasure are not the same thing


Signal: High-value evaluation methodology


A fresh r/RAG post reran a simple erasure probe against five memory stores. Each store received a deleted marker and an undeleted control marker. The script calls the backend's own delete path, runs its own cleanup/compaction where exposed, then searches the raw persistent files.


The reported September 17 run in the author's write-up shows:
- inspeximus: deleted marker absent
- qdrant-local: absent
- LanceDB: absent after optimize()
- Mem0: marker PRESENT in history.db
- Chroma: marker PRESENT in chroma.sqlite3 below the HNSW sync threshold


The author explicitly labels this as a self-check of one's own stack, not a universal vendor verdict. That framing is correct. The reproducible contribution is the test shape and positive control.


The Chroma-specific concern is independently supported by open issue #7659, opened August 29, which reports deleted document text and embeddings persisting in embeddings_queue on Chroma 1.5.9 even with automatically_purge enabled. The API-level view is correct—the deleted IDs no longer return—but the data remains below the API in the queue.


Why it matters:
Our forgetting tests have primarily focused on behavior and resurrection. This adds a different layer: whether the bytes are actually gone. A serious long-term memory evaluation should be explicit about which definition of "forget" it is testing.


Recommended action:
Add ERASURE-BYTES-vs-RECALL as a separate capability profile with positive controls and backend-specific cleanup receipts.


### 2. MemCalib measures the missing middle: how much influence memory should have


Signal: Catch-up benchmark / high research value


MemCalib was submitted September 21 and revised September 22. It was not surfaced in earlier daily reports, so it is included today as a catch-up rather than pretending it is a new publication.


The benchmark's central insight is that post-retrieval memory use is not binary. A composite memory block can contain atoms that should be ignored, atoms that should provide bounded support, and atoms that should materially control the answer. The model must calibrate influence per proposition and per query.


The paper reports 15,000 examples across health, general assistance, and coding. Its 1,500-example test set scores over-use, under-use, an overall Sample Calibration Score, and exact calibration. It reports low exact calibration across all evaluated frontier/open models and observes different directional biases.


Why it matters:
This directly operationalizes a distinction that keeps recurring in our bake-off: retrieving a stale or lower-authority fact is not necessarily a failure if the downstream agent gives it appropriately limited influence; conversely, retrieving the governing fact is insufficient if the model underweights it.


Recommended action:
Evaluate benchmark and steal the three-level influence structure for targeted bake-off fixtures.


### 3. Fresh MEX discussion is not a fresh MEX release


Signal: Source-integrity correction


A fresh r/AIMemory post says "just released mex v0.8.0" and reports a small one-repository benchmark: 10.74x less returned context than grep top-3, about 90.7% smaller, 100% expected-symbol recall across six retrieval tasks, and five of five real-agent tasks completed without fallback Read/Grep. The author explicitly cautions that this is a small benchmark and not a universal token claim.


The useful architectural idea remains code-linked staleness: Markdown claims can point to exact symbols so changed, moved, or deleted code can flag dependent project knowledge as stale.


However, the primary GitHub release history shows:
- v0.8.0: September 2
- v0.8.1: September 9
- v0.8.2: September 13


Therefore today's post is fresh discussion of an older release, not a new release event.


Primary release history:
https://github.com/mex-memory/mex/releases


Why it matters:
The intelligence pipeline itself needs provenance/freshness discipline. Social publication time is not release time.


Recommended action:
Keep MEX in the research queue, but add a primary-timestamp gate to future "new release" classification.


### 4. Temporary task state needs explicit death conditions


Signal: Reinforcing insight with sharper mechanism


A fresh r/AI_Agents discussion gives a concrete "ghost blocker" failure: an old migration blocker persisted after the migration shipped and later resurfaced during unrelated work. The useful addition beyond our prior task-state-closure idea is the comment-level mechanism: temporary state should carry a task owner plus the condition that makes it irrelevant, such as task closure or repository evidence that the migration shipped.


Why it matters:
A TTL is only a guess. An explicit close condition lets a system invalidate state when the world changes, while retaining historical context if needed.


Recommended action:
Upgrade TASK-STATE-CLOSURE to test owner + close condition + historical-but-nonoperative retention.


### 5. Shared multi-agent stores need scope tests, not just IDs


Signal: Research lead


A fresh r/AIMemory thread asks whether memories from different agents should live in one repository or be segmented. The author can attach session and agent IDs but correctly notes that ordinary semantic search can still pull conflicting memories from a similar task.


Why it matters:
Metadata presence is not scope isolation. The bake-off should test whether scope is enforced by retrieval behavior, not merely recorded.


Recommended action:
Add AGENT-ORIGIN-SCOPE-BLEED.


### 6. Query expansion can fail by importing competition


Signal: Retrieval-method lead


A fresh r/RAG experiment compared a repeated deterministic baseline against four-query expansion over 32,308 chunks and 210 frozen questions. The baseline found 206/210; multi-query found 203/210. For two of the three lost questions, the target chunk was still present before reranking, but new broader distractors outranked it.


The author appropriately notes a major limitation: the gold questions were generated from the corpus chunks, so there was little vocabulary gap for multi-query expansion to solve.


Why it matters:
Memory retrieval evaluation should record not only whether the right evidence entered the candidate set, but whether retrieval transformations introduced stronger-looking distractors and what finally reached the model.


Recommended action:
Add QUERY-EXPANSION-COMPETITION to retrieval stress tests and score it at candidate, rerank, and delivered-context boundaries.


## Benchmark & Leaderboard Watch


### MemCalib
Status: Catch-up benchmark, newly discovered by this pipeline.
Published: September 21, 2026; revised September 22.
Priority: High for methodological comparison.
Primary: https://arxiv.org/abs/2609.24259
Dataset: https://huggingface.co/datasets/ZiLaotou/MemCalib


### Agent Memory Challenge Cycle 2
Status: Open; no new official results verified today.
Official site: https://agentmemories.ai/
Current official results remain Cycle 1; Cycle 2 results are expected in mid-November 2026.


### No verified strict-window leaderboard change
No new official ranking or benchmark release from the monitored communities was verified in the approximately previous 24 hours.


## New memory systems discovered


No new system from today's strict window cleared the threshold for a new bake-off entrant.


MEX produced useful renewed discussion, but primary release timestamps show the current release predates today's window.


## Emerging patterns


1. "Forget" is becoming a layered concept:
   - not returned by search,
   - not used by the model,
   - logically deleted,
   - physically erased,
   - not resurrected by later maintenance.


2. Retrieval quality is also layered:
   - target enters candidate set,
   - target survives fusion,
   - target survives reranking,
   - target reaches final context,
   - target is given the correct influence.


3. Lifecycle metadata is becoming more important than raw timestamps. Temporary state needs an owner and death condition; governing facts need authority/scope; deleted material needs a disposition.


4. Multi-agent memory requires enforced scope semantics. Recording an agent ID is not the same as preventing cross-agent bleed.


5. Research-intelligence freshness itself needs provenance. A newly posted social thread can describe an older release.


## New resources


- Agent-memory erasure self-check:
  https://github.com/DanceNitra/ramr/blob/main/integrity/erasure_selfcheck.py


- Erasure investigation / methodology:
  https://dancenitra.github.io/agora/public/posts/verify-agent-memory-deletion.html


- Chroma open deletion-residue issue #7659:
  https://github.com/chroma-core/chroma/issues/7659


- MemCalib paper:
  https://arxiv.org/abs/2609.24259


- MemCalib dataset:
  https://huggingface.co/datasets/ZiLaotou/MemCalib


- MemCalib code:
  https://github.com/Quark-Medical/memcalib


- Fresh MEX discussion:
  https://www.reddit.com/r/AIMemory/comments/1wjtloc/my_claude_code_kept_rereading_the_same_repo/


- MEX primary release history:
  https://github.com/mex-memory/mex/releases


- Multi-agent segmentation discussion:
  https://www.reddit.com/r/AIMemory/comments/1wj23qt/thoughts_on_commingled_vs_segmented_multi_agent/


- Task-state lifecycle discussion:
  https://www.reddit.com/r/AI_Agents/comments/1wmh2lg/why_your_agent_keeps_bringing_up_things_you/


- Multi-query retrieval competition experiment:
  https://www.reddit.com/r/Rag/comments/1wikfbe/multiquery_retrieval_cost_us_3_questions_out_of/


## Experiments worth stealing


### A. Erasure with a positive control
Do not accept "marker not found" as proof of deletion unless an undeleted control marker is still visible through the same raw-store reader.


### B. Same memory, different influence
Reuse one proposition across several queries where its correct role changes from Ignore to Bound to Control. This tests whether memory authority is query-dependent rather than globally trusted.


### C. Event-driven memory death
Attach temporary state to a concrete close predicate and test whether an external state transition kills its operative authority without destroying historical provenance.


### D. Candidate ecology logging
When retrieval strategy changes, log which new candidates were introduced and whether they displaced correct evidence at fusion, reranking, or context packing.


### E. Social-to-primary freshness check
For every "new release" lead, record both social-post timestamp and primary release/tag timestamp. Classify freshness from the latter.


## Bottom Line


Today's strict window does not contain a new system or official leaderboard result that should interrupt ongoing work. It does contain one strong evaluation addition: distinguish logical forgetting from physical erasure, with positive controls.


The larger priority change is the catch-up discovery of MemCalib. Its atom-level Ignore / Bound / Control framing looks highly compatible with the bake-off's emerging concern that memory quality is not just "was the fact retrieved?" but "did the agent give that fact the right authority in this particular decision?"


Recommended action:
- add ERASURE-BYTES-vs-RECALL,
- evaluate MemCalib as a fixture/method source,
- harden task-state closure with explicit death conditions,
- add agent-origin scope bleed,
- and add primary-timestamp verification to the daily intelligence workflow.


No current implementation campaign needs to stop for these. Feed them into research and test design.