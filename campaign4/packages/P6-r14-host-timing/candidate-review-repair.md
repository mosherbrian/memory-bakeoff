# P6-r14-host-timing — repair-1 verification (absent execution authority fails closed)

- **Reviewer:** corvid-dsh
- **Action:** `P6r14-repairverify-1` (existing ≤40 m grant)
- **Brief:** `repair-1-receipt.json` / `repair-allocation-1.md`; base `7509caf`;
  prior bounded PASS `84b75ed1…` preserved, not promoted.
- **Final bytes:** `harness.py 50f15cdf…` (was `62b86917…`),
  `case_entry.py 64edb54e…`, `host_adapter.py 231f45f0…`,
  outer manifest `8584cbed…`, composition `0e205500…`, descriptor `a7afd10f…`.
- **Evidence:** `candidate-review-repair-evidence/p6r14-repair-gate.log`.
  No source edit, no live effect.

## Verdict

**PASS (bounded).** The repair is guard-only and correct: an absent/null/empty/
malformed persisted `exec-current` now deterministically rejects with
`E_NO_EXECUTION_AUTHORITY` (superseded → `E_SUPERSEDED_ACTION`) before any
deadline handling or effect, while a genuine registered due execution still
interrupts exactly once. The old fail-open is reproduced on the pinned base
bytes. Full composed gate 70/70 and retained 83+59 are green on the actual final
modules; manifests/descriptor are accurate. Cleared for Tern acceptance.

## Guard-only diff (verified)

Diff vs base `7509caf`: changed files are `harness.py`, `changes.md`, the two
manifests, `R3_REVISION.json`, and two test files. In `harness.py` the **only**
change is the `current_exec` block (`timer_callback`):
`if current_exec is not None and …` → non-string/blank →
`E_NO_EXECUTION_AUTHORITY`; `SUPERSEDED->` → `E_SUPERSEDED_ACTION`; else
`current_exec != execution` → `E_EXECUTION_MISMATCH`. It never recovers authority
from argv and never creates a registration. `host_adapter.py` and
`case_entry.py` are byte-unchanged; accepted core Python remains byte-identical
to R13.

## Independent old-fails / new-rejects (exact CLI)

Ran the callback CLI under the pinned base harness (temp copy of `7509caf`) and
the repaired candidate, on a due current action (`a-C`, grant lapsed):

| scenario | base `7509caf` | repaired `50f15cdf` |
|---|---|---|
| absent `exec-current` | **interrupted, writes** (fail-open) | `E_NO_EXECUTION_AUTHORITY`; stable zero-writes |
| empty / malformed `exec-current` | n/a | `E_NO_EXECUTION_AUTHORITY` |
| callback `--execution` omitted / empty | n/a | `E_NO_IDENTITY` |
| wrong execution vs registered | n/a | `E_EXECUTION_MISMATCH` |
| genuine registered due execution | interrupts | interrupts once; repeat → `already-handled`, `dedup: true` |

The reject path performs no stop/wake and creates no
`cancelled:*`/deadline/ledger rows; only the expected volatile ingress-open
markers (`ingress-boot/epoch/last`) are written by opening the driver — not
deadline state, wake, or ledger mutation. Reopen agrees (no registration created,
`exec-current` still absent). No test pre-registers the missing fact in the
failure fixture.

## Full gate and retained suites (actual final modules)

```
PYTHONPATH=candidate/src python3 -m pytest candidate/tests -q -p no:cacheprovider
```
→ **70 passed in 635.12 s** (rc0), no skips/removals (69 prior + 1 new T1R).
The new `test_T1R_absent_execution_authority_rejects_no_effects_reopen_agrees`
covers the reproduced gap.

- `candidate/tests-retained/p5r2` → **83 passed**.
- `candidate/tests-retained/p3r3` → **59 passed**.

Module-origin is location-derived; tests exercise the actual candidate modules
(`harness 50f15cdf`, `case_entry 64edb54e`, `host_adapter 231f45f0`, core
byte-identical).

## Manifests / descriptors

composition 74 entries and outer 77 entries: 0 missing, **0 drift, no
self-reference**; `R3_REVISION.json` 0 copy-hash drift with correct `identical`
flags. No stale provenance.

## Scope / unchanged

Out-of-scope items untouched (late-recorded-work, shadow-time reconciliation,
lost/queued controls; no `occurred_at`, ingress recorded-time unchanged); R13
protections retained; live held. Counts rose by one explained new regression, no
inherited assertion skipped/deleted.

## Effect

One bounded verdict: **PASS (bounded)** — guard-only repair verified old-fails/
new-rejects, full composed gate 70/70 plus retained 83+59 green, manifests and
descriptor accurate. Returned to Tern for acceptance and the warranted next
package.
