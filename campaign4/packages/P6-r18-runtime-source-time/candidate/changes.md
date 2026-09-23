# P6-r18 changes — explicit runtime source time for real turn ends

Parent: R16 candidate source `c8e99cf`, outer manifest `3862a0a2`
(verified on copy). R17 evidence: onset dir empty, end records
`{"t":"end","item":…}` with no timestamp (reproduced); pinned runtime
`emit()` writes no time and swallows failures (byte-verified).

## New: local runtime copy + stdlib hook (no shared change)
- `candidate/runtime/acp-worker`: local copy of pinned `inputs/acp-worker`
  (`6871ceb1…`); diff confined to `emit()` + one `_runtime_source_fields`
  delegate (38 lines). Shared `~/.config/agent-deck` byte-untouched,
  never executed by tests (asserted).
- `candidate/runtime/srcemit.py` (stdlib only, the shipped hook):
  `source_fields()` stamps host UTC at the actual append with bound
  session/item, provenance `runtime-end-append`, 1s uncertainty and
  wall-vs-monotonic discontinuity handling; `emit_end()` appends the
  versioned-fields end record in one write (+fsync). Fixture-only clock
  injection via `ACP_SOURCE_TEST_NOW`/explicit `now` (records marked
  `test`; never set live). Write failure → stderr + `SourceWriteError`;
  turn continues (telemetry never kills work); downstream sees absence.
- `candidate/runtime/interface.md`: the one exact format + failure
  semantics + consumer binding + task contracts.
- `candidate/fixture-launch-plan.json`: local-only opt-in plan (pinned
  hashes, preserved lanes, `adopted:false`); task texts state the runtime
  records source time.

## Consumer: harness.py + case_entry.py (core/adapter frozen)
- harness `_source_receipt()`: parses the receipt from observed end bytes
  (watcher `extra` included); missing/partial/version-mismatch →
  `(None, reason)`, never fabricated. Persisted per action/execution to
  kv at observation (`_persist_source_receipt`); reopen re-reads bytes.
- Latency rows carry `src_*` (mode/provenance/at/uncertainty/clock/
  status/session, `src_known`); `setup_manifest` declares `source_mode`
  (default `sidecar`, legacy-identical).
- `check_latency(..., source_mode)`: runtime mode gates event instant
  `src_at→detected` (clocks stay distinct); CLI passes manifest mode.
- case_entry runtime mode: `_check_causal(..., source_mode="runtime",
  source_by_action=kv receipts)` joins each action's receipt to its own
  detection via the R16 item→action binding; session/item must match the
  bound current identity; `_detect_source_conflict` rejects kv-vs-row
  divergence. Missing/discontinuous source → INCOMPLETE; sidecars
  ignored (no silent fallback); legacy sourceless records unmeasurable.

## Evidence
- `test_r18_source_time.py` (12): R17 repro; pinned emit schema;
  local-copy confinement; emit format + injected clock; hook subprocess
  producer→consumer on same bytes; discontinuity flagged; write failure;
  runtime join + full negative matrix (missing/empty/wrong/previous/
  malformed/nonfinite/discontinuous/conflict/late/arm-after);
  delayed-observer + restart stability; fixture-plan local-only hashes;
  exact-CLI run-fixture success + verifier-rejection with matched source
  rows and gates-hold (rejection in denominator).
- Full 78 + P5 83 + P3 59 gate on actual new modules (see claim).

## Out of scope
Quiet-rest window correction (still owed); fleet adoption (fresh
prep/review/signature); live timing certification. No backfill: legacy
records stay unmeasurable.

## Manifest repair-1 (packaging only; no production/test/plan/runtime/interface byte edits)
- Removed stale nested duplicate `candidate/candidate/` (79 entries;
  preserved in base commit 05a4568) and bytecode/cache debris.
- Re-emitted composition + outer manifests acyclically: unique canonical
  paths, no escaping/symlink aliases, no self-cycle, no omitted executed
  helper/wrapper. Executable closure smoke-checked (case_entry, harness,
  srcemit, driver/ingress/store/lifecycle import from canonical tree).

## Launch closure-1 (fixture-only lane wrappers; no behavior change)
- New `candidate/runtime/launch-acp-go` + `launch-acp-go-deepseek`:
  same lane semantics as pinned `inputs/acp-go` (+model env,
  approval/stall/promise settings, credential gate for real launches),
  retargeted at the candidate-local runtime/helper with absolute paths.
  No shared-runtime fallback on any branch (missing local = hard fail).
  `P6_SOURCE_MODE=runtime` exported; `ACP_SOURCE_TEST_NOW` present →
  exit 1 (test clocks never leak into launch paths). Fixture-only
  capture hook `FIXTURE_LAUNCH_EXEC` verifies selection on the shipped
  branch without models/credentials.
- `fixture-launch-plan.json`: exact argv/environment/paths + wrapper
  hashes (launch_closure block). All existing production/tests frozen;
  90+83+59 carried on unchanged executable bytes.

## Exact-launch-1 (dedup backend argv at correct layer; wrappers+plan only)
- Root cause: wrappers own the backend triplet (`muse-engine acp`)
  exactly once, but the plan recorded it in the lane argv too, so the
  deepseek chain produced it twice (reproduced:
  `... acp-worker muse-engine acp muse-engine acp`). Fixed at the plan
  layer: exact per-lane argv is the bare wrapper path (wrappers add the
  backend exactly once); verified executable as recorded.
- Per-lane model pinning regardless of inherited env: go lane resolves
  Muse unless the deepseek lane's explicit opt-in with the exact pinned
  DeepSeek value is present; hostile inherited ACP_GO_MODEL/ACP_MODEL
  cannot reselect. Deepseek wrapper overwrites both explicitly.
- Plan environment rewritten as machine-executable per-lane KEY=VALUE
  maps (no prose masquerading as values). Negative tests retained
  (missing-local hard fail, test-clock rejection untouched).
