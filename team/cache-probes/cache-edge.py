#!/usr/bin/env python3
"""Where exactly does Muse's prompt cache die?

Measured 2026-09-14: alive at 30s (99.4% hit), completely gone at 6 min (0.0%).
setCacheKey and promptCacheRetention=24h changed nothing, so the pulse interval
is the only lever - and it has to be chosen against the real lifetime, not a
guess. The team sized item 1 at "<=60s"; if the edge turns out to be 3 minutes
that is needlessly aggressive, and if it is 45s then 60 is already too slow.

METHOD. One session, one stable 24k-token prefix, then a ladder of gaps. Every
call re-writes the cache, so each call measures the gap that preceded IT - a
single session gives the whole curve without re-priming between rungs.

Ascending order, so the first 0% marks the edge. Each rung's hit rate is read
from opencode's own ledger afterwards, not from the client's usage events.
"""
import json
import os
import subprocess
import sqlite3
import threading
import time

LADDER = [float(x) for x in os.environ.get(
    "LADDER", "45,60,90,120,180,300").split(",")]
MODEL = "opencode-go/muse-spark-1.3-contributor"
OUT = os.environ.get("PROBE_OUT", os.path.expanduser("~/cache-edge-probe.md"))
CWD = "/tmp/claude-1000/-var-home-bmosher/09b5ba50-67c7-4535-b27c-5baa3e1c4fa8/scratchpad/cacheprobe/edge"
DB = "file:" + os.path.expanduser("~/.local/share/opencode/opencode.db") + "?mode=ro"
FILLER = ("The chandler recorded the rigging measurement in the ledger before the "
          "tide turned, and the cooper set the hoops while the light held. ")


class Conn:
    def __init__(self, cwd):
        self.n = 1
        self.io = threading.Lock()
        self.replies, self.events = {}, {}
        env = dict(os.environ)
        env.pop("OPENCODE_API_KEY", None)
        self.p = subprocess.Popen(
            ["muse-engine", "acp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1, cwd=cwd, env=env)
        threading.Thread(target=self.reader, daemon=True).start()

    def call(self, method, params, timeout=240):
        with self.io:
            rid = self.n
            self.n += 1
            self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rid,
                                           "method": method, "params": params}) + "\n")
            self.p.stdin.flush()
        ev = threading.Event()
        self.events[rid] = ev
        if not ev.wait(timeout):
            raise TimeoutError(method)
        m = self.replies.pop(rid)
        if "error" in m:
            raise RuntimeError(json.dumps(m["error"])[:200])
        return m.get("result") or {}

    def reader(self):
        for line in self.p.stdout:
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if "id" in m and ("result" in m or "error" in m):
                self.replies[m["id"]] = m
                ev = self.events.pop(m["id"], None)
                if ev:
                    ev.set()
            elif "id" in m and "method" in m:
                self.p.stdin.write(json.dumps(
                    {"jsonrpc": "2.0", "id": m["id"],
                     "error": {"code": -32601, "message": "probe"}}) + "\n")
                self.p.stdin.flush()


def ledger(sid):
    time.sleep(4)
    db = sqlite3.connect(DB, uri=True)
    out = []
    for (d,) in db.execute("SELECT data FROM message WHERE session_id=?"
                           " ORDER BY time_created", (sid,)):
        j = json.loads(d)
        if j.get("role") != "assistant":
            continue
        tok = j.get("tokens") or {}
        ca = tok.get("cache") or {}
        i, cr = tok.get("input") or 0, ca.get("read") or 0
        if i + cr:
            out.append((i, cr, 100 * cr / (i + cr)))
    db.close()
    return out


def main():
    os.makedirs(CWD, exist_ok=True)
    with open(os.path.join(CWD, "opencode.json"), "w") as fh:
        json.dump({"$schema": "https://opencode.ai/config.json"}, fh)
    c = Conn(CWD)
    c.call("initialize", {"protocolVersion": 1, "clientCapabilities": {
        "fs": {"readTextFile": False, "writeTextFile": False}, "terminal": False}})
    sid = c.call("session/new", {"cwd": CWD, "mcpServers": []}).get("sessionId")
    for m in ("session/set_model", "session/setModel"):
        try:
            c.call(m, {"sessionId": sid, "modelId": MODEL})
            break
        except Exception:
            continue
    print(f"session {sid}", flush=True)

    def turn(text):
        c.call("session/prompt", {"sessionId": sid,
                                  "prompt": [{"type": "text", "text": text}]})

    pad = (FILLER * 1400)[:80000]
    turn(f"Reference material, do not summarise:\n\n{pad}\n\nReply with one word: PRIMED")
    print("  primed", flush=True)
    for g in LADDER:
        print(f"  waiting {g:.0f}s ...", flush=True)
        time.sleep(g)
        turn(f"Reply with one word: G{int(g)}")
        print(f"  probed after {g:.0f}s", flush=True)
    try:
        c.p.terminate()
    except Exception:
        pass

    rows = ledger(sid)          # [prime, then one per rung]
    L = ["# Where does Muse's prompt cache die?\n",
         f"Probe {time.strftime('%Y-%m-%d %H:%M %Z')}, model `{MODEL}`, "
         f"one session, 24k-token stable prefix.",
         "Each call re-writes the cache, so each rung measures the gap that "
         "preceded it.\n",
         "Known before this run: **99.4% hit at 30s**, **0.0% at 6 min**. "
         "`setCacheKey` and `promptCacheRetention=24h` made no difference.\n",
         "| gap before the call | fresh input | cache read | hit rate |",
         "|---|---|---|---|"]
    edge_last_ok, edge_first_dead = None, None
    for g, r in zip(LADDER, rows[1:]):
        i, cr, h = r
        L.append(f"| {g:.0f}s | {i:,} | {cr:,} | **{h:.1f}%** |")
        if h > 50 and edge_first_dead is None:
            edge_last_ok = g
        if h <= 50 and edge_first_dead is None:
            edge_first_dead = g
    L.append("")
    L.append("## Verdict\n")
    if edge_first_dead is None:
        L.append(f"Cache survived every rung up to **{LADDER[-1]:.0f}s**. The edge is "
                 f"above the ladder - extend it before choosing a pulse interval.")
    elif edge_last_ok is None:
        L.append(f"Cache was already dead at the first rung (**{LADDER[0]:.0f}s**). The "
                 f"lifetime is under {LADDER[0]:.0f}s, which makes a pulse-interval fix "
                 f"impractical - a cadence that tight is not a fleet, it is a spin loop. "
                 f"Reconsider items 2 and 3 instead.")
    else:
        L.append(f"- last gap that still hit cache: **{edge_last_ok:.0f}s**")
        L.append(f"- first gap that missed: **{edge_first_dead:.0f}s**")
        L.append(f"\nSo the lifetime sits between **{edge_last_ok:.0f}s and "
                 f"{edge_first_dead:.0f}s**. A pulse interval must be comfortably "
                 f"below {edge_last_ok:.0f}s to keep lanes warm - the team's ≤60s "
                 f"figure is "
                 + ("**sound**." if edge_last_ok >= 90 else
                    "**too slow**; it sits at or past the edge.")
                 + " Note every rung re-primes, so a lane pulsed inside the lifetime "
                   "stays warm indefinitely.")
    L.append(f"\nRaw rungs: `{json.dumps(rows)}`\n")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
