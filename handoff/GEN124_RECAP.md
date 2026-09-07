# Gen124 recap, in plain words

## What changed

We stopped hand-writing the test material. For five generations the experiment
used twelve sentences I wrote myself, and most of a day went into making the
thirteenth set better. That path is closed.

Instead we found a public dataset - LongMemEval - that already contains what we
were building. Inside it, 78 items have exactly the shape we need: a person says
something in one conversation, revises it in a later one, and is then asked what
is true now. Someone else built those, professionally, and published them.

## What was tested

Thirty-four of those items, each asked twice. The only difference between the two
askings was the order the two conversations appeared in. Same words, same
content, same question.

## What happened

With the conversation dates shown, as the dataset ships them:

    old conversation first, current one last   23 of 34 right
    current one first, old one last            18 of 34 right

Then we removed the dates and asked all 34 again:

    old conversation first, current one last   22 of 34 right
    current one first, old one last             9 of 34 right

Removing the dates barely touched the first case and cut the second in half.

Then we found a problem with the material itself. Checking every item instead of
a sample, 8 of them have the correct answer in the EARLIER conversation, which
breaks the whole setup. One of those 8 was the single item in the entire pilot
that favoured the reversed order - so the one piece of evidence against the
effect came from an item where the assumption does not hold.

Dropping those, on the 30 items that are sound:

    dates shown      old first 22 of 30    current first 16 of 30
    dates removed    old first 21 of 30    current first  7 of 30

Fourteen items are right only when the current conversation comes last. None go
the other way.

And when it got them wrong, it answered with the outdated value. We checked all
fourteen: twelve of the wrong answers are word-for-word the superseded value
from the earlier conversation.

    correct answer $400,000   ->  it said $350,000
    correct answer Paris      ->  it said Hawaii
    correct answer Friday     ->  it said Thursday
    correct answer Ford F-150 ->  it said Ford Mustang Shelby GT350
    correct answer Yes        ->  it said No

That matters because the reviewers argued our scoring was too crude to trust at
this size. It is crude - it marks "4" wrong when the expected answer is "four".

I first answered that a crude scorer gets it wrong in both orders, so it cannot
create a difference. That reply was wrong, and a reviewer built the case that
breaks it: if the old conversation writes a number as "four" and the new one as
"4", a model that echoes whatever form it read last would answer "four" when the
order is reversed - correct in meaning, marked wrong by a crude scorer, in one
order only. That is a manufactured difference.

So the argument is dead and the check is what stands: we read all fourteen and
twelve are the specific old value, not a formatting variant. A reviewer
independently confirmed none of them are form artifacts. The result survives on
the evidence rather than on the argument I made for it.

## What it means

The reader looks like it answers with whatever it read last, rather than with
whatever is current. Putting the conversations in date order protects it by
accident, because the current fact happens to end up at the end.

The dates were doing some work, and not much. When they were visible the model
recovered about half of what position cost it. When they were gone it barely
recovered anything.

The tempting conclusion is "it follows position, not dates". We cannot say that
yet, and our own technical record says so. Two things other than position are
still in the prompt: most items mention a month or a weekday inside the
conversation text, and - worse - the question we asked ended with "as of the
most recent conversation", which points at POSITION in the transcript rather
than at time. A model that assumes the conversations are in date order would
read the last-shown one as the newest, which in the reversed case is the old
one. So the honest statement is that order changes the answer, and we have not
yet separated position from the leftover time words and our own badly worded
question. The next run's question is already rewritten to fix the second one.

If that holds, it matters directly for the thing this project is choosing
between: a memory system that returns records in relevance order rather than date
order can put the outdated one last, and the model will use it. That would make
"did it retrieve the right record" the wrong thing to score.

## What is NOT established

This is a pilot, not a result. Three reasons, all of them real:

1. The scorer is crude. It marks the answer "4" wrong when the expected answer is
   "four". Good enough to see whether an effect exists, not good enough to
   publish a number.
2. The date removal is partial. The headings are gone, but 29 of the 34 items
   still mention a month or a year somewhere inside the conversation. So the
   second pass is "most of the date cue removed", not "no date cue", and the
   real effect of dates sits somewhere at or beyond what we measured.
3. Half the items were deliberately NOT used. Anything we look at tonight is
   exploratory forever, because a rule chosen after seeing an outcome is the
   error that cost us Gen114. Thirty-four items are held back, untouched, for a
   run whose rule is fixed before anyone looks.

## What I got wrong, and had to retract

The reviewers returned a blocking verdict and were right on all five points. The
worst one: I claimed nobody had published work on this ordering question. That
was false, and I found the work myself within minutes of being challenged.
ConflictQA already runs this manipulation and released its code. What survives is
narrower - it orders two sources that disagree, not an outdated value against a
current one - and the next steps have to be argued on that narrower ground.

I also described a benchmark as being in our repository when it is not, and it
was the pin file that told me so, which I cited without reading.

## Something I found late, which may matter more than the result

I went and read the two published projects nearest to ours, from their actual
data rather than from summaries of them.

**MemConflict** turns out to be much closer to us than I told you earlier. Its
own description is "identify the current valid state after true user updates" -
that is our sentence, written by someone else - and it already harnesses six
real memory systems. It is also already pinned in our repository, and I had
described it in a handoff without reading what it does.

It varies four things: how far apart the two conflicting statements sit, how
long the dialogue is, how many distractors there are, and how the question is
phrased. It does not appear to vary which statement comes first. So our piece
survives, but it is small, and it should be described as small: hold retrieval
perfect, and swap the order.

**The bigger point is that we have been running two different experiments and
calling them one.**

- *Which memory system should we use?* MemConflict is the better ground - it
  already has six systems in a harness.
- *How much of the failure is the reader's fault, whatever the memory system
  did?* LongMemEval-oracle is the better ground, because retrieval there is
  perfect by construction and cannot be blamed.

Both are worth doing and they answer different questions. Deciding which one
Phase 2 is actually asking is the first thing the control plane should rule on,
ahead of anything else in this handoff.

## What comes next

The apparatus - the runner, the sealing, the freeze gates - is reusable and is
not what has to change. What has to change before any of this becomes evidence:

- a real scorer, with both the current and outdated value extracted per item
- a content hash pinning the dataset, which nothing currently does
- a decision about the marking scheme, because the frozen one needs five
  conditions per item and these items afford two
- the ceiling arm balanced across both orders, since on this substrate the
  "perfect records" control is itself one of the two orderings

Those are design questions for the control plane, not implementation work.
