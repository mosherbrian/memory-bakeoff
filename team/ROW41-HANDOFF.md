# ROW 41 HANDOFF — outcome leak gate wired + first de-identified pilot bundle

**Owner who did it:** muse-drafter (Spark), GiLMore assignment 2026-09-14 · **Verifier:** Cairn (goal-2 second seat)
**Cost:** $0, local only. **HARD RULE honored:** no raw transcript content left the machine.

## Deliverable (done)

- `implementer/repo/scripts/experiment_20260912_transcript_mining/outcome_leak_gate.py`
  — Assay's validated §5.2 gate, vendored with the sentinel list **pinned from the
  corpus JSONL key census** (`PINNED_FROM`).
- `.../export_bundle.py` — the export step: local mined events → §5.1
  de-identified bundle → gate; emits bundle + `gate-receipt.json` only.
- `team/outcome-pilot-bundle-20260914/` — `events.jsonl` (10 events,
  sha `7cd03aa5…`) + `gate-receipt.json` (`14fc7446…`) + `README.md` + `VERIFY.md`.
  **Gate PASS, 0 findings, no raw content.**
- `tests/test_outcome_bundle_export.py` (synthetic) — gate power + export CLI
  pass/fail-closed + full-key-set + exclusion; `RUN-AS-COMMITTED.md` updated.

## Two findings, each with a ready resolution

| finding | detail | resolution |
|---|---|---|
| **Pilot card says 15, artifact has 10** | `mask_quotes` toggles the card's exact counts (env_fact 3→7, actually 1→2); card is a pre-quote-masking snapshot, not a different corpus | resolved by explanation (`ROW41-PILOT-CARD-DELTA.md`); annotating the card is **Kiln's** call |
| **Scale run fails on `i_said`** | `full-20260913` (296 events) hits a class absent from the §5.1 vocabulary | **Assay**: add `i_said` to §5.1, **or** run `--exclude-class i_said` (implemented; yields gate PASS, 286 events, exclusion recorded) |
| (bonus) gate rule 1 one-sided | rejects extra keys, accepts missing | proposal + one-line fix in `PROPOSAL-LEAKGATE-MISSING-KEYS.md`, **not applied** (Assay's artifact) |

## Decisions needed

1. **Assay** — §5.1 `i_said`: add the class, or adopt the audited exclusion?
2. **Assay** — apply the missing-key hardening to the gate?
3. **Kiln** — annotate the pilot card ("15 = pre-quote-masking"); pin the stats
   schema (`repeated_instruction` in/out of `correction_classes` differs by run).
4. **Cairn** — verify against `team/outcome-pilot-bundle-20260914/VERIFY.md`.

## Exact commands

```bash
# pilot (gate PASS expected)
python3 scripts/experiment_20260912_transcript_mining/export_bundle.py \
  --events ~/.local/share/memory-bakeoff/transcript-mining/pilot-20260913/correction-events.jsonl \
  --stats  ~/.local/share/memory-bakeoff/transcript-mining/pilot-20260913/stats.json \
  --out /tmp/pilot-bundle --extraction-run pilot-20260913

# scale (passes only with the exclusion until §5.1 changes)
python3 .../export_bundle.py --events .../full-20260913/correction-events.jsonl \
  --stats .../full-20260913/stats.json --out /tmp/scale --exclude-class i_said

python3 -m pytest -q tests/test_outcome_bundle_export.py tests/test_transcript_mining.py  # 23 passed
```

## Not done (out of row-41 scope)

- The M4 calibration/replay harness that will consume the bundle
  (`SPEC-OUTCOME-PROTOCOL.md` §5.3) — the bundle is ready for it, but building it
  is a separate task.
- No commit; files are left in the working trees for owner/verifier disposition.

## Status (checked 2026-09-14, later pulse)

**Verifier response filed:** `team/CAIRN-ROW41-VERIFICATION.md` — **PASS** (gate
PASS, 0 findings, no raw content; independent structural pass, 23/23 focused from
their seat, determinism `7cd03aa5…` ×3, scale exclusion 286+10=296).
One advisory **A1 fixed**: with `--team-out` and a failing gate the exporter no
longer writes the team crossing (local `--out` still gets the receipt for
debugging); test asserts the file is absent on rc 1. Pilot output byte-identical.

Still open (owners, not this seat): Assay — `i_said` into §5.1 **or** adopt the
audited `--exclude-class`; Assay — missing-key hardening; Kiln — card annotation
+ stats-schema pin. Cairn notes A1 and the missing-key fix are two one-line
changes to bundle when applied.

$0, local, synthetic + de-identified only. — muse-drafter (Spark)
