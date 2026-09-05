# Round 2 — the canonical retrieval result

**Contract:** `round2-retrieval-closure-gen94-v1`
**Scope:** perseus-vault 2.23.2, mem0 2.0.19, hindsight 0.9.2, agentmemory 0.9.29,
on `longitudinal-v1` and `backfill-v1`.
**Generations frozen:** Gen68 through Gen93. **No engine runs in this closure.**

## What changed between the first result and this one

Round 2 ended with an eight-row table of clean counts that appeared to separate
four memory systems sharply. Twenty-six generations of audit found that most of
that separation was **the harness being measured as if it were the products**.

Four rows of the original table do not survive as product results:

- two asked questions **no retriever can answer** and now sit at the reader layer;
- the temporal rows rested on a **coordinate error**, and four claims were
  retracted, qualified or reattributed;
- the scope row measured **adapters that were never given a scope to honour**;
- the current-truth row pooled a **mechanism** into a score.

**This is not a ranking.** The axes vary independently, no engine has a total, and
`assert_no_ranking` raises on any sentence that tries to make one.

## Two tables, never merged

**`frozen_configuration`** answers *what did the tested setup do?* — real
behaviour of a real configuration, handicaps included, because the handicaps were
real. **14 MEASURED, 6 NOT_DEMONSTRABLE, 4 NOT_APPLICABLE.**

**`native_capability`** answers *what can this pinned engine and interface do when
correctly bound?* — one variable moved at a time. **8 MEASURED,
1 NOT_DEMONSTRABLE, 3 NOT_APPLICABLE.**

The scope row is why they stay apart: three engines are `NOT_DEMONSTRABLE` in the
first and **isolate perfectly** in the second. That is not a contradiction. It is
the difference between a configuration and a capability.

## What Round 2 established

| claim | layer | status |
|---|---|---|
| **perseus uniquely preserves transaction-time belief history** | configuration | MEASURED |
| **hindsight's temporal filter is accepted and ignored**, 15 of 15 | configuration | MEASURED |
| mem0 and agentmemory expose no temporal surface | configuration | NOT_APPLICABLE |
| **no engine records effective time** — perseus untestable on this build, the rest have no surface | capability | NOT_DEMONSTRABLE / NOT_APPLICABLE |
| **all four isolate scopes** when given their own scope key | capability | MEASURED |
| **three separate a second configuration inside one scope; agentmemory cannot through this interface** | capability | MEASURED |
| **every engine retrieves the current fact — never once lost**, 0 of 84 | configuration | MEASURED |
| **one demonstrated ranking defect remains**, hindsight's, in its reranker | configuration | MEASURED |

That is the whole result. It is a much smaller set of claims than Round 2 started
with, and each one names the generation that can be checked.

## The current-truth row, in full

48 observations on the four cases that ask purely for present truth:
**24 already clean**, **15 retrieval-window policy**, **9 that no prefix can fix**.
The nine split one way per engine — hindsight a **demonstrated ranking defect**,
mem0 an **unresolved ordering of effectively tied revisions**, perseus **not
diagnosable through the measured surface**, agentmemory **none**.

The window curve is recorded and is **not** a recommendation; a guard raises on
any prescriptive phrasing of it.

## The method, which is the durable part

Four rules survived more than one line of evidence. Each is enforced by a check
somewhere in this repository, not left as advice.

**1. Prove a failure class can fire before interpreting its zero.**
*Gen69, Gen83, Gen84, Gen89.* Four universal zeros were read as product failures.
None of them was evidence about a memory system.

**2. Never read an adapter choice as a product capability.**
*Gen73, Gen76, Gen78, Gen84.* Three engines were recorded as collapsing scopes
when their adapters passed no scope filter at all. Given one, all three isolate
perfectly.

**3. Never mix the retrieval and reader layers.**
*Gen83, Gen84, Gen87.* Two rows that read as universal failure were asking for a
judgement and a refusal — neither of which a retriever performs. They stay
`NOT_DEMONSTRABLE` at the retrieval layer permanently, and
`assert_no_layer_mixing` fails closed on a table that mixes them.

**4. Decompose a pooled failure by mechanism before comparing systems.**
*Gen89, Gen90, Gen91, Gen93.* The current-truth row looked like widespread
forgetting. The current fact was never once lost, and most failures were the
width of the result window.

## Round status: CLOSED
