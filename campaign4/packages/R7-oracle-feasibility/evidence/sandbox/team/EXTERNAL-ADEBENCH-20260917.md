# External benchmark: adebench — candidate discovery, 2026-09-17

**Found by the intel channel** (D-12/D-13): r/AIMemory daily backfill
2026-09-11..17, `team/INTEL/AGENT_MEMORY_INTEL_2026-09-17.md`, BENCHMARKS TO
INVESTIGATE. **Source:** `github.com/adecubed/adebench`, plus the author's
r/AIMemory post of September 13. **Status: CANDIDATE DISCOVERY ONLY — method
adopted as a design idea, no integration, no number imported.**

## What it is

A benchmark for the memory "door": the exact text a client actually receives
from memory AFTER the system's final composition step — retrieval results
already ordered, merged, summarized, and cut to a budget. The published
comparison used a 2,400-character door and repeated the measurement under
simulated pressure from large MCP tool responses competing for the same
context.

The reported finding that matters: changing retrieval improved recall while
WORSENing the delivered context (repeated chunks), and a two-step retrieval
path behaved differently from a one-call composed path at the same final
budget. "The store found it" and "the agent saw it" came apart.

## Why it matters to us, in order of importance

**1. It operationalizes a rule we already wrote.** AGENTS.md's standing
evaluation rules require reporting exact returned context size and
prohibited/stale presence alongside every score — because a hit delivered
inside noise is not selectivity. adebench is that rule as a first-class
metric, with a pressure dimension we do not exercise.

**2. It advances G3 (invocation) and G4 (material outcome).** The door is the
antecedent of outcome: S6-2 measured what the store returns; the outcome
experiment (next-experiment.json, proposed-not-built) tests what work does
with it. The door metric is the missing middle instrumentation between those
two, and it is $0 local instrument work.

**3. It gives the S7-4 numbers their second axis.** Our KnowledgeDrift run
scored retrieval families; the card's own caveat and the upstream ladder both
warn that token-efficiency is a separate phenomenon. A door metric over the
same frozen items would show whether our engines' delivered bytes are signal
or padding, without importing anyone's weights.

## What it lets us stop building

Nothing — deliberately. This is a measurement layer, not a system or an
integration. It stops retrieval scores standing in for did-the-agent-see-it,
which is a measurement mistake, not a missing component.

## What NOT to trust

- The published winner (gbrain/ADE Brain) ran on the author's own golden set,
  and in that run consumed already-distilled facts — the comparison's method
  is the contribution, its ranking is not evidence.
- Single-author, single-system comparison; no independent reproduction.
- The 2,400-character door and the tool-pressure simulation are that benchmark's
  parameters, not laws — ours would be declared before the run, like every
  other frozen configuration.

## Next step (bounded, $0, no run admitted by this card)

Backlogged as rank 11 in `BACKLOG-NEXT.md`: a minimal door metric over our
existing adapters — score evidence presence and irrelevant delivered bytes at
a declared budget, normal and under competing tool-output pressure — before
any thought of adebench integration.

---

## UPDATE 2026-09-19 — the author's follow-up run, and a design result

**Source:** r/AIMemory, `Soft-Lie-434`, 6 days before reading —
https://www.reddit.com/r/AIMemory/comments/1wffx8s/i_benchmarked_my_assistants_memory_against_garry/
Brian supplied the link. Post is locked and archived; two comment threads, no
substantive critique in them. **Still no number imported, still no
integration.**

The author ran their own memory and Garry Tan's `gbrain` on one golden set: 25
questions, 3,568 pages, local embeddings both sides, both doors cut at 2,400
characters, repeated under measured MCP pressure (census p95 = 35 KB).

### The result worth having is not the head-to-head

It is the **one-call versus two-step door at a fixed budget**, run on the same
memory:

| door | clean | under p95 pressure |
|---|---|---|
| one-call composed | 23/25 | 19/25 |
| two-step (brief, then fetch) | 17/25 | **8/25** |
| two-step, details capped at 300 chars | 18/25 | — |

The author's explanation: the brief spends about 1,400 of the 2,400 characters
on previews, which the one-call door spends on the entity card whole plus facts
cut at 220. Their conclusion, which is the sentence to keep:

> "Under a tight budget the winner is whoever spends it on content, not the
> number of calls."

And it did not generalize - on `gbrain` the two-step door went the other way,
18 -> 20. So this is a property of a memory's composition, not of two-step
retrieval as such.

### Why this bears on our own measurement

Our Q6 answer already says competing text displaces useful evidence at a
600-character limit on five constructed cases. This is the same phenomenon,
independently found, at a 2,400-character budget, on a different corpus, with a
repo behind it. That is the first external corroboration of a finding this
project made on its own - which is worth more than the benchmark itself.

It also names the open problem in our own terms: their remaining five lost
points are "answers that live in facts, not in the entity card, and don't make
it into the 2,400 characters." Their question to the sub is the one we have not
answered either: **how do you decide what goes in the door when the answer is a
fact and not a card?**

### Caveats - the author states most of them, which is why they are quotable

- Their own golden set, their own scoring.
- `gbrain` received facts the author's system had already distilled, so the
  comparison measures **retrieval and composition, not extraction**.
- `gbrain`'s real door is two-step and could not be scored in one call, so its
  search door was measured with a cut - not the door its users get.
- 25 questions. Head-to-head margins of 76.9 vs 71.9 on 80 points are not
  separable at that n, and nothing here should be cited as one system beating
  another.
- The separate claim that vectors on episodes moved LongMemEval-S retrieval from
  64.5 to 88.7 is unverified and on their stack.

### What changed about what we might do

The card previously said "method adopted as a design idea, no integration." The
author now asks for exactly what we could supply - "a third system measured the
same way is what the benchmark lacks most" - and states the adapter is one
class. We hold several measured systems and a frozen corpus.

That is a cheap, local, external-lane measurement aimed at the door problem we
have already measured internally. Whether it is worth a row is the Director's
call, and it belongs in the agenda audit rather than ahead of it.
