# Assay power check — S5 nudge detector (`record_is_nudge` / `classify`)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 ~00:2x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Target:** `s5_pairing.record_is_nudge` and `classify`. Synthetic records only.

## Result — 11/12 shapes correct; one latent false-negative

Detected: top-level `customType`/`custom_type`/`type`, message-level
`customType`, content-item `customType`, custom item carrying `customType`,
non-normal role naming the channel. Correctly **not** detected: a toolResult
quoting the phrase, and ordinary user/assistant text mentioning it.
`classify` precedence is correct: MEMORY beats nudge, NUDGED_NO_CALL when nudged
with no call, EXCLUDED when incomplete.

**Missed:** a content item shaped
`{"type": "custom", "text": "[recall-nudge] injected"}` (text-only custom item,
no `customType`).

## Cause and impact

`s5_pairing.py:204` uses `content_text(item)`, which reads `item["content"]` —
but a content item carries its text under `text`. So the fallback never fires
for that shape, and `record_is_nudge` returns False.

NUDGED_NO_CALL is **classless by Note 2** and must never pair. A nudged,
zero-perseus-call turn that is misclassified as NO-MEMORY would become eligible
for pairing — a real correctness risk. It is **latent**: the real extension marks
injected nudges with `customType` (caught by the earlier branches), so the
text-only shape is not observed in the committed session logs.

## Fix

In the line-204 fallback, inspect the item's `text` as well as `content`
(e.g. `content_text(item) or str(item.get("text", ""))`). One-line change; the
S5 rule must not otherwise move mid-window.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_nudge_detector_power_check.py`
  sha256 `f6f4ece661853884c64a77aae213751a31d7ad35fe3f6b2a4272d294c16bf67d`
- Result: `.../nudge-powercheck-20260912/result.json`
  sha256 `c655507fe2968204d9d50bf35458ad40267dbf7d446f132805ff9562ddec4aff`
- Re-run: `python3 scripts/experiment_20260912_s5/s5_nudge_detector_power_check.py` (exit 1 while the shape is missed)

— **Assay** (worker-glm-dsh2).
