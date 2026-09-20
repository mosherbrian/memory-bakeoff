# Anvil deck route check: AMT connect controls

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Finding

The deck UI exposes AMT connect/disconnect controls that call routes the
conductor-chat server does not implement.

Evidence:

- `deck/app.js:3532` calls `POST /api/amt/connect` when saving an AMT key.
- `deck/app.js:3539` calls `DELETE /api/amt/connect` when clearing the key.
- `server.py:2371` implements only `GET /api/amt/status`, returning
  `{"connected": false, "message": "not applicable"}`.
- `server.py:2494-2499` has a POST allowlist for deck routes; it does not
  include `/api/amt/connect`.
- No `do_DELETE` handler was found in `server.py`.

## Impact

The preferences panel can render an AMT key workflow, but saving a key will
404 before `_deck_post` runs, and clearing a key has no DELETE handler. The
status call is intentionally benign, but the controls are not inert: they show
toasts and depend on routes that cannot succeed.

## Minimal fix options

1. Hide or disable the AMT key controls when `/api/amt/status` reports
   `connected: false` with `message: "not applicable"`.
2. Or add explicit no-op `POST` and `DELETE /api/amt/connect` handlers that
   return a clear 409/501 JSON response, so the UI can show "not supported on
   this deck" instead of route failure.
3. If AMT is intended to work here, add `/api/amt/connect` to the server's
   deck route allowlist and implement the storage/clear path before exposing
   the controls.

Recommended for now: option 1. It matches the current server contract and keeps
the preferences surface from advertising an unavailable integration.
