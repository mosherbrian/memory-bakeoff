# S7-4 design — KnowledgeDrift frozen worlds as a second instrument

Row S7-4 (sprint 7, BACKLOG-NEXT rank 5). Author: kiln-flash, 2026-09-17.
The binding declaration is `declaration.json`, written before any receipt and
sha-bound into all of them; the item list is frozen by sha256 inside it. This
file is the prose companion. $0, local, no LLM, no score import.

## What was run, and on whose corpus

Our engine (the pinned in-tree bm25 baseline, evidence class `baseline`) was
run against the upstream frozen worlds — not against anything we built. The
worlds are the 500-fact `worlds/v2` files at seeds 1 and 2, from
`github.com/techtheist/KnowledgeDrift` at the commit pinned in the
declaration (MIT; the clone sits under `upstream/` here and each used file is
pinned by sha256). Per the card, the STRUCTURE is adopted and every SCORE is
re-derived here; no upstream number is cited or approached.

## Replay and sampling (declared before the run)

Ops are replayed in stream order, which the upstream protocol declares
load-bearing: inscribe/supersede/release/purge mutate a flat store exactly as
the protocol's flat column says (replace in place, delete, delete); links,
endorsements and settlements are no-ops the engine honestly cannot honour.
Each sampled probe is answered at its own position in the stream, against
the store as it then stands.

Items: 120 probes, 20 per family per seed across three families — Retrieval
(expect gold, stratified 5 per phrasing across lexical/paraphrase/oblique/
crossed so no phrasing block dominates), Abstention (the family this row
exists for), Rationale. Judging rules are in the declaration: gold in top-k
hits for Retrieval/Rationale (k=10, the op's own k); a zero-hit decline for
Abstention, which is the only decline a flat lexical store can produce.

## Families not run, and why (in the declaration)

Currency, Contradiction, Drift, Deletion, Temporal and the optional
Authority family each need a capability the declared engine honestly lacks
(history, suspects, release traces, native temporal windows, endorsement
store). Measuring them on this engine would record a capability absence as
if it were a behavior score. The upstream protocol itself marks such
families N/A; we say so per family and claim no number there.

## Prior measurement, per the standing rule

No run of our engines on these worlds exists — none exists. The card
recorded the candidate discovery only, with the caveat that travels:
`The benchmark's author has a system in its own ranking, and it wins.`
It is quoted verbatim in verdict.json and applies to every number here as
much as to the upstream's.

## Pre-registered expectation

Abstention near the floor (the engine has no declined concept: on a
several-hundred-note store some token always matches, so it fires on
questions about nothing) — the central claim this instrument tests.
Rationale middling. Retrieval: expected high; measured middling once
stratified across phrasings, with the lexical block alone near-perfect —
reported as measured, and itself informative: the upstream phrasings are
doing real work, which makes the corpus worth having.
