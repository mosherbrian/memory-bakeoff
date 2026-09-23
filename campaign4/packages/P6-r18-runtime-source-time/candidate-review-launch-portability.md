# P6-r18-runtime-source-time — launch portability verification

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-launch-portabilityverify-1` (existing ≤10 m grant)
- **Brief:** `launch-portability-receipt.json` (`P6r18-launch-portability-1`),
  allocation `launch-portability-allocation-1.md`; prior INCOMPLETE
  `03b42b46…` preserved.
- **Claim:** `completion-claims/ex-p6r18-launch-portability-1.json`.
- **Scope:** read-only, no credentials/models/live effects.

## Verdict

**PASS.** The alias-portability defect is fixed (launch-only suite now **5 passed**
under this hostile deepseek-lane environment), the plan carries a
machine-executable per-lane environment schema (set map + unset array +
application order), the hostile-inheritance model policy holds (worker Muse,
verifier DeepSeek), manifests and claim bind with the two "dangling"-named
fixtures present, and the diff is tests/plan/metadata only with all production
frozen. Cleared for Tern.

## Alias-safe identity (PASS)

- `candidate/tests/test_r18_launch_closure.py` now asserts **realpath equality**
  (both `/home` and `/var/home` aliases), a same-basename **decoy is rejected**,
  and the argv tail/length plus selected model are checked.
- Reproduced independently under the ambient hostile env
  (`ACP_GO_MODEL=ACP_MODEL=opencode-go/deepseek-v4.1-flash` inherited):
  `PYTHONPATH=candidate/src pytest candidate/tests/test_r18_launch_closure.py`
  → **5 passed in 0.14 s** (was 1 failed / 3 passed before the fix).

## Executable-env schema (PASS)

`fixture-launch-plan.json` `launch_closure.exact_environment` is machine-executable:
`application_order` = copy ambient → unset named keys → apply literal set values.
- **go** lane: `unset [ACP_SOURCE_TEST_NOW, FIXTURE_LAUNCH_EXEC, PINNED_MODEL_OVERRIDE,
  ACP_GO_MODEL, ACP_MODEL]` then `set ACP_MODEL=muse-spark…, P6_SOURCE_MODE=runtime,
  ACP_AUTO_APPROVE=1, ACP_PROMISE_CHECK=1, ACP_STALL_SECS=1800` → worker Muse
  regardless of inherited overrides.
- **deepseek** lane: `unset [ACP_SOURCE_TEST_NOW, FIXTURE_LAUNCH_EXEC]` then
  `set ACP_GO_MODEL=deepseek-v4.1-flash, PINNED_MODEL_OVERRIDE=deepseek, …` →
  verifier DeepSeek.
- Test `test_both_lanes_resolve_local_runtime_and_settings` applies the plan argv
  **and** env together under hostile inherited values: local runtime identity,
  backend `muse-engine acp` exactly once, worker Muse / verifier DeepSeek, no
  fallback.

## Bound manifests / dangling entries (PASS)

- `candidate/manifest.json` **86**, `composition-manifest.json` **74** — no
  missing, no drift, no self-reference, no nested tree.
- The **two "dangling" entries** are `candidate/tests-retained/fixtures/
  snapshots/dangling.json` (one per manifest): both exist and hash-match — a
  fixture whose name contains "dangling", **not** actually dangling.
- New claim filed; 90+83+59 carried on unchanged executable bytes.

## Diff-only (PASS)

vs base `3964080`: changed only `candidate/changes.md`,
`candidate/composition-manifest.json`, `candidate/manifest.json`,
`candidate/fixture-launch-plan.json`, `candidate/tests/test_r18_launch_closure.py`;
added only the empty package markers `candidate/src/r3harness/__init__.py` and
`candidate/tests/__init__.py`. **No production wrapper/runtime/helper/consumer/core
byte changed** — confirms the claim's "production frozen".

## Carried / limits

Prior PASSes preserved; test-clock rejection, missing-local hard fail, no shared
fallback and plan/inputs binding are covered by the 5 launch tests. This check
certifies launch selection/portability only, not live runtime adoption; no
credentials read, no installs, no live/prep.

## Effect

One bounded verdict: **PASS** — alias-safe, executable-env schema verified,
manifests/claim bound, production frozen. Returned to Tern.
