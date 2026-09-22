# P6-r8-case-execution — execution-binding check (independent, derive-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r8-execbinding-1`, start `2026-09-22T09:05Z`, deadline
  `2026-09-22T09:10Z`
- **Artifact under check:** `live-preparation-1/execution-binding.json`
  sha256 `8496c10aeb5aacd79a6173425f7fcfbd387ceea3bc539136f0af16e7c339f254`
- **Scope:** derive-only schema/binding check vs raw launch records, director
  registry, live sockets and the signed plan. **No `run-case`; no task sent;
  no package state modified.**

## Verdict

**PASS.** `8496c10aeb5a…` is the true hash of the execution binding, every
per-seat field reconciles exactly to its raw launch record, registry row and
live socket, the declared plan/reconciliation parents re-derive, and
`derive-config` accepts the binding (rc0) with
`parent_binding_sha256 = 8496c10a…`.

## Checks

- **Hash:** sha256(`execution-binding.json`) =
  `8496c10aeb5aacd79a6173425f7fcfbd387ceea3bc539136f0af16e7c339f254`.
- **Parents:** `plan_sha256` = `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; `original_reconciliation_sha256` = `fbfb3ca7795d…`
  re-derives from `launch-manifest-reconciled.json` (prior check).
- **Raw records:** `worker.raw_record_sha256` `fedbd532…d0cf` and
  `verifier.raw_record_sha256` `c59ac55e…8554` match
  `launch-manifest.json.raw.worker.json` / `.raw.verifier.json` byte-for-byte.
  Raw `id`/`session_id`, `title`, `lane`, `workdir` equal the binding fields;
  `launch_command == role_lane`.
- **Registry:** `director-registry.json` carries both rows
  (`6c0b6725-1790067489` worker `idle`, `ed54bf3d-1790067490` verifier
  `waiting`); title, command, path and `profile: campaign4` all match. Stale
  p6r6 fixtures remain `stopped`; no collision.
- **Sockets/incarnation:** both sockets exist as real Unix sockets;
  `(ino, mtime)` equal the binding's `incarnation` exactly (worker
  `23658978 / 1790067491.2928183`, verifier `23658983 / 1790067491.3716857`).
- **Schema/plan semantics:** `producer_root` is the live
  `/home/bmosher/.config/agent-deck/acp-stream` and each `stream_path` is the
  per-session `<id>.jsonl` directly under it; socket dir differs from the
  producer root; no placeholder tokens. The stream `.jsonl` files do not yet
  exist — expected before the first turn (the producer creates them on
  launch/first append), not a binding defect.
- **Derive-only gate:** ran `case_entry.py derive-config` against the signed
  plan + this binding to a private `/tmp` output → rc0, producing a config
  whose `parent_binding_sha256` is `8496c10a…`. No `run-case`, seat send,
  socket write or package mutation.

## Effect

Execution binding `8496c10aeb5a…` confirmed faithful and derivable read-only.
Ready for a separate launch/execution gate; this check neither launches nor
authorizes one. Returned to cairn.
