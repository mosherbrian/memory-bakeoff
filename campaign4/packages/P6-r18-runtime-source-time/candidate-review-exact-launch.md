# P6-r18-runtime-source-time — exact-launch verification

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-exact-launchverify-1` (existing ≤10 m grant)
- **Brief:** `exact-launch-receipt.json` (`P6r18-exact-launch-1`), allocation
  `exact-launch-allocation-1.md`, findings `director-exact-launch-findings.json`.
- **Claim:** `completion-claims/ex-p6r18-exact-launch-1.json`.
- **Scope:** read-only, no credentials/models/live effects.

## Verdict

**INCOMPLETE (bounded).** The duplicated-backend argv and hostile-inheritance
model selection are **fixed and independently reproduced**: the plan argv is bare,
the wrapper adds `muse-engine acp` exactly once, and the worker stays Muse under
hostile inherited `ACP_GO_MODEL`/`ACP_MODEL`. Manifests and the claim bind. But
the launch-only test suite is **not portably green**: 1 of 4 fails on a
`/home` vs `/var/home` path-alias assertion, so the claim's "4 launch tests
green" is not reproducible across environments.

## Dedup / exact argv (PASS)

- Plan `launch_closure.exact_argv` now bare (`candidate/runtime/launch-acp-go`,
  `…-deepseek`); wrapper owns the backend triplet once.
- Independent capture through the shipped `FIXTURE_LAUNCH_EXEC` branch with
  **hostile inherited** `ACP_GO_MODEL=ACP_MODEL=opencode-go/deepseek-v4.1-flash`,
  no opt-in: go lane → `argv = <candidate-local acp-worker> muse-engine acp`
  (exactly once) and `ACP_MODEL = opencode-go/muse-spark-1.3-contributor`.
- DeepSeek lane with the plan's documented env (`PINNED_MODEL_OVERRIDE=deepseek`
  + `ACP_GO_MODEL=deepseek-v4.1-flash`): `ACP_MODEL = opencode-go/deepseek-v4.1-flash`,
  same single triplet. So worker=Muse / verifier=DeepSeek hold regardless of
  inherited values, and the old duplication is gone.
- Per-lane `exact_environment` maps are machine-executable; test-clock rejection
  and missing-local hard fail retained (wrappers exit 1).

## Manifests / dangling entries (PASS)

- `candidate/manifest.json` **86** and `composition-manifest.json` **74** entries:
  no missing, no drift, no self-reference, no nested tree.
- The **two "dangling" entries** are `candidate/tests-retained/fixtures/
  snapshots/dangling.json` (one per manifest); both files **exist and hash-match**
  — they are retained fixtures whose name contains "dangling", not actually
  dangling.
- New claim filed; 90+83+59 carried on unchanged executable bytes
  (launch-only diff).

## Launch-test portability defect (blocker for "green" claim)

`candidate/tests/test_r18_launch_closure.py::test_both_lanes_resolve_local_runtime_
and_settings` compares the captured runtime path against `os.path.realpath(LOCAL_RT)`
(`/var/home/bmosher/…`) while the wrapper emits its `cd "$(dirname …)" && pwd`
path (`/home/bmosher/…`). In this environment that is **1 failed, 3 passed**
(both with and without `ACP_GO_MODEL` unset after the wrapper fix); the earlier
`ACP_GO_MODEL` failure is gone, but the alias mismatch remains. The substantive
closure is correct; the test assertion is not path-portable. Smallest correction:
compare `os.path.realpath(got["argv"][0])` to `os.path.realpath(LOCAL_RT)`, or
have the wrapper emit the resolved realpath, then rerun the launch-only suite.

## Carried / limits

Prior PASSes preserved; runtime/helper/consumer/core and retained tests frozen;
no credentials read, no installs, no live/prep. This check certifies launch
selection only, not live runtime adoption.

## Effect

One bounded verdict: **INCOMPLETE (bounded)** — dedup and hostile-inheritance
model pinning verified, manifests bound; the launch-only test is not portably
green (path-alias assertion). Returned to Tern.
