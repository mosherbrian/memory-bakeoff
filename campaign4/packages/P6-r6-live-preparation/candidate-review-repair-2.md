# P6-r6-live-preparation — candidate review, repair-2 (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Repair receipt:** `repair-2-receipt.json`, action `P6r6-repair-2`,
  owner kiln, start `2026-09-22T04:10Z`, deadline `2026-09-22T04:30Z`
- **Authorization:** `allocation-extension-2.md`; new 20m worker + 15m verify;
  cumulative **415/315**; live 15 + fixture 15 HELD; no live launches
- **Predecessor evidence (preserved):** `P6r6-prepare-2` FAIL —
  `live-preparation-2/director-reconciliation.json`, `stop-receipt.json`,
  `stdout.txt`, `launch-manifest.json.partial`; `P6r6-prepare-1` FAIL and
  `candidate-review-repair.md` (`301c7d76…`) untouched
- **Binding under review:** `src/prepare_live.py`
  `462596ee721f651924ad03d24f6480b466b04a402768012a6736cbc44ce6ddd3`
  (`462596ee721f`), plus companions below
- **Contract:** `package.md` `f2b7df48…` @ `e32c0dccacb28ba0dc9b9ab107ee9f8f2c569a38`
  (unchanged)

## Verdict

**PASS** — the correction removes quiet suppression while keeping JSON, persists
raw launch evidence before validation, and treats empty/malformed success as an
ambiguous **EFFECT** (never zero created). Parser-safe `--idle-timeout=25m` is
retained; partial ownership survives second-side and post-create binding
failures. The SUCCESS-vs-error JSON distinction is independently confirmed
against the installed CLI source and evidence.

## Root cause confirmed (independent, read-only)

- `agent-deck` installed source
  `/home/bmosher/src/agent-deck/cmd/agent-deck/cli_utils.go`: `Success`
  (`:608`) checks `quietMode` **before** `jsonMode` (`:609` returns early,
  `:612` renders JSON), while `Error` (`:620`) checks `jsonMode` (`:629`) before
  `quietMode` (`:645`). So `-json -q` on a **successful** launch exits rc0 with
  empty stdout (session created, identity lost), but **errors** still emit JSON
  under quiet — which is exactly why the prior error-only `NOT_FOUND` probe
  misled.
- Pinned prepare-2 evidence agrees: the tool raised `E_LAUNCH_NO_ID` /
  `E_LAUNCH_PARTIAL` while the launcher registry shows the created worker
  `0e734b30-1790050074` (`status: error`, then `stopped` by Tern). The
  reconciliation correctly calls the earlier "zero created" claim wrong: saved
  `post-registry.txt` itself totals 5.
- Independent error probe (safe, invalid path, no seat): `… launch
  /tmp/p6r6-none --idle-timeout=25m -json -q …` → rc1 with structured JSON
  `{"code":"NOT_FOUND","success":false}`, demonstrating Error-JSON survives
  quiet. A SUCCESS JSON cannot be probed without creating a seat and was
  correctly **not** attempted; it is instead covered by inspected CLIOutput
  semantics plus the pinned live evidence above.

## Repair conformance

- **Quiet suppression removed, JSON retained:** `launch_idle`
  (`src/prepare_live.py:109–167`) argv is
  `["agent-deck","launch",PATH,"-t",NAME,"-cmd",LANE,"--idle-timeout=25m","-json"]`
  — no `-q`/`--quiet`. Parser-safe single `=` token kept; no `-message` (idle).
- **Raw evidence before validation:** intent + `rc` + `stdout` + `stderr` are
  persisted via `_persist_raw` to `manifest-out.raw.<role>.json` **before** any
  parse/validation (`:149–151`), and each side records `raw_record`,
  `identity_source: launch-response-id`, `preparation_argv`, `idle_timeout`.
- **Ambiguous EFFECT, never zero:** timeout (`:134`), transport error (`:142`)
  and rc0-without-id / malformed / empty (`:160–164`) all raise
  `E_LAUNCH_AMBIGUOUS` instructing reconcile-and-never-blind-retry; rc≠0 keeps
  `E_LAUNCH` with the raw path. No response is silently discarded.
- **Strict id correlation:** the manifest `session_id` comes only from the
  returned `out["id"]`, never from title; post-create binding re-resolves by
  exact id and `check_record` verifies profile/lane, then the real socket
  (`S_ISSOCK`) and incarnation are captured.
- **Partial ownership retained:** after each completed side a journal is
  written; a second-side failure returns `E_LAUNCH_PARTIAL` with the partial
  manifest and raw records; a **post-create binding failure** returns
  `_write_partial("bind-<role>", e)` so completed launches stay owned and
  reconcile via cleanup. Exactly one attempt per role — no retry.
- **Schema:** `launch-manifest.schema.json` (`2d5d7c46…`) side props now include
  `raw_record`/`identity_source`/`preparation_argv`/`idle_timeout`; top-level
  adds `journal`/`pending_role`/`raw_records`.

## Artifact hashes (recomputed this review)

- `src/prepare_live.py` `462596ee721f651924ad03d24f6480b466b04a402768012a6736cbc44ce6ddd3`
- `src/cleanup_live.py` `57bb7e4e4d4cc938ae41c4532f0a98311e15d05e2cbed1246e10793a156cd8fa` (unchanged)
- `src/prewake_gate.py` `5e3d333b9a1f22520da2f72ee17a8a703e086a790fe850f06b22756db20f8d73` (unchanged)
- `src/witness_timing.py` `0bf9903371210b4ee2ae87e21d5ce2b81f33e16f9f4eb86dfcc47bc9e8585ca3` (unchanged)
- `launch-manifest.schema.json` `2d5d7c4645fff27ba92e36e99e0d39d5a8914f6570d5c467edcf246e51d5f913`
- `tests/test_repair1_argv.py` `6cce3c725b637f33cf6f083b0bee2937b649bfd2eaab3d5e69bb4e817e1c71f4`
- `tests/test_repair2_success.py` `bd925f54299cee084e1d533a647a3ebbed6451edf06f3bb168cdd0d3a68d9ded`
- `tests/test_p6r6_tools.py` `2478642407704faf43fdd73079397129e264b0f46b88b778e0d5ce85d3f74a64` (unchanged)
- `live-fixture-plan.json` `1a536965…`, `operator-brief.md` `ddff22f0…` (unchanged)

## Proposed preparation argv (of record, bound)

```
agent-deck launch WDIR -t NAME -cmd LANE --idle-timeout=25m -json
```
`NAME=p6-fixture-worker | p6-fixture-verifier`, `LANE=/home/bmosher/.config/agent-deck/acp-go | acp-go-deepseek`,
`WDIR=${workdir-base}/NAME`, `AGENTDECK_PROFILE=campaign4`. No `-q`, no
`-message`. Full manifest schema `2d5d7c46…`; tool `462596ee721f…`.

## Regression

`PYTHONPATH=src python3 -m pytest tests/ -q` → **18 passed** (12 prior + 6
repair-2). `tests/test_repair2_success.py` separates SUCCESS JSON from error
JSON, covers quiet+json old failure (empty rc0 → `E_LAUNCH_AMBIGUOUS` with raw),
corrected success returning an exact id, empty/malformed/timeout/transport →
ambiguous with retained raw, second-side failure preserving partial and no
retry, post-create binding failure retaining both sides, and an error-JSON
parser-only probe. Registry checked before/after: 5 (the four main seats plus the
stopped owned fixture `0e734b30-1790050074` retained as evidence) — no new seat
created or messaged by this review.

## Non-blocking observations

- `witness_timing.check` still reports but does not gate recover/total; plan
  phase 5 candidate assertions remain required (carried forward).
- The full manifest writes `launcher_source` from `live_source`; the pre-wake
  gate still independently rejects anything not `live-agent-deck`, so a dry-run
  manifest cannot pass — unchanged and verified previously.

## Effect

Verdict **PASS** bound to `src/prepare_live.py`
`462596ee721f651924ad03d24f6480b466b04a402768012a6736cbc44ce6ddd3` and the
hashes above, under contract `f2b7df48…` @ `e32c0dc`. Both failed preparations
and their reconciliation/stop receipts are preserved, not overwritten. No live
launch, Stage C, seat/service creation, Signal, wrapper edit or clock change
occurred. A fresh exact-hash preparation release is still required before any
live step; the stopped fixture is not reused/restarted/removed without a future
release. Verdict returned to cairn.
