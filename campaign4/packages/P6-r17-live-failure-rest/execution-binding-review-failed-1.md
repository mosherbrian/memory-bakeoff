# P6-r17 — failed-1 execution-binding review (independent, derive-only)

- **Reviewer:** corvid-dsh
- **Action:** `P6r17-failed-binding-1` (existing ≤5 m grant)
- **Artifact under check:** `live-preparation-failed-1/execution-binding.json`
  sha256 `6bf90b1dcbe8c0db555e4148b4fb9b6288ab22e7b2c1bea6644f6a981a934fef`
- **Scope:** derive-only vs raw records, live registry, sockets/incarnations,
  plan, cleanup bound, no-task status; host inventory. No task/launch/restart.

## Verdict

**PASS (bounded).** Every identity, hash, socket, registry and cleanup fact
reconciles; `derive-config` re-derives **rc0** under the filed Tern `derive-only`
signature; no tasks were sent; the automatic cleanup timer is active for the
exact fixture IDs. Ready for Tern's separate exact live signature.

## Checks

- **Hash:** sha256(`execution-binding.json`) = `6bf90b1d…`; matches
  `derive-signature.json.binding_sha256`. Canonical schema (per-side
  `profile`/`identity_source`/`raw_record`+`raw_record_sha256`, `role_lane` = raw
  lane string, `recorded_at`, `tool_rc3_preserved`, `no_tasks_sent`).
- **Plan:** `plan_sha256` `3256b5a3…` re-derives from `live-plan-failed-1.json`,
  matching the release/partial.
- **Raw records:** `raw_record_sha256` `99b2f9b0…` (worker) and `b77e604a…`
  (verifier) recomputed byte-for-byte. Raw stdout ids/paths/lanes match the
  binding (`a94e7711-1790129305` acp-go, `576b7ed5-1790129305`
  acp-go-deepseek), both rc0. Partial preserves `E_LAUNCH_PARTIAL` socket race;
  not retro-PASS.
- **Workdirs:** actual launch workdirs
  `/tmp/p6r17-failed1-20260923T020709Z/workdirs/…` equal the signed argv — no
  deviation this attempt.
- **Sockets/runtime:** both sockets exist as real Unix sockets; `(ino, mtime)`
  equal the binding (worker `23772183 / 1790129306.7005434`, verifier `23772187 /
  1790129306.7537746`). No streams (`acp-stream/<id>.jsonl` absent) → **no tasks
  sent** (`no_tasks_sent: true`).
- **Registry:** live `agent-deck -p campaign4 list` carries both rows — worker
  `idle`, verifier `waiting`, profile `campaign4`, `command` = exact `role_lane`,
  `path` = exact workdir.
- **Derive-only:** `…/P6-r16-causal-identity/candidate/src/case_entry.py
  derive-config --plan live-plan-failed-1.json --binding …/execution-binding.json
  --signatures …/derive-signature.json` → **rc0**,
  `{"parent_binding_sha256": "6bf90b1d…"}`. No `run-case`, task, send or mutation.
- **Cleanup bound:** release/`binding-release-failed-1.md` state the exact-ID
  cleanup; live `systemctl --user is-active campaign4-p6r17-failed1-cleanup.timer`
  = **active** (scheduled ~`02:48Z`), unit `campaign4-p6r17-failed1-cleanup`.
  Partial manifest owns exactly the two prepared IDs. Keep it armed until actual
  cleanup is verified.
- **Host inventory:** `host-inventory-failed-1.json` filed per release; no
  rehash/stale-signature issue observed in the binding itself.

## Effect

Binding `6bf90b1d…` confirmed faithful, canonical and independently derivable
read-only; cleanup bound active for the exact IDs; no task/launch/send/mutation.
Returned to Tern for the separate exact live signature.
