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
Fourteen items were then right only when the current conversation came last;
one was right only the other way.

And when it got them wrong, it answered with the outdated value:

    correct answer $400,000  ->  it said $350,000
    correct answer Paris     ->  it said Hawaii
    correct answer 120       ->  it said 125

## What it means

The reader looks like it answers with whatever it read last, rather than with
whatever is current. Putting the conversations in date order protects it by
accident, because the current fact happens to end up at the end.

The dates were doing some work, and not much. When they were visible the model
recovered about half of what position cost it. When they were gone it barely
recovered anything. So it is not reading the dates and reasoning about which is
newer - it is mostly following position, with the dates as a weak correction.

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
