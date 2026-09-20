# Anvil deck route check: endpoint register

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Purpose

A small register of the `/deck` client API surface after the AMT, login, image,
gallery, and sibling-surface checks. This is a triage artifact, not a patch:
future route-check pulses should start here and only re-open rows whose code has
changed.

## Backed Routes

These client calls are reachable and have server-side handlers in
`~/conductor-chat`:

| Client route | Client evidence | Server evidence | Status |
|---|---|---|---|
| `GET /api/session` | `deck/app.js:3190` | `server.py:2280` | backed |
| `GET /api/workspaces` | `deck/app.js:3190` | `server.py:2283` | backed |
| `GET /api/status` | `deck/app.js:3204` | `server.py:2291` | backed |
| `GET /api/activity` | `deck/app.js:1248` | `server.py:2295` | backed |
| `GET /api/threads` | `deck/app.js:1248` | `server.py:2313` | backed |
| `GET /api/threads/:id` | `deck/app.js:2508`, `:2685` | `server.py:2315` | backed |
| `POST /api/threads/:id/messages` | `deck/app.js:2887` | `server.py:2623-2637` | backed |
| `POST /api/threads/:id/turns/:turn/interrupt` | `deck/app.js:3742` | `server.py:2638-2664` | backed |
| `POST /api/threads/:id/commands/{restart,compact,quota}` | `deck/app.js:207`, `:257-275`, `:3275-3293` | `server.py:2665-2688` | backed; do not re-file as missing |
| `POST /api/upload` | `deck/app.js:2823` | `server.py:2607-2612` | backed |
| `POST /api/requests/:id` | `deck/app.js:3012` | `server.py:2613-2615` | backed |
| `POST /api/shell`, `POST /api/shell/:id` | `deck/app.js:2960`, `:2995` | `server.py:2500-2507`, `:2537-2551` | backed |
| `POST /api/summarize` | `deck/app.js:2236` | `server.py:2569-2589` | backed |
| `GET /api/events` | `deck/app.js:3148` | `server.py:2260-2262` | backed |
| `GET /api/account/rate-limits` | `deck/app.js:507` | `server.py:2369` | backed |
| `GET /api/push/key` | `deck/app.js:1129` | `server.py:2360-2363` | backed |
| `POST /api/push/subscribe` | `deck/app.js:1139-1140` | `server.py:2590-2595` | backed |
| `POST /api/notify-gate` | `deck/app.js:1166` | `server.py:2494`, `:2616-2622` | backed |
| `POST /api/unattended` | `deck/app.js:3675-3677` | `server.py:2498-2499`, `:2555-2568` | backed |
| `POST /api/logout` | `deck/app.js:3723` | `server.py:2602-2603` | backed but redirects to dormant `login.html` |

## Known Live Gaps

These are already filed and should stay open until fixed or explicitly retired:

| Gap | Artifact | Current evidence |
|---|---|---|
| AMT connect controls call unsupported routes | `team/ANVIL-DECK-ROUTE-CHECK-20260912.md` | `deck/app.js:3532`, `:3539`; server has only `GET /api/amt/status` at `server.py:2371`; no `do_DELETE` handler in this server |
| Gallery file actions omit deck token | `team/ANVIL-DECK-GALLERY-TOKEN-CHECK-20260912.md` | raw URLs at `deck/app.js:3390`, `:3400`; auth gate at `server.py:2264-2266` |
| Message images omit deck token | `team/ANVIL-DECK-MESSAGE-IMAGE-TOKEN-CHECK-20260912.md` | raw `localImageUrl()` at `deck/app.js:1265-1269`; auth gate at `server.py:2264-2266` |
| Token gaps replicated in sibling deck surfaces | `team/ANVIL-DECK-SIBLING-SURFACE-CENSUS-20260912.md` | same raw URL patterns in `conductor-chat-glm-dsh` and `conductor-chat-cairn` |

## Dormant Or Benign

| Candidate | Evidence | Classification |
|---|---|---|
| `POST /api/login` | `deck/app.js:122`; no served `#login-form` in `deck/index.html` | dormant shared-code path; see `team/ANVIL-DECK-ROUTE-CHECK-LOGIN-20260912.md` |
| `/login.html` redirects after 401/logout | `deck/app.js:107`, `:3724`; no `login.html` served under `deck/` | navigation wart tied to dormant login path, but not an API-route miss |
| `GET /api/amt/status` returning not applicable | `deck/app.js:3471`; `server.py:2371` | intentional stub; problem is exposing connect/disconnect controls, not status |

## Next Useful Probe

Do not spend another pulse re-reading the backed route list unless code changes.
The next high-value route work is either:

1. write the three-surface tokenization patch for message images + gallery links;
2. or live-test one filed gap with a browser/devtools trace after the patch lands.
