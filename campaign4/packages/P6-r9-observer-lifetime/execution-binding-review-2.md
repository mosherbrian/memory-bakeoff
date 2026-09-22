# P6-r9-observer-lifetime — execution-binding check 2 (independent, derive-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-bindingcheck-2`, start `2026-09-22T12:29Z`, deadline
  `2026-09-22T12:39Z`
- **Artifact under check:** `live-preparation-2/execution-binding.json`
  sha256 `af42ea874718f068286007c576f75bafcf3bc8050336369a7cb422d6d030efbe`
- **Scope:** derive-only schema/binding check vs raw launch records, current
  director registry, live Unix sockets and the signed plan. **No `run-case`;
  no task sent; no package state modified.**

## Verdict

**FAIL.** `af42ea874718…` is the true hash of the file, and every identity it
does declare (IDs, titles, workdirs, sockets, incarnation) reconciles exactly
to the raw launch records, registry and plan. But the binding is **not
schema-conformant and does not derive**: `case_entry.py derive-config` rejects
it rc3 `E_SYNTHETIC "worker.stream_path missing or placeholder"`, and its
`role_lane` carries the registry *group* (`workdirs`) where the signed schema
requires the launch lane command, which the H2 gate compares against
`registry.command` (`case_entry.py:257`). It cannot be consumed as the live
execution binding without repair.

## Checks

- **Hash:** sha256(`live-preparation-2/execution-binding.json`) =
  `af42ea874718f068286007c576f75bafcf3bc8050336369a7cb422d6d030efbe`.
- **Plan:** `plan_sha256` = `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; matches the binding and the partial manifest.
- **Raw records:** raw worker `id`/`session_id` `4fbbeb0a-1790080127`, lane
  `/home/bmosher/.config/agent-deck/acp-go`, title/path `p6-fixture-worker-r9p2`
  and raw verifier `072d1e95-1790080128`, lane `acp-go-deepseek` (both
  `rc: 0`, `success: true`) equal the binding's `session_id`/`title`/`workdir`.
  `launch-manifest.json.partial` records the same two ids, `pending_role`
  `bind-worker`, `E_NO_SOCKET`; the rc3 partial failure is preserved, not
  masked.
- **Registry:** `agent-deck -p campaign4 list -json` carries both rows —
  worker `4fbbeb0a-1790080127` `idle`, verifier `072d1e95-1790080128`
  `waiting`, group `workdirs`, `profile: campaign4`, commands `acp-go` /
  `acp-go-deepseek` and paths equal to the binding workdirs. Stale p6r6/p6r8
  and stopped r9p1 fixtures remain `stopped`; no collision.
- **Sockets/incarnation:** both sockets exist as real Unix sockets;
  `(ino, mtime)` equal the binding exactly (worker `23668498 /
  1790080129.2100136`, verifier `23668503 / 1790080129.2650135`).
- **Preserved failure:** `stdout.txt` still records `E_LAUNCH_PARTIAL`
  (`bind-worker failed after 2 sides completed`); `tool_rc3_preserved` and
  `no_tasks_sent` are true. Streams `.jsonl` absent, expected before a first
  turn.

## Blocking defect (derive gate)

`case_entry.py derive-config` against the signed plan + this binding (private
`/tmp` output, local derive-only probe signature) → **rc3**
`{"detail": "worker.stream_path missing or placeholder", "error":
"E_SYNTHETIC"}`. Required-but-absent per side:

| field (derive_config, `case_entry.py:104-131`) | worker | verifier |
|---|---|---|
| `producer_root` | missing | missing |
| `stream_path` | missing | missing |
| `role_lane` = lane command | present but `"workdirs"` (group) | same |
| `launch_command` | missing | missing |
| `profile` | missing | missing |
| `identity_source` | missing | missing |
| `raw_record` / `raw_record_sha256` | missing | missing |

The tool's canonical side schema (`prepare_live.py:337-349`) sets
`role_lane` to the lane command, `producer_root` to the live stream root and
`stream_path` to `<id>.jsonl`; the reconciled file dropped those and set
`role_lane` to the group. Control: the P6-r8 execution binding
(`8496c10a…`, which carries these fields) derives rc0 under the same tool.
Had the file reached the H2 gate it would additionally fail `E_MISMATCH` at
`case_entry.py:257` on the lane/command comparison.

## Effect

Binding `af42ea874718…` is faithful in identity but **unusable as the live
binding**: not derivable, missing `producer_root`/`stream_path` (and
`launch_command`/per-side `profile`/`identity_source`/`raw_record`), and
`role_lane` mis-set to the group. Repair requires re-filing
`live-preparation-2/execution-binding.json` in the `prepare_live.py` side
schema (at minimum add `producer_root = /home/bmosher/.config/agent-deck/acp-stream`,
`stream_path = <id>.jsonl`, `launch_command`/`role_lane` = lane command) and
re-deriving to rc0 before any live release. No `run-case`, task, send, socket
write or package mutation occurred. Returned to cairn.
