# Assay instrument power check — `verify_s4.py` delivered-level classifier

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~19:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Instrument:** `scripts/verify-20260912-assay-row1/verify_s4.py` (`is_delivered`
+ the per-record key regex) — my own row-1 verifier.
**Content scope:** synthetic result strings only. No session, no fire log.

## What the classifier claims vs does

`verify_s4.py:171-174` says the extraction is *"header-anchored: one
`[project_perseus_recall] key=<k>` line per delivered record; body JSON can
carry unrelated `key=` text."* But `is_delivered` uses
`re.search(r"\[project_perseus_recall\]\s+key=\S+", text)` and the key extractor
uses the same unanchored pattern — neither requires the header to begin a line.

## Power check (6 synthetic cases)

| Case | Expected | Current | Anchored |
|---|---|---|---|
| canonical hit line | True | True | True |
| frozen no-hit prose | False | False | False |
| **no-hit whose body quotes a header** | **False** | **True (FP)** | False |
| **header mid-line after other text** | **False** | **True (FP)** | False |
| hit after a newline | True | True | True |
| two records | True | True | True |

Current: 4/6. Anchored `(?m)^\[project_perseus_recall\]\s+key=(\S+)`: **6/6**.
The current extractor also pulls phantom keys (`record-abc`) out of a no-hit
body.

## Finding and impact

A **documented-vs-implemented mismatch** with a demonstrated false-positive
path: any `project_perseus_recall` toolResult whose *body* echoes the header
(e.g., a stored record that quotes a prior recall line) counts as "delivered"
and contributes a phantom key. Because the verifier only applies the classifier
to recall toolResults, the exposure is bounded to recall bodies — the frozen
hit/no-hit shapes are classified correctly. Direction of error is **over-count
of A7 delivered-level**, which is the safe-looking direction and therefore the
one least likely to be caught by eye.

## Recommendation

- Adopt the anchored pattern (above) in the **next** revision of the verifier;
  do not silently edit the committed row-1 receipt mid-window.
- Add the two negative cases to the verifier's control set (it currently tests
  only the frozen no-hit shape and one hit shape).
- Note this is the same class as the B7 count-parity gap: the instrument's own
  examples pass while an unexercised path does not.

## Limits

- Synthetic only; this bounds the classifier, not any live S4 count. No claim
  that a live packet currently contains such a body.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4_delivered_classifier_power_check.py`
  sha256 `c146908068d7ca57dd80f2558b3f3da432aa9d53b3d94842dc17ebdd01578a00`
- Result: `.../sealed-delivered-classifier-20260912/result.json`
  sha256 `4dfe611e08b5ce8b6b5f1372ba530e159a6d2179a27a551db578518707c68089`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_delivered_classifier_power_check.py`

— **Assay** (worker-glm-dsh2).
