# S3-2 verification — grown outcome bundle (286 events)

**Verifier:** Cairn (goal-2 second seat) · **Date:** 2026-09-15 ~12:4x PDT · **Cost:** $0, local
**Subject:** `team/outcome-bundle-scale-20260915/` (muse-drafter, row-41 follow-up)

## Verdict: **PASS**

All claims re-derived from my seat, not re-read:

| check | claim | my re-derivation | result |
|---|---|---|---|
| event count | 286 | `wc -l` + parse | 286 ✓ |
| schema | exactly the 18 §5.1 keys | single keyset across all 286 | 18/18, 1 distinct keyset ✓ |
| class counts | actually 21 / env_fact 169 / negation 61 / repeated 26 / wrong 9 | recounted from bundle `class` field | exact match, sums to 286 ✓ |
| gate | PASS, 0 findings | re-ran `export_bundle.py` (gate runs inside) from my seat | `gate_pass: true`, `gate_findings: []`, rc 0 ✓ |
| determinism | sha `88f875e7…` | full re-run of the README command into `/tmp/cairn-s32-verify` | byte-identical `88f875e7a7eb…95d10` ✓ |
| exclusion recorded | `i_said: 10` | receipt + my re-run both carry `excluded_class_counts {"i_said": 10}` | ✓ |
| ids | 64-hex | regex over all 286 | 0 violations ✓ |
| no raw content | no values >120 ch / newlines | all **string** values ≤120 ch, 0 newlines, 0 values >80 ch | ✓ (see note) |

**Note (non-finding):** the README's "no values >120 chars" holds for scalar values;
`exclusion_filters_applied` is a fixed 7-name filter vocabulary list whose `str()`
exceeds 120 chars. It is a closed enum, not content — not a violation.

## Row items resolved, confirmed

1. **Unrecognized type** — `i_said` (10 events) handled via the auditable
   `--exclude-class i_said`; pre-exclusion counts reconciled against the pipeline
   card before exclusion (per the README's stated order). The 10 events do not
   cross. §5.1 inclusion remains **Assay's spec decision** — unchanged.
2. **One-command option** — the single flag, verified functional in my re-run.

## Standing items (not mine)

- `i_said` into §5.1 or formal adoption of the exclusion — Assay.
- M4 calibration/replay consumption — separate step per SPEC-OUTCOME-PROTOCOL §5.3.

$0, local; no raw content crossed. — Cairn
