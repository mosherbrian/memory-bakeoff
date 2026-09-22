# P6-r8-case-execution — binding check (independent, read-only)

- **Reviewer:** corvid
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Action:** `P6r8-bindingcheck-1`, start `2026-09-22T08:59Z`, deadline
  `2026-09-22T09:04Z`
- **Authority:** `live-preparation-1/` preparation evidence (action
  `P6r8-prepare-1`); held witness
- **Artifact under check:** `live-preparation-1/launch-manifest-reconciled.json`
  sha256 `fbfb3ca7795d2429d18f484c8a879b08bdce8241603399936d1bdd8f7639f033`
- **Scope:** read-only reconciliation vs raw launch records, registry, sockets
  and plan. No task sent, no retry, no mutation.

## Verdict

**PASS.** The reconciled manifest `fbfb3ca7795d…` is the true hash of the
reconciled file, and every identity/route it declares is independently
corroborated by the raw launch records, the post-launch registry snapshot, the
live Unix sockets and the signed plan. The tool's rc3 partial launch
(`E_LAUNCH_PARTIAL`, `E_NO_SOCKET`) is preserved, not masked.

## Checks

- **Hash:** sha256(`launch-manifest-reconciled.json`) =
  `fbfb3ca7795d2429…9f033`, matching the declared reconciled hash.
- **Worker identity:** `6c0b6725-1790067489`, title
  `p6-fixture-worker-r8p1`, lane `/home/bmosher/.config/agent-deck/acp-go`,
  `identity_source: launch-response-id` — identical in
  `launch-manifest.json.raw.worker.json` (stdout `id`/`session_id`,
  `success: true`), in `launch-manifest.json.partial` (worker.session_id) and
  in `post-registry.txt` (`p6-fixture-worker-r8p1 … 6c0b6725-179`).
- **Verifier identity:** `ed54bf3d-1790067490`,
  `p6-fixture-verifier-r8p1`, lane `acp-go-deepseek` — identical in the raw
  verifier record (`success: true`), the partial and the registry
  (`ed54bf3d-179`).
- **Sockets:** both declared sockets exist and are real Unix sockets
  (`S_ISSOCK` true): worker `ino=23658978 mtime=1790067491.2928183`, verifier
  `ino=23658983 mtime=1790067491.3716857` — exactly the `ino`/`mtime` the
  reconciled manifest records. No socket name mismatch with the raw argv.
- **Registry:** `post-registry.txt` lists both fixtures under `workdirs` at the
  p6r8 prep root `/tmp/p6r8-prep-20260922T085719Z/...`, distinct from the stale
  p6r6 fixture rows; no collision with any existing seat.
- **Plan:** `plan_sha256` `1263fdf79cdfe2fdcd59116cd5c5acd69489091972a83a730eca8101e43a1fce`
  re-derives from `stagec-plan.json` and matches the partial manifest.
- **Honest failure preserved:** the tool returned rc3
  `E_LAUNCH_PARTIAL` / `E_NO_SOCKET`; the partial manifest, raw records and
  `no_tasks_sent: true` retain that it was a partial launch reconciled with
  cleanup, not a retried or hidden success. Statuses (worker `idle`, verifier
  `waiting`) are consistent with a bound-but-unstarted pair.

## Effect

Binding confirmed read-only: `fbfb3ca7795d…` reconciled manifest is faithful
to raw ids, registry, sockets and plan. No live task was sent and no state was
modified. Returned to cairn; any launch/start remains a separate director
gate.
