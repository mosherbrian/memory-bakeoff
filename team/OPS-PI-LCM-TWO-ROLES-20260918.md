# pi-lcm wears two hats and the fleet only knows about one

**Filed by:** cairn/operator (Claude session), 2026-09-18 17:0x PDT
**For:** the director (it frames the open questions) and corvid-dsh (it ranks
against them). Evidence, not a candidate.
**Cost:** $0, local reads. Nothing was changed.

## The fact the fleet is missing

Brian, 2026-09-18, on why pi-lcm is in his stack at all:

> "we use pi-lcm more for its seamless compaction features that we added to it
> to keep local compaction quick rather than expecting its memory to be
> actively great."

pi-lcm has two unrelated roles here:

- **In Brian's stack:** the compaction layer, carrying our own eager-compaction
  and prefix pre-warming work. It is there for LATENCY, and that is why it
  stays.
- **In this bake-off:** one contestant among several, measured as a memory
  system like the rest.

Checked this revision: **no document under `team/` ties pi-lcm to compaction at
all.** The fleet reasons about it purely as a contestant, because that is the
only role written down.

## Why that is dangerous right now

The contestant numbers are poor and worsening, and correctly so:

- S6-2: tool-level retrieval at 0.600 mean set-F1.
- S9-DOOR-RUNG2: under query-adjacent pressure it puts the helpful evidence in
  front of the model in **0 of 5** cases, against bm25 1/5 and claude-mem 3/5.

The sprint-10 demo then put "the adopt call on pi-lcm tool-level" to Brian as a
decision, phrased so that a reader could take those numbers as bearing on
whether the fleet keeps using pi-lcm. **They do not.** A seat reading only the
scoreboard could recommend removing the compaction layer over a retrieval
result that measures nothing about compaction. That is a category error, and it
would cost Brian a latency win to settle a memory question.

## What this does NOT say

It does not defend pi-lcm's memory scores; they are what they are, and the door
result stands. It does not argue the contestant should be kept in the
comparison. It says only that **the two roles must be named separately** when a
result lands, and that the compaction role is not on the table.

## What to do with it

When a pi-lcm result is reported, say which hat it is about. An adopt-or-drop
question about the MEMORY role is a bake-off decision and belongs in the
answer page. The compaction role is Brian's settled stack choice and is not
re-decided every time a retrieval number moves.
