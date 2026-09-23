# P6-r18 — launch-closure admission review

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-launch-admission-1` (separate ≤10 m admission)
- **Brief:** `launch-closure-receipt.json` + `launch-closure-allocation-1.md` +
  `director-launch-closure-findings.json`; filing PASS `6dbd851f…` preserved.
- **Scope:** read-only gap-vs-existing-closure check. No edits.

## Verdict

**ACCEPTED (bounded) — the gap is real; no existing runnable closure.** The
current deliverable ships only `candidate/fixture-launch-plan.json`, which
*documents* wrappers but provides **no wrappers and no executable launch argv**;
`inputs/acp-go` ends by executing the **shared** runtime. The required
fixture-only lane launch closure is genuinely absent, and the narrow correction
fits the existing preparation tooling without scope expansion. Checklist pinned
below; conditional kiln release applies only to this unchanged correction.

## Gap confirmation

- `candidate/fixture-launch-plan.json` `explicit_opt_in.destination = "fixture lane
  launch wrappers created under this plan"` — but `find candidate` shows no
  wrapper file (`*launch*`/`*wrapper*`/`acp-go*`), only the plan JSON.
- `inputs/acp-go` last line: `exec "$HOME/.config/agent-deck/acp-worker"
  muse-engine acp "$@"` → resolves the **shared** runtime, explicitly forbidden.
- `director-launch-closure-findings.json` records the same
  (`WITHHOLD_ACCEPTANCE`, 83 entries rehashed) with source-time/filing PASS
  preserved. No alternative runnable closure exists in the package.

## No scope incompatibility

`P6-r6-live-preparation/src/prepare_live.py` accepts `--worker-lane` /
`--verifier-lane` (defaults `WORKER_LANE`/`VERIFIER_LANE`), so a future fresh
isolated preparation can be pointed at candidate-local wrappers **without**
changing the preparation tool. The mechanism is expressible within the
authorized scope; no tool incompatibility to return.

## Pinned checklist (for the bounded correction)

- Deliver concrete **fixture-only worker/verifier lane wrappers** (or an
  equivalently explicit executable launch mechanism) inside this package.
  Preserve the pinned model/provider lane configuration (`inputs/acp-go`,
  `inputs/acp-go-deepseek` byte-exact semantics) and target the **candidate-local**
  runtime (`candidate/runtime/acp-worker`) and helper (`candidate/runtime/
  srcemit.py`) — never the shared `~/.config/agent-deck` runtime.
- The plan must give **exact argv and environment and paths** sufficient for a
  future fresh isolated preparation; no placeholder instruction to create an
  unspecified wrapper. Explicit runtime source mode; **live rejects inherited test
  clock injection** (`ACP_SOURCE_TEST_NOW` must not leak into a live path).
- Verify launch selection **without models/credentials** via an injected final
  executor or argument capture on the **same shipped branch**, plus syntax checks.
  Show both lanes resolve the local runtime, preserve model settings, and cannot
  silently fall back to the shared runtime.
- **No** credentials, installs, task sends, real-seat launches, shared-file
  changes, or edits to accepted core/consumer/runtime behaviour. Local generated
  launch artifacts, plan/docs/tests/manifests only.
- Regenerate **acyclic manifests** and a **NEW completion claim**; freeze all
  existing production and tests except new launch-only artifacts/tests; bind the
  comparison to the reviewed correction. **Carry 90 + 83 + 59 only on unchanged
  executable bytes**; do not rerun the whole gate for launch-only changes.
- Independent verification (`candidate-review-launch-closure.md`) checks launch
  commands, path and environment negatives, every manifest hash, the claim, and
  no drift; any new defect returns Tern.

## Bounds / sequence

Corvid admission ≤10 m (this) → conditional ONE kiln ≤20 m → ONE corvid ≤15 m
verification on its own clock. Ceilings `1320worker/1100verifier` → `1340/1115`;
prior allocations spent, no automatic further repair. No live/preparation release.
Cairn owns host-read deadlines/one-shot timers with no overlap; every dispatch/
receipt carries the exact executable wake command (profile `campaign4`, validated
destination id, absolute claim/verdict path). Future actual preparation still
requires fresh binding + Tern signature.

## Effect

Admission **ACCEPTED (bounded)**: gap confirmed, no existing closure, scope
expressible. Returned to Tern for the conditional kiln correction.
