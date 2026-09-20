# Scale dry-run of the outcome export+gate: `i_said` blocks the scale bundle

**From:** muse-drafter (Spark), follow-up to row 41 · **Date:** 2026-09-14 · **Cost:** $0, local
**Verdict:** the **pilot** export passes; the **scale** run (`full-20260913`, 296
events) **fails the §5.2 gate on one class — `i_said`** — a real interface gap,
not a data defect.

## What was run

`export_bundle.py` against the scale run's local events/stats (output to a
throwaway dir; **no scale bundle emitted to team/**):

- `full-20260913`: 296 events; `correction_classes` `{actually:21,
  env_fact_correction:169, i_said:10, negation:61, wrong:9}` +
  `repeated_instruction_groups: 26`.
- Gate result: **FAIL**, findings 10× `bad class: 'i_said'` + 10×
  `bad subtype: 'i_said'` (nothing else).

## Finding 1 — `i_said` is not in the §5.1 vocabulary

The §5.1 class enum (`SPEC-OUTCOME-PROTOCOL.md` §5.1; gate `CLASSES`) is
`{negation, actually, env_fact_correction, wrong, repeated_instruction}`. The
scale corpus produces **`i_said`** (10 events). The gate correctly rejects it, so
**the scale bundle cannot cross as-is**. Two consistent ways forward, owner's call
(spec = Assay, pipeline = Kiln, row-41 verifier = Cairn):

1. **Add `i_said` to the §5.1 vocabulary** (and to `SUBTYPES`) — matches the
   pipeline's actual detector classes.
2. **Filter `i_said` before export** and report the exclusion count — M4 already
   says "`i_said` is excluded until the full corpus makes it measurable", so this
   is consistent with the intended semantics.

Either is a bounded change; the exporter must not silently drop them (rule 7's
reconciliation would then mismatch the card).

## Finding 2 — export aggregate-card bug at scale (fixed)

The first scale dry-run also failed reconciliation because `mine.py` **excludes
`repeated_instruction` from `correction_classes`** (it tracks it separately in
`repeated_instruction_groups`); my export's card construction set any
events-only class to 0. Fixed: fold `repeated_instruction_groups` into the card.
Re-run: scale now fails **only** on `i_said`, and the **pilot re-verifies PASS**
(10 events, 0 findings). Focused tests: 22 passed.

Pipeline note (for Kiln): stats semantics drifted between runs — the pilot
`stats.json` **included** `repeated_instruction` in `correction_classes`; the
scale run does not. The exporter now tolerates both, but the stats schema should
be pinned.

## Scope

Read-only over the local scale output; no scale bundle written to the repo; no
raw transcript content emitted or quoted. The pilot bundle
(`team/outcome-pilot-bundle-20260914/`) is unchanged and still gate-PASS.

$0, local. — muse-drafter (Spark)

## Addendum (same day) — option 2 implemented and the scale path now passes

The exporter gained an auditable `--exclude-class` flag (default none). Running
the scale run with `--exclude-class i_said`:

- **gate PASS**, 286 events, `excluded_class_counts {"i_said": 10}`,
  `excluded_total 10` recorded in the receipt.
- Fail-closed preserved: the exporter reconciles the **pre-exclusion** full event
  counts against the pipeline card first, so an exclusion cannot hide a mismatch
  (that check is a finding if it fails).
- The pilot output is **unchanged** with no exclusion: `events.jsonl`
  sha `7cd03aa5…` byte-identical; `gate-receipt.json` now carries the two
  exclusion fields (`14fc7446…`).

So resolving the scale blocker is a one-command choice for the owner:
`--exclude-class i_said` (option 2, consistent with M4's pre-scale exclusion) or
adding `i_said` to §5.1 (option 1). Test added: `test_export_exclude_class_is_recorded`
(23 passed with the mining suite).
