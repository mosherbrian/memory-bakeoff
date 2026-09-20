# S7-1 design — the bm25 arm re-measured under a declared stopword prefilter

Row S7-1 (sprint 7, BACKLOG-NEXT rank 3). Author: kiln-flash, 2026-09-17.
The binding declaration is `declaration.json` — written before any retrieval
run and sha-bound into every result row. This file is the prose companion.
$0, local, no LLM, no score import.

## Prior measurement, cited per the standing re-measurement rule

- `team/S6-SELECTIVITY/results.jsonl`
  (sha256 `5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab`):
  arm `bm25`, mean set-F1 **0.500** over the 10 frozen cases — 5/5 retrieve
  cases answered top-1 correct, **0/5 abstain cases retrieved anything** (it
  fired on all five: sel-006→r2, sel-007→r3, sel-008→r1, sel-009→r1,
  sel-010→r2).
- `team/S6-SELECTIVITY/review.json`
  (sha256 `7b6f738cfb4b1c99eb4fccfd3b4d0705507913ef320be0f4a008b61293509119`),
  deviation (1): bm25 fired on ALL five abstain cases because the in-tree
  tokenizer keeps function words; "no stopword prefilter was declared or
  applied (S4-12's fire-log bm25 usage did filter; the difference is declared
  here rather than tuned away post-run)".
- What this row expects to DIFFER from, in writing: if the abstention failure
  is a tokenizer artifact, a declared prefilter should move at least the three
  unwritten-subject cases (sel-006, sel-007, sel-010) from fire to abstain
  while leaving the retrieve-case top-1s intact. The two written-subject /
  no-note cases (sel-008, sel-009) are expected to keep firing on the subject
  token — S6-2's design said so before the prior run, and the prefilter is not
  claimed to fix them.

## The declared prefilter (before the re-run; zero post-run choice)

The prefilter is the project's one existing stopword set, reused verbatim:
the `pi-change-trigger` STOPWORDS from
`implementer/repo/extensions/pi-change-trigger/index.ts`
(sha256 `ec6d8794…`, the same pin S4-12 recorded as trigger_pin), 64 words,
loaded the way `team/invocation-corpus-v3-standard/run_standard.py
load_stopwords()` loads it. Chosen for provenance, not fit: it was frozen for
a different instrument before this corpus existed, so it cannot have been
fitted to these cases, and S6-2's review names exactly this usage as the
filtering reference whose absence was the deviation. Any other list — a
generic English list, a list trimmed after seeing these cases — would be a
post-hoc choice. If the trigger-grade set does not move the abstain cases,
that IS the finding; a different list is a new declared configuration for a
future row, not a second try inside this one.

Application (sole delta from the pinned baseline): tokens in the set are
dropped from BOTH the query and the ingested record text before BM25 scoring.
Everything else — tokenizer regex, k1=1.5, b=0.75, per-case ingest, top-1 iff
score > 0 — is the S6-2 bm25 arm unchanged (`BM25Provider` @ repo `be2bfa9`,
`src/memory_bakeoff/providers/bm25.py` sha256 `259b15dc…`).

## Corpus and arms (the prior frozen corpus, controls first)

`corpus.jsonl` here is a byte-identical copy of the prior frozen corpus
(sha256 `5a8668f7…`), and `declaration.json` pins both prior files by sha256
(`manifest.json` = `d2d18912…`). Arms, in run order:

1. `return-nothing` — control, unchanged semantics.
2. `return-everything` — control, all 4 store ids per case.
3. `bm25-nofilter` — paired determinism control: the pinned BM25Provider,
   unfiltered. Must reproduce the prior bm25 retrieval per case, exactly, or
   the gate fails the artifact as harness drift and no conclusion is drawn.
4. `bm25-prefilter` — the measured arm: identical to arm 3 except the declared
   prefilter, with per-row `query_tokens` recording the tokens actually
   scored, so the gate can verify the prefilter ran by its values.
5. `oracle` — exactly the declared helpful set.

The engine arms of S6-2 (pi-lcm, claude-mem) are NOT re-run: no prefilter
applies to them, and this row re-measures exactly the bm25 arm.

## Decision rule (frozen in declaration.json before the run)

`rule: {artifact_if_abstain_at_least: 3}` — `artifact-confirmed` iff the
prefiltered arm abstains on at least 3 of the 5 abstain cases, else
`artifact-refuted`. N=3 because the tokenizer-artifact hypothesis concerns
the three unwritten-subject cases; the two written-subject/no-note cases are
declared by the prior design to possibly keep firing on the subject token.
`retrieve_correct` is recomputed and reported beside the verdict either way;
the staging pre-registration also required it to stay 5/5 for "confirmed",
and that condition travels in the verdict finding. An `artifact-refuted`
verdict is a PASS: an honest negative is a completed result.

Pre-registered expectation, recorded before the run (honest, not convenient):
the set filters what/when/which/does but NOT is/the/for/how/many, and "the"
appears in most store records, so residual query tokens keep every abstain
case above score zero. Expected: abstain_correct 0 of 5, retrieve_correct
5 of 5, verdict `artifact-refuted`; the mean set-F1 will not move from 0.500,
which is why the rule keys on abstentions. A surprise either way is reported
as measured.
