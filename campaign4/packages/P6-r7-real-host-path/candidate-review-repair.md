# P6-r7-real-host-path — candidate review, repair-1 (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Receipt:** `repair-1-receipt.json`, action `P6r7-repair-1`, owner kiln,
  start `2026-09-22T04:52Z`, deadline `2026-09-22T05:12Z`
- **Authorization:** `allocation-extension-1.md`; new 20m worker + 15m verify;
  cumulative **525/390**; live 10 + fixture 15 HELD
- **Predecessor (preserved):** `candidate-review.md` FAIL + pinned original
  bytes at `5643f2dd…` (`src/stagec_host.py` `4c34b65c019e…`)
- **Binding under review:** `src/stagec_host.py`
  `46681fbb82cbfe2b411f8f58d336532a074a1da8f6ca277b2b727e418e0940f1`
  (`46681fbb82cb`); `tests/test_repair1_hashes.py`
  `325c31502fd5981ea5c2b6182a6b1b7351c89cc54ac82f5b1017c85771c70099`;
  `tests/test_stagec_host.py` unchanged `3a956425…`;
  `stagec-plan.json` unchanged `cc5993ab…`; `src/fault_onset.py` unchanged
  `9af9c25c…`
- **Checklist:** `ce7401f1…`; contract `515deb16…` @ `fd497e7`; pinned candidate
  `harness.py` `cd84e8dd4db623586d960233ffc8f674c0cbfb801b4fffb5bfa9fb6289109142`

## Verdict

**PASS** — the fail-open default is removed. The gate now rejects missing/null/
empty/wrong required signature hashes before any effect, the fully bound
signature passes, and the original omission-PASS is reproduced on the pinned
original bytes. H1/H3/H4 results are retained.

## Repair conformance

- **Fail-closed candidate hash:** `gate()` now does
  `got = sig.get("candidate_" + name.replace(".py","") + "_sha256")` then
  `if not got or got != want: raise E_TOOL_CHANGED` (`stagec_host.py:210–215`).
  No expected-value default remains. A new import-time `E_CORE_DRIFT` check also
  hashes the pinned candidate `harness.py` against `_CANDIDATE_HASHES`.
- **No unrelated change:** diff scope is the guard/default removal plus the core
  hash check; H1 branch, H2 registry/socket checks, H3 join and H4 cases are
  otherwise unchanged (same hashes for plan/tests/fault_onset).

## Independent exact-CLI checks (subprocess; test env, injected registry)

Using the candidate's test env with a fully bound signature:
- **Positive:** `gate` rc0 `{"gate":"PASS"}`.
- **Omit `candidate_harness_sha256`:** rc3 `E_TOOL_CHANGED`.
- **Omit `stagec_entry_sha256`:** rc3 `E_TOOL_CHANGED`. **Omit `plan_sha256`:**
  rc3 `E_PLAN_CHANGED`. **Omit `config_sha256`:** rc3 `E_CONFIG_CHANGED`.
- **`candidate_harness_sha256` = null / "" / wrong:** rc3 `E_TOOL_CHANGED` each.
- **Original pinned bytes** (`5643f2d`, `4c34b65c…`, with the signature binding
  that old entrypoint and omitting the candidate hash): **rc0 `gate PASS`** —
  the old fail-open reproduced; the repaired script under the identical setup
  rejects. (Omitting the hash while the signature binds the *new* entrypoint
  fails earlier on `E_TOOL_CHANGED`, which is why the old-bytes signature must
  bind the old entrypoint to expose the original hole.)
- **Zero effect:** negatives occurred before any send; the test's filesystem
  snapshot is unchanged and no seat/stream was touched.

`binding_sha256` omission still yields `gate PASS` — **by design, not a hole**:
`gate` independently re-hashes the live binding file and compares it to
`config.parent_binding_sha256`, then re-checks each side's
session/stream/socket and the live registry, so the accepted binding cannot be
substituted. `test_repair1_hashes.py:REQUIRED_HASHES` correctly lists
`plan_sha256`, `config_sha256`, `stagec_entry_sha256`, `candidate_harness_sha256`
and excludes `binding_sha256` for this reason.

## Retained H1/H3/H4

`PYTHONPATH=src python3 -m pytest tests/ -q` → **11 passed** (8 prior host tests
+ 3 repair tests), including the no-overlay host positive (1 worker + 1 verifier
send, `accept`, `overlay:false`), lost-completion/failed-verification
`accept-open`, queued-restart and quiet-rest, stopped/lane/socket gate
negatives, wrong-execution and omitted-ack timecheck negatives, and
archive-first rollback. The repaired CLI is exercised by subprocess, not
direct-import alone.

## No live side effects

`agent-deck list --json` = 7 before and after (four main seats + stopped
`0e734b30`/p3 fixtures), statuses unchanged. All checks used private tmp sockets
and an injected registry file; no real seat task, launch/restart/timer/service,
shared-wrapper or accepted-core edit, research, shadow or retirement. Stopped
fixture IDs remain historical evidence only; no revival. Candidate PASS returns
Tern; no live release.

## Non-blocking observations

- `binding_sha256` is intentionally not a gate-required hash (enforced via
  `config.parent_binding_sha256` + live re-hash). If a future contract wants the
  signature itself to carry it, add it to the required set explicitly.
- `_CANDIDATE_HASHES` / `P6R6_ENTRY_SHA256` remain constants; any future pinned
  candidate change must update both and the release signature.

## Effect

Verdict **PASS** bound to `src/stagec_host.py`
`46681fbb82cbfe2b411f8f58d336532a074a1da8f6ca277b2b727e418e0940f1`, tests
`325c3150…`, plan `cc5993ab…`, under contract `515deb16…` @ `fd497e7` and
checklist `ce7401f1…`. `candidate-review.md` preserved. Returned to cairn and
Tern.
