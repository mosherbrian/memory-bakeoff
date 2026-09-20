#!/usr/bin/env python3
"""Does a cache-retention setting keep Muse's cache alive across the pulse gap?

Item 6 of the team's plan, and it decides item 1. Measured 2026-09-14: Muse's
cache hit rate falls 96.3% -> 18.6% as the idle gap grows 0-1 min to 5-6 min,
while DeepSeek holds 99.9% at every gap. If a setting keeps the cache warm,
that beats tightening the pulse: no extra calls, no extra output, and no
dependence on a TTL we only inferred from a curve.

TWO ARMS, same prompts, same gaps:
  A  the config the fleet runs today
  B  provider options setCacheKey + promptCacheRetention=24h

Each arm primes a large stable prefix, then asks a short follow-up at +30s
(inside the cache lifetime) and again after the gap (outside it). The number
that matters is the cache hit rate on that last call.

The config is written to the probe's OWN directory, never to
~/.config/opencode, so the thirteen live lanes are untouched.
"""
import json
import os
import subprocess
import sys
import threading
import time

GAP = float(os.environ.get("PROBE_GAP", 360))     # seconds of idleness to test
MODEL = "opencode-go/muse-spark-1.3-contributor"
OUT = os.path.expanduser("~/cache-retention-probe.md")
ROOT = "/tmp/claude-1000/-var-home-bmosher/09b5ba50-67c7-4535-b27c-5baa3e1c4fa8/scratchpad/cacheprobe"

FILLER = ("The chandler recorded the rigging measurement in the ledger before the "
          "tide turned, and the cooper set the hoops while the light held. ")


class Conn:
    def __init__(self, cwd):
        self.n = 1
        self.io = threading.Lock()
        self.replies, self.events = {}, {}
        self.usage = []
        env = dict(os.environ)
        env.pop("OPENCODE_API_KEY", None)          # force the stored Go credential
        self.p = subprocess.Popen(
            ["muse-engine", "acp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1, cwd=cwd, env=env)
        threading.Thread(target=self.reader, daemon=True).start()

    def call(self, method, params, timeout=180):
        with self.io:
            rid = self.n
            self.n += 1
            self.p.stdin.write(json.dumps(
                {"jsonrpc": "2.0", "id": rid, "method": method,
                 "params": params}) + "\n")
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
                # answer anything the agent asks so nothing stalls
                self.p.stdin.write(json.dumps(
                    {"jsonrpc": "2.0", "id": m["id"],
                     "error": {"code": -32601, "message": "probe"}}) + "\n")
                self.p.stdin.flush()
            elif m.get("method") == "session/update":
                u = (m.get("params") or {}).get("update") or {}
                if u.get("sessionUpdate") == "usage_update":
                    self.usage.append(u)


def arm(label, opts):
    cwd = os.path.join(ROOT, label)
    os.makedirs(cwd, exist_ok=True)
    cfg = {"$schema": "https://opencode.ai/config.json"}
    if opts:
        cfg["provider"] = {"opencode-go": {"options": opts}}
        # stop the small_model calling a model this account cannot pay for:
        # gpt-5.4-nano failed 97 times with "No payment method" on 2026-09-14
        cfg["small_model"] = MODEL
    with open(os.path.join(cwd, "opencode.json"), "w") as fh:
        json.dump(cfg, fh, indent=2)

    rows = []
    c = Conn(cwd)
    c.call("initialize", {"protocolVersion": 1, "clientCapabilities": {
        "fs": {"readTextFile": False, "writeTextFile": False}, "terminal": False}})
    sid = c.call("session/new", {"cwd": cwd, "mcpServers": []}).get("sessionId")
    for m in ("session/set_model", "session/setModel"):
        try:
            c.call(m, {"sessionId": sid, "modelId": MODEL})
            break
        except Exception:
            continue

    def turn(text, tag):
        before = len(c.usage)
        t0 = time.time()
        c.call("session/prompt", {"sessionId": sid,
                                  "prompt": [{"type": "text", "text": text}]},
               timeout=240)
        u = c.usage[-1] if len(c.usage) > before else {}
        rows.append({"tag": tag, "secs": round(time.time() - t0, 1),
                     "used": u.get("used"), "raw": {k: v for k, v in u.items()
                                                    if k != "sessionUpdate"}})
        print(f"  [{label}] {tag}: {time.time()-t0:.1f}s used={u.get('used')}",
              flush=True)

    # a big stable prefix, so a miss is unmistakable against a hit
    pad = (FILLER * 1400)[:80000]
    turn(f"Reference material, do not summarise:\n\n{pad}\n\nReply with one word: PRIMED",
         "prime (writes the cache)")
    time.sleep(30)
    turn("Reply with one word: WARM", f"+30s (inside the cache lifetime)")
    print(f"  [{label}] waiting {GAP:.0f}s ...", flush=True)
    time.sleep(GAP)
    turn("Reply with one word: COLD", f"+{GAP/60:.0f}min (the pulse gap)")
    try:
        c.p.terminate()
    except Exception:
        pass
    return sid, rows


def db_rows(sid):
    """Authoritative per-call tokens, from opencode's own ledger."""
    import sqlite3
    time.sleep(4)
    db = sqlite3.connect(
        "file:" + os.path.expanduser("~/.local/share/opencode/opencode.db")
        + "?mode=ro", uri=True)
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
    os.makedirs(ROOT, exist_ok=True)
    results = {}
    for label, opts in (("A-current", None),
                        ("B-retention", {"setCacheKey": True,
                                         "promptCacheRetention": "24h"})):
        print(f"=== arm {label}", flush=True)
        try:
            sid, rows = arm(label, opts)
            results[label] = {"session": sid, "rows": rows, "db": db_rows(sid)}
        except Exception as exc:
            results[label] = {"error": str(exc)[:300]}
            print(f"  [{label}] FAILED {exc}", flush=True)

    L = ["# Does a cache-retention setting survive the pulse gap?\n",
         f"Probe run {time.strftime('%Y-%m-%d %H:%M %Z')}. Model `{MODEL}`.",
         f"Gap tested: {GAP/60:.0f} minutes. Config written per-arm in the probe's",
         "own directory; the live fleet was not touched.\n",
         "Baseline to beat: Muse's measured hit rate is 96.3% under one minute",
         "and 18.6% at five to six minutes.\n"]
    for label in ("A-current", "B-retention"):
        r = results.get(label) or {}
        L.append(f"## {label}\n")
        if r.get("error"):
            L.append(f"FAILED: `{r['error']}`\n")
            continue
        L.append("| call | latency | fresh in | cache read | hit rate |")
        L.append("|---|---|---|---|---|")
        db = r.get("db") or []
        for row, d in zip(r["rows"], db + [None] * len(r["rows"])):
            if d:
                L.append(f"| {row['tag']} | {row['secs']}s | {d[0]:,} | {d[1]:,} | "
                         f"**{d[2]:.1f}%** |")
            else:
                L.append(f"| {row['tag']} | {row['secs']}s | — | — | — |")
        L.append("")
        if len(db) >= 3:
            L.append(f"Hit rate after the {GAP/60:.0f}-minute gap: "
                     f"**{db[-1][2]:.1f}%**\n")
    a = (results.get("A-current") or {}).get("db") or []
    b = (results.get("B-retention") or {}).get("db") or []
    L.append("## Verdict\n")
    if len(a) >= 3 and len(b) >= 3:
        L.append(f"- current config, after the gap: **{a[-1][2]:.1f}%** cache hit")
        L.append(f"- with setCacheKey + 24h retention: **{b[-1][2]:.1f}%** cache hit")
        # Arm A must actually decay, or the experiment measured nothing. Without
        # this guard a warm cache in both arms reads as "the setting failed",
        # which is the conclusion a zero-gap smoke run wrongly produced.
        if a[-1][2] > 80:
            L.append(f"\n**INCONCLUSIVE — the control did not decay.** Arm A held "
                     f"{a[-1][2]:.1f}% across a {GAP/60:.0f}-minute gap, where the "
                     f"fleet measured 18.6%. So the decay is not reproducible in a "
                     f"clean single session, and something about the live lanes "
                     f"causes it — context size, concurrent traffic, or the restarts "
                     f"that contaminated the original sample. Neither item 1 nor "
                     f"item 6 is justified by this run; find the real trigger first.")
        elif b[-1][2] > a[-1][2] + 20:
            L.append("\n**The setting holds the cache.** Prefer this over tightening "
                     "the pulse (team item 6 beats item 1): no extra calls, no extra "
                     "output, no dependence on an inferred TTL.")
        else:
            L.append("\n**The setting does not hold the cache.** Fall back to team "
                     "item 1 — tighten the Muse pulse to under a minute.")
    else:
        L.append("Inconclusive - one or both arms did not produce three billed calls.")
    L.append(f"\nRaw: {json.dumps(results, default=str)[:1500]}\n")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L[-8:]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
