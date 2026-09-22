# P6-r10-live-recovery-matrix — failed-1 execution-binding review (independent, derive-only)

- **Reviewer:** corvid-dsh
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r10-failed-binding-1`, deadline 5m from wake
- **Artifact under check:**
  `live-preparation-failed-1/execution-binding.json` sha256
  `dca68487e2f588a46a332c139daf1cab00daa61b4dcb9689ac94f57febc7838d`
- **Scope:** derive-only schema/binding vs raw records, live registry,
  sockets/incarnations, runtime liveness; hash/derive; amendment-1 case-check
  preservation. **No task/send/launch; no package state modified.**

## Verdict

**PASS.** `dca68487…` is the true hash, first-authored from the raw records in
the canonical corrected schema, every identity reconciles to its raw launch
record, live registry and live socket incarnation, both seats are
runtime-live, and `derive-config` independently re-derives **rc0** under the
filed Tern `derive-only` signature. Amendment-1 leaves all four case checks
intact. Ready for Tern's exact live signature.

## Checks

- **Hash:** sha256(`execution-binding.json`) = `dca68487…`; matches
  `derive-only-signature.json.binding_sha256` and
  `director-derive-result.json` parent.
- **Schema:** canonical corrected shape — top-level `launcher_source`,
  `profile`, `plan_sha256`, `recorded_at`, `tool_rc3_preserved`,
  `no_tasks_sent`, `supersedes_schema_sha256`; per-side `session_id`,
  `title`, `profile`, `role_lane`, `launch_command` (lane strings),
  `workdir`, `producer_root`, `stream_path`, `socket`, `incarnation`,
  `identity_source`, `raw_record`+`raw_record_sha256`. No old summary
  (`action_id`/`raw_record_hash`). `supersedes_schema_sha256: null` is honest:
  no prior binding for these fresh identities.
- **Plan:** `plan_sha256` `1263fdf7…1fce` re-derives from the parent
  `P6-r9-observer-lifetime/stagec-plan.json`, matching the release and partial.
- **Raw records:** `raw_record_sha256` `385f1437…` and `e527e7eb…` recomputed
  byte-for-byte against `launch-manifest.json.raw.worker.json` /
  `.raw.verifier.json`. Raw stdout `session_id`/`title`/lane and partial
  records agree (`ac50c556-1790096454` worker `acp-go`,
  `679662d2-1790096454` verifier `acp-go-deepseek`; both `rc: 0`,
  `success: true`). The `E_NO_SOCKET` bind-worker partial is preserved, not
  masked.
- **Registry (live):** live `agent-deck -p campaign4 list` carries both r10f1
  rows — worker `idle`, verifier `waiting`, `profile: campaign4`, `command` =
  exact `role_lane`, `path` = exact `workdir`; the live snapshot equals
  `director-registry.json` row-for-row (13 rows). So the H2
  lane/workdir/profile checks hold.
- **Sockets/runtime liveness:** both sockets exist as real Unix sockets now;
  `(ino, mtime)` equal the binding exactly (worker `23683857 /
  1790096455.9332457`, verifier `23683864 / 1790096456.0282707`) — no rebind;
  both sessions live and not stopped/expired.
- **Derive-only:** re-ran `case_entry.py derive-config` against the signed plan
  + this binding + the filed `derive-only-signature.json` (signer tern) to a
  private `/tmp` output → **rc0**,
  `{"config": "/tmp/…", "parent_binding_sha256": "dca68487…"}`, matching
  `derived-config.json` / `director-derive-result.json`. No `run-case`, send or
  mutation.
- **Amendment-1:** `amendment-1-case-order.md` reorders Stage B
  (failed-verification, quiet-rest, then unresolved lost-completion and
  queued/ambiguous) and explicitly keeps all four matrix rows mandatory with
  unresolved cases marked NOT EXECUTED / MISSING MECHANISM — case requirements
  preserved, no source redesign. Automatic exact-ID cleanup timer remains
  active; not yet fired.

## Effect

Binding `dca68487…` confirmed faithful, canonical, runtime-live and
independently derivable read-only. Proceed to Tern's exact live signature for
failed-verification; this check neither launches nor authorizes one. Returned
to Tern.
