# P6-r6-live-preparation — candidate review, composition (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `composition-receipt.json`, action `P6r6-composition-1`,
  owner kiln, start `2026-09-22T04:19Z`, deadline `2026-09-22T04:49Z`
- **Authorization:** `allocation-extension-3.md`; new 30m worker + 20m verify;
  cumulative **445/335**; live 15 + fixture 15 HELD
- **Binding under review:** `src/stagec_entry.py`
  `2b167dd88fe5e8835142521d912c19521fae3c51a742d3a28e0f55a3db55b586`
  (`2b167dd88fe5`); plan `stagec-plan.json`
  `a866091f298363480defccf4edcfaff4da6a5411c69c7714336b6c1e6b755576`;
  tests `tests/test_stagec_composition.py`
  `83b8c49eed08126b042195b8351caf92c53e2d6aa316825b7fb850f2972acab8`;
  `binding-acceptance.json`
  `630139f0cf2fc4d1f04c9ed08ec5d1052ea9bb526b1f297053c48d0746653241`
- **Accepted binding (read-only, unmodified):**
  `live-preparation-3/launch-manifest-reconciled.json`
  `b3eaf3cc8d48…`; contract `f2b7df48…` @ `e32c0dc`

## Verdict

**FAIL** — the composition's module-level logic is sound, but the **documented
exact entrypoint is not runnable**: `src/stagec_entry.py` defines `main()` and
never calls it. Running any exact command from `stagec-plan.json` exits `0`
without output and without effect. This is the "fake executor" extension-3
explicitly forbids, and it is the one thing the connected Stage C path exists
to provide.

## Blocking defect (bounded)

1. **`src/stagec_entry.py` (`2b167dd88fe5…`) has no `__main__` guard.**
   `tail`/grep show the file ends at the `rollback` branch of `main()` with no
   `if __name__ == "__main__": raise SystemExit(main())` (and no
   `__main__.py`). Consequently:
   - `python3 …/src/stagec_entry.py derive-config --plan … --binding … --signatures … --out …`
     → rc0, no stdout, **no `execution-config.json` written**.
   - `python3 …/src/stagec_entry.py gate --help` → rc0, no output.
   - `python3 …/src/stagec_entry.py` → rc0, no output.
   - `PYTHONPATH=src python3 -m stagec_entry` → no output (same missing guard).
   All seven exact commands recorded in `stagec-plan.json`
   (`derive-config`, `gate`, `run-case`, `timecheck`, `rollback`) are dead.
2. **The regression suite masks the defect.** `tests/test_stagec_composition.py`
   imports the module (`import stagec_entry as se`) and calls
   `se.derive_config` / `se.run_case` directly; it never invokes the script or
   `se.main([...])`. `pytest` therefore reports 28 passed while the advertised
   CLI is a no-op. The tests do not exercise the composition path the plan
   commits to.

**Bounded fix:** add the standard `if __name__ == "__main__": main()` guard
(and one CLI-level test that shells out to the exact documented argv).
Expected: `derive-config` writes the config and prints
`{"config": …, "parent_binding_sha256": …}`; `run-case`/`timecheck`/`rollback`
execute. No other change.

## What is sound (so the defect is precisely bounded)

- **Derive-config logic (module):** consumes the Tern-signed plan + accepted
  live binding, rejects changed plan/binding hashes
  (`E_PLAN_CHANGED`/`E_BINDING_CHANGED`), non-live source (`E_NOT_LIVE`),
  placeholder/`MANIFEST_STREAM`/`ITEM`/`ACT`/`EX` tokens (`E_SYNTHETIC`),
  stream-not-under-producer-root and implausible socket dir (`E_MISMATCH`).
  The accepted manifest is read only; a separately derived config records
  `parent_binding_sha256` + `resign_required`.
- **Gate:** re-verifies signature and that the accepted binding has not drifted
  (session_id/stream_path/socket), immediately before any send; `run-case`
  calls it unconditionally (`g = gate(...) # mandatory, no bypass`).
- **Run-case (module, injected overlay):** I executed all three enumerated
  cases end-to-end through the candidate's own live path against PATH-shimmed
  OS effects with a fresh producer seeing only its dispatched text/named
  files. Positive → `sends {worker:1, verifier:1}`, timecheck `accept`;
  failed-verification → `accept-open` (never COMPLETE); restart-quiet →
  `duplicate-end-ignored` with no fresh sends. Items are resolved from observed
  stream `end` records ∩ onset sidecars, never operator-guessed. `rollback`
  archives witness rows + config before candidate cleanup.
- **Timing gate (`timecheck`, module):** positive row (10s detect / 20s recover
  / 30s total) → `accept`; and it rejects late-detect, late-recovery-despite-
  fast-detect, late-total, negative interval, unknown onset/source, missing ack,
  queued-only wake, unknown uncertainty, all-failure corpus, wrong action and
  missing success; failed-verification stays `accept-open`. Worker execution
  duration is reported separately, never as stall latency. Detection/recovery/
  total **30/60/90** with suspicion **180/60/240** are enforced from
  `config.timing_bounds`.
- **No live side effects:** `agent-deck list --json` was 7 before and after
  (four main seats + stopped predecessor `0e734b30` + p3 fixtures unchanged);
  no fixture wake/launch/restart; accepted binding bytes
  `b3eaf3cc8d48…` unchanged.

## Regression run (this review)

`PYTHONPATH=src python3 -m pytest tests/ -q` → **28 passed**. This pass count is
**not** acceptance of the connected entrypoint (see defect 2). Independently,
CLI invocations of the exact planned commands produced no effect (defect 1),
while module-level `se.run_case`/`se.timecheck` behave as above.

## Non-blocking observations

- `derive_config`'s socket check (`os.path.dirname(side["socket"]) ==
  os.path.dirname(side["socket"])`) is tautological; only the later
  sock-dir/producer-root distinction has force. Harmless but should be a real
  inequality against the expected sock dir.
- `timecheck` builds an `allowed` case set but does not use it; case membership
  is enforced in `run_case`, not `timecheck`.

## Effect

Verdict **FAIL** bound to `src/stagec_entry.py`
`2b167dd88fe5e8835142521d912c19521fae3c51a742d3a28e0f55a3db55b586`, plan
`a866091f…`, tests `83b8c49e…`, under contract `f2b7df48…` @ `e32c0dc` and
binding `b3eaf3cc8d48…`. No fixture task, wake, restart, launch, cleanup, core
edit or Stage C signature occurred. Accepted binding/manifest preserved
unmodified. Returned to cairn (and Tern) for a bounded repair.
