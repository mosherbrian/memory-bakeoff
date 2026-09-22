# P6-r6-live-preparation — composition CLI repair review (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `composition-repair-receipt.json`, action
  `P6r6-composition-repair-1`, owner kiln, start `2026-09-22T04:30Z`,
  deadline `2026-09-22T04:50Z`
- **Authorization:** `allocation-extension-4.md`; new 20m worker + 15m verify;
  cumulative **465/350**; live 15 + fixture 15 HELD
- **Binding under review:** `src/stagec_entry.py`
  `211f495be11eaa44e1a3c3f9fc497b365aa7ab24bef099374d178bc9caf95a6a`
  (`211f495be11e`); new `tests/test_stagec_cli.py`
  `72c678ea231694b8900f1f704e8fbaf47f23a69f4322fd9c7765fb9c0ad850cb`;
  `stagec-plan.json` unchanged
  `a866091f298363480defccf4edcfaff4da6a5411c69c7714336b6c1e6b755576`;
  `tests/test_stagec_composition.py` unchanged `83b8c49e…`
- **Predecessor:** `candidate-review-composition.md` (`9c060279…`) FAIL preserved;
  `composition-cli-failure.json`; original bytes pinned
  `2b167dd88fe5…` (`dc51558a`)
- **Contract:** `f2b7df48…` @ `e32c0dc`; accepted binding
  `b3eaf3cc8d48…` (read-only, unmodified)

## Verdict

**PASS** — the `__main__` guard restores the documented entrypoint, exit status
propagates, and every exact CLI command now produces its output artifact with
correct stdout/exit. The previous defect is fixed without module behavior
changing; the old failure is reproduced on the pinned original bytes.

## Old failure reproduced (pinned original bytes)

Extracted `dc51558a:…/src/stagec_entry.py` → sha256
`2b167dd88fe5…` (matches the pin). `python3 orig_stagec.py gate --help` → **rc0,
empty stdout/stderr** — the original no-op, reproduced. New script:
`gate --help` rc0 with output, no-args rc2, `derive-config` missing-args rc2.

## Independent exact-CLI checks (subprocess, injected overlay, no live effects)

All run via `/tmp/opencode/cli_drive.py` against the exact script argv:
- **derive-config:** rc0, reads signed plan+binding, **writes
  `execution-config.json`**, prints
  `{"config": …, "parent_binding_sha256": "b3eaf3cc8d48…"}`.
- **gate:** rc0 `{"gate":"PASS","worker":"085360c2-1790050499","verifier":"caac0ba3-1790050500"}`.
- **run-case positive-handoff:** rc0, receipt written, stdout
  `{"case":"positive-handoff","sends":{"worker":1,"verifier":1},"timecheck":"accept"}`.
- **run-case failed-verification:** rc0, `accept-open` (never COMPLETE).
- **run-case restart-quiet:** rc0, `accept`, rerun recognized duplicate with no
  fresh sends.
- **timecheck positive:** rc0 `verdict:accept` (10s detect / 20s recover /
  30s total). **timecheck late:** **rc3**
  `["late detection for WA: 50.0s"]`, `verdict:reject` — never prints/returns
  acceptance.
- **rollback:** rc0, `witness_archived:true`, `archive/rollback-report.json`
  exists (archive before cleanup).
- **Negatives before any send:** unsigned signer → rc3; binding drift
  (`session_id` tampered) → rc3 `E_BINDING_CHANGED`; missing args → rc2.
- **Aliases:** `derive-config --binding` and `gate --config` (documented argv)
  both parsed and executed; the CLI test additionally exercises the `--config`
  alias on real paths.

Output artifacts **and** stdout/exit status asserted, so a silent rc0 cannot
pass. `PYTHONPATH=src python3 -m pytest tests/ -q` → **34 passed** (28 prior +
6 new CLI tests), but the CLI behavior above was verified by direct
subprocess, not pytest alone.

## No live side effects

`agent-deck list --json` = 7 before and after (four main seats + stopped
predecessor `0e734b30` + p3 fixtures), statuses unchanged. No fixture wake,
launch, restart, service mutation or core edit. Accepted binding
`b3eaf3cc8d48…` bytes unchanged; the p3 sockets/IDs were used only as config
identity inputs, never contacted. Stage C remains HELD. Cairn's `04:39Z`
exact-ID cleanup of `085360c2` / `caac0ba3` still applies and was not
anticipated or raced by this check.

## Non-blocking observations

- The prior `derive_config` tautological socket-dir check and the unused
  `allowed` set in `timecheck` remain; both were flagged before and have no
  effect on the repaired CLI path.
- Module-level PASS still carries no claim that the rest of the live plan is
  accepted; a Stage C signature over the plan + derived config is still
  required before any send.

## Effect

Verdict **PASS** bound to `src/stagec_entry.py`
`211f495be11eaa44e1a3c3f9fc497b365aa7ab24bef099374d178bc9caf95a6a`, tests
`72c678ea…`, plan `a866091f…`, under contract `f2b7df48…` @ `e32c0dc` and
binding `b3eaf3cc8d48…`. The composition FAIL (`9c060279…`) and original no-op
evidence are preserved. Returned to cairn and Tern.
