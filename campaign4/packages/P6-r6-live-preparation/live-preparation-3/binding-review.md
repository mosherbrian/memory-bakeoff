# P6-r6-live-preparation — binding witness (independent, read-only)

- **Reviewer:** corvid (independent; duty owner cairn)
- **Date:** 2026-09-22, canonical root `/home/bmosher/memory-bake-off`
- **Dispatch:** `binding-check-dispatch.json`, action `P6r6-bindingcheck-1`,
  recorded `2026-09-22T04:16:16Z`, deadline `2026-09-22T04:21:16Z`
- **Grant:** 5m charged to the existing held 15m witness (10m remains); no new
  verifier allocation
- **Advisory pin:** `@0846c7f` (dispatch brief); plan `1a536965…`
- **Manifest under review:** `live-preparation-3/launch-manifest-reconciled.json`
  sha256 `b3eaf3cc8d485942404e6e318bdfc759bd024486c38a995d6c0c6152c6a2e2bf`
  (`b3eaf3cc8d48`) — **recomputed, matches**
- **Limits honored:** no wakes to fixture seats, no restart/launch/cleanup, no
  core edits, no Stage C. Purely read-only.

## Verdict

**BINDING VERIFIED** — recorded IDs, current registry profile/lane/workdirs,
both live Unix sockets and incarnations, plan hash, and the no-task argv all
reconcile. The original tool failure is preserved (not retroactively PASSed).

## Checks (all read-only, this pass)

- **Manifest integrity:** `sha256sum` = `b3eaf3cc8d48…`, matching the dispatch
  pin; `launcher_source = live-agent-deck`; `profile = campaign4`.
- **Exact returned IDs:** worker `085360c2-1790050499`, verifier
  `caac0ba3-1790050500`. Both appear verbatim in the persisted raw stdout
  (`launch-manifest.json.raw.{worker,verifier}.json`, `rc: 0`), i.e. identity
  is the launch response id, not a title. Titles `p6-fixture-worker-p3` /
  `p6-fixture-verifier-p3` are distinct from the main seats and match the
  release-3 names.
- **Current registry:** `agent-deck list --json` shows both IDs with
  `profile=campaign4`, worker command `/home/bmosher/.config/agent-deck/acp-go`,
  verifier command `/home/bmosher/.config/agent-deck/acp-go-deepseek`, and
  workdirs `/tmp/p6r6-prep3-20260922T041423Z/workdirs/p6-fixture-{worker,verifier}-p3`
  — exactly the manifest values. Status idle/waiting. Registry total 7 (four
  main seats + stopped prepare-2 fixture `0e734b30` retained as evidence + the
  two p3 fixtures).
- **Sockets real + incarnation:** both socket paths exist and
  `S_ISSOCK=True`; worker ino `23642717`, verifier ino `23642715`, and mtimes
  `1790050501.2286367` / `1790050501.2193313` match the manifest
  `incarnation` blocks exactly — no stale/mismatched socket.
- **Plan hash:** `live-fixture-plan.json` = `1a536965f0db4cf092a08777dfb25518262b5d4f38c5c9f8f863e181bbefb072`,
  matching `plan_sha256`.
- **No task message:** the recorded `preparation_argv` for both sides ends
  `… --idle-timeout=25m -json`; no `-m`/`-message` token anywhere. No fixture
  turn was sent.
- **Missing idle stream accounted for:** `stream_path` is under the inventoried
  producer root `/home/bmosher/.config/agent-deck/acp-stream`, whose files are
  named `<session_id>.jsonl`. Neither p3 id has a `.jsonl` yet
  (`stream_exists:false`), consistent with an idle runtime that has had no
  turns — the mapping is inspected, not assumed.
- **Preserved failure:** `live-preparation-3/stdout.txt` still records the tool
  rc3 `E_LAUNCH_PARTIAL` (`bind-worker failed after 2 sides completed`), with
  `launch-manifest.json.partial` and the raw records retained. The reconciled
  manifest explicitly states `original_tool_result: preserved partial rc3, not
  retrospectively PASS` and `stage_c: HELD`. The reconciliation (immediate
  post-launch `E_NO_SOCKET` vs. now-observed real sockets; no retry / no
  fabricated stream / no task) is independently consistent with the artifacts.

## Non-blocking observations

- The reconciled manifest was written by tern (`reconciliation.actor`), not by
  the tool; its bindings are nevertheless reproducible from the raw launch
  responses and live registry/sockets, which I did.
- `identity_source` is prose
  (`"launch-response-id + registry + current socket reconciliation"`); the
  underlying evidence (raw stdout id + registry + socket inode) is what I
  bound, so this is descriptive, not a claim of a single mechanism.

## Effect

Verdict **BINDING VERIFIED** bound to manifest
`b3eaf3cc8d485942404e6e318bdfc759bd024486c38a995d6c0c6152c6a2e2bf`, plan
`1a536965…`, IDs worker `085360c2-1790050499` / verifier `caac0ba3-1790050500`,
under contract `f2b7df48…` @ `e32c0dc`. No fixture task, wake, restart, new
launch, cleanup, core edit or Stage C occurred. Cairn's existing cleanup bound
`04:39Z` is retained. Returned to Tern (and cairn).
