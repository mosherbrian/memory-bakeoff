# Anvil deck route check: three-surface token patch spec

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Scope

Patch specification only. No live deck files were changed in this pulse.

Targets:

- `/home/bmosher/conductor-chat/deck/app.js`
- `/home/bmosher/conductor-chat-glm-dsh/deck/app.js`
- `/home/bmosher/conductor-chat-cairn/deck/app.js`

Purpose: close the two token gaps filed in:

- `team/ANVIL-DECK-MESSAGE-IMAGE-TOKEN-CHECK-20260912.md`
- `team/ANVIL-DECK-GALLERY-TOKEN-CHECK-20260912.md`
- `team/ANVIL-DECK-SIBLING-SURFACE-CENSUS-20260912.md`

## Patch 1: Message Images

In each target file, change `localImageUrl(value)` from returning a raw
`/api/image` URL to returning a tokenized URL.

Current sites:

| Surface | Line |
|---|---:|
| `conductor-chat` | `deck/app.js:1269` |
| `conductor-chat-glm-dsh` | `deck/app.js:1204` |
| `conductor-chat-cairn` | `deck/app.js:1239` |

Replacement:

```js
return deckUrl(`/api/image?path=${encodeURIComponent(value)}`);
```

Why this works: `appendImage(...)` already funnels Markdown images and structured
image attachments through `localImageUrl(...)`, so the fix covers both without
changing server auth or render logic.

## Patch 2: Gallery Links

In each target file, replace the raw gallery `preview.href` / `download.href`
construction with tokenized variables.

Current sites:

| Surface | Raw preview | Raw download |
|---|---:|---:|
| `conductor-chat` | `deck/app.js:3390` | `deck/app.js:3400` |
| `conductor-chat-glm-dsh` | `deck/app.js:3293` | `deck/app.js:3303` |
| `conductor-chat-cairn` | `deck/app.js:3360` | `deck/app.js:3370` |

Replacement shape inside `for (const file of files) { ... }`, immediately before
assigning `preview.href`:

```js
const previewUrl = deckUrl(file.isImage
  ? `/api/image?path=${encodeURIComponent(file.path)}`
  : `/api/file?path=${encodeURIComponent(file.path)}`);
const downloadUrl = deckUrl(`/api/file?path=${encodeURIComponent(file.path)}`);
preview.href = previewUrl;
```

Then set:

```js
const download = document.createElement('a'); download.href = downloadUrl; download.textContent = 'Download';
```

`img.src = preview.href` and `open.href = preview.href` can stay as-is after
`preview.href` is tokenized.

## Validation

Static post-patch checks:

```bash
for d in ~/conductor-chat ~/conductor-chat-glm-dsh ~/conductor-chat-cairn; do
  grep -n "return deckUrl(.*api/image" "$d/deck/app.js"
  grep -n "const previewUrl = deckUrl" "$d/deck/app.js"
  grep -n "download.href = downloadUrl" "$d/deck/app.js"
done
```

Expected: one hit for each grep in each surface.

Negative checks:

```bash
for d in ~/conductor-chat ~/conductor-chat-glm-dsh ~/conductor-chat-cairn; do
  grep -n 'return `/api/image?path=' "$d/deck/app.js" || true
  grep -n 'preview.href = file.isImage' "$d/deck/app.js" || true
  grep -n 'download.href = `/api/file?path=' "$d/deck/app.js" || true
done
```

Expected: no hits.

Live smoke after deployment/reload:

1. Open `/deck` using the normal saved-token flow, without adding `?token=` to
   the page URL manually.
2. Send or load a message containing a local Markdown image path that is inside a
   session workspace, for example `![probe](/absolute/path/to/image.png)`.
3. Confirm the conversation image loads and its opened link includes `token=`.
4. Open Files, confirm image thumbnails load, then confirm Open and Download URLs
   include `token=` and return 200 rather than 401.

## Non-goals

This patch does not address the AMT connect controls. That is a separate live
route gap because the server intentionally implements only `GET /api/amt/status`
for this deck.
