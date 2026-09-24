# P13-binding-2 — independent binding review (corvid)

- **Action:** `P13-binding-2`, owner corvid, `19:13:08Z`–`19:22:12Z`; prep
  `PASS no tasks` (`prep-binding-release-2.json`). Read-only; no task/launch/cleanup.
- **Verdict: PASS.** Fresh `p13l2` fixtures bind to the current campaign4 registry
  with live socket incarnations; `bind-p13.sh` PASSes 4/4.

## Prep hashes (all match `binding-receipt-2.json`, 13/13)

`fixture-ids.txt` `7679c2fa…`, `registry-before.json` `48a9cc20…`, `cleanup.sh`
`f55fabd1…`, `prep-result.env` `f815088e…`, `worker.json` `57addf4e…`,
`verifier.json` `2b95b6c4…`, `director.json` `db9bc582…`, `duty.json` `19a11452…`,
`registry-after.json` `443eb7b1…`; all four `.stderr` empty.

## Four distinct fixtures (raw ⇄ current registry)

| role | id | title | lane | workdir | status |
|---|---|---|---|---|---|
| W | `1a36bc29-1790277147` | `p13-fixture-worker-p13l2` | `acp-go` | `.../p13-prep-p13l2/workdirs/worker` | idle |
| V | `e6f75a85-1790277148` | `p13-fixture-verifier-p13l2` | `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| D | `cb8ac44f-1790277148` | `p13-fixture-director-p13l2` | `acp-go` | `.../workdirs/director` | idle |
| U | `332c83ea-1790277148` | `p13-fixture-duty-p13l2` | `acp-go-controller` | `.../workdirs/duty` | idle |

- `fixture-ids.txt`/`prep-result.env` and the live registry agree exactly; four
  distinct ids (one `…1790277147`, three `…1790277148`); profile `campaign4`.
- **No main seats** (`0c933c75`, `493c0317`, `a79067ca`, `56513e0e`) among the
  fixtures; no tasks sent.

## Live socket incarnations (inode/mtime)

| id | inode | mtime (PDT) |
|---|---|---|
| `1a36bc29-1790277147` | `24104944` | 2026-09-24 12:12:29.156 |
| `e6f75a85-1790277148` | `24104946` | 2026-09-24 12:12:29.163 |
| `cb8ac44f-1790277148` | `24104957` | 2026-09-24 12:12:29.475 |
| `332c83ea-1790277148` | `24104962` | 2026-09-24 12:12:29.754 |

Four distinct inodes with fresh mtimes under
`/home/bmosher/.config/agent-deck/acp-sock/` — distinct incarnations.

## Pinned `bind-p13.sh` (read-only) — PASS 4/4

Each id: exactly one registry row, declared title, `campaign4`, not archived,
expected status, distinct from main seats; rc 0.

## Cleanup timer

`p13prep-cleanup-p13l2.timer` **active**; `OnCalendar=2026-09-24 20:00:00 UTC`
(`next_elapse` 13:00 PDT), exactly the receipt's `cleanup`. Removes only the
recorded exact IDs.

**PASS** with the hashes and socket facts above; returned to Tern for the live
signature. No task/launch/cleanup/edit by corvid.
