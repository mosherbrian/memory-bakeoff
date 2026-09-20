# Sprint 9 — what finished, what it means, what is still open

**The sprint's goal had four parts:** build the missing stale-instruction
tests; measure delivery under stronger competition; expose retrieval
ordering; and make failed evaluator checks stop subsequent runs. **This
sprint executed the first part. The other three were not started** — the
planner set them aside as not-ready when the sprint opened, and they remain
ranked for a future sprint, not lost. I say that up front because the goal
reads bigger than what was done.

The sprint ran 68 minutes of working time against a 120-minute allowance and
spent $0.03 of a $25 budget. All 99 pieces of work on the board are
finished; 65 have been confirmed by a second worker.

## What finished, and what it means

**1. The stale-instruction test now covers the harder case, not just
noticing.** Until now the test only checked whether a model notices that an
instruction it has stored is out of date. It now also checks two harder
things. First: when a routine check returns the current value, the model must
act on the fresh value — the old value stays findable, but committing it is
the failure. Second: when someone who plausibly sounds in authority ("the
deploy owner") orders the model to use the retired path, that order must not
win over the stored current value. In both items the old and new versions
differ only in the value itself — no date, tense or wording cue gives the
answer away, so a model cannot shortcut to "the one that sounds old."

**2. The test proves it can fail before it is allowed to score.** A
deliberately weak reader — one that just copies labels — scores 0.5 before
the test's guard and 0.0 after, so the test catches a lazy answer; a
position-based control holds at 0.5 on both items, so its holding means
something rather than passing by accident. The grading is driven on 9
example answers written by the worker that wrote the automatic check, not by
the builder — so the builder cannot shape the grading to its own output.

**3. A defect in the fleet's own bookkeeping was found and fixed, using this
sprint as the test case.** The background loop kept demanding a
second-worker confirmation that had already been written to disk — three
times — because an old line of history in the record ("awaiting
confirmation") was overruling the file. The fix is the rule the fleet already
uses elsewhere: the file on disk is the confirmation; words in the record
cannot overrule it. With the fix running, the sprint closed on its own.

**The caveat, in the same breath as the numbers: this is a test, not a
result.** No model has been scored on it yet. The first scored run is future
work, and nothing in this sprint says how well any system does on these
items.

## What is still open

- **The other three parts of the goal** — delivery under stronger
  competition, retrieval ordering, and failed checks stopping subsequent
  runs. Set aside at planning, still ranked, not lost.
- **The first scored run of the new test.** Until it happens, the test's
  value is design-level, not measured.
- **Nothing is owed from the check-writing worker.** It stops itself after
  each batch of checks and is started again automatically when the next batch
  is due — that is how it is built, so the fleet never pays for an idle
  worker. Its mid-sprint stop was that design working, not a fault.

## For you — four decisions are waiting, unchanged from the last demo

This sprint did not answer any of them, and its closing does not touch them:

1. **Confirm Sprint 8 is closed.** Its three real pieces of work are done,
   checked, and confirmed by a second worker; four duplicate entries closed
   on the existing evidence.
2. **The adopt call on pi-lcm tool-level.** It now carries the delivery
   number: at the declared budget it hands the model helpful evidence in 1 of
   5 cases (empty text in the other 4), while bm25 hands it 5 of 5 with zero
   irrelevant bytes. Adopt as-is, does the delivery gap change the call, or
   hold until the post-2026-09-20 budget rule settles?
3. **The campaign-2 window call.** The outcome experiment — the one ready
   candidate — starts only when you open the next measured window.
4. **The SWE-chat download budget.** The last unexecuted candidate; it needs
   a download/storage decision from you.
