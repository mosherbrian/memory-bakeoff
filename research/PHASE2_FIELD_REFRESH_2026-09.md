# Phase 2 field refresh, September 2026

The refresh PHASE B of `research/PHASE2_ROADMAP.md` asked for on 2026-09-02 and
that has never been done. Ordered by the control plane in Gen125.

**Governing question, unchanged from the roadmap:** what systems maintain
evolving agent state while preserving lossless history, provenance, scope,
recoverable historical belief, semantic recall, and bounded working context?

**Evidence status of everything below: EXTERNAL.** Nothing here is our
measurement. No score below may enter our leaderboard; these are candidate
discovery and external validation only, per the roadmap's own rule. Figures are
quoted from abstracts and repositories read on 2026-09-07, not reproduced
locally - the class of claim that produced LEDGER 119, so it is labelled.

---

## 1. HaluMem — hallucination at the OPERATION level

- `github.com/MemTensor/HaluMem`, arXiv:2511.03506
- Two datasets, Medium and Long: ~15,000 memory points, ~3,500 questions each;
  conversations average 1,500 and 2,600 turns, contexts over 1M tokens.
- **Measures each internal stage separately: extraction, updating, question
  answering.** That is the only benchmark found that decomposes the memory
  pipeline rather than scoring it end to end.
- Reported: systems generate and accumulate hallucination during extraction and
  UPDATING, which then propagates to QA; QA hallucination 17-30% even for the
  best systems.

**Why it matters here:** it is the external analogue of what Gen124 did
internally - attributing failure to a stage instead of to a system. Its
"updating" stage is exactly supersession.

Dimensions: state-heavy, extraction-heavy. Open code, open data.

## 2. Supersede / Memora — the memory-update gap, named

- arXiv:2606.27472, "Diagnosing and Training the Memory-Update Gap in LLM Agents"
- Introduces **FAMA, a metric that explicitly penalises reliance on superseded
  or deleted memory**, plus temporal-conflict QA for facts that change over time.
- The agent rewrites a bounded notes memory after each session and answers from
  memory alone.

**Why it matters here:** this is the closest published work to the project's
central concern, and closer than either ConflictQA or MemConflict on the
*metric* axis - it does not merely test supersession, it scores using stale
memory as a penalty. Code availability NOT yet verified; that is the first check
before this is admitted.

Dimensions: state-heavy, governance-adjacent.

## 3. EvoMemBench — and a negative result the project must face

- `github.com/DSAIL-Memory/EvoMemBench`, arXiv:2605.18421
- Axes: memory scope (in-episode vs cross-episode) x content (knowledge-oriented
  vs execution-oriented).
- Reported findings, quoted because they are uncomfortable: **long-context
  baselines remain highly competitive; memory helps most when the current
  context is insufficient or the task is hard; no single memory form works
  consistently across settings.**

**Why it matters here:** it is the strongest external evidence that "which
memory system" may be the wrong first question, and that the honest answer for
some workloads is "none, use the context window". Any intake that ignores this
is selecting on hope.

Dimensions: workflow-heavy, execution-heavy.

## 4. LongMemEval-V2 — the successor to our own substrate

- `github.com/xiaowu0162/LongMemEval-V2`, HuggingFace `xiaowu0162/longmemeval-v2`,
  arXiv:2605.12493. Released May 2026, updated August 2026.
- 451 curated questions over 1,870 task trajectories in WebArena-style and
  ServiceNow-style environments.
- Five abilities: static state recall, **dynamic state tracking**, workflow
  knowledge, environment gotchas, **premise awareness**.

**Why it matters here:** we are using LongMemEval V1's oracle split. V2 exists,
is agent-trajectory shaped rather than chat shaped, and names dynamic state
tracking as a first-class ability. It does not replace V1-oracle for the
reader-attribution lane - the oracle construction is what makes that lane work -
but it is a strong system-selection substrate.

Dimensions: state-heavy, workflow-heavy.

## 5. GateMem — governance, access control, deletion

- `github.com/rzhub/GateMem`, arXiv:2606.18829
- Multi-principal shared memory: utility, access control, and **deletion
  probes**. Explicitly distinguishes itself from recall, personalisation,
  reliability, collaboration and experience-reuse work.

**Why it matters here:** deletion and scope are two of the roadmap's six named
properties and we have measured neither. It is also the only candidate that
tests whether "forget this" actually forgets.

Dimensions: governance-heavy.

## 6. Agent Memory Leaderboard (AML)

- `github.com/AML-memory/agent-memory-leaderboard`. Launched 2026-07-29 by
  20+ universities and research organisations; shared protocol, versioned
  evaluation, public leaderboard. Agent Memory Challenge 2026 is open.

**Why it matters here:** infrastructure, not a contestant. A shared protocol is
worth reading before we invent more of our own, and it is the cheapest route to
discovering systems we have not heard of.

## 7. StateMemBench — searched, NOT FOUND

Recorded in `research/BENCHMARK_HARVEST_CHECK.md`. No repository in the paper,
nothing on HuggingFace, no project page. The search is incomplete by its own
admission - no GitHub code search, no papers-with-code, no author contact - and
must not be cited as "not released".

## 8. STALE — searched, not located

Named in the roadmap. Search returned staleness as a discussed PROBLEM
(prominently: a memory about an employer stays confidently wrong after a job
change) but no benchmark of that name. Either it was renamed, absorbed, or the
roadmap's name is imprecise. Unresolved; do not cite.

---

## Required metadata, per control-plane item 7

Review found the narrative above carries attribution but NOT the provenance
fields the instruction mandates. Recorded here rather than left implicit.
Blank means NOT ASSESSED, which is different from absent.

| | version / date | open? | code | evaluator assumptions | architectural or model-driven? | evidence weight |
|---|---|---|---|---|---|---|
| HaluMem | arXiv 2511.03506 | yes | `MemTensor/HaluMem` | not assessed - LLM-judged stages, judge identity unread | not assessed | state, extraction |
| Supersede / FAMA | arXiv 2606.27472 | unknown | **NOT LOCATED** | not assessed | not assessed | state |
| EvoMemBench | arXiv 2605.18421 | yes | `DSAIL-Memory/EvoMemBench` | not assessed | its headline IS the question - long-context vs memory | workflow, execution |
| LongMemEval-V2 | arXiv 2605.12493, May 2026, upd. Aug 2026 | yes | `xiaowu0162/LongMemEval-V2` + HF dataset | not assessed | not assessed | state, workflow |
| GateMem | arXiv 2606.18829 | yes | `rzhub/GateMem` | not assessed | not assessed | governance |
| AML leaderboard | launched 2026-07-29 | yes | `AML-memory/agent-memory-leaderboard` | versioned shared protocol - the point of it | n/a, infrastructure | n/a |
| StateMemBench | arXiv 2608.19652 | **NOT FOUND** | none found | n/a | n/a | n/a |

**"Not assessed" appears eleven times, and that is the honest state.** Reading
each paper's evaluator setup and separating architectural gains from
model-driven ones is a per-paper job that this refresh did not do. It is the
first work of whichever intake row admits that benchmark, and no candidate
passes the Phase-D gate without it.

## What changed in the field since the roadmap was written

1. **The frontier moved from recall to state and governance.** Five of the six
   located benchmarks post-date the roadmap and none is recall-shaped.
2. **Stage-level attribution is now standard practice** (HaluMem), which
   retroactively validates the Gen124 instinct and means we do not need to
   invent it.
3. **Superseded-memory penalties exist as a published metric** (FAMA).
4. **A shared evaluation protocol now exists** (AML), which did not when we
   started building our own.
5. **The most useful external result is negative:** long-context baselines
   remain competitive with memory systems (EvoMemBench). The project needs a
   long-context control arm or its comparisons are unanchored.

## What we must NOT conclude from any of this

None of it is our measurement. External scores stay external. Every candidate
below still has to pass the PHASE D admission gate on our hardware, with our
identity discipline, before any number of ours exists.
