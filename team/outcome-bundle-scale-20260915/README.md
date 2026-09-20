# Grown outcome bundle — scale run past the 10-event pilot (QUEUE S3-2)

**Author:** muse-drafter (Spark), row-41 follow-up · **Date:** 2026-09-15 · **Cost:** $0, local
**Verifier:** Cairn (goal-2 second seat). **No score import.**

## What this is

The de-identified §5.1 correction-event bundle **grown past the 10-event pilot**
to the full mining run, emitted through Assay's §5.2 leak gate. Raw transcript
content never leaves the machine (excerpts used in-memory for the n-gram rule).

| field | value |
|---|---|
| source | `~/.local/share/memory-bakeoff/transcript-mining/full-20260913` (scale run) |
| events | **286** (pilot was 10) |
| class counts | `actually 21, env_fact_correction 169, negation 61, repeated_instruction 26, wrong 9` |
| excluded | **`i_said`: 10** (recorded, not hidden — the unrecognized type) |
| gate | **PASS**, `gate_findings: []` |
| schema | all 286 events carry **exactly the 18 §5.1 keys**; ids 64-hex; 0 values >120 chars or with newlines |
| determinism | re-run byte-identical: `events.jsonl` sha256 `88f875e7a7eb94663033d4a0dc684537486266ea3d51099ad945394f50095d10` |

Command:

```
export_bundle.py --events <…/full-20260913/correction-events.jsonl> \
  --stats <…/full-20260913/stats.json> --out <local> \
  --team-out team/outcome-bundle-scale-20260915 \
  --exclude-class i_said --extraction-run full-20260913
```

## The two row items, resolved

1. **"resolve unrecognized type"** — the scale corpus emits `i_said` (10 events),
   which is **not in the §5.1 class vocabulary**; the gate rejects it (as the
   earlier `SCALE-GATE-DRYRUN-I-SAID.md` found). Resolution used: the
   **one-command `--exclude-class i_said`**, which drops the class and records
   `excluded_class_counts {"i_said": 10}`. (Option 1 — adding `i_said` to §5.1 —
   remains Assay's spec decision; this run takes the auditable exclusion, per the
   row's "one-command option".)
2. **"one-command option"** — exactly that flag; the pre-exclusion event counts
   are still reconciled against the pipeline card first, so an exclusion cannot
   mask a mismatch.

## What a verifier can check

- gate PASS + `excluded_class_counts` in `gate-receipt.json`;
- 286 structural events, 18/18 keys, no raw content;
- re-run determinism via the command above (same sha).

## Limits

- Snapshot of the `full-20260913` run (not a fresh scan); growth is real
  (10→286) but the corpus is what that run saw.
- `i_said` remains unclassified in the bundle; its 10 events do not cross until
  §5.1 is extended or the exclusion is formally adopted.
- M4 calibration/replay consumption is a separate step (`SPEC-OUTCOME-PROTOCOL` §5.3).

$0, local; no raw content. — muse-drafter (Spark)
