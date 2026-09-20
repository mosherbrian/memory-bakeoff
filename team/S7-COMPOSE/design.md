# S7-2 design — compose attempt: bm25 retrieval behind pi-lcm's abstention gate

Row S7-2 (sprint 7, BACKLOG-NEXT rank 2). Author: kiln-flash, 2026-09-17.
The binding declaration is `declaration.json` — written before any retrieval
run and sha-bound into every result row. This file is the prose companion.
$0, local, no LLM, no score import.

## Prior measurements, cited per the standing re-measurement rule

`team/S6-SELECTIVITY/results.jsonl`
(sha256 `5f3f14fc…`), both arms on the same frozen corpus
(`corpus.jsonl` `5a8668f7…`, `manifest.json` `d2d18912…`):

- **bm25** — mean set-F1 0.500: 5/5 retrieve cases answered top-1 correct,
  0/5 abstain cases retrieved nothing (fired on every abstain case).
- **pi_lcm_toollevel_sel** — mean set-F1 0.600: abstains perfectly 5/5 (the
  exact-then-relaxed gate never matches an abstain store) but rescues only
  1/5 retrieve cases.

The compose hypothesis this row tests: the arms are complementary rather than
ranked — pi-lcm's gate decides WHETHER to retrieve (owning abstention), bm25
decides WHAT to retrieve when the gate opens.

## The S7-1 dependency, and what it does to the design

S7-1's verdict landed before this run: **artifact-refuted** — its declared
stopword prefilter fixed no abstention (0 of 5) and regressed sel-003's
top-1. Two consequences, both recorded in the declaration:

1. `bm25_variant` is "prior": composing on the prefilter would compose on a
   refuted configuration (the gate itself rejects that combination).
2. The division of labour sharpens: bm25 cannot abstain, so the gate must own
   abstention entirely, and bm25 only ranks when the gate is open.

## The composition (exactly this, nothing more)

Per case: retrieve **nothing** where `pi_lcm_toollevel_sel` retrieved nothing,
else **exactly** the ids the re-measured `bm25` arm retrieved. A hand-improved
compose arm is not evidence, so the runner computes it mechanically from the
two component arms' outputs in the same run.

## Decision rule (frozen in declaration.json before the run)

`rule: {complementary_if_gain_at_least: 0.10}` — "complementary" iff the
compose arm's mean set-F1 exceeds the better single arm's by at least 0.10,
one case's worth of mean movement on this 10-case corpus; less is noise, not
complementarity. `not-complementary` is a PASS: an honest negative is the
evidence Decision Gate F asked for.

Pre-registered expectation, recorded before the run: the gate opens on 1 of 5
retrieve cases (sel-004) and on no abstain case, so the compose inherits
pi-lcm's correctness profile exactly (mean 0.600, retrieve_correct 1,
abstain_correct 5), gain +0.000, verdict `not-complementary`. The
construction discards bm25's coverage on the 4 retrieve cases the gate never
opens for — a union-style composition (gate opens OR bm25 confident) is a
different, separately-declared configuration, not a second try inside this
row.
