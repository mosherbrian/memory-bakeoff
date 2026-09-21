# P4-r2-durable-events — cleanup verification (grant ext-1)

- **Verifier:** corvid (independent; did not author these outputs)
- **Grant:** `allocation-extension-1.md` — one cleanup ≤5 min then one verifier
  ≤5 min; cumulative P4 worker 133m56s / verifier 85m
- **Deadline:** 2026-09-21T22:54Z from the dispatch wake
- **Rejected repair:** `p4r2-attempt-history/repair-rejected/` (driver
  `b285bc7f…`); cleaned present driver `8f7c61ce…`; prior verdicts retained.

## Verdict

**PASS.** The cleanup removed only redundant byte-identical duplicate
definitions and duplicate comments; the effective module (Python
last-definition semantics) is AST-identical to the rejected repair, method names
are unique, all other 15 outputs are untouched, and 36 local + 59 core tests
pass with no live effects.

## Commands and results

```bash
sha256sum src/driver.py                       # 8f7c61ce…
sha256sum …/repair-rejected/src/driver.py     # b285bc7f…
python3 - <<AST normalization>>               # effective AST identical: True
PYTHONPATH=src python3 -m pytest tests/ -q    # 36 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q  # 59 passed
```

## Expected/observed

| Check | Expected | Observed |
|---|---|---|
| cleaned `src/driver.py` hash | `8f7c61ce…` | `8f7c61ce846c643756554c0e67b9b1423d3838de5368589418037f0e702e4c79` |
| rejected-repair driver | `b285bc7f…` | `b285bc7ff4096081ac82d5d006e9e5577ed5a9b3b9668063787d47b4c5f7895c` |
| effective AST equivalence (last-definition collapse) | identical | **identical** (normalized dump sha `84c35805ad981680` both) |
| unique `Driver` method names | no duplicates | 26 methods, 0 duplicate names |
| duplicate actor-mapping comments | 1 | 1 (was 8) |
| only redundant defs/comments removed | yes | `_maybe_crash` 19→1, `cancel_deadline` 18→1, `is_cancelled` 18→1, comments 8→1 |
| other 15 worker outputs byte-identical to rejected archive | unchanged | **unchanged** (0 mismatches over the 15 non-driver manifest paths) |
| lines | reduced | 944 → 577 (effective logic retained) |
| 36 local tests | pass | 36 passed |
| 59 accepted core tests | pass | 59 passed |
| live effects | none | no subprocess/socket/signal/os.kill/os.system/popen/requests/urllib/time.sleep/while True |

The worker's `cleanup-receipt.json` independently reports before/after hashes
(`b285bc7f…` → `8f7c61ce…`), the duplicate-only scope, and 36 passing tests,
consistent with the above.

## Notes

- Effective AST comparison was done by collapsing each class's method
  definitions to the last definition per name (exactly Python's semantics),
  then comparing `ast.dump(..., include_attributes=False)`; the two effective
  modules are identical, so removing the earlier byte-identical copies changed
  no runtime behaviour.
- The cleanup did not add the pending clock-authority successor requirement,
  consistent with the grant.
- Prior verdicts are retained unchanged: `verification-r2.md`
  (`e2e617f5…`) and `verification-r2-repair.md` (`4e6eb965…`); this file is the
  cleanup verdict only. Simulated evidence only; no live effects.
