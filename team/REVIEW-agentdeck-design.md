# REVIEW — agent-deck + conductor web UI

Scope correction applied (builder, 2026-09-12): the conductor UI **is** reachable
(`:8421/deck/`, `:8443/deck/` — the earlier "unreachable" finding was a wrong-port
artifact: 8420 is agent-deck's own API, not the UI) and its source **is** on this
host: `~/conductor-chat/` (server.py 2,944 lines, deck/app.js 3,731, app.css 859,
claude-theme.css 811, viewport.js 117). This review is line-level on that source.
agent-deck itself stays design/behaviour-level (stripped binary at
`~/.local/bin/agent-deck`).

Fact for Brian's checkout decision: an upstream checkout **already exists** at
`~/src/agent-deck` (git, HEAD `61cc4d68` "release: v1.16.4 (#2188)", ~67k lines of
Go). It is not "landed" — per the correction it is not the source of truth yet, so
this review does not line-review it.

Method: read in four slices, findings written as each slice closed. Every finding
carries file:line from `~/conductor-chat/`. Read-only: nothing changed.

Severity: **S1** = can grant more than the button says / can be abused by a
token-holder / can lose work. **S2** = wrong behaviour or availability coupling.
**S3** = robustness, performance, hygiene.

---

## Slice 1 — server.py: auth, route allowlist, approval path

### S1-1 `accept` can grant a PERSISTENT permission (decide fallback)
`server.py:1731-1741` — for `decision == "accept"` the matcher chain ends in
`key = opts[0]["key"]`. If the box offers no label containing allow/once/yes
(e.g. `['Always allow', 'No']`), the one-time button types the **first** option,
which is the persistent grant. The comment at 1733-1735 shows the author fought
exactly this for Claude's `['Always Allow','Allow','Reject']` ordering and fixed
it with the `exclude=("always","session")` matcher — but the fallback below it
re-opens the hole for any box whose first option is the persistent one.
Fix: when no allow-ish label matches, refuse with an error instead of falling
through to `opts[0]`.

### S1-2 `acceptForSession` silently degrades to one-time (same function)
`server.py:1729-1730` — `find("always","session") or find("allow","yes") or
opts[0]["key"]`. A box with no "always/session" label falls to `find("allow",
"yes")` → one-time allow. The button says "for session"; the grant is one turn.
Under-grant, so less dangerous than S1-1, but the UI will show "approved for
session" while the agent re-asks next call.

### S1-3 deny matcher: `"no"` is a substring
`server.py:1746` — `find("deny","reject","no","cancel")`. `any(w in low for w in
words)` matches "no" inside "Note", "Nono", "None of these". A box offering a
"Note…" option is treated as a refusal. Use word-boundary matching for short
tokens.

### S1-4 unbounded POST body / unbounded threads
`server.py:2485` (do_POST) — `n = int(self.headers.get("Content-Length", 0))`
with no cap; the body is read fully into memory. `save_upload` checks 25 MB only
**after** base64-decoding the whole body (`server.py:1331-1341`), and
`/api/deck-debug` appends the entire body to `deck-debug.jsonl` with no limit at
all (`server.py:2573-2575`). A token-holder (or anyone who learns the token —
see S2-2) can OOM the server or fill the disk.
Separately, `POST /api/threads/<id>/messages` spawns one daemon thread per call
(`server.py:2602-2603`) with no per-session in-flight guard: a double-tap sends
the prompt twice. The frontend may debounce; the API does not.

### S1-5 shell passthrough: timeout kills bash, not its children
`server.py:1408-1410` — `subprocess.run(["bash","-lc", cmd], timeout=120)`. On
timeout, bash dies; grandchildren (a `sleep 3600 &`, a build) keep running with
the server's credentials. Also `re.sub(..., count=1)` at 1404 injects `-k -S -p ''`
into the **first** sudo only — a chained second sudo prompts on a closed stdin and
fails confusingly.
What is genuinely good here: the two-step ask→run split, `sudo -k` dropping a
cached timestamp, password via stdin never written to transcript/logs
(`server.py:1386-1420`), and the HTTPS gate decided by socket type, not header
(`server.py:2529-2533`, `2515`).

### S2-1 token compared with `!=`
`server.py:2129` — `if tok != TOKEN:`. Not constant-time. Use
`hmac.compare_digest`. Low practical risk (single-user LAN) but it is one line.

### S2-2 the token travels in every URL
The embedded page fetches `/api/state?token=…` (`server.py:2082`) and stores the
link token in localStorage (`server.py:1985`); the deck client does the same
(app.js, slice 2). Query-string tokens land in browser history, proxy logs, and
any future server log. Mitigating: `log_message` is disabled
(`server.py:2658`), so the server itself logs nothing. The Authorization-header
path exists (`server.py:2127-2128`) but the clients don't use it — browsers can't
set it cross-origin without CORS, which is presumably why. Document the trade, or
move to a short-lived per-device session cookie on the HTTPS listener.

### S2-3 `/api/logout` is a no-op
`server.py:2576-2577` — returns `{"ok": true}` and changes nothing. The token is
static, shared, and never rotated by any route. "Log out" only clears one
browser's localStorage; every other device keeps working. If that is intended
(shared family token), the button should say so; if not, there is no rotation
path at all.

### S2-4 availability coupling: approvals die when agent-deck's API hiccups
`answer()` builds its allowlist from `conductors() | targets()`
(`server.py:170-172`); `targets()` returns `[]` on any exception
(`server.py:1752-1762`). A transient failure of agent-deck's `/api/sessions`
makes every approval raise `ValueError("unknown session")` — the one moment the
UI is most needed is when a 500 is most likely. Cache the last good session list
(`_sticky` exists for exactly this, `server.py:209-247`).

### S3-1 SSE loop cost + silent death
`server.py:2350-2461` — every connected client polls `sessions()` (an HTTP
round-trip to agent-deck) every 2 s, plus `deck_requests()`; N phones × M tabs
multiplies load on agent-deck. And `except Exception: return` at the end of
`_sse` swallows every error — a wedged loop just stops pushing, and the client
sits on stale state until its own resync.

### S3-2 plaintext HTTP to agent-deck carries the Bearer token
`server.py:24` (`AD = http://ZT:8420`) and every call site (253, 1756, 1767,
1885). Safe only because ZeroTier encrypts the mesh; if the host ever joins an
unencrypted network segment, the fleet token rides in the clear. Worth a comment
or a check at startup.

### S3-3 unauthenticated `/deck` embeds live state
`server.py:2204-2214` — index.html is served without auth and inlines
`window.DECK_UNATTENDED = unattended_state()`. Today that is a human string
("unattended: 2h 05m left", `server.py:480-505`) — minor. But the pattern
(inline live state into an unauthenticated page) is one edit away from leaking
more. `?debug=1` also injects debug.js into the unauthenticated page
(`server.py:2176-2178`).

### Genuinely good (slice 1)
- `download_ok` — realpath resolved **before** containment check against session
  working dirs; `..` and escaping symlinks both rejected (`server.py:447-463`).
- `answer()` — only known sessions, only keys `[1-9]` or Escape, never arbitrary
  keystrokes (`server.py:164-193`).
- `decide()` label-based matching with explicit `always/session` exclusion for
  the one-time button (`server.py:1731-1741`) — the right idea; only the
  fallbacks (S1-1/S1-2) undercut it.
- upload: basename sanitized to `[A-Za-z0-9._-]`, 25 MB cap, uuid-prefixed name
  (`server.py:1335-1340`).
- `_sticky` — never replaces a good value with nothing; survives restart
  (`server.py:209-247`).
- `with_attachments` — one line, because a newline is an Enter in the pane
  (`server.py:1351-1362`); the comment records the measured bug.
- HTTPS gates decided by `isinstance(self.connection, ssl.SSLSocket)`, not by a
  client-set header (`server.py:2529-2533`, `2515`).
- `log_message` disabled — no request log to leak query-string tokens
  (`server.py:2658`).

---

## Slice 2 — deck/app.js: turn / queue / running state machine

Context: app.js is the vendored codex-webui frontend (deck/UPSTREAM.md) with
`AGENT DECK:`-marked local patches. The state machine is one big `state` object
(app.js:134-176) driven by SSE `codex_event`s (`handleCodexEvent`, app.js:3000)
plus a 2 s resync poll while running (`startResyncLoop`, app.js:2614-2624) and
an 8-step catch-up ladder after completion (`scheduleCatchupResync`,
app.js:2605-2612: 250 ms … 30 s, each a full thread fetch).

### S2-5 a second pending approval hides the first until reconnect
`showApproval` overwrites: `state.pendingApproval = requestMessage`
(app.js:2897-2898). The server knows only one card fits and says the rest need
a marker (server.py:2285-2287); the client does keep a `pendingThreads` marker
set for the thread list (app.js:1028, 1223) — but the **card** is singular.
Sequence: session A and B both pending → B's `server_request` replaces A's card
→ user decides B → `clearApproval(B.id)` hides the drawer (app.js:2911-2918) →
**A's approval card is gone from this client**; only the thread marker says
something is pending, and tapping it does not re-open the card. `pendingRequests`
is only re-sent on `connected` (server.py:2411-2414), so A's card returns only
on a full SSE reconnect or reload. `clearApproval`'s id-guard (app.js:2913)
prevents the wrong card closing, but cannot resurrect the covered one. Fix: keep
a queue of pending requests, show the oldest, and re-show the next on
`request_resolved`.

### S2-6 "New thread" leads to a dead end
`newThread` sets `state.threadId = null` (app.js:2683-2700); the next send calls
`ensureThread` (app.js:2716-2729) → `POST /api/threads` → the server answers
409 "create the session in Agent Deck" (server.py:2578-2580). Correct by design
(sessions belong to agent-deck), but the UI offers the button and then fails
with a raw 409 toast. The button should be hidden or turned into a hint naming
the agent-deck command.

### S3-4 resync storm on a tool-heavy turn
While `state.running`, every 2 s a forced full-thread fetch (app.js:2614-2624),
and on completion eight more forced fetches over 30 s (app.js:2605-2612) — each
`/api/threads/<id>` re-parses the whole transcript server-side (slice 4). The
comment at app.js:2548-2553 shows the render churn was already fixed; the
fetches remain "the recovery path" (the `/api/state` page adds its own 2.5 s
poll, server.py:2121). On N devices watching the same long turn
this is N × ~10 full transcript parses per 30 s. A `?since=`/fingerprint query
would let unchanged fetches be cheap.

### S3-5 token in localStorage on an unauthenticated origin
`deckToken()` stores the link token in `localStorage` (app.js:23-31); the
code's own comment (app.js:40-43) states why (installed web app has no address
bar). Consequence: any script that ever runs on the `/deck` origin — the page
is served without auth (server.py:2170-2175) — can read the fleet token. This
makes XSS-on-deck == full fleet access. There is no CSP header on `/deck`
responses (server.py:2170-2230 sets only Content-Type/Cache-Control/
Service-Worker-Allowed). A `Content-Security-Policy: default-src 'self'` plus
the existing inline-script allowances would narrow that gap without breaking
the runtime-rewritten index.html (server.py:2204-2230) — though the inline
`<script>` seeds would need nonces.

### S3-6 donor residue
`initialize` prefers a workspace literally named `media-tool`
(app.js:3168) and the tip modal points at `https://agentmediatools.com/tip`
(app.js:3337, 3392-3398) — the donor app's identity. The tip link is a payment
page, not telemetry (verified: `TIP_BASE` is used only in
`openTipCheckout`), but both are dead weight in a fleet tool and the
`media-tool` preference silently reorders the workspace list for anyone who
happens to have such a directory.

### Genuinely good (slice 2)
- Queue drain moved to the running→idle **transition** in `setRunning`
  (app.js:811-835), with the comment recording the measured bug (ACP sessions
  go idle via the 2 s poll, which never drained the queue). `flushMessageQueue`
  persists after splice (app.js:361-372), so a reload mid-queue loses nothing.
- Enter/Ctrl+Enter split keyed off `html.kb` (soft keyboard present), not
  device type (app.js:3268-3278) — a tablet with a physical keyboard gets
  desktop behaviour; the comment records why.
- `clearApproval(id)` guard so a resolution for request A never closes card B
  (app.js:2911-2918); the server side emits `request_resolved` for decisions
  made in any other client (server.py:2455-2460).
- Optimistic user message is removed on send failure (app.js:2876-2884), and
  the catch path resets running/awaitingTurn/resync — no stuck spinner on a
  rejected POST.
- `openThread` stops the previous thread's resync loop first (app.js:2649-2652),
  with the comment recording the cross-thread polling bug.
- Reconnect replay: `recentEvents` filtered to the open thread, then a forced
  resync (app.js:3130-3142) — belt and braces, and the resync is the
  authoritative path (disk beats UI, app.js:2555-2585).

## Slice 3 — viewport.js + CSS cascade

### S2-9 the dark theme is offered but the cascade makes it impossible
`claude-theme.css:5` — `:root, body[data-theme][data-accent] { --bg: #faf9f5; …
--accent: #d97757; … }` re-points **every** colour token to the light Claude
palette, and the `body[data-theme][data-accent]` selector matches **whatever
value** the theme attribute holds. `app.js:392-393` always sets both
`data-theme` and `data-accent` on `<body>`, so this block (specificity 0,2,1)
beats app.css's dark block `:root, [data-theme="dark"]` (specificity 0,1,0,
app.css:1) on the same element. Picking "Dark" in Preferences changes
`body.dataset.theme` (app.js:3671-3673) and nothing else visible. The donor's
light block `[data-theme="light"]` (app.css:25) is likewise shadowed. The
author was specificity-aware — the comment at claude-theme.css:27-30 records
outranking the donor's `:root` on purpose — but did not notice the same
mechanism kills the dark theme. The server compounds it: it rewrites
`data-theme="dark"`→`"light"` and seeds the stored pref to light
(server.py:2204-2210). Fix: scope the token block to
`body[data-theme="light"][data-accent]`, or drop the theme picker's dark
option until a dark token set exists.

### S3-7 viewport.js: permanent 250 ms poll
`viewport.js:69` — `setInterval(sync, 250)` runs for the life of the page. The
comment justifies it (iOS can settle after the event window closes; rAF stops
when backgrounded), and `sync()` dirty-checks so it writes nothing at rest —
but it reads `clientHeight`/`activeElement`/`visualViewport` four times a
second forever, and background-tab timer throttling means the poll is exactly
unreliable in the state (backgrounded) that motivated it; the
`visibilitychange`/`pageshow` handlers (viewport.js:99-116) are what actually
cover the return. Keep the poll, but it is the one part of the file whose
justification does not fully hold.

### S3-10 dead hand-maintained version strings
`index.html:9,10,319` carry `?v=15` / `?v=3` / `?v=17`, but the server rewrites
every deck asset URL with an mtime-based version (server.py:2204-2230; the
regex explicitly consumes and replaces any existing `?v=…`). The comment at
server.py:2200-2203 says so. The numbers in index.html are maintenance
theatre — bumping them changes nothing.

### Genuinely good (slice 3)
- viewport.js as a whole: every block carries the **measured** failure it
  fixes (262/433 frozen pair, focus-restoration-after-blur, bfcache pageshow),
  and the final design — focus is part of the dirty-check key
  (viewport.js:36), a rAF pump with a settle window, and a blur-on-return
  with a 1 s re-catch guard (viewport.js:99-112) — is the product of iterating
  on those measurements. `html.kb` is set from focus+height, not height alone
  (viewport.js:44-45), which is what lets app.js's Enter-key split work on a
  tablet with a physical keyboard.
- `#new-thread { display: none !important }` with the reason in a comment
  (claude-theme.css:230-232) — the dead-end of S2-6 is already closed at the
  UI layer; the JS handler and the 409 remain only as a trap for anyone who
  un-hides the button.
- `prefers-reduced-motion` honoured (claude-theme.css:345, 424), `@media
  (hover: none)` enlarges touch targets (claude-theme.css:257, 438, 460),
  self-hosted variable font with `font-display: swap` and no CDN
  (claude-theme.css:33-52) — /deck makes zero outside requests.
- `color-scheme: light` set (claude-theme.css:6) so form controls and scrollbars
  match the palette.

## Slice 4 — transcript readers (server.py)

The readers: `transcript()` (server.py:40-88), `_claude_turns` (819-845),
`_codex_turns` (847-892), `_zcode_turns` (894-986), `_acp_turns` (1024-1092),
`_pi_turns` (1126-1158), dispatched by `read_session` (1220-1246). Live deltas
come from the worker sidecar via `stream_file`/`acp_file` (465-478, 590-592)
with offset tracking and truncation reset in the SSE pump (server.py:2378-2400)
and `watch_transitions` (2796-2830).

### S2-10 `transcript()` shows the newest Claude session, not the conductor's
`server.py:58-60` — `files = sorted(glob.glob(SESS_GLOB), key=os.path.getmtime)`
then `files[-1]`. `SESS_GLOB` (server.py:37-38) is **every** Claude session
under the deck home, and the pick is by mtime, not by the conductor's
`claudeSessionId`. `read_session` does it right — it keys on
`s.get("claudeSessionId")` (server.py:1224-1228) — but the conductor view used
by the hand-built page (`/api/state`, polled every 2.5 s, server.py:2121) takes
whatever Claude session was written to most recently. Any other claude session
active under that home (a worker, a manual run) silently swaps the conductor's
transcript out from under the page. The ACP branch (server.py:46-56) is
correct; the fallback branch is the hazard.

### S3-11 every read re-parses the whole file
All readers open the full JSONL and parse every line on every call; nothing is
memoized or offset-tracked (contrast the SSE pump, which tracks offsets). A
resync fetch is a full parse (slice 2's 2 s loop + 8 catch-ups), and
`/api/state` re-parses on every 2.5 s poll per client. Fine at today's sizes;
it is the first thing to break as sessions grow to tens of MB. A
`(path, mtime, size)` memo would make unchanged reads free.

### S3-12 one malformed line kills the whole thread read
`_acp_turns` indexes `d["id"]` directly in six places (server.py:1057-1079)
inside the `role == "tool"` branch; the `try` there covers only
`json.loads`. A tool record without an `id` raises `KeyError` out of
`read_session` → the whole `/api/threads/<id>` answers 502 (the do_POST
wrapper, server.py:2492-2494) — one bad line hides the entire transcript.
`d.get("id")` with a skip would contain it. The same shape (per-line try around
loads only) is shared by all readers, but the others index with `.get`.

### S3-13 token usage may double-count (verify)
`_claude_turns` sums `message.usage` from **every** record, user and assistant
(server.py:826-829). If Claude's user records carry the same request's usage as
the assistant record, the strip shows ~2× input. `_pi_turns` does the same
(server.py:1140-1143). `_codex_turns` handles the reset-to-zero running total
correctly (peak-per-run, server.py:858-872 — verified by hand against the
reset semantics in the comment). Worth a one-line check against a known session.

### Genuinely good (slice 4)
- `session_active` trusts the worker's sidecar `start`/`end` marks, not
  agent-deck's status, with the measured failure recorded (agent-deck reports
  `idle` for the whole turn of a tool=shell session — the #1978 gap,
  server.py:763-795). The last mark wins; a `start` with no `end` **is** the
  turn.
- `acp_file` keys on the agent-deck instance id with cwd-slug fallback for
  workers run outside agent-deck (server.py:465-478) — no path guessing for
  the common case.
- `_pane_for` trusts agent-deck's reported pane name and keeps the prefix guess
  only as fallback, with the rename bug recorded (server.py:99-115).
- `pending()`'s pane-scrape is heavily guarded: cursor line required, ≥2
  options, answered-box detection (anything real after the last choice → None),
  question anchored on the trailing `?` (server.py:117-162). It is the most
  brittle code in the file and the comments show each guard was earned.
- `_codex_turns` filters codex's XML-wrapped context injection and developer
  preamble out of the conversation (server.py:876-884).
- `_acp_turns` attaches tool cards **in file order** at the point the tool ran,
  and merges later `tool_call_update` records by id instead of replacing
  (server.py:1035-1080) — both fixes carry their measured symptom in comments.
- `watch_transitions`'s dead-turn tripwire: a turn ending with no reply always
  pushes, bypassing cooldown, with the 23:16 incident recorded
  (server.py:2871-2885). `_no_reply` matches `startswith`, not `contains`,
  because a report that QUOTES the tripwire line must not re-fire it
  (server.py:2716-2744).
- `summarize` backend selection: NPU first because the GPU is the bakeoff's
  measurement subject, with measured timings and a `DECK_SUMMARY_ORDER` escape
  hatch; a typo in the env falls back instead of silently disabling
  (server.py:596-626).

---

## agent-deck (design/behaviour level — needs source)

Per the scope correction this half stays behavioural. Evidence base: CLI
surface, support tickets T-001…T-008 (`~/.local/share/agent-deck/
support-tickets/`), config surface, and the conductor server's own comments
recording measured agent-deck behaviour. Note: an upstream checkout now exists
at `~/src/agent-deck` (v1.16.4) — every question below is answerable from it
once Brian lands it.

Behavioural findings (each already cost something in the field):

1. **Send confirmation is unreliable** (T-001; issue #1978). agent-deck reports
   a prompt undelivered when it cannot see a submission signal; a tool=shell
   session never produces one, so sends read as failed when they landed. The
   conductor server works around it three ways (worker socket first,
   advisory-only return code, `confirmed` flag) — server.py:1816-1889. Question
   for source: is the submission-detection table extensible per tool, or is the
   socket path the sanctioned fix?
2. **Tool re-inferred from command on restart** (T-002, T-003). A restarted
   session comes back with a re-guessed `tool` (observed: worker pinned to
   tool=codex, uncorrectable from the CLI). Question: where is the tool stored
   per session, and why does restart re-derive it?
3. **Cancel destroys in-flight writes** (T-004). Question: does the worker
   flush its sidecar/transcript on SIGTERM, or is the loss in the adapter?
4. **Status stuck / pane rebinds** (T-005; the `idle`-during-turn measurement
   at server.py:763-771). The busy-pattern table has no entry for the shell
   preset. Question: is there a per-session status source the conductor could
   poll instead of pane scraping?
5. **CLI shadow state under redirected HOME** (T-008). agent-deck resolves
   some state from the real home and some from `$HOME`; wrappers that redirect
   HOME get split state. Question: which paths are `$HOME`-relative by design?
6. **Cron/scheduling rejected** (T-006) and **no native worker pulse** (T-007):
   design gaps the conductor fills with `watch_transitions` (server.py:2796).
   Questions: would upstream take a per-session turn-boundary webhook or file
   touch? That would replace the 4 s poll loop.

What is genuinely good (behaviour level): the session/pane model is stable
enough that the conductor can build approvals, streaming, and fleet watch on
it; the `session send` / `command-center/ask` split is a real API even if its
confirmation is advisory; the web-token file is shared with this server, so
there is one credential to rotate; and the tmux pane names are reported, not
reconstructed (server.py:99-115 depends on it).

---

## Fix list, ordered (all proposals — nothing changed)

| # | Fix | Where | Effort |
|---|-----|-------|--------|
| 1 | `decide()`: no `opts[0]` fallback for `accept`; refuse when no allow-ish label matches (S1-1); word-boundary match for "no" (S1-3) | server.py:1726-1748 | ~10 lines |
| 2 | `hmac.compare_digest` for the token (S2-1) | server.py:2129 | 1 line |
| 3 | Content-Length cap in do_POST; cap `/api/deck-debug` (S1-4) | server.py:2485, 2573 | ~5 lines |
| 4 | Per-session in-flight guard on `/api/threads/<id>/messages` (S1-4) | server.py:2602-2603 | ~10 lines |
| 5 | Pending-approval queue in the client; show oldest, advance on resolve (S2-5) | app.js:2896-2918 | ~30 lines |
| 6 | Scope claude-theme token block to `data-theme="light"` or drop the dark option (S2-9) | claude-theme.css:5 | 1 line |
| 7 | `transcript()`: key on the conductor's claudeSessionId like `read_session` does (S2-10) | server.py:58-60 | ~5 lines |
| 8 | `d.get("id")` in `_acp_turns` (S3-12) | server.py:1057-1079 | 6 lines |
| 9 | Cache last-good session list for `answer()` (S2-4) via existing `_sticky` | server.py:170-172 | ~5 lines |
| 10 | CSP header on `/deck` (S3-5) — needs nonces for the inline seeds | server.py:2170-2230 | ~15 lines |
| 11 | `(path,mtime,size)` memo for transcript readers (S3-11) | server.py readers | ~15 lines |
| 12 | Kill donor residue: `media-tool` preference, tip modal (S3-6); dead `?v=` in index.html (S3-10) | app.js:3168, 3337; index.html | deletion |

Verify, not fix: S3-13 (usage double-count) — one known session settles it.

## Fix review — T-009 notification fixes (Cairn, 2026-09-13)

Scope: verify the three landed fixes (0bab969, ff7becd, 32614e4) plus the
follow-ups (aa6de90, 0f89e9f) against the code, applying T-009's own lesson
as the review rule: **any finding of the form "X was fixed" gets checked for
a second path.** Line numbers are `~/conductor-chat/` at 934f327.

### Verified fixed (not open findings)

1. **One rule for the news decision.** `_reply_is_news()` (server.py:2862)
   is pure text-in/decision-out with the three suppression cases ([quiet],
   `[cancelled by request`, machine tripwire). The normal path reads it via
   `_needs_brian` (2851 → 3102). Both doors are closed for the events that
   were buzzing: a cancel line never matches the tripwire (no dead alarm)
   AND is not news (no push); a machine-nudge death is logged-only on the
   dead door (3062-3069) AND not news on the normal door.
2. **The floor lives inside `broadcast()`.** `push.broadcast()` →
   `reserve()` stamps the clock BEFORE the send (race-safe), 180s from
   notify.json `push.minGapSeconds`. Every caller inherits it: the watcher
   drain (server.py:3136), `/api/push/test` (2597), and the ticket helper
   (`~/.config/agent-deck/ticket` → `webpush.broadcast()`, which now reports
   "queued" when held instead of lying "pushed"). The fourth sender — the
   in-page notifier — shares the SAME clock via `/api/notify-gate` →
   `push.reserve()` (2620); the old localStorage floor is gone. The old
   600s cooldown is gone rather than left to disagree.
3. **Presence skips both watcher paths.** `watching()` = a browser request
   within 90s (three cycles of the 2s poll), gated on a Mozilla user-agent
   so scripts can't fake presence (_auth, 2142-2146). Dead path and normal
   path both skip-and-log while he is watching (3075-3079, 3104-3107), and
   buzzes already queued are DROPPED if he opens the app before the floor
   lifts (3128-3134) — the right call, since a late buzz points at something
   already read.

### Findings (second-path rule applied)

**F1 — the in-page notifier carries its own weaker copy of the news rule.**
`notifyTurnComplete` (deck/app.js:1196-1208) checks only
`/^\s*\[quiet\]/` inline; it does not know about cancels or machine
tripwires. With `notifyOnComplete` on (default off), a cancelled turn or a
machine-nudge death still produces an in-page "X finished" notification —
and via `swReg.showNotification` that surfaces as a system notification
even when the tab is in the background. `markTurnComplete` (2672) fires on
every turn end, cancel included. The FLOOR is shared (good); the NEWS RULE
is not (bad). This is the two-door pattern one surface down: the phone door
got the full rule, the page door kept the first version of it. Fix
direction: one rule, one place — the page already holds the reply text, so
either ask the server (text in, decision out) or mirror all three cases.
Duplicating the rule in JS is exactly what created this divergence.

**F2 (precision note, not a defect) — "the single rule both paths read" is
loose.** The dead door reads `_no_reply` + `_dead_was_machine` (2752/2782),
not `_reply_is_news`. Functionally clean — I checked the event partition:
no event exists where the dead door pushes while the news rule would
suppress (tripwire text can never be [quiet]/a cancel line, and a cancel
line never matches the tripwire). The risk is future: an edit that adds a
case to `_reply_is_news` assuming "both doors" honour it will silently not
reach the dead door.

**F3 (trivial) — `last_push` is vestigial.** Written (3140), never read; the
comment at 3069 ("last_push is deliberately NOT touched") describes a
mechanism that no longer gates anything. Delete the variable, fix the
comment.

**F4 (one-liner, their call) — presence has a designed hole.** The ticket
helper and `/api/push/test` call `broadcast()` directly with no presence
check, so a ticket filed while he is watching /deck still buzzes the phone.
Probably intentional (a ticket is a ticket), but it is the one path where
"app open ⇒ no phone buzz" does not hold.
