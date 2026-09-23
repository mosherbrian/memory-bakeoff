# P6-r18-runtime-source-time — manifest-repair verification

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-manifestverify-1` (existing ≤20 m grant)
- **Brief:** `manifest-repair-receipt.json` / `manifest-repair-allocation-1.md`;
  base `05a4568`; prior FAIL `b89c5862…` preserved.
- **Candidate:** outer manifest now 83 entries, composition 74; production bytes
  unchanged (`case_entry a07f82e4`, `harness d44e6103`, `runtime/acp-worker
  9f228b47`, `srcemit fa44ab78`, `interface 0005bcd1`).
- **Scope:** read-only. No source edit, no live effect.

## Verdict

**INCOMPLETE (bounded).** The manifest correction is **correct**: the stale
`candidate/candidate/` duplicate tree was removed, both manifests were re-emitted
cleanly, and the diff is packaging/docs-only with all reviewed executable bytes
preserved. However the allocation's required **NEW claim**
(`completion-claims/ex-p6r18-manifest-repair-1.json`) was **not filed**, and the
repair receipt's own `claim_path`/`notify_command` point to that missing file —
so the completion is not bound. One small filing fix remains.

## Diff-only verification (PASS)

- Changes vs base `05a4568`: **deleted 79 files, all under
  `candidate/candidate/`** (stale nested duplicate; non-nested deletions = none);
  **changed** only `candidate/changes.md`, `candidate/composition-manifest.json`,
  `candidate/manifest.json`; **added** only the empty package markers
  `candidate/src/r3harness/__init__.py`, `candidate/tests/__init__.py`.
- **No** production/test/plan/runtime/interface byte edits: `case_entry a07f82e4`,
  `harness d44e6103`, `runtime/acp-worker 9f228b47`, `srcemit fa44ab78`,
  `interface 0005bcd1` are identical to the reviewed candidate.

## Manifest verification (PASS)

- `candidate/manifest.json`: **83** entries; `composition-manifest.json`: **74**.
  No missing paths, no duplicates, no `candidate/candidate/` entries, no hash
  drift, no self-reference, no symlink/escaping alias.
- The only entries matching the `candidate/candidate` substring are the canonical
  `candidate/candidate-plan.md` (exists; **not dangling**) in both manifests.
- R3 descriptor `R3_REVISION.json` 0 copy-hash drift; parent pins retained.

## Closure smoke (PASS, no live effects)

- `runtime/srcemit.py` imports and `emit_end` produced one matching versioned end
  record under an injected test clock (`src_v 1`, `src_clock test`,
  `src_status ok`).
- `runtime/acp-worker` parses and references the shipped `srcemit` hook;
  `case_entry` imports cleanly against `candidate/src`.
- `candidate/fixture-launch-plan.json` references only
  `candidate/runtime/acp-worker` / `candidate/runtime/srcemit.py` — no nested-tree
  or shared-runtime reference. No runtime/import/plan path requires
  `candidate/candidate/`.

## Carried prior evidence (explicitly)

The prior independent review's full gate (**90 passed in 666.61 s**), retained
P5 **83** + P3 **59**, and the subprocess hook probe are carried on the
byte-identical reviewed modules above (metadata-only change, no redundant full
suite per the allocation). As recorded, that review did not individually re-run
every negative beyond the subprocess hook; that limit is preserved. This metadata
grant certifies no additional source behaviour or live runtime adoption.

## Bounded residual

- **Missing NEW claim:** `completion-claims/` contains only
  `ex-p6r18-candidate-1.json`; no `ex-p6r18-manifest-repair-1.json` anywhere in the
  package. The repair receipt's `claim_path` and `notify_command` reference the
  non-existent file. File the new claim binding the final manifests/bytes before
  acceptance.

## Effect

One bounded verdict: **INCOMPLETE (bounded)** — diff-only and manifest-closure
checks pass and the prior gate evidence is carried, but the required new claim is
absent. Returned to Tern; original FAIL preserved.
