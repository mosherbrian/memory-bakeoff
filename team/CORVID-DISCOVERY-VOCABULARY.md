# Discovery vocabulary — our query ontology (defeating "memory" terminology lock-in)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-13
**Origin:** advisory input from the ChatGPT Deep Research directive
(`team/RESEARCH-INTELLIGENCE-DIRECTIVE.md` §7), folded into **our** taxonomy
(`ECOSYSTEM-MAP.md` E-1…E-9, axes A–D; goals G1–G5). **Advisory, not mandate;
$0, static.** Candidate discovery only — **no score import** (Phase-B rule).

## 1. Why this exists

Our field searches under one word, so it misses work that solved our problem
under another discipline's name. The directive's best reusable piece is a
terminology fan-out; this note maps it onto **our** mechanism families and
goals so a frontier scan is a query list, not a fishing trip.

## 2. Our concept → outside-"memory" terms

| Our family / concept | Search outside "memory" | Feeds |
|---|---|---|
| E-9 native capture; admission | salience, admission policy, event extraction, selective retention, sufficient statistic | G3 invocation; formation |
| E-7 conflict / supersession; axis C | effective time, valid time, transaction time, temporal versioning, supersession, belief revision, truth maintenance | **G1/G2**; agentmemory 418/450, Gen38 anchor |
| E-8 session/compaction continuity | event sourcing, change-data-capture, state reconstruction, materialized view, audit log | G5 continuity; pi-lcm line |
| E-3/E-4/E-2 retrieval | evidence retrieval, context gathering, hybrid search, query planning, case retrieval | G3; retrieval arms |
| E-6 agentic/procedural | experience replay, case-based reasoning, workflow induction, runbooks, process mining | G4 outcome; procedural transfer |
| Compression / summarization | context compression, hierarchical summarization, rate–distortion, incremental summarization | M1 tokens; MemForest-type claims |
| Feedback / adaptation | test-time learning, online adaptation, feedback reuse, episodic control | G4; SelfMem-type arms |
| Forgetting / invalidation | selective deletion, forgetting, expiration, truth maintenance | **G2**; stale-use harm |
| Multi-agent / shared state | blackboard system, shared state, distributed knowledge, coordination state | future multi-agent arm |
| Provenance / epistemics | data lineage, auditability, trace reconstruction, temporal consistency, citation lock | our citation rule; evidence gate |
| Security / isolation | persistent poisoning, cross-tenant leakage, untrusted state, tainted retrieval | P3/P4 gate; MemSecBench/GateMem |
| Coding-specific | debugging history, repository experience, failure trajectory, development trace, reusable workflow | G4/G5; transcript miner |

## 3. High-yield query templates (verbatim from the directive, kept)

```text
"cross-session state tracking" agent          "experience replay" software engineering agent
"dynamic state" "workflow knowledge" web agent "failure trajectory" coding agent
"effective time" "transaction time" KG         "case-based reasoning" tool-using agent
"temporal provenance" LLM agent                "workflow induction" agent traces
"state reconstruction" agent trajectory        "process mining" tool-use traces
"event sourcing" autonomous agent              "feedback reuse" long-horizon agent
"change data capture" knowledge assistant      "context compression" coding agent
"belief revision" LLM agent                    "hybrid retrieval" agent trajectory
"selective forgetting" continual learning      "causal graph" trajectory retrieval
"test-time learning" long-horizon agent        "premise awareness" agent benchmark
"repository-context recall" coding agent       "state reconstruction" + correction
```

**Operators:** add artifact/date terms (`site:arxiv.org`, `site:openreview.net`,
`github`, `dataset`, `benchmark`, `ablation`, `released code`, `Docker`,
`evaluation harness`) and **contradiction** terms (`fails`, `negative result`,
`long context baseline`, `no improvement`, `replication`, `stale`,
`contamination`, `cost`, `leakage`). Contradiction search is the highest-value
half: it is where we found the long-context null and the break-even study.

## 4. Discovery path (the pipeline we already half-run)

**question → synonyms from other disciplines → two anchor sources (one
benchmark, one mechanism) → backward citations → forward citations →
author/project graph → repo releases/issues → contradiction search → locally
executable hypothesis.** Stop when further reading has low expected decision
value; "interesting paper" is not a completed research item.

## 5. How it plugs in

- **Phase-B frontier harvest (Sprint-2 goal 5, owners Corvid + Alice):** the
  templates above are the candidate-discovery query set; each hit gets a card,
  not a score.
- **Weekly watchlist delta:** one page of "what changed this week?", clustered
  by our family (E-1…E-9) rather than by venue/brand.
- **Evidence gate:** any adopted hit carries the source/date/pin + operator +
  split/metric/reader/judge fields of the citation rule before it can move a row.

## 6. Limits

The vocabulary is a recall aid, not evidence; a term match is not a mechanism
match. The directive's own numbers are now two-seat spot-checked
(`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §6), but every query result still
needs primary-source verification under our citation rule.

— **Corvid** (`worker-glm-dsh3`). Advisory, $0, static; folds thread-pool item 2
from the directive assessment.
