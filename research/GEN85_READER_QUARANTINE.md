<!-- quarantined: not-evidence -->
# Gen85 reader-layer attempt — QUARANTINED / NOT EVIDENCE

**Nothing in the Gen85 reader-layer work may be used as evidence.** Not as a
result, not as a baseline, not as calibration data, not as hand-tuning examples,
and not to set a threshold or a verdict rule.

## Where it is

**Not on `main`.** The material exists only on the unmerged branch
`reader-layer-gen85`:

- `research/PI_READER_LAYER_GEN85.md`, `research/PI_READER_CLOSURE_GEN87.md`
- `results/reader_layer_gen85/reader.json`, `.../order_ablation.json`
- `results/reader_layer_gen85/superseded_attempt_1/`
- `src/memory_bakeoff/reader_layer.py`, `.../reader_contract_v3.py`

Gen109 audited this and **reconstructed nothing**. The `superseded_attempt_1`
directories that DO appear on `main` belong to Gen58 and Gen61 — different
experiments, unrelated to the reader layer.

## The defect, read from the source and not from the narrative

`src/memory_bakeoff/reader_layer.py` on that branch carries the fix comment
itself: *"v2: match CITE anywhere, not only at line start. Attempt 1 anchored
it to the…"*.

Attempt 1 compiled the citation pattern as `^\s*CITE:` under `re.MULTILINE`. A
reply that placed its citation **inline** rather than at the start of a line did
not match, was classified `UNPARSED`, and was then **scored by the substantive
scorer as a failure**. Three valid replies were charged that way.

Two separate errors, and the second is the one that matters:

1. A presentation choice changed whether a semantically valid reply parsed.
2. **Parse status and semantic grade were entangled**, so a parser failure was
   reported as a reader failure.

## What Gen109 does about it

`reader-interference-v1` keeps parsing and grading in separate functions with
separate vocabularies. A parse failure is `UNPARSED` and can never be graded as
a stale answer, an abstention or a model failure — `assert_parse_and_grade_are_separate`
raises on the attempt. The citation pattern is deliberately unanchored, and a
regression fixture asserts that inline and line-separated citations parse
**byte-identically**.

## Status

`QUARANTINED / NOT EVIDENCE`. Preserved as history, exactly as
`research/PI_SUPERSESSION_ABLATION_GEN102.md` is preserved. Nothing is deleted.
