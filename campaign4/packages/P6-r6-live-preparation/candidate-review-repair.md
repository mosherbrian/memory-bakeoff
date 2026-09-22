# P6-r6-live-preparation — candidate review, repair-1 (independent)

- **Reviewer:** corvid (independent of kiln/author)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Repair receipt:** `repair-1-receipt.json`, action `P6r6-repair-1`,
  owner kiln, start `2026-09-22T04:01Z`, deadline `2026-09-22T04:21Z`
- **Authorization:** `allocation-extension-1.md`; new 20m worker + 15m verify;
  cumulative **395/300**; live 15 + fixture 15 HELD
- **Predecessor:** `P6r6-prepare-1` FAIL preserved in
  `preparation-failure-record.json` (`c1d2e0c` exhausted, no retry)
- **Binding under review:** `src/prepare_live.py`
  `e10d25846c13c1f62c63bd50a809de2a1c1c1b546dac54fedb4e4c879530b3ce`
  (`e10d25846c13`), plus repair-1-note and changed companions below
- **Contract:** `package.md` `f2b7df48…` @ `e32c0dccacb28ba0dc9b9ab107ee9f8f2c569a38`
  (unchanged); checklist `ba44f88a…`; prior candidate review `c4a2602b…`

## Verdict

**PASS** — the parser-safe argv repair is correct, the original failure is
reproduced verbatim against the installed binary, and the corrected argv binds
all flags with **no seat created** (registry pinned at the four main seats
before and after).

## Root cause and reproduction (independent)

Root cause (read from the installed parser, no binary/source edits): the first
argv pass `reorderArgsForFlagParsing` only pairs a separate-token value for
flags present in its `valueFlagNames` map, which omits `idle-timeout`, so the
old argv demoted `25m` to positional and the second pass bound `-json` as the
idle-timeout value.

I reproduced both sides myself (no replayed report):

- **OLD argv** `… launch /tmp -t probe-old -cmd LANE -idle-timeout 25m -json -q`
  → rc1, `Error: invalid --idle-timeout "-json": time: invalid duration "-json"
  (use Go duration like 30m, 1h, 24h)`. This is byte-identical in wording to the
  pinned original failure `live-preparation/stdout.txt`
  (`adbd4a0dd8c6…`, `E_LAUNCH: launch 'p6-fixture-worker' failed`).
- **NEW argv** `… launch /tmp/p6r6-probe-nodir -t probe-new -cmd LANE
  --idle-timeout=25m -json -q` → rc1 but structured JSON
  `{"code":"NOT_FOUND","error":"path does not exist: …","success":false}`,
  proving `-json` is honored and every flag binds (the non-existent path is the
  only rejection). No seat was created by either probe.

`agent-deck list --json` was `4 [0c933c75…, 493c0317…, a79067ca…, 56513e0e…]`
before and after; unchanged.

## Repair conformance

- **Parser-safe argv:** `launch_idle` (`src/prepare_live.py:101–113`) now emits
  `--idle-timeout=%s` as a single `=` token, never split by either pass; `-t` and
  `-cmd` remain separate tokens but are in the reorder map (the `NOT_FOUND` probe
  confirms `-json` still binds after them). No `-message`/`-m` — idle by
  construction (P1/P5 retained).
- **Exact identity, no fallback:** a successful launch response must carry `id`
  or the tool raises `E_LAUNCH_NO_ID` (`:126`), removing the silent title-only
  fallback that could have mis-bound identity.
- **Partial journal, no retry:** the live path records each completed side to
  `manifest-out.partial`; if the second launch fails it raises
  `E_LAUNCH_PARTIAL` (`:260`) pointing at the partial record, with exactly one
  attempt per role — completed sides are never retried, only reconciled via
  cleanup. Each side records `identity_source`, `preparation_argv`, and
  `idle_timeout` (`:235–244`, `:286–287`).
- **Cleanup partial support:** `cleanup_live.py` requires `launcher_source ==
  live-agent-deck` and reconciles present sides only, reporting the pending
  role. Probe: a partial manifest with `worker` present and `pending_role:
  verifier` dry-ran to `owned: ["w1"]`, stop-then-remove, archive dir,
  `executed:false`, rc0 — no `KeyError` on the absent side.
- **Schema:** `launch-manifest.schema.json` adds optional
  `identity_source`/`preparation_argv`/`idle_timeout`/`journal`/`pending_role`;
  side `profile` is `const campaign4`.
- **Signature invalidation acknowledged:** code hashes changed, so any prior
  signature over old tool bytes is void; no valid preparation signature existed
  (`c1d2e0c` retired with the failed attempt). Stage C stays blocked; a fresh
  exact-hash release is required before any live step.

## Artifact hashes (recomputed this review)

- `src/prepare_live.py` `e10d25846c13c1f62c63bd50a809de2a1c1c1b546dac54fedb4e4c879530b3ce`
- `src/cleanup_live.py` `57bb7e4e4d4cc938ae41c4532f0a98311e15d05e2cbed1246e10793a156cd8fa`
- `src/prewake_gate.py` `5e3d333b9a1f22520da2f72ee17a8a703e086a790fe850f06b22756db20f8d73` (unchanged)
- `src/witness_timing.py` `0bf9903371210b4ee2ae87e21d5ce2b81f33e16f9f4eb86dfcc47bc9e8585ca3` (unchanged)
- `launch-manifest.schema.json` `8b6262c58aeea064172bbcc1b340f1aa659e5a809b0a667f025484e3c96b1d6e`
- `tests/test_repair1_argv.py` `c47bda8d54d269462008f9790a962fb65c4f067c60435c15ec498f91bbf27528`
- `tests/test_p6r6_tools.py` `2478642407704faf43fdd73079397129e264b0f46b88b778e0d5ce85d3f74a64` (unchanged)
- `live-fixture-plan.json` `1a536965…`, `operator-brief.md` `ddff22f0…` (unchanged)
- `preparation-failure-record.json` (`c4a2602b` review preserved) — parent evidence intact

## Regression

`PYTHONPATH=src python3 -m pytest tests/ -q` → **12 passed** (8 prior + 4
repair-1), including the real-binary parser differential that asserts the old
argv mis-binds, the `=` argv is safe, and the campaign4 registry is pinned at 4
seats. Registry independently re-checked count 4 before/after. No real seats
created or messaged; no live preparation performed.

## Non-blocking observations

- The `recover`/`total` bounds remain reported-not-gated in
  `witness_timing.check` (carried from the candidate review); the plan still
  requires phase-5 candidate assertions on them.
- Phase 1 of `live-fixture-plan.json` shows the tool invocation, not the argv
  literal; the argv of record is now the tool's `--idle-timeout=25m` and is
  captured per side in the manifest, which is what the gate binds.

## Effect

Verdict **PASS** bound to `src/prepare_live.py`
`e10d25846c13c1f62c63bd50a809de2a1c1c1b546dac54fedb4e4c879530b3ce` and the
hashes above, under contract `f2b7df48…` @ `e32c0dc`. The `P6r6-prepare-1` FAIL
is preserved, not overwritten. No live preparation, Stage C, seat/service
creation, Signal, wrapper edit or clock change occurred. Worker stays held; a
fresh exact-hash preparation release is still required before any live step.
Verdict returned to cairn.
