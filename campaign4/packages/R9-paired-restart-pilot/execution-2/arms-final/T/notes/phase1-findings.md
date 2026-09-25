# Phase 1 inspection - arm T

## Repro
Ran test exactly as given. Result: 116 passed, 1 failed (plus related FAIL line).
Failures:
- `a DECLARED check that cannot run counts FAILED, not absent`: expected `fail`, got `none` for G1 piped check `grep -c x <art> | head -1`.
- `127 logging`: expected log_once naming exit 127, absent.

## Cause in fleet-poller.sh
`row_gate()` lines ~455-465:
```
CE=$(echo "$J" | sed ... check_exit ...)
[ "$CE" = "127" ] && { echo none; return; }
```
Maps ALL exit-127 to `none` (prose/no-gate). But rowcheck splits cells on `|`, so a declared check containing a pipe truncates to literal `check:` -> bash exit 127. That is a broken gate, not an absent gate. Six live rows affected per test comment. Collapsing broken->none pins silently.

Missing: no `TRUNCATED at a pipe` log_once branch.

## Intended fix (phase 2, not applied)
In row_gate: on CE=127, distinguish: if rowcheck JSON shows declared_check present (or artifact path present) -> log_once TRUNCATED at a pipe + echo fail. Only map to `none` when truly no declared check / prose (e.g. T-3 style, empty id, missing binary). Keep existing pass/fail/none for other paths. Verify with the two failing assertions + full suite still green, no edit to test file.
