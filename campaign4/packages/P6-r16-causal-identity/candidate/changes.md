# P6-r16 changes — bind causal evidence to action and execution

Parent: R14 candidate source `02ea693e48cc`, outer manifest `8584cbed8a97`
(verified on copy). Production change ONLY `src/case_entry.py`
(`_check_causal` identity join + its call site, new
`_resolve_causal_items`/`_read_onset` helpers). All other Python,
harness, adapter, accepted core byte-identical (verified per-file).
No timing retouch, no threshold change, no fabrication. Injected only.

## Gap (R15, preserved)
`_check_causal` took the lexicographically-first onset file and paired it
with worker detection: verifier item `i42e65da2879b` (onset 00:52:37)
sorted before worker `id492c9c28b64`, so 00:52:37 vs worker detection
00:51:11 falsely raised `E_CAUSAL`. Reproduced on the immutable R14 parent
with copies of R15 evidence (no historical edit).

## Fix
- New `_resolve_causal_items`: joins each observed action's onset through
  the verified case/action/execution/session/item binding (signed manifest
  + observed runtime item + restored turn-bind records). Missing observed
  ends stay missing; conflicting duplicate bound items → `E_CONFLICT`;
  observed item disagreeing with its bound runtime item, or bound under a
  different execution → `E_ITEM_MISMATCH`. No filename/seat/prefix logic.
- `_check_causal` takes the validated `item_by_action` map: worker onset↔
  worker detection, verifier onset↔verifier detection, never cross-paired;
  verifier onset never required before worker detection. Sidecar content
  must self-assert its filename identity (swapped content rejected).
  Missing bound source/mapping/detection → owned `E_NO_ONSET`/
  `E_NO_DETECTION` (INCOMPLETE); non-numeric/bool/nonfinite/negative
  uncertainty → `E_NO_ONSET`. Causal inequalities and finite-uncertainty
  boundary semantics unchanged (exact-boundary equality passes).
- Genuine onset-after-own-detection and arm-after-source still `E_CAUSAL`;
  producer missing clock proof never replaced with detection time.
- Call site passes the resolved join; receipt `causal` keeps worker
  `onset_at`/`detected_at` keys and adds per-action `pairs`.

## Evidence
- `test_r16_causal_identity.py`: real-parent `E_CAUSAL` repro on R15 copies;
  correct worker+verifier join on new code; filename order both ways +
  unrelated earlier-sorting unbound file; genuine violations; missing/
  swapped/conflicting/wrong-execution/nonfinite-uncertainty negatives;
  exact-CLI `run-case failed-verification` (corrupt-after-worker) asserting
  receipt pairs match bound items.
- Full 70 + P5 83 + P3 59 gate on actual new modules (see claim).

## Out of scope
Late-recorded-work, shadow-time reconciliation, lost/queued live controls;
no `occurred_at` invention. Live stays held. R15 replay is diagnostic, not
a retroactive live PASS.
