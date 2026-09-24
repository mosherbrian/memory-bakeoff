#!/usr/bin/env python3
"""P13 PASSIVE FIXTURE ENGINE (receiver double; NOT evidence of human compliance).

An ACP agent for the fixture director/duty seats, run BEHIND the real acp-worker runtime (real socket, real
wake protocol). It speaks ACP JSON-RPC on stdio, advertises NO tools and NO capabilities, never sends a tool
call or a permission request, and has no process-spawning or shell code at all: the text of any notice,
including absolute command paths, is only recorded. Each prompt is appended as one JSON line to
$HOME/.local/share/p13-passive/<AGENTDECK_INSTANCE_ID>.jsonl (proof of real receipt), and the turn ends
with a fixed reply. Only json/os/sys/time are imported.
"""
import json, os, sys, time
INST = os.environ.get("AGENTDECK_INSTANCE_ID", "unknown")
REC = os.path.join(os.path.expanduser("~"), ".local/share/p13-passive", INST + ".jsonl")
os.makedirs(os.path.dirname(REC), exist_ok=True)
def send(m): sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()
for line in sys.stdin:
    try: m = json.loads(line)
    except Exception: continue
    meth, mid, p = m.get("method"), m.get("id"), m.get("params") or {}
    if mid is None: continue                                    # notifications (session/cancel): nothing to do
    if meth == "initialize":
        send({"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": 1, "agentCapabilities": {},
              "agentInfo": {"name": "p13-passive-receiver", "version": "1"}, "authMethods": []}})
    elif meth == "session/new":
        send({"jsonrpc": "2.0", "id": mid, "result": {"sessionId": "passive-" + INST}})
    elif meth == "session/prompt":
        text = "".join(x.get("text", "") for x in p.get("prompt", []) if isinstance(x, dict))
        with open(REC, "a") as f:
            f.write(json.dumps({"t": time.time(), "instance": INST, "text": text}) + "\n")
        send({"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": p.get("sessionId"),
              "update": {"sessionUpdate": "agent_message_chunk", "content": {"type": "text",
              "text": "received (passive fixture receiver: no tools, nothing executed)"}}}})
        send({"jsonrpc": "2.0", "id": mid, "result": {"stopReason": "end_turn"}})
    else:
        send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "not supported by the passive receiver"}})
