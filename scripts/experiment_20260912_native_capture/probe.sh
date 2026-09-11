#!/usr/bin/env bash
# PROBE-20260912 — native Perseus capture: does it derive replacement lineage?
#
# Mechanism inspection only. Runs the planner's exact two-conversation
# sequence through the NATIVE capture pipeline (no extension, no manual
# lineage) against scratch vaults, then follows the store's own admission
# chain as far as it goes, and dumps everything:
#   vault A: CLI path   (perseus-vault capture, stdin payload)
#   vault B: MCP path   (perseus_vault_capture tool; docs say same pipeline —
#                         verified empirically)
# Inspections: capture reports, full workspace scans, per-key history,
# recall ("how do we deploy to production?"), the admission chain (agent
# registry -> enforce authority manifest -> admission_decide), get_entity,
# and a direct sqlite read of the scratch vault (dispatch-allowed).
# A labeled supplementary dry-run shows the distiller's note-splitting on a
# paragraph-split conversation 2 (the primary run keeps the planner's exact
# single-paragraph conversation 2).
#
# Scratch vaults only. Read-only over the perseus source. Receipts land in
# receipts/ next to this script.
set -u
BIN=/var/home/bmosher/perseus-build/src/target/release/perseus-vault
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/receipts"
rm -rf "$OUT"; mkdir -p "$OUT"
rm -rf /tmp/native-capture-probe; mkdir -p /tmp/native-capture-probe
WS="ws-probe-native"

say() { echo "== $*" | tee -a "$OUT/00-run.log"; }

HELPER=/tmp/native-capture-probe/rpc_session.py
cat > "$HELPER" <<'PYEOF'
import json, subprocess, sys
bin_, db, key, outfile = sys.argv[1:5]
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
        try: sc = json.loads(r["content"][0]["text"])
        except Exception: sc = {"raw": str(r["content"][0]["text"])[:300]}
    return {"isError": r.get("isError", False), "body": sc}
out = open(outfile, "a")
def emit(tag, obj):
    out.write(f"--- {tag}\n{json.dumps(obj, indent=1, sort_keys=True)}\n")
try:
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "probe-operator", "version": "0"}})
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        req = json.loads(line)
        emit(req.get("tag", req["tool"]), call(req["tool"], req["args"]))
finally:
    p.terminate(); p.wait(timeout=10)
    out.close()
PYEOF

# One serve session per vault; JSON-RPC over stdio. Reads command lines of
# {"tag": "...", "tool": "...", "args": {...}} on stdin, appends receipts.
rpc_session() { # rpc_session <db> <key> <outfile>
  python3 "$HELPER" "$BIN" "$1" "$2" "$3"
}

for V in cli mcp; do
  mkdir -p /tmp/native-capture-probe/$V
  "$BIN" keygen --key-file /tmp/native-capture-probe/$V/k.key >/dev/null 2>&1
done

# ── vault A: CLI capture path ────────────────────────────────────────────────
DBA=/tmp/native-capture-probe/cli/vault.sqlite
KA=/tmp/native-capture-probe/cli/k.key
say "[cli] capture conversation 1 (planner's exact payload)"
printf 'Production deploys with Docker Compose.\n' | \
  "$BIN" capture --db "$DBA" --encryption-key "$KA" --workspace-hash "$WS" \
  > "$OUT/cli-capture-1.json" 2>&1
say "[cli] capture conversation 2 (planner's exact payload)"
printf 'Production now uses Helm. Development still uses Docker Compose.\n' | \
  "$BIN" capture --db "$DBA" --encryption-key "$KA" --workspace-hash "$WS" \
  > "$OUT/cli-capture-2.json" 2>&1
say "[cli] inspections: scan (pre-admission), history, get_entity, recall"
rpc_session "$DBA" "$KA" "$OUT/cli-inspect-1.json" <<'CMDS'
{"tag": "scan-pre-admission", "tool": "perseus_vault_scan", "args": {"workspace_hash": "ws-probe-native", "include_archived": true, "limit": 100}}
{"tag": "history-note-1", "tool": "perseus_vault_history", "args": {"category": "capture", "key": "production-deploys-with-docker-compose"}}
{"tag": "history-note-2", "tool": "perseus_vault_history", "args": {"category": "capture", "key": "production-now-uses-helm-development-still-uses-docker-compose"}}
{"tag": "get-entity-note-1", "tool": "perseus_vault_get_entity", "args": {"id": "mem-c15fbc19e031"}}
{"tag": "get-entity-note-2", "tool": "perseus_vault_get_entity", "args": {"id": "mem-a68d598b37e3"}}
{"tag": "recall-pre-admission", "tool": "perseus_vault_recall", "args": {"query": "how do we deploy to production?", "limit": 10, "mode": "hybrid", "workspace_hash": "ws-probe-native"}}
CMDS

say "[cli] admission chain: register agent -> enforce authority -> admission_decide"
rpc_session "$DBA" "$KA" "$OUT/cli-admission.json" <<'CMDS'
{"tag": "agent-register", "tool": "perseus_vault_agent", "args": {"agent_id": "probe-operator", "name": "probe operator", "trust_tier": 3}}
{"tag": "authority-set", "tool": "perseus_vault_authority_set", "args": {"agent_id": "probe-operator", "workspace_hash": "ws-probe-native", "allowed_capabilities": ["memory.admission.review"], "scope_anchors": ["ws-probe-native"], "mode": "enforce", "capability_constraints_json": "{}", "approver_principals": ["probe-operator"]}}
{"tag": "admit-note-1", "tool": "perseus_vault_admission_decide", "args": {"category": "capture", "key": "production-deploys-with-docker-compose", "workspace_hash": "ws-probe-native", "requesting_agent_id": "probe-operator", "decision": "approve", "reason": "PROBE-20260912 mechanism inspection"}}
{"tag": "admit-note-2", "tool": "perseus_vault_admission_decide", "args": {"category": "capture", "key": "production-now-uses-helm-development-still-uses-docker-compose", "workspace_hash": "ws-probe-native", "requesting_agent_id": "probe-operator", "decision": "approve", "reason": "PROBE-20260912 mechanism inspection"}}
{"tag": "scan-post-admission-attempt", "tool": "perseus_vault_scan", "args": {"workspace_hash": "ws-probe-native", "include_archived": true, "limit": 100}}
{"tag": "recall-post-admission-attempt", "tool": "perseus_vault_recall", "args": {"query": "how do we deploy to production?", "limit": 10, "mode": "hybrid", "workspace_hash": "ws-probe-native"}}
CMDS

say "[cli] direct sqlite read of the scratch vault (dispatch-allowed; bodies are encrypted at rest)"
python3 - "$DBA" > "$OUT/cli-sqlite-dump.txt" <<'PYEOF'
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
for row in c.execute("SELECT id,key,category,status,source,workspace_hash,agent_id,links,importance,layer,archived FROM entities ORDER BY id"):
    print(row)
PYEOF
cat "$OUT/cli-sqlite-dump.txt"

# ── vault B: MCP capture path (agentic) ──────────────────────────────────────
DBB=/tmp/native-capture-probe/mcp/vault.sqlite
KB=/tmp/native-capture-probe/mcp/k.key
say "[mcp] capture conversations 1+2 via perseus_vault_capture, then inspect + admission chain"
rpc_session "$DBB" "$KB" "$OUT/mcp-inspect.json" <<'CMDS'
{"tag": "capture-1", "tool": "perseus_vault_capture", "args": {"text": "Production deploys with Docker Compose.", "workspace_hash": "ws-probe-native"}}
{"tag": "capture-2", "tool": "perseus_vault_capture", "args": {"text": "Production now uses Helm. Development still uses Docker Compose.", "workspace_hash": "ws-probe-native"}}
{"tag": "scan-pre-admission", "tool": "perseus_vault_scan", "args": {"workspace_hash": "ws-probe-native", "include_archived": true, "limit": 100}}
{"tag": "recall-pre-admission", "tool": "perseus_vault_recall", "args": {"query": "how do we deploy to production?", "limit": 10, "mode": "hybrid", "workspace_hash": "ws-probe-native"}}
{"tag": "agent-register", "tool": "perseus_vault_agent", "args": {"agent_id": "probe-operator", "name": "probe operator", "trust_tier": 3}}
{"tag": "authority-set", "tool": "perseus_vault_authority_set", "args": {"agent_id": "probe-operator", "workspace_hash": "ws-probe-native", "allowed_capabilities": ["memory.admission.review"], "scope_anchors": ["ws-probe-native"], "mode": "enforce", "capability_constraints_json": "{}", "approver_principals": ["probe-operator"]}}
{"tag": "admit-note-1", "tool": "perseus_vault_admission_decide", "args": {"category": "capture", "key": "production-now-uses-helm-development-still-uses-docker-compose", "workspace_hash": "ws-probe-native", "requesting_agent_id": "probe-operator", "decision": "approve", "reason": "PROBE-20260912 mechanism inspection"}}
{"tag": "recall-post-admission-attempt", "tool": "perseus_vault_recall", "args": {"query": "how do we deploy to production?", "limit": 10, "mode": "hybrid", "workspace_hash": "ws-probe-native"}}
CMDS

say "[supplementary, labeled] dry-run: paragraph-SPLIT conversation 2 (distiller note-split view)"
rpc_session "$DBB" "$KB" "$OUT/mcp-dryrun-split.json" <<'CMDS'
{"tag": "dryrun-split-conv2", "tool": "perseus_vault_capture", "args": {"text": "Production now uses Helm.\n\nDevelopment still uses Docker Compose.", "workspace_hash": "ws-probe-native", "dry_run": true}}
CMDS

say "done"
