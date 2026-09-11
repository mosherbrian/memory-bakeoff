# TRIAL-20260911 — worker-pi decision-memory trial: setup record + runbook

Brian-approved experiment. Extension **frozen at `e9e5621`** (commit range
`3f9498f..e9e5621`); this trial is config + process only. If the loop cannot
close without touching extension code, STOP and report — do not un-freeze.

## 0. Setup record (Part 1 — what was chosen and why)

**Mechanism: dedicated agent dir via `PI_CODING_AGENT_DIR`, injected by the
worker's launcher.** pi's project-scoped settings (`<cwd>/.pi/settings.json`)
were considered first and do exist (deep merge, arrays replace) — but the
extension reads its `perseusRecall` config from the agent-dir settings.json
directly (frozen code), so project-scoped settings would load the package
without configuring it. The dedicated agent dir covers both in one
config-only move and matches the P1/P1B study precedent.

Changed (all outside Brian's personal config; wrapper is deck config used
only by acp-pi-worker):

| Path | What |
|---|---|
| `/home/bmosher/.config/agent-deck/pi-local` | now exports `PI_CODING_AGENT_DIR=/home/bmosher/acp-pi/.pi-agent` before the unchanged `pi --model night/qwen3.8-27b-code` exec; prior version kept at `pi-local.bak-trial-20260911` |
| `/home/bmosher/acp-pi/.pi-agent/settings.json` | trial config (below) |
| `/home/bmosher/acp-pi/.pi-agent/models.json` | **symlink** → real `~/.pi/agent/models.json` (defines `night`; link, never copy) |
| `/home/bmosher/acp-pi/.pi-agent/auth.json` | **symlink** → real `~/.pi/agent/auth.json` (secrets; link, never copy) |
| `/home/bmosher/acp-pi/trial.vault` | trial vault (created on first confirmed write) |
| `/home/bmosher/acp-pi/notifications.jsonl` | pending-draft notify file (conductor polls this) |

Brian's personal sessions are untouched: the shared
`/home/bmosher/.pi/agent/settings.json` was checksummed before/after setup
(`0a073043…` both times) and nothing in his agent dir changed.

### FIX-20260911 — why deck-launched worker-pi initially missed the trial config

**Root cause (launcher/bridge, not extension):** restarting worker-pi from
the deck re-uses a stable deck instance id, and the worker client
(`acp-worker`) resumes by calling ACP `session/load` with the session id
stored in `/home/bmosher/.config/agent-deck/acp-sessions/<instance>.json`.
pi-acp resolves that id through its own persistent map
(`~/.pi/pi-acp/session-map.json`) to an **absolute session-file path** and
spawns `pi --mode rpc --session <file>`. The stored binding predated the
trial: it pointed into the OLD shared agent dir
(`~/.pi/agent/sessions/--var-home-bmosher-acp-pi--/…`), so every deck
start resumed the pre-trial conversation with its pinned config — perseus
tools absent, turns appending to the old file. `PI_CODING_AGENT_DIR`
(which enters the chain only inside `pi-local`, at the pi leaf) was
irrelevant to this: the resume is decided before pi's config is consulted.

**Fix (state-only, no source changes):** cleared worker-pi's stale deck
binding (`acp-sessions/721125ec-1788910840.json`, prior content kept in
the private evidence dir) and restarted the deck session. `resume()` found
no stored id → fresh `session/new` → pi spawned via `pi-local` → trial
agent dir.

**Verified after a real deck restart + probe turn:** banner shows
`pi-acp 0.0.33` with NO `(resumed)`; binding re-created with a NEW session
id; session file lands under
`/home/bmosher/acp-pi/.pi-agent/sessions/…/2026-09-11T21-39-32Z_01a09269….jsonl`;
pi-acp's map now points that id at the trial file (so future resumes
re-inherit the trial config correctly); a probe turn successfully drafted
via `project_perseus_remember` (draft-cda288, notify line in
`notifications.jsonl`, `trial.vault` still absent — the gate held).

**Knob for the future:** to force worker-pi onto a fresh conversation,
remove its deck binding file
`/home/bmosher/.config/agent-deck/acp-sessions/<AGENTDECK_INSTANCE_ID>.json`
while the worker is stopped and restart the deck session — it starts fresh
and re-binds on first save. Normal restarts resume the (trial) session,
which now carries the trial tool set.

Trial `perseusRecall` config: `bin` = the provenance-verified study binary;
`db` = explicit `/home/bmosher/acp-pi/trial.vault` (trial owns its data; the
7c default derivation is for production later); `workspaceHash` omitted →
derived from cwd, per-project by construction; `write.enabled: true`;
`allowAgentConfirmed: false` (7a — operator confirms everything);
`notifiers: ["in-session", "file"]` — the extension ships NO out-of-band
channel at all (Brian's scope correction: Signal is conductor-side; the
briefly-wired clawdbot channel was removed from the extension), so the
CONDUCTOR sends the Signal summons from the notify file; `notifyFile`
explicit as above; `PI_PERSEUS_RECALL` unset.

Part 1 smoke — all PASS:
- registration in a real worker-pi session (`pi-local -p`): extension loads
  from the trial agent dir, registers all four tools (stderr receipt:
  `~/.local/share/memory-bakeoff/…/trial-pi-registration.stderr.log`);
- kill switch: `PI_PERSEUS_RECALL=0` → `pi-perseus-recall: disabled`
  (`trial-pi-killswitch.stderr.log`);
- scratch draft round-trip in the trial config shape (gate refusal on wrong
  code, operator-code write, notify-file line, supersede status flip,
  current-only recall): `scripts/experiment_20260911_trial/trial_smoke.ts`
  → `TRIAL SMOKE RECEIPT: PASS` 6/6.

## 1. The loop (Brian's shape, verbatim intent)

worker-pi runs with the extension loaded. When a write draft needs input,
the **CONDUCTOR** is notified; the conductor sends Brian a **Signal
summons**; Brian unblocks it by **confirming IN the worker-pi thread** (the
deck UI thread IS the pi session, so the in-session gate as built is
correct and unchanged).

In tool terms:

1. worker-pi drafts via `project_perseus_remember` /
   `project_perseus_supersede` — nothing is written; the draft tool result
   (id + one-time confirmation code) is presented in-thread and a line
   lands in `notifications.jsonl`.
2. Conductor sees the pending line → sends Brian a Signal summons.
3. Brian replies in the worker-pi deck thread; the worker calls
   `project_perseus_confirm` with `draft_id` + `confirmation_code`.
4. Write executes (CLI write / MCP supersede), receipt (incl. status flip
   + `from_valid_to_unix_ms`) comes back in-thread.

Nothing writes without Brian's code. `confirmed_by: "agent"` is refused
(`allowAgentConfirmed: false`). Draft TTL 60 min; 5 wrong codes destroy the
draft. TTL expiry is SAFE: the draft is dropped, nothing was ever written.

### Draft presentation format (REQUIRED)

Trial finding #1 (Brian, first live cycle): the mechanical draft output was
not self-explanatory — he confirmed without being 100% sure what he was
confirming. Every time the worker presents a draft for confirmation, it
MUST open with a plain-language block, in this shape, before any
mechanical details:

> **I want to save this decision:** \<one sentence, no jargon\>
> **Where:** \<vault path\>
> **If you confirm:** this ONE record becomes persistent memory I will
> retrieve in later sessions.
> **If you ignore:** nothing happens — the draft expires in 60 minutes.

For the trial the vault path is `/home/bmosher/acp-pi/trial.vault`. Only
after that block come the mechanical details (record fields, `draft_id`,
`confirmation_code`, expiry) so the operator can act. The code must still
be presented verbatim — it is the gate. The same discipline applies to a
`project_perseus_supersede` draft: say in plain language what the NEW
decision is and that confirming retires the OLD one ("the old record stops
showing up when I search").

## 2. Conductor side

**Primary detection — poll the notify file** (pi-acp sessions may not fire
fleet nudges; polling is the primary signal, fleet-idle nudge is a
secondary hint only):

```
/home/bmosher/acp-pi/notifications.jsonl
```

One JSON line per pending draft, written the moment a draft registers:

```json
{"kind":"pending_confirmation","at":"…","draft_id":"draft-…",
 "confirmation_code":"…","tool":"project_perseus_remember",
 "summary":"create decision/record-… in environment project: …",
 "expires_at":"…","agent_confirmed_allowed":false}
```

Poll (e.g. every 30 s), track `draft_id`s already summoned; a line whose
`expires_at` has passed can be dropped. There is no completion signal in
the file — treat "the operator confirmed in-thread" as observed from the
worker-pi session, not from this file.

**Signal summons** — clawdbot JSON-RPC `method:"send"`, envelope identical
to `~/clawdbot/trigger-*.py`. Account + recipient are READ FROM THOSE
SCRIPTS AT SEND TIME and are never written into any file this repo tracks:

```bash
python3 - <<'EOF'
import json, re, urllib.request
src = open("/home/bmosher/clawdbot/trigger-google-healthcheck.py").read()
account = re.search(r'SIGNAL_ACCOUNT\s*=\s*"([^"]+)"', src).group(1)
uuid    = re.search(r'BRIAN_UUID\s*=\s*"([^"]+)"', src).group(1)
msg = ("[perseus-write] worker-pi draft awaiting your confirmation\n"
       + DRAFT_SUMMARY_LINE_FROM_THE_NOTIFY_FILE + "\n"
       + "Confirm IN the worker-pi thread (deck): the agent needs draft_id "
       + DRAFT_ID + " with code " + CODE + " (expires " + EXPIRES_AT + ").")
body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "send",
                   "params": {"account": account, "recipient": [uuid], "message": msg}})
req = urllib.request.Request("http://127.0.0.1:8081/api/v1/rpc",
                             data=body.encode(), headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(req, timeout=10).status)
EOF
```

The same daemon answers a zero-side-effect liveness probe:
`{"jsonrpc":"2.0","id":1,"method":"version","params":{}}` → `0.14.1`.

## 3. Trial design (pre-registered — descriptive, small-n, honest)

**First task is real work in `/home/bmosher/acp-pi`:** standing up the
trial workspace is genuine work and will naturally produce the first
decision record (vault location + trial conventions). No scripted demo
tasks; the worker works, the memory system either helps or doesn't.

Metrics (recorded per draft/turn; all **exploratory**, no causal claims):

| Metric | Definition |
|---|---|
| drafts raised | count of `notifications.jsonl` lines |
| recall deliveries | `project_perseus_recall` calls whose toolResult carried ≥1 record (session log) |
| confirm latency | draft timestamp → Signal send timestamp → operator confirm (confirm tool receipt time) |
| overhead vs no-memory turn | wall + tokens of a memory turn vs a comparable no-memory turn (pi session logs; descriptive pairing only) |
| stale-action events | acting on a superseded record — **target 0** (the whole point of supersession) |
| TTL expiry events | drafts never confirmed before `expires_at` |

Small-n honesty: this is a plumbing + shape trial on one worker and one
operator. It can show the loop closes and what it costs; it cannot show
that decision memory improves worker performance.

## 4. Failure handling

- TTL expiry: safe by construction — draft dropped, nothing written, no
  partial state.
- Confirm refused (wrong/expired code, agent-confirmation attempt): the
  tools answer `NOT WRITTEN` with the reason; re-draft if still wanted.
- Daemon down: the Signal send fails visibly (conductor side); the
  in-session gate is unaffected — Brian can still confirm from the thread.
- **Hard stop:** if the loop cannot close without extension code changes,
  STOP and report. `e9e5621` stays frozen; reviewer verification gates any
  unfreeze.
- Kill switch: `PI_PERSEUS_RECALL=0` disables the whole extension
  (verified); `perseusRecall.write.enabled: false` would degrade to
  recall-only without touching code.
