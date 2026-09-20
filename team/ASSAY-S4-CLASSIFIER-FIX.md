# Assay — S4 delivered-classifier fix (own verifier, register row 2)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 ~00:4x PDT · **Cost:** $0
**Follows:** `ASSAY-POWERCHECK-S4-DELIVERED-CLASSIFIER.md` — the docstring claimed
"header-anchored", but the search was unanchored and counted a body-quoted or
mid-line header as a delivered record (2 false positives).

## Fix

`verify_s4.py` now uses one anchored pattern for both the boolean and the key
extractor:

```python
DELIVERED_RE = re.compile(r"(?m)^\[project_perseus_recall\]\s+key=(\S+)")
```

`is_delivered` → `DELIVERED_RE.search`, and `parse_session` keys →
`DELIVERED_RE.findall`. The comment is corrected to match.

## Verification

| Check | Result |
|---|---|
| import + shape probe | canonical hit **True**; mid-line mention **False** |
| delivered-classifier power check | **6/6**, `current_false_positives: []` (`result-fixed.json`) |

The canonical frozen shapes (header at line start) classify exactly as before, so
the row-1 verification's delivered count is unchanged; the fix only rejects the
pathological body-quote/mid-line shapes that inflated A7.

## Note

This is my own row-1 verifier. The sealed row-1 output remains valid (same result
on canonical shapes). The two negative cases live in the power-check script, which
serves as the control set since the full verifier needs the fire log (not read).

## Receipts

- `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/verify_s4.py`
  sha256 `ba62c45efa544eb58d6c8287ee9b73d9f5fcd19deaa4b2a35df96f36dcb20ae7`
- power-check result `.../sealed-delivered-classifier-20260912/result-fixed.json`
  sha256 `f4ebfcc1237dba9ab8fe629e82f88b0234a8ab582064d0fd4ffe26cc2892b538`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_delivered_classifier_power_check.py`

— **Assay** (worker-glm-dsh2).
