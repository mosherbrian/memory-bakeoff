# Two lanes, never one score

Written in Gen125 under a control-plane ruling. Short on purpose: this is the
distinction the project spent seven generations not making, and it must be
readable in one sitting.

## The two questions

**SYSTEM SELECTION — the primary lane, and the project's actual question.**

> Which memory system maintains and returns the right evolving state under
> realistic ingestion and retrieval?

Everything is under test: what gets extracted, what gets written, what
supersedes what, what is retrieved, with what provenance and scope.

Substrates: `longitudinal-v1`, MemConflict, and any external system benchmark
admitted through the Phase-D gate.

**READER ATTRIBUTION — the explanatory lane.**

> Given the same relevant old and current records, how much do order and
> chronology change the reader's answer?

Retrieval is held perfect by construction, so nothing here can be blamed on a
memory system. Substrate: LongMemEval **oracle** split, which is what makes the
lane possible.

## The rule

**Never combine the two lanes' metrics into one score, and never use
reader-ordering performance as a proxy for memory-system quality.**

A reader that answers with whatever it read last will look bad in this lane and
tells you nothing about whether Mem0 retrieves better than Perseus.

## Why the reader lane exists at all

It answers a question the primary lane cannot: *can a memory system fail even
when its retrieval recall looks perfect?* If co-returning a stale record and a
current one changes the answer depending on order, then "retrieved the right
record" is not sufficient, and retrieval hit-rate is the wrong thing to score.

That is its whole job. It explains failures seen in the primary lane. It does
not rank systems and never produces a winner.

## Where Gen124 fits

Gen124 is reader-attribution, exploratory, and stays that way permanently.

- 17 items after eligibility cleaning, dates stripped: chronological 14/17,
  reversed 5/17, discordant 9 vs 0.
- 12 of the 14 discordant items in the as-run arm returned the SUPERSEDED value.
- Confounded: 28 of 34 items carry a month or year in the conversation text, and
  the pilot's own question said "as of the most recent conversation", which
  points at transcript position.
- Scorer and eligibility rule were both repaired DURING review, so it is
  exploratory by construction and cannot be promoted later.
- 14 holdout items remain untouched and unauthorised. See
  `research/pilot_ordering/PREREGISTRATION.md`.

It is not a roadmap phase and never was. It is Phase-D-quality apparatus that
was pointed at the explanatory question during an unpaused queue.

## The check to apply before publishing any number

1. Which lane produced it?
2. Was retrieval under test, or held perfect?
3. If it came from the reader lane, does the sentence around it claim anything
   about a memory system? If so, it is wrong.
