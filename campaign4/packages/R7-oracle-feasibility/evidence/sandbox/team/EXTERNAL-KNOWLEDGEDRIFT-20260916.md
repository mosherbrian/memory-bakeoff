# External benchmark: KnowledgeDrift v1 — candidate discovery, 2026-09-16

**Found by Brian** on r/AIMemory, which he flagged as a resource worth watching.
**Source post:** `reddit.com/r/AIMemory/comments/1wg074z/` (fetched via nanobrowser;
Reddit refuses WebFetch). **Repo:** `github.com/techtheist/KnowledgeDrift`, **MIT**.

**Status: CANDIDATE DISCOVERY ONLY. No score imported.** This card records what
the benchmark claims and what it would be useful for. It does not adopt its
numbers, for a reason stated at the bottom.

## What it is

Eight scored families, plus an optional ninth:

| family | what it tests |
|---|---|
| Retrieval | finds facts by own words, paraphrase, oblique reference, file path |
| **Abstention** | **correctly DECLINES on an unwritten subject, or a written subject with no note** |
| Currency | current state after a re-decision, and the complete history |
| Contradiction | flags disagreement between notes for human judgement |
| Drift | detects stale siblings imported without supersession |
| Deletion | purged notes stay gone; released notes return WITH a warning |
| Rationale | retrieves the reasoning behind a decision |
| Temporal | respects a ±5 day window in scoped queries |
| Authority (optional) | endorsement hierarchy: retrieval < assistant < user < supervisor |

**Scale:** 1,500 facts / 9,008 tasks at seed 1. Three-seed stability runs use
500 facts at seeds 1–3. Worlds are frozen under `worlds/v2/` and regenerate
from seed.

**Scoring, out of 1,000:** family points = Σ(pass rate × 100) over the eight
families (0–800); signal score = mean token relevance (0–100); token score =
logarithmic efficiency, 200 tokens ideal and 3,000 penalised (0–100).

## Why it matters to us, in order of importance

**1. ABSTENTION IS THE GAP WE IDENTIFIED TONIGHT.** The council's S6-2 exists
because our invocation instrument cannot fail a firehose: with one record per
store, returning everything guarantees a hit, so claude-mem's 30/30 measures
coverage rather than selectivity. KnowledgeDrift makes "should have retrieved
nothing" a first-class scored family — a question about a subject never written,
and a question about a written subject with no note. That is precisely the
control we were about to build from scratch.

**2. IT INDEPENDENTLY REPRODUCES OUR HEADLINE.** Its table has **TF-IDF at 580,
vector RAG at 359, Mem0 at 348.** A lexical baseline beating the memory systems
is the same shape as our own 2026-09-16 result (bm25 25/30 against claude-mem
and pi-lcm at 0/30 raw, 30/30 and 7/30 corrected). Two instruments, built by
different people, ranking a keyword baseline above memory products. That is
worth far more than either result alone.

**3. ITS FAMILIES MAP ONTO OUR FROZEN GOALS.** Contradiction → **G1** conflict
handling. Currency, Drift, Temporal → **G2** supersession. Abstention → the
selectivity property G3 invocation needs and our corpus lacks. Deletion and
Rationale have no G-equivalent and may be gaps in our own goal set rather than
extras in theirs.

## The caveat, which is the whole reason this is a card and not an adoption

**The benchmark's author has a system in its own ranking, and it wins.** The
repo lists "reference Engram" at 718, the top score, and the Reddit post leads
with "Engram Alpha: 80%". Under our own standing rule that is a **vendor-adjacent
claim**, in the same class as Mem0's 92.5% self-reported LoCoMo figure against
Memobase's independently measured 66.88% for the same system.

**The numbers also disagree with themselves.** The post says Mem0 55% / score 47
and Engram Alpha 80% / 459; the repo table says Mem0 348 and Engram 718. Same
project, two different scales, no reconciliation offered. Cite neither until
that is explained.

So: **adopt the STRUCTURE, verify any SCORE ourselves.** The eight families and
especially the abstention construction are a design contribution we can use
immediately. The leaderboard is a claim to be re-derived on our own instrument,
if we care about it at all.

## What this changes tomorrow

**S6-2 must cite this before building its corpus** — the standing rule is that a
row which re-measures anything cites the prior measurement or states that none
exists. One now exists, with frozen worlds under an MIT licence. The row should
say explicitly whether it is:

- **reusing** KnowledgeDrift's abstention construction (cheapest, and it is the
  exact control we lack),
- **running our engines against its frozen worlds** to get a second instrument
  on the same systems, or
- **building its own** anyway, with a stated reason why theirs does not fit.

Any of the three is defensible. Not knowing it exists is not.

**Also worth a look:** the post's discussion proposes adding **source authority**
and **evidence provenance** as dimensions. That is our own week in miniature —
recorded knowledge that was unreachable, and a verifier certifying arithmetic
rather than validity.
