# Anvil deck route check: `/api/login` is dead-code, not a live gap

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Finding

The deck bundle contains a client call to `POST /api/login`, but the current
served deck surface has no login page/form that can reach it.

Evidence:

- `deck/app.js:113-122` binds `#login-form` and submits
  `POST /api/login`.
- `server.py:2488-2509` has no `/api/login` POST route; unknown POST routes
  return 404 before auth.
- `deck/` contains `index.html`, assets, icons, manifest, and service worker,
  but no `login.html`.
- `deck/index.html` contains no `#login-form`; its password fields are for
  sudo approval and AMT key entry, not login.
- The live `/deck` token flow is separate: `app.js` asks for a deck token in
  place when no token is saved, then appends `?token=` to API calls.

## Interpretation

This is not a current user-visible route failure for `/deck`. It is leftover
shared/login code in `app.js`. A static client/server route diff will flag it,
but it should be classified as dormant unless a `login.html` page or
`#login-form` is reintroduced.

## Follow-up rule for route checks

When a client route appears missing server-side, classify it as:

- **live gap** if reachable from served DOM or active event wiring;
- **dormant gap** if the call exists but no served element/page can trigger it;
- **intentional stub** if the server answers a benign not-applicable response.

Under that rule, `/api/amt/connect` remains a live gap because the served
preferences DOM exposes the AMT key controls; `/api/login` is dormant.
