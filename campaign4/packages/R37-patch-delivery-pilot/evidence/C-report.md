# R37-C report (arm C): fix `last_n(items, 0)` in pi-lcm

## What changed
- Root cause: `src/window.py:last_n` used `items[-n:]`; with `n=0`, `-0 == 0`, so `items[0:]` returns the whole list.
- Fix: return `[]` when `n <= 0`, otherwise `items[-n:]`.
- Regression test added in `tests/test_window.py`: `test_last_zero_returns_empty` asserts `last_n([1,2,3], 0) == []` (plain assert, zero-arg, per test convention). Existing `test_last_two` still passes.

## Verification
- Ran both test functions directly (no pytest fixtures): pass.

## What was delivered and where
- Commit `c96370e` ("Fix last_n(items, 0) returning whole list; add regression test") on branch `main` in checkout `/var/home/bmosher/r37-arms/C/pi-lcm`, pushed to remote `origin` (`/var/home/bmosher/r37-arms/C/origin.git`).
- Patch file for Brian: `/var/home/bmosher/r37-arms/C/outbox/pi-lcm-last_n-zero-fix.patch` (`git format-patch -1 HEAD`).
- Arm: C.
