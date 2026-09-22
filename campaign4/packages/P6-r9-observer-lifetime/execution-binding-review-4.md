# P6-r9-observer-lifetime — execution-binding review 4 (independent, derive-only)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r9-bindingcheck-4`, start `2026-09-22T16:19Z`, deadline
  `2026-09-22T16:24Z`
- **Artifact under check:** `live-preparation-4/execution-binding.json`
  sha256 `a224daf4aa7f4e065cbbb3cf030d2cfa68be81fbfbdaf8f5e0ef67ed094866b9`
- **Scope:** derive-only schema/binding check vs the r9p4 raw records, live
  registry, live sockets and the signed plan. **No `run-case`; no task sent;
  no socket write; no package state modified.**

## Verdict

**FAIL — schema non-conformance, not identity.** `a224daf4aa7f…` is the true
hash of the file; every *identity* reconciles exactly (IDs, titles, workdirs,
raw-record hashes, registry rows, socket incarnations, plan hash), the
gate-blocking `role_lane` defect that failed review-3 is **fixed** (both sides
now carry the raw lane command), and the file re-derives **rc0** against the
signed plan. But the file is still written in the **old rejected summary
shape** (`action_id` + `raw_record_hash`), not the canonical
`execution-binding-corrected.json` schema, which directly violates signed
release-4 condition 7. No `derive-only-signature.json` / `derived-config.json`
is filed. It is therefore not an acceptable live handoff artifact yet.

## Checks

- **Hash:** sha256(`live-preparation-4/execution-binding.json`) =
  `a224daf4aa7f4e065cbbb3cf030d2cfa68be81fbfbdaf8f5e0ef67ed094866b9`.
- **Plan:** `plan_sha256` `1263fdf79cdfe2fdcd59116cd5c5acd69489091972a83a730eca8101e43a1fce`
  re-derives from `stagec-plan.json`; matches the binding and the partial
  manifest.
- **Raw records:** `raw_record_hash` `1a7523442d93bf8a344b111aa4e6595bd2871eb0fa2068c1957462ccf10556d3`
  and `cfd3527b6bcd28ee87737edaaf4d01e2783ac795b89c414aa21a91201e9ada37`
  match `launch-manifest.json.raw.worker.json` / `.raw.verifier.json`
  byte-for-byte (recomputed). Raw stdout `id`/`session_id` `ba5a1ae8-1790093908`
  (worker, lane `/home/bmosher/.config/agent-deck/acp-go`) and
  `203af130-1790093909` (verifier, lane `acp-go-deepseek`), `rc: 0`,
  `success: true`, equal the binding's `session_id`/`title`/`workdir`.
- **Registry:** live `agent-deck -p campaign4 list` carries both rows — worker
  `ba5a1ae8-1790093908` and verifier `203af130-1790093909`, group `workdirs`,
  `command` = the raw lane, `path` = the binding workdir. `post-registry.txt`
  records the same two rows. No r9p4 collision.
- **Sockets/incarnation:** both sockets exist as real Unix sockets;
  `(ino, mtime)` equal the binding exactly (worker `23681134 /
  1790093910.2891402`, verifier `23681136 / 1790093910.3361883`). The
  `E_NO_SOCKET` recorded in the partial was a launch-time race; the sockets are
  live now, so the H2 lane/workdir/incarnation checks would hold.
- **Schema mapping:** `producer_root` = live stream root
  `/home/bmosher/.config/agent-deck/acp-stream`; each `stream_path` =
  `<session_id>.jsonl` directly under it; socket dir ≠ producer root.
- **Derive-only gate:** ran `case_entry.py derive-config` against the signed
  plan + this binding to a private `/tmp` output using a throwaway local
  `derive-only` signature → **rc0**,
  `{"config": "/tmp/p6r9p4-derived-config.json", "parent_binding_sha256":
  "a224daf4aa7f4e065cbbb3cf030d2cfa68be81fbfbdaf8f5e0ef67ed094866b9"}`. The
  four derive-required keys (`session_id`, `socket`, `stream_path`,
  `producer_root`) are present and non-placeholder on both sides.
- **Preserved failure:** `stdout.txt` still records `E_LAUNCH_PARTIAL`
  (`bind-worker failed after 2 sides completed`); the partial journals
  `pending_role: bind-worker`, `E_NO_SOCKET`. Not masked.

## Blocking defect (signed condition 7)

Release-4 condition 7 requires exactly: *"Use schema of prior
`execution-binding-corrected.json`, NEVER old rejected summary."* The file
under check is neither. Key diff vs
`live-preparation-3/execution-binding-corrected.json`:

| canonical corrected key | r9p4 binding |
|---|---|
| `recorded_at` | absent |
| `supersedes_schema_sha256` | absent |
| `tool_rc3_preserved`, `no_tasks_sent` | absent |
| per-side `profile`, `identity_source` | absent |
| per-side `raw_record` + `raw_record_sha256` | replaced by `raw_record_hash` |
| `launch_command` = lane **string** | argv **array** |
| — | `action_id` present (old summary marker) |

The old summary markers `action_id` and `raw_record_hash` are precisely what
review-3 struck down; the file is the rejected shape re-filed with `role_lane`
corrected. It also does not ship the `derive-only-signature.json` /
`derived-config.json` / `director-registry.json` evidence that r9p3's PASS
carried, so condition 7's *"derive-only rc0 before corvid handoff"* has no
filed artifact. (Derivation itself now succeeds — the defect is the schema and
the missing filed derive evidence, not derivability.)

## Effect

Binding `a224daf4aa7f…` is faithful in identity and now derivable and
gate-plausible, but **not in the required schema** and with no filed
derive-only step: it reuses the rejected summary shape and omits per-side
`profile`/`identity_source`/`raw_record`+`raw_record_sha256`,
`recorded_at`/`supersedes_schema_sha256`/`tool_rc3_preserved`/`no_tasks_sent`,
and sets `launch_command` to an argv array instead of the lane string. Repair:
re-file `live-preparation-4/execution-binding.json` as
`execution-binding-corrected.json` in the `execution-binding-corrected.json`
schema (raw lane for `role_lane` and lane-string `launch_command`, per-side
`profile`, `identity_source`, `raw_record`+`raw_record_sha256`, top-level
`recorded_at`, `tool_rc3_preserved`, `no_tasks_sent`), then file a Tern
`derive-only` signature and rc0 `derived-config.json` before any corvid
handoff. No `run-case`, task, send, socket write or package mutation occurred.
Returned to cairn.
