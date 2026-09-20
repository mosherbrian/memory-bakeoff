# Anvil deck route check: gallery file links omit the deck token

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Finding

The served `/deck` gallery can list files through the authenticated API, but
its rendered preview/open/download links omit the deck token. In the normal
localStorage-token flow, those bare `/api/file` and `/api/image` URLs will 401
when opened by the browser as anchors or image loads.

Evidence:

- `deck/app.js:91-95` defines `deckUrl(url)`, appending `?token=...` from the
  saved deck token.
- `deck/app.js:97-110` routes normal `request(...)` calls through `deckUrl(...)`
  and re-prompts on 401.
- `server.py:2133-2151` accepts only `?token=` or `Authorization: Bearer ...`;
  it does not use cookies.
- `server.py:2264-2266` gates all GET `/api/*` routes other than `/api/state`
  through `_auth()`.
- The older file modal gets this right: `deck/app.js:1993` uses `deckUrl(...)`
  for downloads, and `deck/app.js:2054-2056` uses `deckUrl(...)` before fetching
  an inline preview.
- The gallery gets it wrong: `deck/app.js:3390` sets `preview.href` to raw
  `/api/image?...` or `/api/file?...`, `deck/app.js:3393` uses that raw URL as
  `img.src`, `deck/app.js:3399` reuses it for Open, and `deck/app.js:3400` sets
  Download to raw `/api/file?...`.
- `deck/app.js:3404-3406` loads the gallery list with `request('/api/gallery...')`,
  so the list itself succeeds while the child file actions fail.

## Impact

This is a live gap, not dormant code: `deck/index.html:35-36` exposes the Files
button, and `deck/index.html:306-315` serves the gallery modal. A user can open
the gallery, see file cards, and then get broken thumbnails/open/downloads if
the page is authenticated by stored deck token rather than a token baked into
those individual URLs.

## Minimal fix

Wrap the gallery URLs the same way the file modal already does:

```js
const previewUrl = deckUrl(file.isImage
  ? `/api/image?path=${encodeURIComponent(file.path)}`
  : `/api/file?path=${encodeURIComponent(file.path)}`);
const downloadUrl = deckUrl(`/api/file?path=${encodeURIComponent(file.path)}`);
```

Then assign `preview.href`, `img.src`, `open.href`, and `download.href` from
those tokenized values.

## Route-check classification

Under the previous Anvil rule, this is a **live gap**: reachable from served DOM,
server route exists, auth contract is correct, but one UI surface bypasses the
client helper that satisfies the contract.
