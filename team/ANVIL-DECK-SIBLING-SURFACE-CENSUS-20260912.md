# Anvil deck route check: sibling surface census

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Scope

Static census across the three local conductor-chat deck surfaces:

- `/home/bmosher/conductor-chat`
- `/home/bmosher/conductor-chat-glm-dsh`
- `/home/bmosher/conductor-chat-cairn`

Question: are the prior Anvil token findings isolated to one checkout, and is
the slash-command route another missing server route?

## Result

The two token findings are shared across all three deck surfaces. The slash
command route is not a gap: it is client-reachable and server-backed in all
three.

## Evidence Matrix

| Surface | Message image raw `/api/image` | Gallery raw file/image links | Older file viewer tokenized | Slash command route backed |
|---|---:|---:|---:|---:|
| `conductor-chat` | `deck/app.js:1269` | `deck/app.js:3390`, `:3400` | `deck/app.js:1993`, `:2054`, `:2193` | client `deck/app.js:207`, server `server.py:2665` |
| `conductor-chat-glm-dsh` | `deck/app.js:1204` | `deck/app.js:3293`, `:3303` | `deck/app.js:1912`, `:1973`, `:2112` | client `deck/app.js:206`, server `server.py:2302` |
| `conductor-chat-cairn` | `deck/app.js:1239` | `deck/app.js:3360`, `:3370` | `deck/app.js:1963`, `:2024`, `:2163` | client `deck/app.js:207`, server `server.py:2632` |

Server auth shape is also shared:

- `conductor-chat`: `_auth` at `server.py:2132`, GET `/api/*` gate at `:2264`,
  `/api/file`/`/api/image` implementation at `:2322`.
- `conductor-chat-glm-dsh`: `_auth` at `server.py:1825`, GET `/api/*` gate at
  `:1944`, `/api/file`/`/api/image` implementation at `:1995`.
- `conductor-chat-cairn`: `_auth` at `server.py:2125`, GET `/api/*` gate at
  `:2246`, `/api/file`/`/api/image` implementation at `:2297`.

## Interpretation

The minimal token fixes should be ported as a small three-surface patch, not
applied only to `~/conductor-chat`:

1. Wrap `localImageUrl()`'s `/api/image` return with `deckUrl(...)` in all
   three `deck/app.js` files.
2. Tokenize gallery preview/open/download URLs in all three `renderGallery()`
   implementations.

The slash-command candidate should be dropped from the bug queue. The client
advertises `/restart`, `/compact`, and `/quota` through `WEBUI_COMMANDS`, and
each server has an explicit `if "/commands/" in path` dispatch block.
