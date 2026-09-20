# Anvil deck route check: message images omit the deck token

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Finding

Rendered conversation images use bare `/api/image` URLs instead of the deck
helper that appends the saved token. Under the normal `/deck` localStorage-token
flow, local image Markdown and structured image attachments will load as 401s
and be replaced with "Image unavailable" even though the file route exists.

Evidence:

- `deck/app.js:91-95` defines `deckUrl(url)`, appending `?token=...` from the
  saved deck token.
- `deck/app.js:97-110` uses that helper for ordinary JSON requests and prompts
  again on 401.
- `server.py:2133-2151` authenticates only `?token=` or `Authorization: Bearer ...`;
  it does not use cookies.
- `server.py:2264-2266` sends every GET `/api/*` route other than `/api/state`
  through `_auth()` before dispatch.
- `server.py:2322-2359` implements `/api/image`, but only after that auth gate.
- `deck/app.js:1265-1269` turns every absolute local image source into raw
  `/api/image?path=...`, with no `deckUrl(...)` wrapper.
- `deck/app.js:1272-1287` assigns that raw URL to both the image link and
  `img.src`; on load failure it replaces the element with `[Image unavailable: ...]`.
- The path is live: Markdown images are parsed in `deck/app.js:1345-1348`,
  `renderMarkdownBlocks(...)` drives normal message text at `deck/app.js:1540-1542`,
  and structured `images` arrays call `appendImage(...)` at `deck/app.js:1578`.
- By contrast, the file viewer path already gets this right with
  `deckUrl('/api/image?...')` before `fetch(...)` at `deck/app.js:2054-2056`.

## Impact

This affects the main conversation pane, not only the Files modal. A worker can
return Markdown like `![plot](/tmp/plot.png)` or a structured local image, the
server can legally serve the bytes, and the deck still fails to display it
because the browser's `<img>` request carries neither bearer header nor query
token.

## Minimal fix

Make local image URLs token-aware at the single conversion point:

```js
function localImageUrl(value) {
  if (typeof value !== 'string') return null;
  if (value.startsWith('data:image/')) return value;
  if (!value.startsWith('/')) return null;
  return deckUrl(`/api/image?path=${encodeURIComponent(value)}`);
}
```

That should cover Markdown images and structured image attachments without
changing the server auth contract. The prior gallery artifact still needs its
own fix for `/api/file` download links.

## Route-check classification

Under the Anvil route-check rule, this is a **live auth-contract gap**: the
server route is implemented and correctly authenticated, but a reachable client
render path bypasses the helper that satisfies the route's auth contract.
