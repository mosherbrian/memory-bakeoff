# Anvil deck route check: patch readiness drift check

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Scope

Readiness check for the two existing patch specs:

- `team/ANVIL-DECK-TOKEN-PATCH-SPEC-20260912.md`
- `team/ANVIL-DECK-AMT-STUB-PATCH-SPEC-20260912.md`

No live deck files were changed. This artifact answers: do the specs still match
the current three local deck surfaces, or did code drift make them stale?

## Verdict

The specs are still current and apply to all three surfaces. No conflicting AMT
server route appeared, and the token defects are still present at the exact raw
URL sites named by the specs.

## Drift Check Results

| Surface | Raw message image URL | Raw gallery preview URL | Raw gallery download URL | AMT status stub |
|---|---:|---:|---:|---:|
| `conductor-chat` | `deck/app.js:1269` | `deck/app.js:3390` | `deck/app.js:3400` | `server.py:2371-2372` |
| `conductor-chat-glm-dsh` | `deck/app.js:1204` | `deck/app.js:3293` | `deck/app.js:3303` | `server.py:2044-2045` |
| `conductor-chat-cairn` | `deck/app.js:1239` | `deck/app.js:3360` | `deck/app.js:3370` | `server.py:2346-2347` |

The AMT status handler in all three servers still returns:

```json
{"connected": false, "message": "not applicable"}
```

No `function setAmtConnectAvailable` helper exists yet in any deck file, so the
AMT patch has not already been applied. No `/api/amt/connect` server route or
`do_DELETE` handler was found in the three `server.py` files, so the status-only
UI-disabling recommendation remains correct.

## Apply Order

1. Apply the token patch first. It is strictly client-side and fixes broken
   existing file/image routes without changing server behavior.
2. Apply the AMT status-only patch second. It disables unsupported controls using
   the existing status stub and avoids adding fake failure routes.
3. Run the static checks from both specs across all three surfaces.
4. Reload `/deck` and run the live smoke checks from the token and AMT specs.

## Residual Risk

The patch specs cover three independent working trees outside `memory-bake-off`.
Apply them as one coordinated slice, or the surfaces will diverge again. The
existing grep checks are enough to catch partial application before browser
smoke testing.
