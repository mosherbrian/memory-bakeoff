# External system: Engram Alpha — candidate discovery, 2026-09-17

**Found by the intel channel** (D-12/D-13): r/AIMemory daily backfill
2026-09-11..17, `team/INTEL/AGENT_MEMORY_INTEL_2026-09-17.md`, SYSTEMS TO
INVESTIGATE. **Source:** `github.com/techtheist/engram`. **Status: CANDIDATE
DISCOVERY ONLY — inspection recommended before any run decision. No number on
this card is ours.**

## What it is

A local-first graph memory for software-development agents, and notably the
CURRENT REFERENCE SYSTEM of KnowledgeDrift v2 (the benchmark we ran today as
S7-4). Its architecture makes memory behaviors explicit that our entrants
delegate to vector similarity or prompt reasoning:

- explicit `replaces` and `conflicts-with` edges — supersession and conflict
  as first-class graph state, not retrieval side-effects
- Tombstones for deliberately removed knowledge (deletion/release/purge)
- a local NLI conflict checker (flag-don't-fail, like our contradiction class)
- confidence-aware retrieval with strong/weak/none verdicts
- code-reference drift tracking
- an append-only audit journal (provenance/lineage)
- MCP access shared across coding assistants

## Why it matters to us, in order of importance

**1. It advances G2 (supersession) and G1 (conflict handling) as an ENTRANT
SHAPE.** S7-3 measured that pi-lcm's native store does NOT false-supersede
under stress distractors (0/32) and refused a state layer on that number; a
system whose write path natively encodes supersession edges is the honest test
of whether explicit mutation state buys anything on our fixtures — the
compose/state-layer question re-grounded on an engine that exposes the
operations instead of hiding them.

**2. It is the natural adapter for the HONEST-CAPABILITY-N/A pattern.**
S7-4 had to excuse six of nine KD families because bm25 exposes no mutation
surface. An Engram adapter could DECLARE supersession/deletion/conflict
capabilities instead of silently scoring N/A — the comparison the intel calls
capability-aware and our results schema can carry as declared-vs-failed.

**3. Roadmap R-PE:** a second external lane entrant makes the external lane a
class rather than a single data point.

## What it lets us stop building

Potentially the state layer itself: Gate F option B asked whether pi-lcm needs
supersession state bolted on (S7-3: no). If a candidate system carries
supersession natively, the build-vs-adopt argument finally has a measured
object on both sides — but ONLY after inspection; nothing is adopted from this
card.

## What NOT to trust

- **Every quantitative claim is first-party by the benchmark's own author.**
  Engram is KnowledgeDrift v2's reference system; the owner-bias direction
  runs from both sides (BENCHMARK-OWNER-BIAS CHECK in the same report).
- "Alpha" maturity; self-reported LongMemEval-related retrieval tests and
  supersession ablations. Receipts are published, which makes reproduction
  possible — not true.
- The architecture description above is from the repository's own README as
  relayed by the intel report, not from our reads. Inspection precedes belief.

## Next step (bounded, $0, no run admitted by this card)

Inspect the mutation model and adapter surface — what operations the API
actually exposes, what a receipt of a supersede looks like — before any
bake-off run decision. Phase-G discipline: the deciding property gets
measured before anything is built on top of it.
