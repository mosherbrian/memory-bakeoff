# S11-2 design — KnowledgeDrift cross-system replay on the same frozen sample

Row S11-2 (sprint 11, BACKLOG-NEXT rank 14). Author: kiln-flash, 2026-09-18.
The binding declaration is `declaration.json`, written before any receipt and
sha-bound into all of them; the item list is the prior's, byte for byte. The
declared check is this directory's verified gate `check.py` (row S11-2G,
plumb-fable, verified PASS by corvid-dsh 17:03 PDT before the build started).
$0, local, no LLM, no score import.

## What was run, and on whose corpus

The prior instrument's replay protocol (team/S7-KD-WORLDS, row S7-4) is
reused unchanged: the upstream frozen worlds/v2 500-fact files at seeds 1
and 2 (the `upstream` symlink here resolves into the prior's clone; both
files re-hashed against the prior's sha256 pins before anything ran), ops
replayed in stream order, each sampled recall answered at its own position
against the store as it then stands. The 120-probe item list is the prior's
`items.jsonl` byte for byte, and the runner re-derives the prior's
deterministic sample and dies if it disagrees — the sampler is checked, not
trusted.

What is new: at every sampled recall the query is put to the other pinned
in-repo providers — dense_lsa, tfidf_cosine, hybrid_rrf — alongside a fresh
bm25 control; the declared stretch arm claude_mem_chroma_lsa runs under the
same protocol. One replay per world serves all five engines (the flat store
is engine-independent), so no arm can see a different stream.

## The stop rule (declared before the run)

bm25 must pass and fail exactly the prior's items; otherwise the harness has
moved and the run dies before any receipt is written, because a difference
between systems must not be confoundable with a difference between runs.
It held: item for item, 120/120 (Retrieval 21/40, Rationale 5/40,
Abstention 0/40 — the prior's cells).

## The stretch arm decision

The row declares one claude_mem stretch arm, run if its store can ingest the
op stream honestly. It ran: `claude_mem_chroma_lsa`, the controlled core
with the S6-2 precedent. Raw ingest is honest by the arm's design (raw
records enter the observation text as-is; the product compression pipeline
is deliberately not run), and its default 90-day recency window is pinned —
CLAUDE_MEM_EVAL_NOW=2026-08-30T12:00Z, replay record timestamp 2026-09-01 —
so the window keeps every record and the policy is reproducible rather than
ambient. Its ranking is the shared LSA representation, so it is expected to
track dense_lsa; the claude-mem-specific policy (top-100 batch, recency
filter) is pass-through on this corpus, which is itself worth knowing.

Environment, recorded because it is part of reproducibility: numpy 2.4.4 /
scikit-learn 1.9.0 from the user site-packages
(/var/home/bmosher/.local/lib/python3.14/site-packages), added explicitly by
the runner — this seat's HOME-isolated shell does not see the user site.

## Prior measurement, per the standing rule

`team/S7-KD-WORLDS/verdict.json` — bm25 only: Retrieval 21/40, Abstention
0/40, Rationale 5/40 (oblique 1/10, crossed 0/10). This row re-measures the
same frozen sample on additional systems; expected to differ: which engine
sits where on Retrieval/Rationale, and nothing on Abstention. Quoted cells
travel in verdict.json `prior`; family scores stay separate.

## Result (family-separate; the gate recounts every cell)

No system declines anything: Abstention 0/40 on all five engines, as
pre-registered — the externally-authored weakness is now five systems deep,
the flat ranked-retrieval shape itself. Retrieval/Rationale move by system:
tfidf_cosine 0.500/0.100 and hybrid_rrf 0.500/0.075 sit close to the bm25
control's 0.525/0.125; dense_lsa 0.275/0.075 and the claude-mem controlled
core 0.275/0.075 fall well below — the low-rank projection gives up exact
identifiers (lexical phrasing 4/10 against the control's 10/10) yet is the
only family of arms that gains on oblique phrasing (3/10 vs 1/10). Crossed
stays 0/10 everywhere. By-phrasing cells are in verdict.json
`retrieval_by_phrasing`; they are data, not verdicts.

Families not run: the six capability-absent families, with the prior's
reasons carried over and extended — every arm in this run is the same flat
ranked-retrieval shape, so a capability absence would be measured five times
over, not once. The card's caveat travels in verdict.json beside every
number.
