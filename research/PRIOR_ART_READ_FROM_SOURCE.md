# ConflictQA read from the dataset, not from a search summary

Fetched 2026-09-07 from `github.com/Tianzhe26/ConflictQA`. SIGIR 2026, paper
arXiv:2604.11209. Seven JSON files, ~802 items in the one inspected.

## What an item actually is

    id                WebQTest-0
    question          "what does jamaican people speak"
    answer            ["Jamaican English", "Jamaican Creole English Language"]
    q_entity          ["Jamaica"]
    a_entity          [...]
    positive_triples  ["(Jamaica, location.country.official_language, ...)"]
    positive_texts    ["- Patois: Patois, often referred to as ..."]

The splits are `_Pos` (clean), `_TextConf` (the textual evidence is made
inconsistent) and `_TripleConf` (the KG evidence is). Two settings, COMP and
Non-COMP, for complementary and non-complementary evidence.

## Why this matters for our claim

I said twice tonight that nobody had published the ordering manipulation, then
retracted it to "ConflictQA does this, our niche is narrower". That retraction
was made from a search summary. Reading the data confirms the narrowing and
makes it precise:

- **ConflictQA has no time dimension at all.** No timestamps, no sessions, no
  speaker, no before and after. Its conflict is between two SOURCES about a
  static world fact, where one has been made wrong.
- **Ours is one speaker at two times, and BOTH statements were true when made.**
  Nothing in the record is false. The earlier value is not wrong evidence; it is
  correct evidence that has been superseded.
- **The tasks differ.** ConflictQA asks which source to trust. Ours asks what is
  true NOW. A model can be perfectly faithful to sources and still fail ours.
- **The failure differs.** Theirs is a model believing a corrupted passage.
  Ours is a model reporting a value the user themselves has since revised.

So the ordering result they report - correct evidence first helps - is about
source ordering under corruption, not about recency under supersession. The two
can come apart: a model with a strong "trust the last source" bias would score
WELL on ours if the current record is last, and its position bias would look
like faithfulness.

## What this does NOT license

It does not restore any novelty claim. Position bias is separately and heavily
benchmarked, and "order of conflicting evidence matters" is published. What is
open is the supersession-in-a-memory-setting version, and that is a niche, not
new ground. The handoff must keep saying so.

## Usable as a substrate?

No, and it should not be forced. Without a time dimension there is no
superseded-vs-current pair to order. Converting it would mean inventing the
supersession, which is hand-writing fixtures again with extra steps.

---

# MemConflict, read the same way - and it is closer to us than ConflictQA

`github.com/TaoZhen1110/MemConflict`, already PINNED in this repo
(`research/MEMCONFLICT_PIN.json`, upstream `ec51d5d`), though not vendored.

Its own README:

> **Dynamic conflict | Temporal validity | Identify the current valid state
> after **true user updates**.**

That is our problem statement, written by someone else, with three conflict
types (dynamic/temporal, static/factual, conditional/contextual) and real
memory systems in the loop: `eval_a_mem`, `eval_langmem`, `eval_letta`,
`eval_memobase`, `eval_memos`, `eval_memzero`.

So the honest position moves again:

- **ConflictQA** is NOT our neighbour. No time dimension, corrupted sources,
  "which source do I trust".
- **MemConflict** IS our neighbour, and it is nearer than I said in the handoff.
  It owns "supersession in a memory setting" outright.

## What it ablates, and what it does not

Its `Ablation/` directories are exactly four:

    Conflict_Interval   distance between the conflicting mentions, Long / Short
    Long                dialogue length
    No_Interference     distractors removed
    Question_Style      query phrasing

`Conflict_Interval` varies **how far apart** the two conflicting statements sit.
It does not appear to vary **which comes first** - in a multi-session dialogue
the sessions run forward, and nothing in the tree permutes them. Distance is not
order.

## What our niche actually is now

Not "supersession ordering in a memory setting" - MemConflict has that.
It is narrower:

  **hold retrieval perfect, and reverse the presentation order of a superseded
  and a current record.**

MemConflict measures memory systems end to end, so a failure there could be
retrieval OR reading. The oracle split plus an order swap isolates the reading
half. That is a real and small contribution, and the handoff must say small.

## Consequence for Phase 2 that outranks the niche

MemConflict is the better substrate for the BAKE-OFF question, which is which
memory system to use - it already harnesses six of them and is already pinned
here. LongMemEval-oracle is the better substrate for the READER question,
because retrieval is perfect by construction.

Those are two different experiments and we have been conflating them. The
control-plane question for Gen125 is which one Phase 2 is actually asking.
