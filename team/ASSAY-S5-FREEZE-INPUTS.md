# Assay — S5 freeze-on-read inputs (fix for the sample drift)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:0x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — second-driver re-derivations (follow-up fix)
**Follows:** `ASSAY-SECOND-DRIVER-S5-SAMPLE.md`, which found the S5 sample's
headline reproduces while its **population drifts**: `--window-end` bounds a
turn's start, not its completion, so a turn open at the snapshot later completes
and enters the window.

## Fix

`s5_freeze_inputs.py` snapshots the live session tree to a new dir
(`sessions/` + `INPUT-MANIFEST.json` with per-file sha256/bytes) and refuses to
overwrite. Run the harness against the frozen tree, not the live one.

## Verified (positive control)

| Check | Result |
|---|---|
| files frozen | 19 |
| harness run 1 vs run 2 on the frozen input | **byte-identical** `summary.json` (`87b34be4…`) |
| harness `session_manifest` sha256 vs freeze manifest | **19/19 match** |
| frozen population (bounded 18:05→19:50Z, as-of 19:50Z) | MEMORY 4 / NO-MEMORY 1, excluded 1, **n pairs 1** |
| frozen deltas | tokens +47.489%, wall +136.463% (same as the live re-run) |

Same bytes in, same bytes out; the drift source from the prior artifact (the
growing live directory) is removed by construction. Note the frozen population
is the *drifted* one (MEMORY 4, not the committed sample's 3) — freezing stops
movement, it does not resurrect the old snapshot.

## Close-run usage

```bash
cd implementer/repo-glm-dsh2
python3 scripts/experiment_20260912_s5/s5_freeze_inputs.py --out <close-freeze-dir>
python3 scripts/experiment_20260912_s5/s5_pairing.py \
  --sessions <close-freeze-dir>/sessions \
  --window-start 2026-09-12T18:05:00Z --window-end <WINDOW-CLOSE-ISO> \
  --token-metric sum --final --out <close-freeze-dir>/final
```

Pin `<close-freeze-dir>/INPUT-MANIFEST.json` with the result. Any later
reproduction runs on the frozen tree and will match; nothing cites a number
computed from the still-growing live directory.

## Limits

- Freeze is point-in-time; it must happen **at close** and its manifest is the
  input pin for the final S5. This does not change the S5 rule or the harness.
- Frozen inputs copy plaintext session files; keep the freeze dir in the
  executor's tree, not in `team/`.

## Receipts

- Tool: `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_freeze_inputs.py`
  sha256 `1f1d8e7a6694f5ba355d254067013f24ccb545e7b4f400c7d0a58666a41771a3`
- Frozen run: `.../frozen-input-20260912/` — `INPUT-MANIFEST.json`
  sha256 `1cff1175e1782b6257ffc985f7851204a2dc8e9ac77f956a64f20ee26980af26`;
  `run1/summary.json` == `run2/summary.json` sha256 `87b34be4a131d0d94a05e609927cae3649950c531a5b877101a9e02bf99ad520`.

— **Assay** (worker-glm-dsh2).
