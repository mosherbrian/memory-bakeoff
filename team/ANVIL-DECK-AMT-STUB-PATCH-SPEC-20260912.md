# Anvil deck route check: AMT status-only patch spec

Seat: anvil-oai
Date: 2026-09-12
Thread: `RD-THREADS.md` / anvil-oai / web-surface checks of deck UI routes

## Scope

Patch specification only. No live deck files were changed in this pulse.

Targets:

- `/home/bmosher/conductor-chat/deck/app.js`
- `/home/bmosher/conductor-chat-glm-dsh/deck/app.js`
- `/home/bmosher/conductor-chat-cairn/deck/app.js`

Purpose: close the AMT connect live gap from
`team/ANVIL-DECK-ROUTE-CHECK-20260912.md` without pretending AMT storage exists
in these conductor-chat servers.

## Current State

All three deck surfaces expose AMT save/disconnect controls, and all three
servers implement only `GET /api/amt/status`.

| Surface | Status call | Save call | Clear call | Status handler |
|---|---:|---:|---:|---:|
| `conductor-chat` | `deck/app.js:3471` | `deck/app.js:3532` | `deck/app.js:3539` | `server.py:2371` |
| `conductor-chat-glm-dsh` | `deck/app.js:3369` | `deck/app.js:3430` | `deck/app.js:3437` | `server.py:2044` |
| `conductor-chat-cairn` | `deck/app.js:3441` | `deck/app.js:3502` | `deck/app.js:3509` | `server.py:2346` |

Markup exposes the controls directly:

| Surface | Save button | Clear button |
|---|---:|---:|
| `conductor-chat` | `deck/index.html:285` | `deck/index.html:286` |
| `conductor-chat-glm-dsh` | `deck/index.html:264` | `deck/index.html:265` |
| `conductor-chat-cairn` | `deck/index.html:285` | `deck/index.html:286` |

No server has a `do_DELETE` handler, and `/api/amt/connect` is not a supported
route in any of the three servers.

## Recommended Patch

Keep `GET /api/amt/status` as the single source of truth. When it returns
`connected: false` with `message: "not applicable"`, disable the key input,
Save, Disconnect, and tools-enabled checkbox. Leave Refresh enabled so the UI
can re-check if a future server gains AMT support.

Add a small helper near the AMT functions in each `deck/app.js`:

```js
function setAmtConnectAvailable(enabled) {
  $('#pref-amt-key')?.toggleAttribute('disabled', !enabled);
  $('#pref-amt-save')?.toggleAttribute('disabled', !enabled);
  $('#pref-amt-clear')?.toggleAttribute('disabled', !enabled);
  $('#pref-amt-tools-enabled')?.toggleAttribute('disabled', !enabled);
}
```

Then in `refreshAmtStatus()`, inside the `if (!result.connected) { ... }` block,
set availability from the status message:

```js
const available = result.message !== 'not applicable';
setAmtConnectAvailable(available);
```

In the connected branch, re-enable controls:

```js
setAmtConnectAvailable(true);
```

Optional polish: if `available === false`, clear the key field value so a typed
secret is not left in a disabled box.

## Why This Patch

This matches the current server contract and avoids adding no-op `POST`/`DELETE`
routes whose only purpose would be to fail more neatly. It also keeps future AMT
support possible: if a server later returns a real disconnected-but-supported
status, the existing Save and Disconnect handlers can be used after adding the
server routes.

## Validation

Static checks after patching:

```bash
for d in ~/conductor-chat ~/conductor-chat-glm-dsh ~/conductor-chat-cairn; do
  grep -n "function setAmtConnectAvailable" "$d/deck/app.js"
  grep -n "setAmtConnectAvailable(available)" "$d/deck/app.js"
  grep -n "setAmtConnectAvailable(true)" "$d/deck/app.js"
done
```

Expected: one hit for each grep in each surface.

Live smoke:

1. Open `/deck` preferences on each surface.
2. Confirm AMT status reads `not applicable` or equivalent.
3. Confirm API key input, Save, Disconnect, and tools-enabled checkbox are
   disabled; Refresh remains enabled.
4. Click Refresh and confirm no route-error toast appears.
5. Confirm no browser request to `POST /api/amt/connect` or `DELETE /api/amt/connect`
   is possible through the disabled controls.

## Non-goals

This patch does not implement AMT key storage. If AMT is intended to work in
these decks, the server must first add an explicit storage/clear contract and a
`do_DELETE` path or alternate POST route.
