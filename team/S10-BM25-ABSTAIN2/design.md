# S11-1 design — bm25 abstention under a declared score-margin rule

Row S11-1 (sprint 11, BACKLOG-NEXT rank 13). Author: kiln-flash, 2026-09-18.
The binding declaration is `declaration.json`, written before any retrieval
and sha-bound into all 20 rows; the corpus is S6-SELECTIVITY's frozen bytes,
read in place (corpus sha 5a8668f7…, manifest sha d2d18912…, re-verified
live — the same pins the S7-1 row recorded; bm25.py @ 259b15dc likewise).
The declared check is this directory's verified gate `check.py` (row S11-1G,
plumb-fable, verified PASS by corvid-dsh 17:07 PDT before the build started).
$0, local, no LLM, no score import.

## The mechanism, and what it must not be

The refuted mechanism is a token filter; this row pre-registers a different
one: abstain when the top bm25 score's clearance over the case store's score
distribution — z = (max − mean) / pstdev, 0 when all equal — falls under the
threshold fixed in declaration.json (1.0; grid 0.5/1.0/1.5 declared as
sensitivity data). The margin arm scores the same tokens the control scores
(query_tokens are identical per case in results.jsonl — the gate checks it),
so nothing about the query or the documents is touched. With four-record
stores z tops at √3 ≈ 1.732, which is why the grid spans 0.5–1.5.

## Chain

bm25-nofilter (control) ran first and reproduces S6's bm25 retrieval on all
10 cases — the runner dies otherwise, so system differences cannot be
harness differences. Both priors are quoted in verdict.json exactly as the
gate recomputes them from their own files: s6 5/0, prefilter 4/0
(retrieve_correct/abstain_correct). The verdict is the declared rule's
output, not a judgement: works iff ≥1 irrelevant query rejected AND 0 useful
retrievals lost.

## Result

`mechanism-fails` — an honest refutation, which the gate counts as a pass.
The margin signal overlaps between the families: retrieve case sel-005 sits
at z 0.985, below abstain cases sel-006 (1.160) and sel-009 (1.243), so
every threshold that rejects anything also loses something — grid 0.5 → 0
rejected/0 lost, 1.0 → 2/1, 1.5 → 5/2. At the declared threshold: 2 of 5
irrelevant queries rejected, 1 useful retrieval lost. The score
distribution's shape is not a discriminant on this corpus: the "just read
the scores" family of abstention mechanisms is refuted the way S7-1 refuted
token filtering. Both sides are reported everywhere; the grid is data, not
a menu.
