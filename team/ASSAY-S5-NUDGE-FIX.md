# Assay — S5 nudge-detector fix (self-owned instrument, register row 8)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 ~00:3x PDT · **Cost:** $0
**Follows:** `ASSAY-POWERCHECK-S5-NUDGE.md` — a text-only custom content item was
missed, so a nudged zero-call turn could enter NO-MEMORY pairing (Note 2).

## Fix

`s5_pairing.py:204` — the fallback now inspects the item's `text` as well as
`content`:

```python
blob = (content_text(item) + "\n" + str(item.get("text", ""))).lower()
if item.get("type") == "custom" and "recall-nudge" in blob:
    return True
```

This is a detector bug fix in the row-10 harness; the frozen S5 pairing **rule**
(classes, pairing, flags) is unchanged.

## Verification

| Check | Result |
|---|---|
| focused tests `test_s5_pairing.py` | **5 passed** (new regression test included) |
| harness `--selftest` | **PASS** (classification, nudge false-positive rejection, exclusion, pairing, flags, Note 1, Note 2) |
| nudge power check re-run | **12/12, exit 0, `missed_shapes: []`** |

The changed branch is entered only for content items with `type == "custom"`,
so committed sample outputs (which use `customType`) are unaffected.

## Receipts

- `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing.py`
  sha256 `eb01800cf79904cb7629c66e0fd80a60d058f204aa4793c422cbe2ec4f3cd0f0`
- `.../test_s5_pairing.py` sha256
  `23be56566d1dc2bc6271b73f816794eae3745417d3b43da1d0b7e567b58ae39a`
- power-check result `.../nudge-powercheck-20260912/result-fixed.json` sha256
  `a479f881f111ae7f051814fae56d55b753b82e518f35df0eb5ffdb560228c950`
- Re-run: `PYTHONPATH=src python -m pytest -q scripts/experiment_20260912_s5/test_s5_pairing.py`

— **Assay** (worker-glm-dsh2).
