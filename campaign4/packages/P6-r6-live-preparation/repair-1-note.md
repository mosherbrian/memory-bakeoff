# P6r6-repair-1 note (kiln, tool repair, no live seats)

## Root cause (installed parser source, read — no binary/source edits)

`agent-deck launch` runs two argv passes: `reorderArgsForFlagParsing`
(`main.go`) then `normalizeArgs` (`cli_utils.go`). The reorder pass pairs a
separate-token value ONLY for flags in its `valueFlagNames` map, which has
no `idle-timeout` entry. Our old argv
`launch PATH -t NAME -cmd LANE -idle-timeout 25m -json -q` therefore demoted
`25m` to positional and let the second pass bind `-json` as idle-timeout's
value → `invalid --idle-timeout "-json"`. Shell quoting was never the
cause (subprocess uses argv). Reproduced parser-only against the installed
binary with zero effects (see regression test).

## Corrected PREPARATION argv (exact, per seat)

```
agent-deck launch WDIR -t NAME -cmd LANE --idle-timeout=25m -json -q
```

`-t`/`-cmd` separate tokens are safe (both in the reorder map, verified:
bad-path probe returns JSON `NOT_FOUND`, proving `-json` honored and all
flags bound). The `=` token is never split by either pass. No `-message`:
idle by construction. `WDIR=/tmp/p6live/NAME`, `NAME=p6-fixture-worker |
p6-fixture-verifier`, `LANE` = inventoried `acp-go` / `acp-go-deepseek`.

## Tool changes (package only)

- `src/prepare_live.py` (`e10d25846c13`): `=` argv; launch response must
  carry exact `id` (`E_LAUNCH_NO_ID`, no silent title-only fallback);
  per-side `preparation_argv` + `idle_timeout` + `identity_source` recorded
  in manifest/journal; partial journal (`manifest-out.partial`) records each
  completed side, and a second-launch failure returns `E_LAUNCH_PARTIAL`
  with the partial path — reconcile via cleanup, never retry completed sides.
- `src/cleanup_live.py` (`57bb7e4e4d4c`): accepts partial manifests (≥1
  recorded side; pending role reported, present IDs reconciled).
- `launch-manifest.schema.json` (`8b6262c58aee`): new optional
  `identity_source`/`preparation_argv`/`idle_timeout`/`journal`/`pending_role`.
- `tests/test_repair1_argv.py` (`c47bda8d54d2`): exact-argv assertion,
  no-id refusal, real-binary parser differential (old mis-binds, `=` safe,
  registry pinned at 4 seats), partial-journal no-retry.

## Signature invalidation

Code hashes changed, so any signature over the old tool bytes is void.
No valid preparation signature existed (release `c1d2e0c` retired with the
failed attempt; nothing was created). The next preparation needs a fresh
exact-hash release. Stage C stays blocked per `director-candidate-record.json`.
