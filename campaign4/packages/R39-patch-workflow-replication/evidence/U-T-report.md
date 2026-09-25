# Report — R39-U-T (pi-lcm stable_unique fix)

## What changed
- `pi-lcm/src/seq.py`: `stable_unique` was `sorted(set(items))`; replaced with first-occurrence-order dedup loop (seen-set + append). `stable_unique([3,1,3,2])` now returns `[3,1,2]`.
- `pi-lcm/tests/test_seq.py`: added regression test `test_preserves_first_occurrence_order` asserting `stable_unique([3, 1, 3, 2]) == [3, 1, 2]`. Existing `test_already_unique_sorted` kept. Both pass (2 passed).
- Committed locally on `main` as `036aa04 Fix stable_unique to preserve first-occurrence order`. Not pushed (per pi-lcm patch-file workflow).

## What delivered and where
- Delivered as `git format-patch` file for Brian to download and apply himself:
  - `/var/home/bmosher/r39-arms/U-T/outbox/0001-Fix-stable_unique-to-preserve-first-occurrence-order.patch`
- Nothing pushed to `origin`. No other files produced for Brian.
