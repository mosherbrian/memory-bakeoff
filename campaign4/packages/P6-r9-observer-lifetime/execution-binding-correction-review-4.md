# P6-r9-observer-lifetime — corrected-4 execution-binding check (independent, derive-only)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-correctioncheck-4`, start `2026-09-22T16:24Z`, deadline
  `2026-09-22T16:29Z`
- **Artifact under check:** `live-preparation-4/execution-binding-corrected.json`
  sha256 `7cacfbcb61ef961cf51e2f18611975970204723303809acc659b199a26519394`
- **Original preserved:** `live-preparation-4/execution-binding.json` sha256
  `a224daf4aa7f4e065cbbb3cf030d2cfa68be81fbfbdaf8f5e0ef67ed094866b9` unchanged;
  corrected file declares `supersedes_schema_sha256 = a224daf4…`
- **Scope:** derive-only re-check vs original, raw records, live registry, live
  sockets/runtime liveness and the signed plan. **No `run-case`; no task sent;
  no socket write; no package state modified.**

## Verdict

**PASS.** `7cacfbcb61ef…` is the true hash of the corrected binding, it
supersedes the preserved `a224daf4…` rejected-summary file, it matches the
canonical `execution-binding-corrected.json` schema key-for-key, every per-seat
field reconciles exactly to its raw launch record, live registry row, live
socket and the signed plan, and `derive-config` independently re-derives
**rc0** with `parent_binding_sha256 = 7cacfbcb61ef…`. The review-4 blocking
defects (old summary shape, missing derive evidence) are fixed.

## Checks

- **Hash:** sha256(`execution-binding-corrected.json`) =
  `7cacfbcb61ef961cf51e2f18611975970204723303809acc659b199a26519394`.
- **Original preserved:** sha256(`execution-binding.json`) still `a224daf4…`;
  `supersedes_schema_sha256` = `a224daf4…` (no overwrite).
- **Schema fixed:** top-level and per-side key sets are identical to
  `live-preparation-3/execution-binding-corrected.json` (verified
  programmatically; no extras, no missing). `worker.role_lane`/`launch_command`
  = `/home/bmosher/.config/agent-deck/acp-go`; `verifier` =
  `/home/bmosher/.config/agent-deck/acp-go-deepseek` — raw lane commands as
  lane **strings**, not the group `workdirs` or an argv array. Per-side
  `profile`, `identity_source`, `raw_record`+`raw_record_sha256`,
  `recorded_at`, `tool_rc3_preserved`, `no_tasks_sent`,
  `producer_root`/`stream_path` all present; no `action_id`/`reconciled_at`
  summary shape.
- **Raw records:** `raw_record_sha256` `1a752344…56d3` and `cfd3527b…da37`
  recomputed byte-for-byte against
  `live-preparation-4/launch-manifest.json.raw.worker.json` / `.raw.verifier.json`;
  raw `id`/`session_id`, lane and workdir equal the binding.
- **Registry (live + archived):** live `agent-deck -p campaign4 list` carries
  worker `ba5a1ae8-1790093908` `idle` and verifier `203af130-1790093909`
  `waiting`, `profile: campaign4`, `command` = the binding's `role_lane`,
  `path` = the binding `workdir`. `director-registry.json` records the same
  rows; `post-registry.txt` consistent. So the H2 gate's
  `rec.command == role_lane` and workdir checks hold.
- **Sockets/incarnation/runtime liveness:** both sockets exist as real Unix
  sockets at check time; `(ino, mtime)` equal the binding exactly (worker
  `23681134 / 1790093910.2891402`, verifier `23681136 / 1790093910.3361883`)
  — no rebind. Both sessions present in the live registry and not
  stopped/archived/error.
- **Plan/schema:** `plan_sha256` `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; each `producer_root` is the live stream root and each
  `stream_path` is `<session_id>.jsonl` under it; socket dir ≠ producer root.
- **Derive-only gate:** re-ran `case_entry.py derive-config` against the signed
  plan + this binding + the filed `derive-only-signature.json` to a private
  `/tmp` output → **rc0**,
  `{"config": "/tmp/…", "parent_binding_sha256": "7cacfbcb61ef…"}`, matching the
  filed `derived-config.json` and `director-derive-result.json` (rc0,
  same `parent_binding_sha256`). No `run-case`, seat send, socket write or
  package mutation.
- **Preserved failure:** `tool_rc3_preserved`/`no_tasks_sent` true;
  `stdout.txt` still records the tool rc3 `E_LAUNCH_PARTIAL`; the
  `E_NO_SOCKET` partial is retained, not masked.

## Effect

Corrected binding `7cacfbcb61ef…` confirmed faithful, canonical, runtime-live
and independently derivable read-only. Ready for a separate launch/execution
gate; this check neither launches nor authorizes one. Returned to cairn.
