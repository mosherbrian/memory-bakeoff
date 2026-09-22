# P6-r9-observer-lifetime — corrected-3 execution-binding check (independent, derive-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-correctioncheck-3`, start `2026-09-22T13:55Z`, deadline
  `2026-09-22T14:00Z`
- **Artifact under check:** `live-preparation-3/execution-binding-corrected.json`
  sha256 `661e80940aa3f5745d388d4f76d5368541094b678f9227b190a0ff048946f213`
- **Original preserved:** `live-preparation-3/execution-binding.json` sha256
  `0536cbdb…` unchanged; corrected file declares
  `supersedes_schema_sha256 = 0536cbdb…`
- **Scope:** derive-only re-check vs original, raw records, registry, live
  sockets and plan. **No `run-case`; no task sent; no package state modified.**

## Verdict

**PASS.** `661e80940aa3…` is the true hash of the corrected binding, it
supersedes the preserved `0536cbdb…` rejected summary, it is in the canonical
`execution-binding-corrected.json` schema (raw lane for BOTH `role_lane` and
`launch_command`), every per-seat field reconciles exactly to its raw launch
record, registry row, live socket and the signed plan, and `derive-config`
independently re-derives **rc0** with `parent_binding_sha256 = 661e8094…`. All
three blocking defects from review-3 are fixed.

## Checks

- **Hash:** sha256(`execution-binding-corrected.json`) =
  `661e80940aa3f5745d388d4f76d5368541094b678f9227b190a0ff048946f213`.
- **Original preserved:** sha256(`execution-binding.json`) still `0536cbdb…`;
  `supersedes_schema_sha256` = `0536cbdb…` (no overwrite).
- **Schema fixed:** `worker.role_lane`/`launch_command` = `/home/bmosher/.config/agent-deck/acp-go`;
  `verifier` = `/home/bmosher/.config/agent-deck/acp-go-deepseek` — the raw
  lane commands, not the group `workdirs` or the CLI prefix. Per-side
  `profile`, `identity_source`, `raw_record`+`raw_record_sha256`, `recorded_at`,
  `producer_root`/`stream_path` all present; no `action_id`/`reconciled_at`
  summary shape. Matches `execution-binding-corrected.json` (r9p2) schema.
- **Raw records:** `raw_record_sha256` `0df0e817…93e6` and `85861d32…7024`
  match `launch-manifest.json.raw.worker.json` / `.raw.verifier.json`
  byte-for-byte (recomputed); raw `id`/`session_id`, lane and workdir equal the
  binding.
- **Registry:** live/archived registry carries both rows — worker
  `2382c1d3-1790085057` `idle`, verifier `b1c91738-1790085057` `waiting`,
  `profile: campaign4`, commands and workdirs exactly the binding values (so
  the H2 gate's `rec.command == role_lane` check now holds).
- **Sockets/incarnation:** both sockets exist as real Unix sockets;
  `(ino, mtime)` equal the binding (worker `23672472 / 1790085058.8673623`,
  verifier `23672474 / 1790085058.8803623`).
- **Plan/schema:** `plan_sha256` `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; each `producer_root` is the live stream root and each
  `stream_path` is `<id>.jsonl` under it; socket dir differs from producer root.
- **Derive-only gate:** re-ran `case_entry.py derive-config` against the signed
  plan + this binding to a private `/tmp` output → **rc0**,
  `{"config": "/tmp/…", "parent_binding_sha256": "661e80940aa3…"}`, matching the
  pre-filed `derive.stdout` (rc0) and `derived-config.json`. No `run-case`, seat
  send, socket write or package mutation.
- **Preserved failure:** `tool_rc3_preserved`/`no_tasks_sent` true;
  `stdout.txt` still records the tool rc3 `E_LAUNCH_PARTIAL`.

## Effect

Corrected binding `661e80940aa3…` confirmed faithful, canonical and
independently derivable read-only. Ready for a separate launch/execution gate;
this check neither launches nor authorizes one. Returned to cairn.
