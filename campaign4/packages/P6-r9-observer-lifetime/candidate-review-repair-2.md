# P6-r9 repair-2 — independent candidate verification (timer identity + callback)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-repair2verify-1`, start `2026-09-22T14:13Z`, deadline
  `2026-09-22T14:38Z`
- **Receipt:** `repair-2-receipt.json` (`P6r9-repair-2`, kiln)
- **Bound manifest:** `composition-manifest.json` sha256
  `83e9dabf5f52de042d905a70fef4059166ac2af3afd68802215bb694ba2c161d`
  (recomputed, matches claim)
- **Claim:** `completion-claims/ex-p6r9-repair-2.json` (manifest_sha256
  `83e9dabf…`)
- **Authority:** `amendment-2-host-timer.md` `592d24c1…` + pinned
  `amendment-2-checklist.md` `5b8ae89f…`
- **Scope:** read-only verification. No live effect, no retry, no mutation.

## Verdict

**FAIL.** The timer-identity and callback fixes are substantively correct and
their targeted tests pass, but the candidate is **not admissible**: the
manifest-bound R3 revision gate rejects the edited working copy
(`E_R3_DRIFT`), so the full no-simulated five-case CLI composition fails, and
the observer suite hangs past the window. The claim's "test_host_composition
green" is false and check5 materially understates the breakage.

## Scope — correct

Working tree change set vs pinned parent `ac1613c` is exactly the authorized
files: `src/r3harness/harness.py` (`d1369ce5…`), `src/r3harness/host_adapter.py`
(`8c3f8c3d…`), plus new `tests/test_amendment2_timer.py`. `case_entry.py`
unchanged (`9a1bb23c…`); frozen parents/core untouched. Fixes read correctly:
`canonical_unit`/`canonical_timer_id` normalize the `.timer` suffix once;
`command_for`/`create_host`/`cancel_host`/`query_host`/guard use canonical
identity; the reattach guard now checks `timer-arm:<canon>` (aligned with
`create_host`'s persistence); the callback argv carries
`--db <driver.store.path>` and `--action`, and `timer-callback` accepts
`--action`. `Driver.store.path` exists (`driver.py:90`, `store.py:36`), so the
`/tmp/p6h/harness.db` fallback is dead defensive code on the real path.

## Blocking findings

1. **`E_R3_DRIFT` blocks the CLI path (checklist item 5).**
   `tests/test_host_composition.py::test_d4_full_host_sequence` — the full
   no-simulated five-case host composition — fails at the first case
   (`positive-handoff`) with `{"detail": "R3 working copy harness.py drifted",
   "error": "E_R3_DRIFT"}` (rc3). `_r3_hash_check` (`case_entry.py:574-586`)
   compares the working copy to `src/r3harness/R3_REVISION.json`'s
   `copy_sha256`. That file was **not** refreshed: it still records
   `harness.py 2a19f1b8…` and `host_adapter.py 68741f8e…`, while
   `composition-manifest.json` records the new `d1369ce5…` / `8c3f8c3d…`. The
   two manifests are inconsistent and every `run-case`
   (`_r3_hash_check`) is refused. Result: `host_composition` 4/5 (test_d4
   FAIL), so the no-simulated composition is not green — contradicting the
   claim check5/check6.
2. **Observer suite does not complete.** `tests/test_observer_lifetime.py`
   passes `test_old_fails_parent_delayed_worker`, then **hangs** on
   `test_delayed_worker_commits_new` (killed at 170s and again in a combined
   run, rc124). The full gate therefore cannot complete and cannot be
   certified. (A longer combined run showed further failures before the
   timeout.)

## What did pass (bounded)

- `tests/test_amendment2_timer.py`: **3/3** — unit normalization once;
  duplicate create rejects via the faithful `RejectingRunner`; same-grant reuse
  with no second `systemd-run`; conflicting deadline → `E_TIMER_CONFLICT`;
  callback argv carries `--db` bound fixture and runs the exact parser with the
  foreign DB byte-size unchanged.
- `tests/test_r3_lifetimes.py`: **5/5** (160s) — exact-CLI delayed worker /
  verifier / expiry path (these exercise the harness directly, not the
  `run-case` R3 gate, which is why they pass while test_d4 fails).
- `tests/test_host_composition.py`: 4 passed, test_d4 failed.

## Coverage weaknesses (secondary)

- The callback test asserts the foreign DB is untouched but never asserts the
  intended bound DB changed; the "twice-fired" step asserts only rc ∈ {0,3},
  not the absence of a duplicate state effect (checklist item 4 wording not
  fully evidenced).
- Reopen with a **missing host timer** is not exercised through `run_fixture`:
  the guard calls `query_host` but ignores its result/exception
  (`except OwnedFault: pass`), and `create_host` reuses on kv presence alone,
  so "reconcile actual host timer facts rather than kv presence alone" is not
  demonstrated.

## Effect

Repair-2 is a **FAIL**. The timer-identity/callback code changes are correct in
substance, but `R3_REVISION.json` was not refreshed to the new
`harness.py`/`host_adapter.py` hashes, so the manifest-bound R3 gate rejects the
candidate and the required no-simulated composition (test_d4) fails; the
observer suite also hangs. Required fixes: update `R3_REVISION.json`
`copy_sha256` for both edited files (mechanically, no self-hash), resolve the
observer-suite hang, then re-run the full gate. No live effect occurred.
Returned to cairn/Tern; no automatic repair.
