# P6-r18-runtime-source-time — launch-closure verification

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-launchverify-1` (existing ≤15 m grant)
- **Brief:** `launch-closure-receipt.json` (kiln `P6r18-launch-closure-1`);
  admission `launch-closure-admission-review.md` (`b8da58d6…`).
- **Claim:** `completion-claims/ex-p6r18-launch-closure-1.json`.
- **Scope:** read-only. No source edit, no live/credentials.

## Verdict

**PASS (bounded).** The required fixture-only lane launch closure is now
delivered: two wrappers target the **candidate-local** runtime/helper with **no
shared-runtime fallback**, preserve the pinned lane model/provider settings,
reject inherited test-clock injection, and expose a fixture-only argument-capture
branch on the same shipped code. Manifests and claim bind correctly, core bytes
are unchanged, and the 4 launch tests pass (in a clean launch environment). One
bounded launch-environment hazard is reported for disposition.

## Wrappers / executable closure (PASS)

- `candidate/runtime/launch-acp-go` (`d0f5b56d…`) and
  `candidate/runtime/launch-acp-go-deepseek` (`e9f085d2…`), both executable.
- Resolve `HERE/acp-worker` + `HERE/srcemit.py` via the wrapper dir; **no
  `~/.config/agent-deck` path and no shared fallback** — missing local runtime or
  helper exits non-zero. No shared-runtime string appears in either wrapper.
- `ACP_SOURCE_TEST_NOW` set → **exit 1** (live rejects leaked test clock);
  `P6_SOURCE_MODE=runtime`; pinned lane config preserved (`OPENCODE_API_KEY`
  unset, `ACP_MODEL`/`ACP_GO_MODEL`, `ACP_AUTO_APPROVE`, `ACP_STALL_SECS`,
  `ACP_PROMISE_CHECK`); real credential gate retained but unexercised.
- Independent capture on the shipped branch: `FIXTURE_LAUNCH_EXEC=/bin/echo
  candidate/runtime/launch-acp-go --session s1` → prints the absolute
  **candidate-local** runtime with `muse-engine acp --session s1`.

## Plan / manifests / claim (PASS)

- `fixture-launch-plan.json` `launch_closure` block: exact argv (both lanes),
  exact environment, local `runtime`/`helper` paths, wrapper hashes, and
  `scope: future prep needs fresh binding + Tern signature`. Wrapper hashes match
  the files (`d0f5b56d`, `e9f085d2`).
- `candidate/manifest.json` **86** entries, `composition-manifest.json` **74** —
  no missing, no drift, no self-reference, no nested `candidate/candidate/`.
  Wrapper + plan + new test entries present with matching hashes.
- New claim filed; carried 90+83+59 on unchanged executable bytes (launch-only
  additions).

## Launch tests

`candidate/tests/test_r18_launch_closure.py`: **4 passed** in a clean launch
environment (no inherited `ACP_GO_MODEL`/`ACP_MODEL`/`ACP_SOURCE_TEST_NOW`).
Covers local-runtime resolution + settings, no shared-path/leak, missing-local
hard fail, test-clock rejection, syntax/exec bits, plan hash binding, inputs
untouched.

## Bounded launch-environment hazard

The go wrapper sets `ACP_MODEL="${ACP_GO_MODEL:-opencode-go/muse-spark-1.3-contributor}"`.
Under an environment that already exports `ACP_GO_MODEL` (e.g. this deepseek
lane, `ACP_GO_MODEL=opencode-go/deepseek-v4.1-flash`), the **go worker lane
silently selects the deepseek model**, and
`test_both_lanes_resolve_local_runtime_and_settings` fails (I reproduced: 1
failed under the agent env, 4 passed under `env -u ACP_GO_MODEL`). This is not a
shared-runtime fallback (that remains a hard fail) but a model-selection
hazard: a future fresh preparation must **explicitly unset/pin `ACP_GO_MODEL`**
for the go lane, or the wrapper should not inherit an ambient override. Report
for Tern disposition (explicit unset in the launch env, or fail-closed on an
unexpected `ACP_GO_MODEL` for the go lane).

## Carried / limits

Prior source-time/filing PASS preserved; R17/R15 remain non-live. This check
certifies only launch selection/closure, not live timing or runtime adoption.
No credentials read, no installs, no shared-file or accepted-core edits.

## Effect

One bounded verdict: **PASS (bounded)** — fixture-only local launch closure
delivered, manifests/claim bound, core frozen; one `ACP_GO_MODEL` inheritance
hazard noted for disposition. Returned to Tern.
