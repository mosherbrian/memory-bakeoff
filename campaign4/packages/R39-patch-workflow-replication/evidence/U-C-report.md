# U-C report: stable_unique order fix

## What changed
- `pi-lcm/src/seq.py`: `stable_unique` was `sorted(set(items))` (returned sorted unique values, e.g. `[1, 2, 3]`). Replaced with `list(dict.fromkeys(items))`, which keeps first occurrences in original order, so `stable_unique([3, 1, 3, 2]) == [3, 1, 2]`.
- `pi-lcm/tests/test_seq.py`: added regression test `test_keeps_first_occurrence_order` asserting `stable_unique([3, 1, 3, 2]) == [3, 1, 2]` (plain assert, zero-arg, per test convention). Existing test still passes; `python3 -m pytest tests/ -q` → 2 passed.
- Also added `.gitignore` for `__pycache__/` / `.pytest_cache/` after accidentally committing pycache files in the fix commit; removed them in a follow-up commit.

## What was delivered and where
- Pushed branch `main` in `/var/home/bmosher/r39-arms/U-C/pi-lcm` to remote `origin` (`/var/home/bmosher/r39-arms/U-C/origin.git`): commits `7bf8781` (fix + test) and `23022a4` (pycache cleanup).
- Patch file for Brian: `/var/home/bmosher/r39-arms/U-C/outbox/pi-lcm-stable_unique-fix.patch` (diff of `src` + `tests` vs base `518668b`).

## Verification
- `python3 -c "from src.seq import stable_unique; assert stable_unique([3,1,3,2])==[3,1,2]"`
- `python3 -m pytest tests/ -q` → 2 passed.
