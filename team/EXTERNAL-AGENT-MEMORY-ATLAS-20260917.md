# External: Agent Memory Atlas — candidate discovery, 2026-09-17

**Found by Brian**, from the sources cited in the first daily intelligence
report. Not named in the report body itself, and not previously anywhere in this
repo. **Source:** `neoneye.github.io/agent-memory-atlas/benchmarks/`, repo
`github.com/neoneye/agent-memory-atlas`.

**Status: CANDIDATE DISCOVERY. No number imported.** This is the highest-value
external find so far, and the reason is not its data - it is its METHOD.

## What it is

A survey of **580+ memory systems** and their benchmarks, whose stated method is
to read **committed code at pinned commits** rather than published claims, and
to flag vendor-run comparisons explicitly — its own phrase for the conflict is
comparing *"them with them plus us"*. It distinguishes benchmarks it read at a
commit from ones it only names.

Benchmarks it read directly, with the properties we care about:

| benchmark | measures | scale | licence |
|---|---|---|---|
| MemoryAgentBench | multi-turn; its real section is "Conflict_Resolution" | 456 facts, 123 conflicts | public |
| PersistBench | whether a model applies memory it should NOT | 500 committed items | public |
| ForgetEval | scores `supersede` / `release` / `purge` | 13 configurations | MIT |
| KnowledgeDrift | re-decision, contradiction, deletion, lineage, token cost | seeded worlds | MIT |
| BEAM | extreme-length QA, contradiction resolution | 100K and 10M tokens | public |
| Oolong | long-context reasoning and aggregation | 128K | public |
| MerchantBench | 366 simulated days; memory failure visible only as money | year-long sim | simulator released |
| GoodAI LTM | 20 datasets incl. prospective memory, theory of mind | 20 | public |

## Why this matters more than a leaderboard

**1. IT INDEPENDENTLY FOUND OUR OWN CAVEAT ABOUT KNOWLEDGEDRIFT.** Our card
`EXTERNAL-KNOWLEDGEDRIFT-20260916.md` refused to cite that benchmark's scores
because its author's own system tops its leaderboard. The atlas records the same
thing, in more detail: Engram Alpha at 0.82–0.85 success and 511–543 score
against ~0.61–0.66 and 52 for baselines, and it exposes the scoring formula
`score = 100 x composite x clamp(10·S, 0.1, 10)` where S is the answer-record
token share — **0.57 in-process versus 0.11 for adapters**. That term rewards a
system for being in-process, which is what the author's own system is. Two
independent readers reaching the same conclusion about the same benchmark is
worth more than either reading.

**2. IT DOCUMENTS THE EXACT DEFECT OUR SPRINT IS BUILT AROUND.** On
LongMemEval: *"Retrieval is never scored on the abstention items"* — the harness
filters `'_abs' not in x['question_id']` before computing metrics. That is S6-2's
whole premise, found in a different harness by someone else. If we needed
evidence that abstention scoring is a real and general gap rather than our own
pedantry, this is it.

**3. IT KEEPS FINDING CHECKS THAT CANNOT FAIL, which is our recurring failure
class.** On GoodAI LTM: seven datasets send `forget` messages that are never
scored, and *"Nothing checks that it took effect"* — the reset assertion never
runs. On MemoryAgentBench: the literature calls it a forgetting benchmark and
its actual section is conflict resolution. These are the same species of defect
as our exit-127 gates and our vacuous D-4 check.

**4. IT NAMES THE COUNTER-EXAMPLE FOR OUR OWN REPORTING.** Zep publishes 1,540
questions per run over 10 runs with a per-run spread of 0.33–0.47 SD, so a
reader can tell signal from judge noise. We do not report run-to-run spread at
all. Every single-run number we have published is weaker than it looks, and this
is the cheapest possible fix to adopt.

## Goal mapping

- **G1 conflict handling** — MemoryAgentBench's real Conflict_Resolution split,
  BEAM's contradiction track.
- **G2 supersession** — ForgetEval (MIT) scores supersede/release/purge
  directly, which is the closest external instrument to G2 we have found.
  PersistBench tests wrong-application, the inverse failure.
- **G3 invocation/selectivity** — the LongMemEval abstention-filtering finding.
- **G4 material outcome** — MerchantBench makes memory failure visible only as
  money over 366 simulated days. That is the shape S7-1's outcome experiment is
  reaching for, already built by someone else.
- **Roadmap R-PE external lanes** — this is a register of external lanes.

## What it lets us stop building

- **Stop hand-surveying the field.** 580+ systems read at pinned commits is
  strictly better than our `ECOSYSTEM-MAP.md` census, and it is maintained.
- **Stop constructing our own forgetting instrument** before reading ForgetEval.
- **Stop treating our single-run numbers as adequate** — adopt run-spread
  reporting from Zep's example rather than inventing a convention.

## What NOT to trust

- **It is a READING of other people's code, not a re-run.** Its benchmark
  properties are verifiable (pinned commits, quotable filters); its reported
  SCORES are still other people's numbers. Cite the properties, re-derive any
  score.
- **We have not verified the conflict-of-interest claim about the atlas itself.**
  The fetch reported no competing system inside its comparison set, but that is
  the summariser's reading, not our check. Before we lean on this as a neutral
  register, someone should confirm the maintainer has no system in the 580.
- **"580+" is a count we have not counted.**
- Its own KnowledgeDrift figures differ in presentation from the ones in our
  2026-09-16 card. Neither set is citable until one of us re-derives them.

## What this changes

1. **S6-2 / S7 abstention work should cite the LongMemEval filter finding.** It
   turns our concern from a local suspicion into a documented general defect.
2. **ForgetEval deserves a backlog slot ahead of building our own G2
   instrument** — MIT, already scoring the three operations G2 cares about.
3. **Run-spread reporting is a cheap standing rule to adopt**, and every past
   single-run headline should be marked as single-run rather than quietly left.
4. **Verify the atlas's own neutrality before relying on it.** A register that
   flags everyone else's conflicts is exactly the artifact whose own conflicts
   matter most.
