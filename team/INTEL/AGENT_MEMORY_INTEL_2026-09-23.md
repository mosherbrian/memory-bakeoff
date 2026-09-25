<!-- intake: drive id 1TABbmF3yaNk5_mgoRROTJs35YVHfVwRId9ITASmCeRc, name 'AGENT_MEMORY_INTEL_2026-09-23', modified 2026-09-23T14:03:37.293Z, fetched 2026-09-23T14:15:24Z, 18355 chars. Pulled by intel-intake; NOT written by the fleet. -->

report_type: agent_memory_daily_intelligence
report_date: 2026-09-23
generated_at: 2026-09-23T06:59:46-07:00
lookback: approximately_previous_24_hours
status: complete
priority_change: yes
agent_action_recommended: yes


# Agent Memory Daily Intelligence — 2026-09-23


## Executive Signal


- Glasshouse v0.1 is the strongest new development. The benchmark files are now actually present in the public repository, after earlier versions of the repo contained only rules and structure. It tests 2,847 question instances across 17 axes over a conversation that grows to 1.97M tokens, including multilingual retrieval, uncaptioned images, stale facts, contradiction, reconciliation, false-memory probes, temporal reasoning, updates, abstention and multi-session combination.
- Glasshouse's most useful design for this project is not the raw scale but the controlled accumulation test: the authored answer-bearing material is held constant while unrelated history grows from 1,882 turns to 103,572. The core/full comparison therefore separates baseline capability from degradation under accumulated memory noise.
- Its grading model explicitly distinguishes safe failure from dangerous stale confidence: for STALE, a correct new value gets full credit, "I don't know" gets partial credit, and repeating the superseded value gets zero. CONTRADICT separately rewards recognizing unresolved disagreement, while RECONCILE checks whether apparently conflicting statements are actually conditionally compatible.
- The repo still has maturity inconsistencies: the v0.1 subdirectory contains the benchmark corpus, scorer, baselines, hashes and question files, but its README still says "Draft, not yet released," while the top-level README says v0.1 is not drafted yet. Treat this as an available benchmark candidate, not a settled standard.
- Two adjacent RAG results suggest bake-off hardening tests: (1) a routing-table experiment failed only where a human-written routing sentence was false/semantically incomplete, producing a confident, well-cited wrong answer; (2) a fresh Jev claim-verification benchmark matched frontier-model aggregate accuracy but allowed materially more unsupported claims through. Both reinforce that aggregate accuracy can hide the failure mode that matters most.


## Agent Handoff


PRIORITY CHANGES


- Evaluate Glasshouse v0.1 as a benchmark/fixture source now that the actual files are public. Do not adopt it wholesale yet; map its axes against the bake-off taxonomy and identify unique coverage.
- Specifically compare Glasshouse STALE, CONTRADICT, RECONCILE, UPDATE, FALSE_MEMORY, TEMPORAL and accumulation/core-vs-full design against the bake-off's existing supersession, temporal, contradiction and continuity tests.


SYSTEMS TO INVESTIGATE


NONE


BENCHMARKS TO INVESTIGATE


- Glasshouse v0.1
  Primary source: https://github.com/wontopos/glasshouse/tree/main/glasshouse-v0.1
  Reason: newly materialized open benchmark with explicit stale/contradiction/reconciliation semantics and a controlled history-growth design that could contribute fixtures and evaluation dimensions to the bake-off.


EXPERIMENTS TO CONSIDER


- ACCUMULATION-CURVE
  Capability/failure mode: retrieval and memory quality degradation as irrelevant history accumulates.
  Source: Glasshouse v0.1.
  Proposed adaptation: hold the same answer-bearing episodes byte-for-byte constant while injecting progressively larger irrelevant histories; measure when each memory system's recall, temporal correctness, stale-answer rate and delivered-context cost degrade.


- SAFE-STALE-FAILURE
  Capability/failure mode: distinguishing "cannot establish current state" from confidently serving superseded state.
  Source: Glasshouse STALE axis.
  Proposed adaptation: score correct current value > explicit uncertainty > stale confident answer, rather than collapsing the latter two into one wrong bucket.


- CONTRADICT-VS-RECONCILE
  Capability/failure mode: unresolved contradiction versus statements that are both valid under different conditions.
  Source: Glasshouse CONTRADICT and RECONCILE axes.
  Proposed adaptation: pair adversarial cases that look superficially similar so the system must distinguish true conflict from condition-dependent compatibility.


- CONTROL-PLANE-MAP-POISON
  Capability/failure mode: high-authority routing/index metadata silently overrides true underlying evidence.
  Source: September 22 routing-table RAG experiment.
  Proposed adaptation: inject one incorrect or incomplete routing/index summary while leaving source memories correct; require the system either to detect inconsistency or verify against primary evidence before acting.


- ASYMMETRIC-VERIFIER-RISK
  Capability/failure mode: cheap judge/gate has acceptable average accuracy but a dangerous false-accept profile on unsupported claims.
  Source: September 22 Jev-as-a-Judge evaluation.
  Proposed adaptation: evaluate memory observers/critics by false-accept rate on unsupported/stale memory claims, not only balanced accuracy, and route low-confidence cases to a stronger verifier.


RESEARCH LEADS


- Glasshouse does not appear to have explicit axes for scope isolation, provenance/authority, multi-agent write conflicts, transaction-time/effective-time distinction, resurrection after deletion, or mutation API semantics. These may remain useful differentiators for the bake-off rather than gaps to copy from Glasshouse.
- Inspect whether Glasshouse's evidence_turns mechanism can be borrowed to separate "retrieval missed the evidence" from "reader saw evidence but reasoned incorrectly" in our own harness.
- Test whether a core/full accumulation curve exposes systems that look strong at small scale but collapse once stale/noise density rises.


## High-Value Findings


### Glasshouse v0.1 is now a real benchmark artifact, not just a proposal


Signal: Research lead / potentially high-value benchmark


What happened:
A new r/AI_Agents post on September 22 announced that Glasshouse v0.1 now contains the real benchmark files. Verification of the public repository confirms that the v0.1 directory now contains the corpus files, question/probe files, scorer, BM25 baseline, hashes, weights, submission rules and supporting assets. The release commit is titled "glasshouse v0.1: the benchmark."


Primary sources:
- Reddit discovery thread: https://www.reddit.com/r/AI_Agents/comments/1wn3fks/kept_seeing_complaints_about_memory_benchmarks_so/
- Repository: https://github.com/wontopos/glasshouse
- v0.1 benchmark: https://github.com/wontopos/glasshouse/tree/main/glasshouse-v0.1


What it measures:
The benchmark describes 2,847 question instances across 17 axes: XLING_QUERY, FALSE_MEMORY, BASIC, XLING_STORE, IMAGE, MULTI, IMPLICIT, TEMPORAL, CONFLICT, ABSTAIN, UPDATE, STALE, CONTRADICT, PARAPHRASE, CROSS, GATHER and RECONCILE.


Several are unusually relevant to the bake-off:
- STALE: current fact changed; safe uncertainty is scored above repeating an obsolete value.
- CONTRADICT: two facts disagree and nothing resolves them; naming the conflict is correct.
- RECONCILE: two statements look contradictory but are both valid under different conditions; the system must preserve both rather than supersede one.
- FALSE_MEMORY: the query itself asserts something never stated; the system must resist adopting the premise.
- UPDATE: changed facts should return current state.
- TEMPORAL: order and elapsed time.
- MULTI/GATHER/CROSS: combinations across sessions or domains.


The accumulation design:
The core authored material is preserved while the corpus grows from 1,882 turns / 78,584 tokens to 103,572 turns / 1,971,338 tokens. The full tier contains large amounts of unrelated filler. The same core questions can therefore reveal whether performance loss comes from baseline capability or degradation under accumulated history/noise.


Evidence boundary:
Question records carry evidence_turns, allowing evaluators to distinguish a retrieval miss from a downstream reader/reasoning miss. This is directly useful to the bake-off because a final wrong answer otherwise conflates memory storage, retrieval, context delivery and reasoning.


Why it matters:
Glasshouse is close to the bake-off's concerns but not redundant with them. Its controlled accumulation curve and explicit stale-vs-uncertain scoring look especially worth stealing. Its multilingual/image dimensions are broader than our current focus, while our scope/provenance and temporal-state work may remain deeper.


Methodological cautions:
- Wontopos builds memory infrastructure and administers the benchmark. Governance rules attempt to limit self-preference, but that conflict of interest remains relevant.
- The v0.1 subdirectory says "Draft, not yet released" even though the benchmark files are public and the Reddit post calls it released. The top-level README is also stale. Treat interfaces/scoring as potentially still settling.
- The benchmark uses judge LLM calls for some scoring modes, so judge/version sensitivity still matters despite fixed-version rules.
- Its standard core/full comparison and language/image question sets have tier-specific constraints; the headline 2,847 count should not be mistaken for one homogeneous single-run set.


Recommended action:
Evaluate benchmark. Import selected fixture shapes first, then decide whether a full comparative run is worth the cost.


### A wrong routing/control-plane sentence can produce a convincing false answer


Signal: Potentially new evaluation insight


What happened:
A fresh r/RAG follow-up reported 699/700 accuracy for a human-authored routing-table approach, but the one failure is more important than the headline. A relocation notice contained an incorrect/semantically incomplete statement about which historical version remained valid. Both routing variants followed it to the wrong-era rule and produced the same confident answer. Fixing the sentence fixed the result; the model did not become more careful.


Source:
https://www.reddit.com/r/Rag/comments/1wmvwfk/followup_measured_the_routingtable_rag_on_700/


Why it matters to memory:
High-level routing summaries, indexes, canonical notes and control-plane memories often have more authority than ordinary retrieved evidence. A single wrong summary can therefore be worse than one bad memory chunk: it controls which evidence is ever considered. The failure can also look unusually trustworthy because it produces a clean source path and specific answer.


Recommended action:
Add an adversarial control-plane metadata test. Corrupt or omit one critical routing/supersession statement while leaving primary evidence correct; score whether the system verifies, detects inconsistency, or silently follows the false authority.


### Jev-as-a-Judge shows why memory critics need asymmetric metrics


Signal: Interesting extension


What happened:
A September 22 r/RAG benchmark compared Jev with GPT-6 Astra on 495 human-labelled grounded-claim examples. Aggregate accuracy was nearly tied (73.3% versus 73.8%) and Jev was much cheaper/faster in that setup. But the error profile differed materially: the published analysis says Jev allowed 23.2% of unsupported claims through versus 14.1% for Astra.


Sources:
- Reddit: https://www.reddit.com/r/Rag/comments/1wnj0ut/we_benchmarked_jevasajudge_for_rag_claim/
- Repo: https://github.com/adorosario/jev-rag-claim-verification


Why it matters to the bake-off:
We have been considering small decision/classifier models as memory observers, gates and critics. This result reinforces that average accuracy is insufficient. For memory safety, the damaging error is often accepting a stale, contradicted or unsupported claim as valid. A cheap gate may still be excellent if it routes uncertainty, but should not be assumed safe as a drop-in verifier.


Recommended action:
When testing observer/gate models, report false acceptance of unsupported/stale claims as a primary metric and test confidence-based escalation to a stronger verifier.


## Benchmark & Leaderboard Watch


### Glasshouse v0.1


What it measures:
Long-term conversational memory under scale/noise, multilingual query/store behavior, images, basic recall, paraphrase, temporal reasoning, updates, stale facts, unresolved contradiction, conditional reconciliation, abstention/false memory, and multi-session fact combination.


What's new:
The actual benchmark artifacts are now public. Earlier repo state contained governance and structure but not the runnable benchmark files.


Distinctive design choices:
- Per-axis reporting rather than one headline score.
- Nested corpora with identical authored answer material and increasing unrelated history.
- Evidence-turn annotations to separate retrieval failure from reader failure.
- Safe-failure scoring for stale facts.
- Explicit distinction between contradiction and reconciliation.


Blind spots relative to the bake-off:
No obvious dedicated axes for scope isolation, provenance/authority, multi-agent memory, explicit memory mutation APIs, deletion/resurrection, or separate transaction-time/effective-time semantics.


Bake-off implication:
High enough to investigate immediately. Most likely value is fixture/method import, not replacing the bake-off.


## New Memory Systems Discovered


No new memory system in the strict daily window is strong enough to recommend as a new bake-off entrant.


## Emerging Patterns


The strongest pattern today is evaluation moving away from single aggregate scores toward failure-mode decomposition:


1. Glasshouse refuses a single headline score and separates 17 behaviors.
2. Its evidence-turn annotations separate retrieval from reader failure.
3. The routing-table result shows a high-level control-plane error can look like successful retrieval and reasoning.
4. The Jev verifier result shows near-equal aggregate accuracy can hide a much worse false-accept profile.


For the bake-off, this argues for preserving per-capability and per-failure-mode results even if we also maintain summary scores.


## New Resources


- Glasshouse v0.1 benchmark: https://github.com/wontopos/glasshouse/tree/main/glasshouse-v0.1
- Glasshouse repository/governance: https://github.com/wontopos/glasshouse
- Glasshouse Reddit launch thread: https://www.reddit.com/r/AI_Agents/comments/1wn3fks/kept_seeing_complaints_about_memory_benchmarks_so/
- Routing-table RAG evaluation: https://www.reddit.com/r/Rag/comments/1wmvwfk/followup_measured_the_routingtable_rag_on_700/
- Jev RAG claim-verification benchmark: https://github.com/adorosario/jev-rag-claim-verification
- Jev Reddit discussion: https://www.reddit.com/r/Rag/comments/1wnj0ut/we_benchmarked_jevasajudge_for_rag_claim/


## Experiments Worth Stealing


### Core-vs-full accumulation curve


Experiment:
Keep answer-bearing history constant and inject progressively more irrelevant conversations around it.


What it tests:
Whether a memory system's retrieval, prioritization and delivered-context quality degrade as its store grows.


Why it is interesting:
It separates "the system never knew how to answer this" from "the system knew, but accumulation broke it."


How we could adapt it:
Take a fixed set of existing bake-off continuity/temporal fixtures and replay them under 1x, 10x and 50x irrelevant-history growth, preserving exact evidence.


### Stale answer severity scoring


Experiment:
Ask for current state after a superseding update but deliberately make retrieval of the new value harder than retrieval of the old value.


What it tests:
Whether the system abstains safely when current authority cannot be established.


How we could adapt it:
Score current value = full, explicit uncertainty/conflict = partial, confident obsolete value = zero or negative severity.


### Contradict versus reconcile paired cases


Experiment:
Create visually similar pairs: one with genuinely unresolved incompatible facts, another with facts that differ only because their conditions/scopes differ.


What it tests:
Whether supersession/conflict logic over-merges valid conditional states.


How we could adapt it:
Use the same entities and phrasing across both cases so recency/similarity shortcuts cannot solve the distinction.


### Control-plane authority poisoning


Experiment:
Leave primary evidence correct but corrupt an index, summary, routing hint or canonical note that points the agent toward the wrong memory.


What it tests:
Whether high-authority metadata is blindly trusted.


How we could adapt it:
Instrument the trace to determine whether the agent ever inspected contradicting primary evidence; fail especially hard when it produces a confident answer with apparently clean provenance from the poisoned control-plane artifact.


### Asymmetric critic evaluation


Experiment:
Evaluate a cheap memory critic on supported vs unsupported/stale claims and report false acceptance separately from overall accuracy.


What it tests:
Whether a cheap observer is suitable as a gate or only as a first-stage router.


How we could adapt it:
Run Jev-class small decision models and stronger LLM judges on identical memory claims; add confidence-threshold escalation and compare cost versus stale/unsupported false accepts.


## Bottom Line


Change to current research priorities: YES, modestly.


Glasshouse v0.1 is worth immediate benchmark review because the actual artifacts are now public and several design choices map directly to hard bake-off problems. The likely win is to steal its accumulation-control design, stale-answer severity scoring, contradiction-vs-reconciliation pair structure and evidence-turn failure decomposition.


No new memory system surfaced today that merits interrupting implementation work. The RAG-adjacent findings are useful mainly as evaluation hardening: test high-authority control-plane metadata for poisoning/omission, and judge memory critics by asymmetric false-accept risk rather than aggregate accuracy.


Nothing found today warrants stopping current experimental work.