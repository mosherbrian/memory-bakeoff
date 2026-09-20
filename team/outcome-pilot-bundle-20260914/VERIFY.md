# Verification receipt — row-41 outcome pilot bundle

For the assigned verifier (Cairn, goal-2 second seat). Local, $0.

## Artifacts and hashes

| artifact | sha256 |
|---|---|
| `team/outcome-pilot-bundle-20260914/events.jsonl` | `7cd03aa575261f9a3a6d2abe177490616810b7c46fb48122778bc0c426ba4d14` |
| `team/outcome-pilot-bundle-20260914/gate-receipt.json` | `14fc744640a746a7a6a6c5e101cdb51fac93b6f04e4b68aeed39f7ce6254fb9c` |
| `scripts/.../export_bundle.py` | `ed0e2f5686f5cf971f296067e0f72a58e77af8b4eac2a810666cabcb3b4317b7` |
| `scripts/.../outcome_leak_gate.py` | `b3f60ed7152b4a66bba541c9f3b228a48b93be37cdc9f2a32bf33c2a1a15ba75` |

## Determinism check (second driver)

Ran the export step twice, independently, into throwaway dirs, then compared to
the shipped bundle. **All three byte-identical** (`7cd03aa5…`). The event stream
is reproducible at the current commit with the fixed pilot salt
(`--salt pilot-20260913`), which is what M4 replay/calibration needs.

```
python3 scripts/experiment_20260912_transcript_mining/export_bundle.py \
  --events ~/.local/share/memory-bakeoff/transcript-mining/pilot-20260913/correction-events.jsonl \
  --stats  ~/.local/share/memory-bakeoff/transcript-mining/pilot-20260913/stats.json \
  --out    <tmp> --extraction-run pilot-20260913
sha256sum <tmp>/events.jsonl   # == 7cd03aa5…
```

## What the verifier can check

1. **Gate PASS**: `gate-receipt.json` → `gate_pass: true`, `gate_findings: []`.
2. **No raw content / full schema**: every `events.jsonl` value is structural
   (hashes, enums, buckets). The exported events carry **all 18 §5.1 keys**
   (verified: 10/10 shipped events; guarded by the focused test, since the gate
   itself only rejects extra keys — `team/PROPOSAL-LEAKGATE-MISSING-KEYS.md`),
   no excerpt string, no >120-char value.
3. **Fail-closed**: the same test's CLI case tampers the aggregate card and
   asserts exit code 1.
4. **Reconciliation basis**: the gate reconciles against the pipeline's own
   `stats.json` (10 events), **not** the pilot card's 15 — see
   `team/ROW41-PILOT-CARD-DELTA.md` (15 = pre-`mask_quotes` snapshot).
5. **Gate vendoring**: `outcome_leak_gate.py` is Assay's validated prototype
   (sha `202479298f83…`) with sentinels pinned from the corpus JSONL key census;
   the focused test re-runs the prototype's control set against the vendored copy.
6. **Scale path** (`team/SCALE-GATE-DRYRUN-I-SAID.md`): the full run fails the
   gate on `i_said` (not in the §5.1 vocabulary). The exporter now supports an
   auditable `--exclude-class i_said`, which drops the class and records
   `excluded_class_counts`/`excluded_total` in the receipt; with it the 286-event
   scale bundle passes and the pre-exclusion counts are still reconciled against
   the card first (an exclusion cannot mask a mismatch).
7. **Own fail-closed schema guard**: because the gate accepts missing keys, the
   exporter asserts each built event carries exactly the §5.1 key set and fails
   closed if not (`test_export_schema_guard_fails_closed`); the pilot output is
   byte-identical after this addition.
8. **Team crossing only when clean** (Cairn row-41 advisory A1): with `--team-out`
   and any finding, the local `--out` still gets the bundle/receipt for debugging
   but the **team crossing is not written** (`test_export_cli_pass_and_failclosed`
   asserts `team2/events.jsonl` absent on rc 1). Fixed 2026-09-14; pilot output
   byte-identical.

Local only; no raw transcript content in any artifact above. — muse-drafter (Spark)
