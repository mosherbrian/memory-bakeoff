# Row 41 verification — first de-identified outcome bundle (verifier seat)

**Verifier:** Cairn (worker-pi), goal-2 second seat · **Date:** 2026-09-14 ~19:0x PDT
**Cost:** $0, local, structural checks only — no raw transcript content read.
**Subject:** `team/outcome-pilot-bundle-20260914/` (muse-drafter, GiLMore assignment)
+ `implementer/repo/scripts/experiment_20260912_transcript_mining/{outcome_leak_gate.py, export_bundle.py}`.

## Verdict: **PASS** — 1 advisory, 1 open finding (card delta, owner Kiln)

The first de-identified correction-event bundle crosses into the outcome lane
validly: gate PASS, 0 findings, no raw content in the bundle or receipt.

## Checklist results (pre-fixed at my seat, 2026-09-14 ~18:5x)

| # | check | result |
|---|---|---|
| 1 | gate actually called at the export step, fail-closed | ✓ `export_bundle.py:161` calls `gate()`; rc 1 + `gate_pass:false` receipt on findings. **ADVISORY (A1):** with `--team-out` given, the team bundle files are written even when the gate fails — the prototype's contract was "emit the bundle if clean"; non-consumability is enforced by receipt+rc, not write suppression. One-line fix: wrap the team_out writes in `if not findings`. The crossed bundle was clean, so the crossing stands. |
| 2 | sentinels pinned from the pipeline's actual JSONL structure | ✓ 32 sentinels, `PINNED_FROM = "mine.py + keys-only census of the corpus JSONL, 2026-09-14"` with the census documented in-source. Accepted structurally (I did not read the raw corpus). |
| 3 | bundle = exactly the §5.1 key set, structural only | ✓ all 10 events carry exactly the 18 §5.1 keys, identical key set per event; hashes/enums/buckets/booleans/lengths only. |
| 4 | gate PASS + power re-run | ✓ `gate-receipt.json`: `gate_pass:true`, `gate_findings:[]`; Assay's power check re-run from my seat: `all_pass:true` rc 0; focused suite `test_outcome_bundle_export.py` + `test_transcript_mining.py`: **22/22 passed** from my seat. |
| 5 | class counts reconcile | ✓ bundle = receipt = pipeline `stats.json`: {actually 1, env_fact_correction 3, negation 3, repeated_instruction 2, wrong 1} = 10 (224 turns, 16 files). |
| 6 | no raw content crosses | ✓ independent structural pass over `events.jsonl`: 0 findings (no value >120 chars, no newlines, event_id/normalized_prefix_hash 64-hex, class/env_fact_kind in frozen vocabularies). |
| 7 | M4 uses | ~ events carry `class`; the "adjudicated truth" pairing for the M4 held-out set is not a §5.1 field (schema frozen) — it must be tracked on the adjudication side when the M4 calibration consumes these events. Question for the M4 step, not a bundle defect. |

## Open finding (owner: Kiln, pipeline owner) — EXPLAINED, annotation pending

**The pilot card's "15 events" is a pre-`mask_quotes` snapshot** (per
`ROW41-PILOT-CARD-DELTA.md`): `mask_quotes` toggles the card's exact counts
(env_fact 3→7, actually 1→2). Both the stored artifact and a fresh `mine.py`
re-run give **10** events (224 turns); the drafter correctly bundled the
actual 10 and reconciled against the pipeline's own `stats.json`. Annotating
the card ("15 = pre-quote-masking") + pinning the stats schema
(`repeated_instruction` in/out of `correction_classes` differs by run) is
Kiln's call.

## VERIFY.md verification (second driver, 2026-09-14 ~19:4x)

Per the handoff's decision item 4, verified against
`team/outcome-pilot-bundle-20260914/VERIFY.md` from my seat:

| check | result |
|---|---|
| 4 artifact hashes (events, receipt, export_bundle.py, outcome_leak_gate.py) | ✓ all match VERIFY.md |
| determinism: two independent export runs vs shipped bundle | ✓ byte-identical `7cd03aa5…` ×3 (fixed pilot salt) |
| focused suite (gate power + CLI fail-closed + full-key-set + exclusion) | ✓ **23/23 passed** from my seat |
| scale path `--exclude-class i_said` (full-20260913, 296 events) | ✓ 286 events, gate PASS 0 findings, exclusion recorded `{i_said: 10}` (286+10=296) |

**Verdict stands: PASS.** New pending decisions (not mine): (1) Assay —
`i_said` into §5.1 or adopt the audited exclusion; (2) Assay — apply the
missing-key hardening (`PROPOSAL-LEAKGATE-MISSING-KEYS.md`, gate rule 1 is
one-sided: rejects extra keys, accepts missing); (3) Kiln — card annotation +
stats-schema pin. Note: my advisory A1 (team-write on gate failure, `export_bundle.py`) and the
missing-keys hardening (`outcome_leak_gate.py`) are two separate one-line
fixes; bundle them when applied.

## Blind-package verdicts (2026-09-14 ~21:4x PDT)

`team/BLIND-VERDICTS-conductor-claude.md` Task B: 8/10 CONSISTENT, 2 INCONSISTENT
(RC-57d592c0, RC-d0767deb: `env_fact_correction` with `env_fact_kind: null`).
**CORRECTED ~21:5x:** Corvid's adjudication
(`team/CORVID-BLIND-VERDICT-ADJUDICATION.md`) is right — verified from my seat:
SPEC-OUTCOME-PROTOCOL §5.1 (L241) defines `env_fact_kind` as **nullable**;
`export_bundle.py:53` `_env_fact_kind -> str | None` (None = no kind matched,
a signal); `outcome_leak_gate.py:36` `ENV_KINDS` includes `None`. The package's
criterion file was stricter than the frozen schema — the two INCONSISTENT
verdicts are a criterion over-reach, not event defects. My initial "miner
defect, owner Kiln" flag is RETRACTED; bundle, classifications and gate stand.
Task A 36/36 AGREE stands as independent confirmation.

## A1 fix verification (2026-09-14 ~20:1x PDT)

muse-drafter applied my advisory A1 to `export_bundle.py` (19:57). Verified from my seat:

| check | result |
|---|---|
| code: team crossing gated on `not findings` (`export_bundle.py:217`) | ✓ local `--out` receipt still written on rc 1 for debugging |
| test: team file asserted absent on rc 1 (`tests/test_outcome_bundle_export.py:141-148`) | ✓ present |
| focused suite from my seat | ✓ **24/24 passed** (23 + new A1 test) |
| pilot re-export vs shipped bundle | ✓ byte-identical `7cd03aa5…` |
| `export_bundle.py` sha vs VERIFY.md | ✓ `ed0e2f56…` (VERIFY.md re-stamped post-fix) |

**A1 CLOSED.** Remaining pending decisions unchanged: Assay ×2 (`i_said` §5.1; missing-key hardening), Kiln ×1 (card annotation + stats-schema pin).

— **Cairn** (worker-pi). $0, structural only.
