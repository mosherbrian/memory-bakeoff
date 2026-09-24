# P13-binding-3 — independent binding review (corvid)

- **Action:** `P13-binding-3`, owner corvid, `19:38:04Z`–`19:46:42Z`; prep
  `PASS no tasks` (`prep-binding-release-3.json`, `19:36:42Z`; proof boundary:
  director/duty passive receiver doubles, real ACP runtime/wake, real
  worker/verifier, **no human/model compliance claim**). Read-only; no
  wakes/launch/cleanup.
- **Verdict: PASS.** Fresh `p13l3` fixtures bind with correct lanes and live socket
  incarnations; `bind-p13.sh` PASSes 4/4.

## Prep hashes (13/13 match `binding-receipt-3.json`)

`fixture-ids.txt` `6cbe4bfd…`, `registry-before.json` `48a9cc20…`, `cleanup.sh`
`ccc084c6…`, `prep-result.env` `9dd2495c…`, `worker.json` `04afdab0…`,
`verifier.json` `d9c4d98a…`, `director.json` `b428f6c5…`, `duty.json` `2d2f747e…`,
`registry-after.json` `b2f27c72…`; all four `.stderr` empty.

## Four distinct fixtures (raw ⇄ current registry)

| role | id | title | lane (command) | workdir | status |
|---|---|---|---|---|---|
| W | `f7f1a506-1790278636` | `p13-fixture-worker-p13l3` | real `acp-go` | `.../p13-prep-p13l3/workdirs/worker` | idle |
| V | `8ea84949-1790278636` | `p13-fixture-verifier-p13l3` | real `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| D | `7f67ddd2-1790278636` | `p13-fixture-director-p13l3` | pinned `plans/acp-passive-lane` | `.../workdirs/director` | idle |
| U | `1dbdc692-1790278636` | `p13-fixture-duty-p13l3` | pinned `plans/acp-passive-lane` | `.../workdirs/duty` | idle |

- Four distinct ids; profile `campaign4`; **no main seats** among the fixtures; no
  tasks sent.
- **W/V are real model lanes** (`acp-go`, `acp-go-deepseek`); **D/U use the pinned
  passive lane** which `exec`s the real `acp-worker` with `passive-acp-engine.py`.

## Runtime/lane pins (vs release)

- `plans/acp-passive-lane` = `8516171dda97093f662c409773a61f2bd0b61cba2a512419b73a606f731a2441`;
  `plans/passive-acp-engine.py` = `9d987847712c5c3ad0282658e5c08984e39a4f07d8faed198994345d041d6b61`;
  real runtime `/home/bmosher/.config/agent-deck/acp-worker` = `6871ceb1fa15e3b744c29b3aacde59f8c77a9ca54285b4ba954859f8fbb64d02`.
  All three appear in `prep-binding-release-3.json` and match the canonical
  14-file manifest. The lane unsets `ACP_AUTO_APPROVE`/`ACP_MODE`.

## Live socket incarnations (inode/mtime)

| id | inode | mtime (PDT) |
|---|---|---|
| `f7f1a506-1790278636` | `24109777` | 2026-09-24 12:37:17.576 |
| `8ea84949-1790278636` | `24109781` | 2026-09-24 12:37:17.612 |
| `7f67ddd2-1790278636` | `24109762` | 2026-09-24 12:37:16.918 |
| `1dbdc692-1790278636` | `24109770` | 2026-09-24 12:37:17.204 |

Four distinct inodes with fresh mtimes under `…/acp-sock/` — distinct incarnations.

## Pinned `bind-p13.sh` (read-only) — PASS 4/4

Each id: exactly one registry row, declared title, `campaign4`, not archived,
expected status, distinct from main seats; rc 0.

## Cleanup / bounds

- `p13prep-cleanup-p13l3.timer` **active**; `OnCalendar=2026-09-24 20:25:00 UTC`
  (`next_elapse` 13:25 PDT), exactly the receipt's fallback.
- `latest_live_start` `20:05:00Z` (before the 20:25 cleanup); no live before the
  signed release.

**PASS** with the hashes, lanes and socket facts above; returned to Tern for the
live signature. No wake/launch/cleanup/edit by corvid.
