# P6-r9-observer-lifetime — corrected execution-binding check (independent, derive-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-correctioncheck-1`, start `2026-09-22T12:34Z`, deadline
  `2026-09-22T12:39Z`
- **Artifact under check:** `live-preparation-2/execution-binding-corrected.json`
  sha256 `09bf07b2bee066642c614b1c0f85b66962f446cacf85e1d276ad490f3f4e42a7`
- **Original preserved:** `live-preparation-2/execution-binding.json` sha256
  `af42ea874718…` unchanged; corrected file declares
  `supersedes_schema_sha256 = af42ea87…`
- **Scope:** derive-only re-check vs original, raw records, registry, live
  sockets and plan. **No `run-case`; no task sent; no package state modified.**

## Verdict

**PASS.** `09bf07b2bee0…` is the true hash of the corrected binding, it
supersedes the preserved `af42ea87…` schema record, every per-seat field
reconciles exactly to its raw launch record, registry row, live socket and the
signed plan, and `derive-config` independently re-derives **rc0** with
`parent_binding_sha256 = 09bf07b2bee0…`. The previous blocking defect
(`E_SYNTHETIC` on missing `stream_path`/`producer_root`; `role_lane = workdirs`)
is fixed.

## Checks

- **Hash:** sha256(`execution-binding-corrected.json`) =
  `09bf07b2bee066642c614b1c0f85b66962f446cacf85e1d276ad490f3f4e42a7`.
- **Original preserved:** sha256(`execution-binding.json`) still
  `af42ea874718…`; `supersedes_schema_sha256` = `af42ea874718…` (no overwrite;
  the failed first filing is retained as evidence).
- **Raw records:** `worker.raw_record_sha256` `476435698e…4648` and
  `verifier.raw_record_sha256` `f0fb5498…5915` match
  `launch-manifest.json.raw.worker.json` / `.raw.verifier.json` byte-for-byte
  (recomputed). Raw `id`/`session_id`, lane and workdir equal the binding;
  `launch_command == role_lane`, both now the lane command (worker `acp-go`,
  verifier `acp-go-deepseek`) instead of the group `workdirs`.
- **Registry:** live `agent-deck -p campaign4 list -json` (and the archived
  `director-registry.json`, 13 rows) carries both rows — worker
  `4fbbeb0a-1790080127` `idle`, verifier `072d1e95-1790080128` `waiting`,
  `profile: campaign4`, commands and workdirs exactly the binding values.
- **Sockets/incarnation:** both sockets exist as real Unix sockets;
  `(ino, mtime)` equal the binding (worker `23668498 / 1790080129.2100136`,
  verifier `23668503 / 1790080129.2650135`).
- **Plan/schema:** `plan_sha256` `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; each `producer_root` is the live stream root and each
  `stream_path` is `<id>.jsonl` directly under it; socket dir differs from the
  producer root; no placeholder tokens.
- **Derive-only gate:** re-ran `case_entry.py derive-config` against the signed
  plan + this binding to a private `/tmp` output → **rc0**,
  `{"config": "/tmp/…", "parent_binding_sha256": "09bf07b2bee0…"}`, matching
  the pre-filed `derive.stdout` (rc0) and `derived-config.json`. No `run-case`,
  seat send, socket write or package mutation.
- **Preserved failure:** `tool_rc3_preserved`/`no_tasks_sent` true;
  `stdout.txt` still records the tool rc3 `E_LAUNCH_PARTIAL`.

## Effect

Corrected binding `09bf07b2bee0…` confirmed faithful and independently
derivable read-only. Ready for a separate launch/execution gate; this check
neither launches nor authorizes one. Returned to cairn.
