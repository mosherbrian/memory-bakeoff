# P6-r9-observer-lifetime — execution-binding check 3 (independent, derive-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-bindingcheck-3`, start `2026-09-22T13:51Z`, deadline
  `2026-09-22T13:56Z`
- **Artifact under check:** `live-preparation-3/execution-binding.json`
  sha256 `0536cbdb3c4b8ff7a36c5b1fee23383b79f043acd41b06657fe39bf898e385cc`
- **Scope:** derive-only schema/binding check vs the r9p3 raw records, current
  registry, live sockets and the signed plan. **No `run-case`; no task sent;
  no package state modified.**

## Verdict

**FAIL.** `0536cbdb3c4b…` is the true hash of the file and every *identity* it
declares (IDs, titles, workdirs, sockets/incarnations, plan, raw-record hashes)
reconciles. But the file is **not in the canonical `prepare_live` /
`execution-binding-corrected.json` schema**, it directly violates signed release
condition 7 ("raw lane (**NOT group**) … Use schema of prior
`execution-binding-corrected.json`, NEVER old rejected summary"), and it cannot
pass the H2 gate. It is the old rejected summary shape re-filed with two fields
added.

## Checks

- **Hash:** sha256(`live-preparation-3/execution-binding.json`) =
  `0536cbdb3c4b8ff7a36c5b1fee23383b79f043acd41b06657fe39bf898e385cc`.
- **Identity reconciles:** worker `2382c1d3-1790085057` / title
  `p6-fixture-worker-r9p3` / workdir `/tmp/p6r9-prep3-20260922T134950Z/workdirs/…`
  and verifier `b1c91738-1790085057` / `p6-fixture-verifier-r9p3` appear verbatim
  in the raw records (`rc: 0`, `success: true`) and in `post-registry.txt`
  (both `workdirs`, `profile: campaign4`, commands `acp-go` /
  `acp-go-deepseek`). `plan_sha256` `1263fdf7…1fce` re-derives from
  `stagec-plan.json`; partial preserves the rc3 `E_LAUNCH_PARTIAL`.
- **Raw hashes:** `raw_record_hash` `0df0e817…93e6` and `85861d32…7024` match
  `launch-manifest.json.raw.worker.json` / `.raw.verifier.json` byte-for-byte.
- **Streams/sockets:** `producer_root` is the live acp-stream root and each
  `stream_path` is `<id>.jsonl` directly under it; both sockets exist as real
  Unix sockets with `(ino, mtime)` equal to the binding (`2382c1d3` ino
  `23672472`, `b1c91738` ino `23672474`).

## Blocking defects (schema / gate)

1. **`role_lane` is the group.** Both sides set `role_lane = "workdirs"`. The
   signed schema (`prepare_live.py:338`) and release-3 condition 7 require the
   **raw lane command** (`/home/bmosher/.config/agent-deck/acp-go` /
   `acp-go-deepseek`). The H2 gate rejects this at `case_entry.py:257`
   (`rec.command != signed.role_lane` → `E_MISMATCH`, "lane/command mismatch").
2. **`launch_command` is not the lane.** Set to `"agent-deck launch"` (the CLI
   prefix), not the raw lane (corrected r9p2 used the lane command).
3. **Wrong schema/keys.** Uses `action_id`/`reconciled_at` and
   `raw_record_hash`; the canonical corrected schema uses `recorded_at` (no
   `supersedes_schema_sha256` here) and `raw_record` + `raw_record_sha256`, and
   carries `identity_source`. This is the old rejected summary shape
   (`af42ea87…`), which condition 7 forbids.
4. **Derive not run.** No derive-only signature exists in `live-preparation-3/`,
   so `derive-config` cannot execute; fail-closed is correct, but release-3's
   "derive-only rc0 before corvid handoff" is unmet. Even with a signature,
   `derive-config` would rc0 (its required keys are present) while the later H2
   gate fails on defect 1 — so rc0 alone would not have caught this.

## Effect

Binding `0536cbdb3c4b…` is faithful in identity but **not executable and not
the required schema**: `role_lane` is the group not the raw lane (gate
`E_MISMATCH`), `launch_command` is the CLI prefix, and it reuses the rejected
summary shape. Repair: re-file `live-preparation-3/execution-binding.json` in
the `execution-binding-corrected.json` schema (raw lane for `role_lane` and
`launch_command`, `raw_record`+`raw_record_sha256`, `identity_source`,
`recorded_at`), then derive-only rc0 before any handoff. No `run-case`, task,
send, socket write or package mutation occurred. Returned to cairn.
