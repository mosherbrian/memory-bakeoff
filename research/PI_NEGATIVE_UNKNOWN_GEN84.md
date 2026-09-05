# Gen84 — Negative-Unknown Reattribution Audit

**Contract:** `negative-unknown-audit-v1`
**Engine runs:** none. **No reader added**, by instruction.

## The question

Gen68 reported `negative_unknown` as **0/3 for all four engines**, and concluded
that "every engine returns evidence for a question whose answer should be
unknown". Gen83 showed the other universal zero on that table was an unpassable
case rather than a memory result. This is the same treatment for the second, and
it finds a different defect.

`LQ16` asks *"Nimbus on call"* at `CP04`, expects no evidence, prohibits nothing.
The scorer charges `unsupported_evidence` for anything returned. **The only clean
answer is the empty result set.**

## The split

Answering an unanswerable question is two abilities, and the benchmark scores
them as one:

- **retrieval abstention** — can the retrieval surface return nothing? Needs a
  relevance floor the caller can set, and a score the caller can see.
- **answer abstention** — can a reader say "unknown" while holding retrieved
  distractors? That is what `score_answer_claim` grades.

Both are real in the code, not just in prose: the retrieval scorer can never emit
`unknown_hallucination`, and the claim scorer can never emit
`unsupported_evidence`. Asserted in the tests.

## 1. Both layers fire, and both stay silent

| layer | fires | silent |
|---|---|---|
| retrieval abstention | one record, or the whole store → `unsupported_evidence` | empty result → clean |
| answer abstention | a confident assertion → `unknown_hallucination` | a refusal → clean |

Neither is a dead class. As with Gen83, the ruler is not the problem.

## 2. What the engines were actually asked

At `CP04` the store holds **four** records. The adapters requested a limit of
**five**. Every engine returned everything it had:

| engine | returned | top score | scored cases peaking *below* it |
|---|---|---|---|
| perseus | 4 of 4 | *(no score emitted)* | — |
| hindsight | 4 of 4 | 0.0410 | **6 of 19** |
| mem0 | 4 of 4 | 0.4644 | **1 of 19** |
| agentmemory | 2 of 4 | **1.05** | **13 of 19** |

Identical across all three repetitions.

**A retriever asked for the best five of four records did exactly what it was
asked. Refusing was never on the menu.**

## 3. No relevance floor can rescue the case

The obvious repair — set a threshold and let the engine abstain — does not work
on any of the four.

**perseus** returns no score at all, so no threshold is expressible by the engine
or the harness. `NOT_DEMONSTRABLE`.

**hindsight** exposes `bank_id`, `query`, `max_tokens`. `max_tokens` is a size
budget, not a relevance floor. Scores come back and nothing consumes them. A
floor above `LQ16`'s own peak would also silence **6 of 19** questions that do
have answers.

**mem0** is the only engine of the four with a caller-settable floor, pinned at
`0.1` by the frozen adapter. `LQ16` peaks at `0.46`. Raising the floor past it
also silences `LQ17`, a legitimate question.

**agentmemory** exposes no threshold, and inverts the problem entirely: `LQ16`
scores **1.05 — the highest of any case in the run**. It is *most* confident on
the one question with no answer, and outranks **13 of 19** real questions. No
floor separates it without cutting nearly everything.

So the unanswerable question is not less similar to the corpus than the
answerable ones. On three engines it is *more*.

## 4. Attribution

**Retrieval abstention: `NOT_DEMONSTRABLE`** for perseus, hindsight and
agentmemory — the surface offers no way to abstain, so failing to abstain is not
evidence about the engine. For mem0 the mechanism exists and was exercised at
`0.1`, but no setting of it separates this case.

**Answer abstention: `NOT_DEMONSTRABLE`** for all four. No reader answer was ever
produced or graded in Round 2. `unknown_hallucination` has been reachable since
Gen69 and **has still never fired in a scored run**. The capability the case is
named for was never exercised by anyone.

## Verdict

**Gen68's line is RETRACTED.** "Every engine returns evidence for a question whose
answer should be unknown" describes the harness asking for top-k and charging the
answer to the engine. It is not a measured hallucination.

The 0/3 measured **top-k retrieval, scored as if it were an abstention
decision**.

## What this does not say

It does not say these engines would abstain correctly — that is exactly what
`NOT_DEMONSTRABLE` withholds. It does not say the fixture is wrong to include an
unanswerable question; the question is good and the grading channel is wrong. And
**no reader was added**: attributing the zero comes first, and a reader is a new
configuration boundary that belongs to its own generation with its own controls.

## Both universal zeros are now attributed

| axis | Gen68 read it as | what it was |
|---|---|---|
| `recommended_procedure` | nobody adopts the recommendation | every engine returned it; an unpassable case (Gen83) |
| `negative_unknown` | everybody hallucinates | nobody was asked to abstain; top-k graded as a decision (Gen84) |

Neither survived as a product result. Four universal zeros have now been examined
across Gen69, Gen73, Gen83 and Gen84, and **none of them was evidence about a
memory system**.
