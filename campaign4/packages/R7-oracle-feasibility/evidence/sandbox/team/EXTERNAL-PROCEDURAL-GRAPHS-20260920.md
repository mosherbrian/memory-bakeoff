# Procedural Graphs (arXiv 2609.09153) — read the paper, ignore the post

Filed 2026-09-20. Source: Brian, via r/AIMemory.

## Provenance, checked

**The paper is real.** arXiv:2609.09153, "Procedural Graphs: Self-Evolving
Execution Structures for LLM Agents", submitted 2026-09-08. Authors: Yuxing Lu,
Yicheng Chen, Shanchan Wu, **Sercan Ö. Arık** — Arık is Google Cloud AI
Research, so the "Google paper" attribution holds. 36 pages, 6 figures, 11
tables.

**The Reddit post is thin** - 7 upvotes, 2 comments, the author promoting his
own library and the single commenter promoting theirs.

**CORRECTION, 2026-09-20.** I wrote here that the library "has not been
measured by anyone". Brian: "They did have measurements on the README of their
repo." He is right, I had not looked, and the measurements are better than most
things this project has reviewed.

## What memoose actually published

LoCoMo, **mem0's protocol with mem0's prompts verbatim**, so the memory system
is the only variable. Claude Haiku 4.5 as answerer and judge, **all 1,540
questions**: 90.4% correct at 4,699 mean prompt tokens, $88.55.

| category | questions | score |
|---|---|---|
| single-hop | 841 | 93.5 |
| temporal | 321 | 89.7 |
| multi-hop | 282 | 88.7 |
| open-domain | 96 | 70.8 |

Called "a reference point, not a competitive entry". Every rival figure in
their comparison table is labelled vendor self-reported and explicitly not
comparable - including Zep's 94.7 against "third-party testing found 75.1" and
ByteRover's "two conflicting figures published". They state they trail mem0
everywhere and quantify it: -6.7 multi-hop, -11.5 open-domain.

And the line that decides how seriously to take the rest:

> "Two findings cut against us and are published anyway: the knowledge graph
> does **not** beat plain chunk retrieval on LoCoMo (paired McNemar p = 1.00)
> and costs 77% more tokens, and a larger retrieval budget does not lift the
> score. LoCoMo asks needle questions over conversations that fit in a context
> window; it does not test what a graph is for."

A published null result against their own central claim, with a named
statistical test, plus the reason the benchmark may be wrong for the method.
They also note that swapping the answerer moves a score more than swapping the
memory system, so the ordering is noise - the same confound discipline this
project uses.

Raw rows, per-category tables, cost and protocol are all published under
`benchmarks/`.

**What this changes.** memoose stops being "one person's unmeasured library"
and becomes a bake-off candidate with a published protocol we can re-run, from
an author who reports against himself. That is rarer than a good score.

## What the paper actually says

Verbatim from the abstract, because the problem statement is uncomfortably
close to our own week:

> "As trajectories lengthen, agents can lose track of their objectives, invoke
> tools out of order, and repeat unproductive actions."

The mechanism:

- A knowledge graph stores `(entity, relation, entity)` for *what-is*
  questions. A Procedural Graph stores `(procedure, relation, procedure)` for
  *what-to-do* questions.
- At each step it localises the agent's active node and a guidance model turns
  the surrounding subgraph into situational guidance that **biases the next
  action without dictating it**.
- Self-evolving: an LLM refiner **contrasts failed trajectories with successful
  ones**, edits the graph, and commits an edit only if it **preserves or
  improves held-out validation performance** — while **retaining rejected edits
  to discourage repetition**.

## Why it is worth our attention specifically

Two properties map onto problems we measured today, not hypothetically:

1. **"Repeat unproductive actions"** is the defect Brian named this morning:
   *"I feel like we have fixed this same class of issues probably a hundred
   times."* Today alone produced seven instances of one family, two of them the
   identical regex in different files.

2. **Retaining rejected edits to discourage repetition** is the part we have
   never had. Our record keeps what worked; it does not keep what was tried and
   refused, so nothing stops the same wrong fix being re-derived. That is a
   cheap idea we could steal without adopting anything else in the paper.

And we already own the two things the method needs: a corpus of successful and
failed trajectories, and a **held-out validation signal** — the gate/verify
pair, where a check written from the row text alone and reviewed by a
non-author decides whether work passes.

## The objection that has to be answered first

The refiner is **an LLM editing its own procedure store**. That is the exact
pattern this project has spent three iterations proving is the root cause of
its failures: a component authoring the state that describes it.

The paper's answer is better than ours has been — an edit is committed only if
held-out performance survives it, which is evidence rather than a claim. But
that defence is only as strong as the validation set, and a graph that guides
an agent toward passing its own validator is a fitting risk we already know by
name: it is what corvid rejected three gates for.

**So: do not adopt the self-evolution loop before measuring whether the
validation gate actually holds it honest.**

## Status

- Paper: real, unread in full. 36 pages. Worth a proper read, not a skim.
- Library (`memoose`): unmeasured, one author, no independent use.
- Next cheap step if we pursue it: extract only the *rejected-edit memory* idea
  and test it against our own record of re-derived fixes. It needs no graph, no
  guidance model and no LLM refiner, and it targets the defect Brian is most
  tired of.
