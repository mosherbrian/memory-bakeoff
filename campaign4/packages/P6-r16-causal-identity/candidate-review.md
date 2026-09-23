# P6-r16-causal-identity — candidate review (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r16-review-1` (existing ≤30 m grant)
- **Brief:** `dispatch-receipt.json` (`P6r16-candidate-1`, contract
  `166125b2…`, admission `f3fda152…`); parent R14 `02ea693e` / manifest
  `8584cbed`, R15 evidence `872bb3c9`.
- **Claim:** `completion-claims/ex-p6r16-candidate-1.json`.
- **Evidence:** `/tmp/p6r16-review-gate.log`. No source edit, no live effect.

## Verdict

**PASS (bounded).** The identity-join fix is correct and confined to
`case_entry.py`; the full composed gate is green on the frozen bytes (76/76),
retained P5 83 + P3 59 are green, descriptors/manifests are accurate, and an
unshared independent mutation confirms own-action joining with correct rejection
of the swapped and missing-source cases. Cleared for Tern acceptance.

## Fix inspection (identity join)

- `_check_causal` now takes `item_by_action` and, for each action, resolves the
  onset through the **verified bound item**, joining each action's onset with
  **its own** detection; worker is required, optional actions skipped, and
  worker/verifier are never cross-paired.
- `_resolve_causal_items` builds the mapping from the signed manifest items plus
  restored turn-bind records (`carried`), not filename order / seat labels /
  prefixes; conflicting duplicates or observed-vs-bound item disagreement raise
  owned errors (`E_ITEM_MISMATCH`/`E_CONFLICT`).
- `_read_onset` rejects a sidecar whose content does not assert its bound
  identity; missing/ambiguous mappings and nonfinite/negative uncertainty raise
  explicit `E_NO_ONSET`/`E_NO_DETECTION` (INCOMPLETE), never arbitrary selection.
  Causal inequalities and finite-uncertainty semantics are unchanged.

## Bound bytes / surface

- Only production change: `case_entry.py b14de4c4…` (parent R14 `64edb54e…`).
  `driver/ingress/store/lifecycle/validator/turn_handoff/harness/host_adapter`
  are **byte-identical** to R14; core unchanged.
- Manifests: composition 74 and outer 78 entries — 0 missing, **0 drift, no
  self-reference**; `R3_REVISION.json` 0 copy-hash drift.

## Gates (actual new modules)

- `PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider`
  → **76 passed in 634.93 s** (rc0), no skips/removals (70 prior + new r16 tests).
- `candidate/tests-retained/p5r2` → **83 passed**; `p3r3` → **59 passed**.

## Unshared independent mutation (corvid)

Direct `_check_causal` on R15-copied onsets with `item_by_action`
`{worker: id492…(00:51:11), verifier: i42…(00:52:37)}`: own-action join succeeds
(worker onset `00:51:11`, both pairs present); a **swapped** detection (worker
detection before its own onset) → `E_CAUSAL`; a **missing** worker bound source →
`E_NO_ONSET`. This confirms the wrong-pair defect is fixed and negatives fail
closed. The claim's diagnostic replay of recorded R15 is new-code evaluation, not
a retroactive live PASS.

## Preserved / limits

Authenticated rejection, no-COMPLETE, no-duplicate sends, T1–T4 and R13
safeguards retained (in the inherited suites). Live remains held; this is
candidate-only. Known limits (from R14/R15) unchanged: late-recorded completion
proof and queued/ambiguous live controls unresolved; finding5 NOT REPRODUCED.

## Effect

One bounded verdict: **PASS (bounded)** — identity-joined causal gate correct,
full composed 76/76 plus retained 83+59 green, descriptors/manifests accurate,
unshared negative verified. Returned to Tern for acceptance and a fresh live
failed/rest witness under separate exact releases.
