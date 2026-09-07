# Which memory system, and on what evidence

**Status: OPEN. Rows: 3 of an expected 6-8. Budget: 8 generations, 2 spent.**

The terminal deliverable. Both independent accountants (2026-09-07) said this
project has no defined end and therefore cannot tell a justified generation from
an unjustified one. This is the end, defined.

**The rule, and it is the whole point of the file:** a generation that does not
add or change a row here is unjustified. Not forbidden - unjustified, which
means it needs an argument in its handoff for why it happened anyway.

**The question this memo must answer, in one sentence when it closes:** which
memory system should an AI coding agent use, under what workload, on what
evidence class, and with what caveats.

---

## Rows filled

| # | Claim | Evidence class | Anchored? | Gen | Status |
|---|---|---|---|---|---|
| 1 | **Every engine co-returns the superseded record alongside the current one.** 192/192 observations, four independent semantic cores, all loads and repetitions. | replicated, frozen, preregistered questions | n/a - universal | 97, 99 | **CLOSED** |
| 2 | **Supersession mechanisms are not commensurable and results diverge completely.** Perseus `EXPLICIT_LINEAGE` removes stale 48/48; Hindsight `STATE_TRANSITION` 0/48; AgentMemory `PRODUCT_DECIDES` 12/48, all in one core; Mem0 unavailable in the pinned profile. Three of four had the surface and had never been asked. | frozen bindings, per-kind, never summed | n/a - per mechanism | 100, 101 | **CLOSED** |
| 3 | **On a third party's benchmark, both measured engines roughly double a lexical baseline on the supersession question and both sit below 44% absolute.** Hit@3 on dynamic conflict, held-out 27-persona slice: perseus 0.434, mem0 0.419, bm25 0.226. On static conflict all three land within seven points. | external benchmark, held-out, exact provenance | **yes - bm25** | 38 | **CLOSED, needs extension** |

## Rows required before this memo can close

| # | Question the row must answer | Why it is required | Assigned |
|---|---|---|---|
| 4 | **Does any memory system beat putting the history in the context window?** | Without it, rows 1-3 compare products to each other and to lexical retrieval, but never to the null the field's own recent work says is competitive. If the answer is no, rows 5-6 are moot and the memo closes early. | intake row 1 |
| 5 | **Do the four unmeasured local engines change row 3's picture?** | Row 3 measures two of six. A recommendation over six candidates cannot rest on two. | intake row 2, extend |
| 6 | **What does each system DO with a stale record it returns, scored as a penalty?** | Rows 1-3 score retrieval. Row 1 says every engine returns stale records anyway, so retrieval quality is not the deciding variable. FAMA (arXiv:2606.27472) is the published metric. | intake row 3 |

## Rows that would be nice and are NOT required

Deletion and scope governance (GateMem), stage attribution (HaluMem), and the
14-item reader-attribution confirmation. Each answers a real question. None is
needed to say which system to use. **They do not justify a generation on their
own** while rows 4-6 are open.

## Caveats that will ship with the answer, whatever it is

- Single hardware, single reader model, single inference configuration.
- Retrieval-heavy evidence throughout; no production workload, no private corpus.
- No external validation. Every independent check to date is an in-house AI review.
- Reader-attribution findings (Gen124) are exploratory permanently and may never
  be quoted as a system score. See `research/EVIDENCE_LANES.md`.

## Budget

**8 generations from Gen126.** Two are already accounted for: rows 4 and 5 are
one generation each if nothing breaks. At Gen134 this memo closes with whatever
rows it has, and the answer is stated at the confidence the evidence supports -
including "the evidence does not support a recommendation", which is a valid
close.

## Close condition

This memo closes when rows 4, 5 and 6 are filled, or at Gen134, whichever is
first. It does not close on the implementer's judgement that it is finished.
