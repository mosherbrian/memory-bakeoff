# Change-trigger config — exact apply artifact for CAIRN (worker-pi lane)

**Prepared by:** Kiln (workstream B build, campaign GO execution). **Applied
by:** CAIRN on his own lane (T0 precedent — Kiln does not touch
`/home/bmosher/acp-pi/`). Config-only; the frozen decision-memory extension
and the nudge companion are untouched. Brian approved campaign-1 including
this workstream.

## The two-key change

`/home/bmosher/acp-pi/.pi-agent/settings.json`:

```diff
  "packages": [
    "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-perseus-recall",
+   "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-change-trigger"
  ],
+ "changeTrigger": {
+   "enabled": true,
+   "gapMinutes": 30,
+   "topicsFile": "/home/bmosher/acp-pi/notifications.jsonl",
+   "fireLog": "/home/bmosher/acp-pi/change-trigger-firelog.jsonl"
+ },
```

Everything else stays byte-identical. Topics source = the trial's own notify
ledger (plaintext summaries); the fire log is the S4 instrument feed (every
evaluation, fired or not; prompt sha256 + length only, never prompt text —
the blind-rater contract in team/S4-ADJUDICATION.md B1/B2).

## Apply (CAIRN runs this)

```bash
python3 - <<'EOF'
import json
p = "/home/bmosher/acp-pi/.pi-agent/settings.json"
s = json.load(open(p))
ext = "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-change-trigger"
if ext not in s["packages"]:
    s["packages"].append(ext)
assert "changeTrigger" not in s, "unexpected existing changeTrigger — stop and reconcile"
s["changeTrigger"] = {
    "enabled": True,
    "gapMinutes": 30,
    "topicsFile": "/home/bmosher/acp-pi/notifications.jsonl",
    "fireLog": "/home/bmosher/acp-pi/change-trigger-firelog.jsonl",
}
json.dump(s, open(p, "w"), indent=2)
print("applied")
EOF
```

## Verify (CAIRN runs after applying)

```bash
python3 -c "import json; s=json.load(open('/home/bmosher/acp-pi/.pi-agent/settings.json')); print(len(s['packages']), 'packages;', s['changeTrigger'])"
```

and on the next worker-pi session start, stderr must show
`pi-change-trigger: registered (gapMinutes=30, topicsFile=…/notifications.jsonl,
fireLog=…/change-trigger-firelog.jsonl; PI_CHANGE_TRIGGER=0 kills)`.

## End-to-end smoke BEFORE any S4 counting (checklist item 0 discipline)

Seed-free variant (the notify ledger already has topic material): run one
real turn whose prompt names a topic token, e.g. `What does the trial ledger
convention say?` — the trigger should fire (`topic`) and inject the visible
`[change-trigger]` message; assert (a) the message is in the session log,
(b) a fire-log line exists with `fired:true`, (c) a follow-up turn with no
topic produces `fired:false` and no message. Freeze all three receipts into
this file's successor or the window ledger before S4 counting starts.

## Rollback

Remove the `changeTrigger` key + the packages entry (or `PI_CHANGE_TRIGGER=0`)
— no restart semantics beyond the next pi process.
