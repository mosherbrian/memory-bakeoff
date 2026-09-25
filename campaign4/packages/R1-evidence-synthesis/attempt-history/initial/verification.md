# R1-synthesis-1 — independent verification

- **Verifier:** corvid-dsh (author kiln; I did not author the worker artifacts).
- **Worker claim:** `ex-R1-synthesis-1-w1.json`, outcome `completed`; artifact
  hashes **verified equal**: `synthesis.md` `2cb16350…`,
  `evidence-table.tsv` `eeecd5de…`, `limitations.md` `f040b2b7…`.
- **Sources:** corrected commit `485d783d…`, **124/124 hash-match via `git show`**;
  original 122 unchanged. My sealed `blind-baseline.md` (`53a5237c…`) with the
  2026-09-25 source-coverage addendum was read before the worker synthesis.
- **Verdict: PASS** — a justified synthesis under the five criteria. This is **not**
  proof that memory helps; no task-outcome evidence exists.

## Criterion 1 — traceable coverage

- **All six answer-page questions** (`ANSWER.20260920-133909.md`) are present:
  real-work benefit (not established), relevance rejection, BM25+pi-lcm compose,
  protection-layer false replacement, external abstention across five
  implementations, competing-text delivery loss.
- **S13 transfer** traced with its grid and the 0.5 headline; the byte-identical
  `results.json`/`results-attempt1-*` (both `59b0a3b2…`) are explicitly not
  double-counted.
- **Gate/measurement episodes** traced as process, not efficacy: S12-1G
  `VERIFIED FAIL` (unsatisfiable shape, rounds 1–3) then PASS round 4; S13 attempt-2
  mismatch caught by Tern, pinned runner byte-identical.
- **Explicit unknowns** in `limitations.md`: S6-SELECTIVITY via sha-pinned priors
  (not re-inspected), S9 instrument rows read for character only, S11 design bar via
  verdict+recomputation. Honest.

## Criterion 2 — no overgeneralization

Proxy (`retrieval`/`abstention`/delivery presence) is consistently separated from
task improvement, and replacement (top-result contest) from deletion
(`compaction_measured: false`). Operational gate/runner defects are counted as
process, never as memory-efficacy evidence. The "nothing supports / nothing refutes"
phrasing is properly bounded.

## Criterion 3 — counterevidence and arithmetic

Previous failed constructions are retained with denominators (S7 prefilter
`artifact-refuted` 0/5+1; S10 margin `mechanism-fails` grid 0.5→0/0,1.0→2/1,1.5→5/2;
S7-COMPOSE `not-complementary`; S10-PI-LCM-HIST `native-failure`; S11-LAYER-HIST
`close_trivial_layer_class`). I independently spot-checked the worker's numbers
against `git show 485d783d:` primary bytes: S13 grid (0/40 & 10/80 at 0.5; 6/40 &
20/80 at 0.75; 24/40 & 51/80 at 1.0), S11 grid (5/5 decl, 3/5 holdout, 0/5 lost;
bar {0.25,0.5}), S7-COMPOSE arms (bm25 0.5/5/0, pi-lcm 0.6/1/5, compose 0.6/1/5),
S10-KD-CROSS/S7-KD-WORLDS (0/40 abstentions; retrieval 11/40–21/40, rationale
3/40–5/40), S9-DOOR-RUNG2 presence (100→20 / 20→0 / 100→60). **All match.**

## Criterion 4 — one next step

Exactly one: a **preregistered memory-on/off matched-task comparison** measuring
task outcomes and delivered evidence, with a falsification/stop condition and an
explicit feasibility limit (agenda audit first; compaction enters only if a real
boundary is instrumented). Alternatives are ranked lower with reasons (external
transfer already failed; positional rerun changes no outcome; new protection needs a
mechanism audit; more local tuning selects after outcomes). A no-experiment option is
acknowledged as valid. Proposal only, not authority to run.

## Criterion 5 — sealed-baseline comparison

My sealed baseline's conclusions agree with the synthesis on every consequential
claim: real-work benefit unestablished; one internal relevance rule that fails
external transfer for a vocabulary-coverage reason; the tested protection class
closed on one shape; delivery fragility unlinked to task harm; a flat-retrieval
abstention gap. The synthesis adds mechanism detail (S13 per-term coverage;
gate-episode tracing) but I found **no disagreement**.

## Non-blocking observations

1. The S9-DOOR-RUNG2 summary in `synthesis.md` compresses the three-cell
   (normal→unloaded→loaded) series to normal→loaded ("100→20" etc.); the
   `evidence-table.tsv` row and the verdict retain the intermediate cell.
2. The contract's "both rejected/unsatisfiable gate episodes" is satisfied as the
   S12-1G unsatisfiable gate plus the S13 attempt-2 measurement-process defect; if a
   second distinct *gate rejection* was intended, it is not separately enumerated.
3. S6-SELECTIVITY cells are verdict-reported via pinned priors (disclosed; not a
   defect).

**PASS** — justified under the five criteria; not proof memory helps. No worker
artifacts edited; no git edits, no new experiment, no source/runtime changes.
