# P13-binding-1 — independent binding review (corvid)

- **Action:** `P13-binding-1`, owner corvid, `18:17:08Z`–`18:26:21Z`; prep
  `PASS no tasks sent`. Read-only; no launch/wake/cleanup/live.
- **Verdict: PASS.** Four distinct prepared fixtures bind to the current campaign4
  registry with live socket incarnations; `bind-p13.sh` PASSes 4/4.

## Prep hashes (all match `binding-receipt-1.json`)

`fixture-ids.txt` `c5f9944b…`, `registry-before.json` `48a9cc20…`, `cleanup.sh`
`1dd48667…`, `prep-result.env` `53b75f24…`, `worker.json` `275ec97b…`,
`verifier.json` `98944b3f…`, `director.json` `11455275…`, `duty.json` `420cfe9f…`,
`registry-after.json` `1cbaef2a…`; all four `.stderr` empty.

## Four distinct fixtures (raw ⇄ current registry)

| role | id | title | lane | workdir | status |
|---|---|---|---|---|---|
| W | `f2afc12a-1790273800` | `p13-fixture-worker-p13l1` | `acp-go` | `.../workdirs/worker` | idle |
| V | `7d079221-1790273800` | `p13-fixture-verifier-p13l1` | `acp-go-deepseek` | `.../workdirs/verifier` | waiting |
| D | `e570eee6-1790273800` | `p13-fixture-director-p13l1` | `acp-go` | `.../workdirs/director` | idle |
| U | `19296a76-1790273801` | `p13-fixture-duty-p13l1` | `acp-go-controller` | `.../workdirs/duty` | idle |

- `fixture-ids.txt`/`prep-result.env` and the live registry agree exactly; four
  distinct ids (three `…1790273800`, one `…1790273801`); profile `campaign4`.
- **No main seats** (`0c933c75`, `493c0317`, `a79067ca`, `56513e0e`) among the
  fixtures; no tasks were sent.

## Pinned `bind-p13.sh` (read-only) — PASS 4/4

```
PASS W p13-fixture-worker-p13l1   f2afc12a-1790273800 (socket .../acp-sock/f2afc12a-1790273800.sock)
PASS V p13-fixture-verifier-p13l1 7d079221-1790273800 (socket .../acp-sock/7d079221-1790273800.sock)
PASS D p13-fixture-director-p13l1 e570eee6-1790273800 (socket .../acp-sock/e570eee6-1790273800.sock)
PASS U p13-fixture-duty-p13l1     19296a76-1790273801 (socket .../acp-sock/19296a76-1790273801.sock)
```
Each id has exactly one registry row, declared title, `campaign4`, not archived,
idle/expected status, distinct from main seats; rc 0.

## Socket incarnation facts (current)

Four live per-seat unix sockets exist under
`/home/bmosher/.config/agent-deck/acp-sock/`, mode `srw-------`, one per fixture id
(`f2afc12a…`, `7d079221…`, `e570eee6…`, `19296a76…`) — distinct incarnations.

## Cleanup timer

`p13prep-cleanup-p13l1.timer` **active**; `OnCalendar=2026-09-24 19:00:00 UTC`
(`next_elapse` 12:00 PDT), exactly the receipt's `cleanup` `19:00:00Z`. The timer
removes only the recorded exact IDs.

**PASS** with the hashes and socket facts above; returned to Tern for the live
signature. No launch/wake/cleanup/live/edit by corvid.
