#!/usr/bin/env bash
# S6 scan-after-write instrument (CAMPAIGN-1 pre-window checklist item 4).
#
# Run ONCE AFTER EVERY WRITE to the trial vault (agent confirm, supersede, or
# operator seed). This is the campaign's observed-state instrument: it asserts
# the vault's own stored state, never a write receipt ("receipts claim; state
# is"). Append the output to the trial ledger.
#
# Authoritative state = the entities table's own columns (status, source),
# read directly from the sqlite file. NOTE: the MCP scan projection flattens
# body_json fields (e.g. the provenance `source` block) over the row, so the
# scan alone cannot distinguish write paths — sqlite is the authority, the
# MCP scan is the recall-visibility check. (First-run lesson, 2026-09-12:
# the scan-only check false-fired on every row because of that projection.)
#
# Expected-state rule (S6, v2): every row must be in the status
# expected-at-that-step — `active` for live records, `deprecated` for records
# superseded through the gated flow (deprecated rows legitimately leave the
# MCP scan: the product filters them, measured in PROBE-20260912). Any other
# status, any non-cli-write source, or an ACTIVE row invisible to the MCP
# scan is an UNSANCTIONED TRANSITION: stop and report.
#
# Usage: s6_scan_after_write.sh
set -u
BIN=/var/home/bmosher/perseus-build/src/target/release/perseus-vault
DB=/home/bmosher/acp-pi/trial.vault
KEY=/home/bmosher/acp-pi/trial.vault.key
WS=84117073c4ead03d   # sha256("/var/home/bmosher/acp-pi")[:16] — derived, verified against all stored rows

HELPER=$(mktemp /tmp/s6XXXXXX.py)
cat > "$HELPER" <<'PYEOF'
import json, subprocess, sys, datetime, sqlite3
bin_, db, key, ws = sys.argv[1:5]
# 1. authoritative columns
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
rows = [{"id": r[0], "key": r[1], "status": r[2], "source": r[3]}
        for r in c.execute("SELECT id,key,status,source FROM entities ORDER BY rowid")]
# 2. recall-visibility surface
p = subprocess.Popen([bin_, "serve", "--db", db, "--encryption-key", key],
                     text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL, bufsize=1)
i = [0]
def rpc(m, pa):
    i[0] += 1
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i[0], "method": m, "params": pa}) + "\n")
    p.stdin.flush()
    return json.loads(p.stdout.readline()).get("result", {})
def call(tool, args):
    r = rpc("tools/call", {"name": tool, "arguments": args})
    sc = r.get("structuredContent")
    if sc is None and r.get("content"):
        sc = json.loads(r["content"][0]["text"])
    return sc
try:
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "s6-scan-after-write", "version": "0"}})
    scan = call("perseus_vault_scan", {"workspace_hash": ws, "include_archived": True, "limit": 1000})
finally:
    p.terminate(); p.wait(timeout=10)
visible = {it.get("key") for it in scan.get("items", [])}
stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
violations = []
for r in rows:
    if r["status"] not in ("active", "deprecated"):
        violations.append(f"{r['key']}: status={r['status']!r} (not active/deprecated)")
    if r["source"] != "cli-write":
        violations.append(f"{r['key']}: source={r['source']!r} (CLI-write-only rule)")
    if r["status"] == "active" and r["key"] not in visible:
        violations.append(f"{r['key']}: ACTIVE but invisible to MCP scan (demoted-out-of-recall class)")
deprecated = [r["key"] for r in rows if r["status"] == "deprecated"]
print(f"# S6 scan-after-write {stamp}")
print(f"# rows: {len(rows)}  active: {sum(1 for r in rows if r['status']=='active')}  "
      f"deprecated(expected-absent-from-scan): {len(deprecated)}  violations: {len(violations)}")
for r in rows:
    vis = "visible" if r["key"] in visible else "absent-from-scan"
    print(json.dumps({**r, "scan": vis}, sort_keys=True))
if deprecated:
    print("# deprecated (expected absent from scan): " + ", ".join(deprecated))
if violations:
    print("S6 VIOLATION — STOP AND REPORT:")
    for v in violations: print("  - " + v)
else:
    print("S6 OK: all rows active/deprecated via cli-write; every active row recall-visible")
PYEOF
python3 "$HELPER" "$BIN" "$DB" "$KEY" "$WS"
rm -f "$HELPER"
