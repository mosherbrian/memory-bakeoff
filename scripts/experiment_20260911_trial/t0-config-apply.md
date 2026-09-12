# T0 tiered-capture config — exact apply artifact for CAIRN (worker-pi lane)

**Prepared by:** Kiln (pre-window checklist item 5). **Applied by:** CAIRN on
his own lane — Kiln does not touch `/home/bmosher/acp-pi/`. **Brian approved**
the T0/T1 tiering amendment (campaign-1 decisions, 2026-09-12). Config-only:
zero extension-code changes; the frozen lineage (code identical to 060d842)
is untouched.

## The one-key change

`/home/bmosher/acp-pi/.pi-agent/settings.json` → `perseusRecall.write`:

```diff
     "write": {
       "enabled": true,
-      "allowAgentConfirmed": false,
+      "allowAgentConfirmed": true,
       "notifiers": ["in-session", "file"],
       "notifyFile": "/home/bmosher/acp-pi/notifications.jsonl"
     }
```

Everything else in the file stays byte-identical. `allowAgentConfirmed: true`
is the 7a exception switch the frozen extension already ships: T0 (low-stakes)
records may then be self-captured with `confirmed_by: "agent"`; T1 (decisions
that bind) are STILL presented for the operator's confirmation code — the
tier discipline is presentation + judgment policy per
docs/TRIAL-20260911-runbook.md ("Draft presentation format (REQUIRED)"),
enforced by Verity's post-hoc T0-proportionality audit (misclassification
rate reported beside the burden number, S3).

## Apply (CAIRN runs this, from anywhere)

```bash
python3 - <<'EOF'
import json
p = "/home/bmosher/acp-pi/.pi-agent/settings.json"
s = json.load(open(p))
w = s["perseusRecall"]["write"]
assert w["allowAgentConfirmed"] is False, "unexpected current state — stop"
w["allowAgentConfirmed"] = True
json.dump(s, open(p, "w"), indent=2)
print("applied")
EOF
```

## Verify (CAIRN runs after applying; also lands in the window ledger)

```bash
python3 -c "import json; print(json.load(open('/home/bmosher/acp-pi/.pi-agent/settings.json'))['perseusRecall']['write'])"
# expect: {'enabled': True, 'allowAgentConfirmed': True, 'notifiers': ['in-session', 'file'], 'notifyFile': '/home/bmosher/acp-pi/notifications.jsonl'}
```

and on the next worker-pi session start, stderr must show
`allowAgentConfirmed=true` in the pi-perseus-recall registration line.

## Rollback

Set `allowAgentConfirmed` back to `false` (same command, inverted value) — or
`PI_PERSEUS_RECALL=0` for the full stop. No restart needed beyond the next pi
process; config is read at extension load.

## Reference target (reconciliation receipt)

**Reconciled 2026-09-12:** CAIRN applied the flip at 10:18:37 -0700 (before
this artifact landed in `team/` — his WINDOW-OPENING entry notes the ordering
honestly). Kiln verified the applied state matches this artifact's diff
exactly: `perseusRecall.write` = `{enabled: true, allowAgentConfirmed: true,
notifiers: ["in-session", "file"], notifyFile:
"/home/bmosher/acp-pi/notifications.jsonl"}`, every other key untouched.
Post-apply settings sha256
`b4fdbef20b2f9427695fa44429a2325765094d002b8bb08ffbb5b3183fa5aae3` (Cairn's
after-scan). Item 5's remaining piece is Cairn's end-to-end T0 self-capture
proof on his next session (his note, correct: the flip is live from the next
pi process, not the one that wrote it).
