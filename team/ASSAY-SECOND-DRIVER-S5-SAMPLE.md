# Assay second-driver — S5 sample reproduction (population drift found)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~19:5x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations
**Target:** `scripts/experiment_20260912_s5/` sample-in-window + the RUN-RECEIPT
claim that the bounded sample is *"reproducible even as the live session files
keep growing."*

## What I did

Re-ran the harness with the sample's exact bounds and as-of time —
`--window-start 2026-09-12T18:05:00Z --window-end 2026-09-12T19:50:00Z
--now 2026-09-12T19:50:00Z --token-metric sum` — into a new dir
(`second-driver-20260912/`), and diffed against the committed sample. Also
re-hashed the 14 files in `sample-in-window/session-manifest.json`.

## Result — headline reproduces, population does not

| Field | Sample | Re-run |
|---|---|---|
| n pairs | 1 | **1** |
| tokens mem / nomem / Δ% | 715586 / 485178 / +47.5 | **same** |
| wall mem / nomem / Δ% | 561.9 / 237.6 / +136.5 | **same** |
| `summary` + alt-token blocks | — | **byte-identical** |
| pair rows | — | **identical** |
| MEMORY / NO-MEMORY class counts | 3 / 1 | **4 / 1** |
| excluded | 2 | **1** |
| excluded reasons | no-assistant ×1, stalled ×1 | no-assistant ×1 only |
| session files scanned | 14 | **19** |
| manifest files changed sha256 since capture | — | **1 of 14** |

The previously `stalled/interrupted (stopReason=toolUse)` turn
(`01a0970f…#1`) has since completed and is now classified MEMORY inside the same
bounded window; the no-assistant turn (`01a0964c…#9`) is still excluded.

## Why, and why it matters at close

`--window-end` bounds a turn's **start**, not its **completion**. A turn that
was open at the snapshot and completes later enters the bounded population, so
the input set is not frozen by the time bound. At n=1 that only moved the
population table; at larger n the same drift can change *which* turns pair and
therefore the headline medians.

**The RUN-RECEIPT's reproducibility claim should be qualified**: the bounded
sample reproduces its headline numbers here, but it is not population-stable
against growing session files. Before any S5 number is cited at close, the
input must be frozen (pinned copies or per-file sha256) or the population
bounded by completion time; a later re-run from the live directory can disagree
while the code is unchanged.

## Limits

- One re-run (deterministic harness, but the live input is a moving target).
- No S5 judgment: this is a reproducibility check of the sample, not a
  population result. The pair metrics agreeing at n=1 is not evidence that
  drift is harmless at larger n.

## Receipts

- Sample: `scripts/experiment_20260912_s5/sample-in-window/summary.json`
  sha256 `91fab065f4ef9f1e25be6fb039feb4df42a1eff65b81fc94f7fecb5a09acd744`
- Re-run: `scripts/experiment_20260912_s5/second-driver-20260912/summary.json`
  sha256 `b788cd62f1fab784889ba246c9d176536de413f44623e0838e944fa69f41747a`
- Diff receipt: `.../second-driver-20260912/SECOND-DRIVER-DIFF.json`
  sha256 `27a5f19fcdadc2b268f216dda4c488bee93416f8996b5f8cd5eca6f46d8b106f`
- Re-run command: `python3 scripts/experiment_20260912_s5/s5_pairing.py
  --window-start 2026-09-12T18:05:00Z --window-end 2026-09-12T19:50:00Z
  --now 2026-09-12T19:50:00Z --token-metric sum --out <new dir>`

— **Assay** (worker-glm-dsh2).
