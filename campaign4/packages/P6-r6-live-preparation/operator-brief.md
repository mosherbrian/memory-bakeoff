# P6-r6 operator brief (bounded; preparation release only)

**Scope:** run preparation tool → record manifest hashes → gate dry-run only.
No live session is created under the candidate grant. Actual `prepare_live.py`
live execution waits for Tern's separately signed ≤10m preparation release;
`prewake_gate.py` live invocation and any task wake wait for Tern's exact
plan+manifest signature. If any step below cannot run as written, stop and
return the bounded blocker to Tern — do not improvise.

## Prereqs (read-only, verified at admission)

- Lanes exist + executable: `/home/bmosher/.config/agent-deck/acp-go`
  (worker), `/home/bmosher/.config/agent-deck/acp-go-deepseek` (verifier).
- `AGENTDECK_PROFILE=campaign4 agent-deck list` shows only the four main
  seats; `p6-fixture-worker` / `p6-fixture-verifier` names are free.
- `agent-deck launch` without `-message` starts idle; `-idle-timeout`
  bounds the runtimes (plan uses 25m).

## Dry-run (candidate grant, no live effect, ~5m)

1. `SRC=/home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation/src`
2. `python3 $SRC/prepare_live.py --dry-run --inject-list <fixture> --inject-sock-dir <dir> --inject-stream-root <dir> --manifest-out /tmp/p6r6-dry/manifest.json`
3. `python3 $SRC/prewake_gate.py --manifest /tmp/p6r6-dry/manifest.json --plan <plan> --signatures <sig> [--inject-*]` — must REJECT dry-run manifests with E_NOT_LIVE (proves shims can't pass the live path).
4. `python3 $SRC/cleanup_live.py --manifest <live-manifest> --archive-dir /tmp/p6r6-dry/archive --dry-run` — prints owned-ID argv only.
5. `python3 $SRC/witness_timing.py observe ...` against a fixture stream + `check --rows ...` — INCOMPLETE when onset missing.

## Live preparation (HELD — needs signed release, ≤10m)

1. `AGENTDECK_PROFILE=campaign4 python3 $SRC/prepare_live.py --plan <plan> --manifest /tmp/p6r6/launch-manifest.json`
2. Record `sha256sum` of plan + manifest; hand both hashes to Tern for the
   `signatures.json` receipt (`{signer:"tern", plan_sha256, manifest_sha256}`).
3. Abort closed on: name collision, lane failure, profile/role mismatch,
   missing or non-socket seat socket, stream-root mismatch. Never adopt,
   repurpose, restart, message, or stop any existing seat.

## NOT authorized

Live fixture sends, Stage C, ledger writes, wrapper edits, Signal/pause
tests, shadow runs, retirement, research runs, or any seat creation before
the signed preparation release. Candidate PASS changes none of this.
