# pi-observational-memory Gen27 — context production and reader scoring

## Status

`complete_context_production_v1_scored_citation_contract_open`.

Three completed repetitions of the frozen `om-context-production-v1` profile.
This is the first published agent-visible context result for OM: it scores what
the product's own compaction puts in front of the agent, and whether an offline
reader can answer from that projection with valid native provenance. It is not
a semantic retrieval score.

## Identity

The evaluated system was pi-observational-memory 3.0.4 at
`ce9fc982b3a219a7839f07c9f4a3e054e81a2b21`, Pi 0.81.0, Node v26.8.1, and
`qwen3.6-35b-vulkan-nothink` with thinking off at `http://strix-halo.local:8080/v1`.
The same frozen model served the foreground session and the offline reader.

Fixture `om-context-production-v1`, SHA-256
`cce9fdf494ad6965897646beff1ef535d4aeb73ba81f3ea83e6fe68e1218acdc`.
Scorer `om-context-production-scorer-v1`, contract SHA-256
`f69068bbb3a76bf9ca64edeb3a5b14411538d6e4494211d765efa82e50e702bd`.
Both were reverified against the live module after execution.

The harness lane was frozen at `2e9d1bd3e3049ee0d9889f62dfbb4c173ad0b791`.
All three published repetitions ran under that commit unchanged, with a clean
working tree.

## What Gen27 changes about the Gen26 boundary

Gen26 could not produce a rendered agent-visible context: Pi's native RPC
compaction declined at every checkpoint with `Nothing to compact (session too
small)`. Gen27 evaluates the product's own compaction event, `om.folded`,
rather than Pi auto-compaction.

The Gen26 decline is now explained rather than worked around. OM folds the
session continuously, so Pi's own auto-compaction threshold is never reached.
Measured session size immediately before each fold stayed between 20,729 and
27,282 tokens across all three repetitions, while the source backlog kept
growing. `operator_compaction` is false in every repetition and all 67 folds
carry `fromHook: true`, so the product triggered every one of them.

## Completed repetitions

Each repetition drove 40 deterministic public turns. The live process saw only
`public_turns`; the 12 reader questions were withheld until after capture.

| rep | run | barriers | folds | full folds | rendered context | projection entries | anchors mapped | reader |
|-----|-----|----------|-------|------------|------------------|--------------------|----------------|--------|
| 1 | `gen27-context-valid-r1c` | 40/40 | 23 | 2 | 9,670 chars | 43 | 16/16 | 9/12 = 0.750 |
| 2 | `gen27-context-valid-r23` rep1 | 40/40 | 23 | 3 | 9,894 chars | 45 | 16/16 | 10/12 = 0.833 |
| 3 | `gen27-context-valid-r23` rep2 | 40/40 | 21 | 3 | 7,391 chars | 34 | 16/16 | 9/12 = 0.750 |

All 16 fixture anchors mapped to native entry IDs in every repetition. Mean
reader pass rate is 0.778 over 28 of 36 graded cases.

## Failure structure

Across all 36 graded cases the frozen scorer recorded **zero**
`missing_required` and **zero** `prohibited_hits`. Every answer was factually
correct against the fixture, including both held-out UNKNOWN cases, and no
prohibited or stale term was propagated from the projection.

All 8 failures are citation-provenance failures: 8 `unsupported_citation`, of
which 5 also carried `invalid_citations`. Answer quality and provenance quality
diverge sharply in this profile and must be reported separately.

## Citation contract defect — diagnostic only, not a published score

`reader_prompt` instructs the reader to return `citations` as "OM IDs such as
`obs-...` or `ref-...`". `grade_reader` looks each citation up directly in the
projection support map, which is keyed by the bare native entry ID. A reader
that follows the prompt literally therefore lands in `invalid_citations` and
fails the case even when the bare ID maps to the case's required anchor.

Q10 failed in all three repetitions for exactly this reason: it cited
`obs-82e397393ad2`, and `82e397393ad2` maps to its required anchor A04 in every
repetition.

Re-grading the stored responses through the unchanged `grade_reader`, with the
`obs-`/`ref-` prefix stripped and nothing else altered, gives 11/12 in all three
repetitions. The single remaining failure per repetition is a genuine
`unsupported_citation` with a different case each time: Q05 in rep 1, Q03 in
rep 2, Q07 in rep 3.

This diagnostic is recorded, not published. The lane is frozen and a grader
change invalidates comparability, so the published Gen27 numbers remain 0.750 /
0.833 / 0.750. Whether v1 is corrected, or a v2 fixture carries a normalized
citation contract, is a control-plane decision.

## Excluded attempts

Four earlier launches produced no score and are published as none:

- `gen27-context-r1` — exited before creating a run directory. No exposure.
- `gen27-context-r1-fresh` — the turn-1 barrier correctly rejected an observer
  launch detected two seconds after start. The harness launch-detection guard
  was widened from 2 s to 15 s in `2e9d1bd`; the run was discarded, not rescored.
- `gen27-context-valid-r1` — the runner refused a pre-created output directory.
- `gen27-context-valid-r1b` — launched with `&`; the shell reaped the child and
  no session was ever created.

## Boundary

OM still exposes no natural-language query surface. Exact-ID `recall` remains
provenance recovery, not semantic retrieval. No Hit@k, no ranking metric and no
generic scalar score is published from this generation, and lifecycle behavior
is not scored here.

The `om-context-production-v1` fixture is now exposed: it drove three live
product sessions and cannot be reused as an unexposed workload.

Raw traces — command and event order, PID and session identity, ledger leaves,
debug run IDs, terminal events, native fold records — remain under
`.control-plane/` and are untracked. The checked-in summary is sanitized.

## Verification

Full suite: 85 passed, one pre-existing metadata deprecation warning. The suite
requires `node` on `PATH`; without it two agentmemory core tests fail on
`FileNotFoundError: 'node'`, which is an environment fault and not a regression.
