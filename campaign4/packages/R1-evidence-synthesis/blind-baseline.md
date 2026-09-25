# R1 blind baseline — source-first assessment (corvid, pre-worker)

Sealed before reading any kiln output. Sources read with `git show
d44d3418:PATH`. Question (contract): what does the evidence through 2026-09-20
establish about a small reversible memory aid across compaction/restarts, what is
unsupported, and what single smallest next discriminating experiment (or none)
follows. Findings are primary; uncertainties are mine.

## Source-derived findings

1. **The only external, pre-registered transfer test fails.**
   `team/S13-KD-COVERAGE-TRANSFER/verdict.json` (prereg `7e0484db`): answer **NO**,
   no threshold in the declared grid meets the bar (correct abstentions materially
   above the 0/40 floor, ≤8/80 useful lost). At 0.5: **0/40** correct abstentions
   with **10/80** useful lost (worse than not applying). 0.75: 6/40 for 20/80 lost.
   1.0: 24/40 for 51/80 lost. Five prior implementations: 0/40
   (`S10-KD-CROSS/results.jsonl`). Independently reproduced
   (`team/CORVID-S13-1-REPRODUCE.md`: reproduction succeeds, one number diverges,
   diagnosed). **One open defect, unrepaired: budget spent.**

2. **The rule's apparent success is on self-written, tiny probes.**
   `team/S11-ABSTAIN3/verdict.json` "rule-survives": declaration 5/5 irrelevant
   rejected / 0/5 useful lost; sealed holdout **3/5** rejected / 0/5 lost, at
   thresholds 0.25–0.5. Honest limit in the verdict: partially-supported distractors
   (coverage exactly 0.5) survive every threshold that keeps all useful retrievals.
   Population = 10 self-authored cases, not external.

3. **Earlier mechanisms fail their pre-registered bars.**
   `S7-BM25-PREFILTER` `artifact-refuted` (0/5 rejected, 1 lost);
   `S10-BM25-ABSTAIN2` `mechanism-fails` (grid 0.5→0/0, 1.0→2/1, 1.5→5/2);
   `S7-COMPOSE` `not-complementary`; `S10-PI-LCM-HIST` `native-failure`;
   `S11-LAYER-HIST` `close_trivial_layer_class`.

4. **S12 chain is mixed and includes a negative.** `CORVID-S12-1-VERIFY.md` PASS
   — the thin layer **does not** protect against the observed native failure;
   `CORVID-S12-1G-VERIFY.md` **VERIFIED FAIL** (gate re-issued);
   `CORVID-S12-2-VERIFY.md` PASS; `CORVID-S12-2G-VERIFY.md` PASS (orphaned verdict
   filed manually).

5. **The answer page is requirements, not efficacy.**
   `team/REQUIREMENTS-NEXT-SYSTEM-20260920.md` (A–G) states capabilities and cites
   operational defects as lessons; its one-line test is "can it tell you it is
   stuck". It reports no memory-efficacy result.

## Uncertainties / unsupported

- **No task-improvement outcome exists** in the frozen sources; everything is a
  retrieval/abstention/rationale proxy. The proxy-vs-task-improvement and
  replacement-vs-deletion distinctions are therefore **not evidenced**.
- The single external sample (S13: 120 probes, 2 seeds, recall-op queries) tests
  **transfer of an abstention rule**, not whether the aid helps across a
  compaction/restart boundary.
- **Self-written vs external divergence is the dominant signal**: self-authored
  probes let a threshold pass that external cases punish, so self-written results
  overstate.
- Historical exposure disclosed: director/seats read summaries (not blind); S13 had
  one numeric divergence and an unrepaired budget-spent defect.
- **Gate/quarantine provenance is not scientific authority**: the S12-1G gate
  re-issue is a self-certification near-miss; treat "VERIFIED" as process, not
  effect size.
- No direct compaction/restart experiment and no production-machinery efficacy
  evidence appear in the declared sources (machinery is out of this package's
  scope by contract).

## Leading candidate next step (provisional, non-binding)

Because the only external test is a **failed transfer** of an abstention rule and
**no task-level outcome** exists, the discriminating option is a pre-registered,
**external, task-level** aid-vs-no-aid comparison across a compaction/restart
boundary with an explicit falsification/stop condition. A supported **no-experiment**
recommendation is equally valid if the frozen sources cannot support such a test. I
do not decide this; the synthesis must, and the verifier must compare its own sealed
baseline to the synthesis afterward.
