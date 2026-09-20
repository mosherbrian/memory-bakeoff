#!/usr/bin/env python3
"""Does OpenCode's free tier survive four concurrent lanes?

v2. v1 was killed by the box's low-memory guard after one clean round: four
separate `opencode acp` processes cost ~6 GB, and llama-server already holds
47 GB with swap full. So this runs FOUR CONCURRENT SESSIONS across TWO
processes instead of four - the same four simultaneous requests against the
account, at half the memory.

CAVEAT, on the record: in the real fleet each lane is its own process. If a
limit were per-CONNECTION rather than per-account, two processes would show a
different answer than four. A per-account limit - the kind that killed the
InferX tenant - shows up identically either way, and that is the one we are
looking for.

The report proves the requests actually overlapped rather than assuming it:
every turn records its start and end, and the verdict states the maximum
number in flight at once. If opencode serialises prompts internally, the
overlap number says so instead of the test quietly measuring nothing.

Aborts itself and still writes a verdict if free memory runs low, so a second
OOM kill cannot leave the morning with no answer.

Writes muse-probe.jsonl (one row per turn) and muse-probe.md (the verdict).
"""
import json
import os
import re
import subprocess
import sys
import threading
import time

PROCS = int(os.environ.get("PROBE_PROCS", 2))
PER_PROC = int(os.environ.get("PROBE_PER_PROC", 2))
MINUTES = float(os.environ.get("PROBE_MINUTES", 20))
CADENCE = float(os.environ.get("PROBE_CADENCE", 30))
MIN_FREE_GB = float(os.environ.get("PROBE_MIN_FREE_GB", 4))
TURN_TIMEOUT = 180
MODEL = "opencode/muse-spark-1.3-contributor-free"
OUT = os.environ.get("PROBE_OUT", os.path.expanduser("~/muse-probe.jsonl"))
REPORT = os.environ.get("PROBE_REPORT", os.path.expanduser("~/muse-probe.md"))
CWD = os.path.expanduser("~/.cache")
LANES = PROCS * PER_PROC

# Wording match is for ERROR strings only. v1 scanned the model's own reply
# for these words while asking it to write about rate limiting, so every turn
# failed on its own answer.
LIMIT = re.compile(r"429|rate.?limit|too many|quota|exceeded|throttl|overload|"
                   r"capacity|try again later|unavailable", re.I)

lock = threading.Lock()
rows = []
abort = threading.Event()


def available_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024 / 1024
    except OSError:
        pass
    return 999.0


def log(row):
    with lock:
        rows.append(row)
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(f"[{time.strftime('%H:%M:%S')}] lane{row['lane']} "
              f"t{row['turn']:<3} {'ok ' if row.get('ok') else 'FAIL'} "
              f"{row.get('secs', 0):6.1f}s {row.get('chars', 0):5d}ch "
              f"{row.get('error', '')[:70]}", flush=True)


class Conn:
    """One opencode process, shared by several sessions."""

    def __init__(self, n):
        self.n = n
        self.next_id = 1
        self.io = threading.Lock()
        self.replies = {}
        self.events = {}
        self.sinks = {}        # sessionId -> list to append message chunks to
        self.dead = None
        self.proc = subprocess.Popen(
            ["opencode", "acp"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1, cwd=CWD, env=dict(os.environ))
        threading.Thread(target=self.reader, daemon=True).start()

    def send(self, obj):
        with self.io:
            self.proc.stdin.write(json.dumps(obj) + "\n")
            self.proc.stdin.flush()

    def call(self, method, params, timeout=60):
        with self.io:
            rid = self.next_id
            self.next_id += 1
        ev = threading.Event()
        self.events[rid] = ev
        # Not self.send(): that would take self.io again. The write needs the
        # lock, the id allocation needs the lock, and taking it twice in one
        # call deadlocks a non-reentrant Lock.
        with self.io:
            self.proc.stdin.write(json.dumps(
                {"jsonrpc": "2.0", "id": rid, "method": method,
                 "params": params}) + "\n")
            self.proc.stdin.flush()
        if not ev.wait(timeout):
            self.events.pop(rid, None)
            raise TimeoutError(f"{method} timed out after {timeout}s")
        msg = self.replies.pop(rid)
        if "error" in msg:
            raise RuntimeError(json.dumps(msg["error"]))
        return msg.get("result") or {}

    def reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if "id" in msg and ("result" in msg or "error" in msg):
                self.replies[msg["id"]] = msg
                ev = self.events.pop(msg["id"], None)
                if ev:
                    ev.set()
            elif "id" in msg and "method" in msg:
                if msg["method"] == "session/request_permission":
                    opts = (msg.get("params") or {}).get("options") or []
                    pick = next((o for o in opts
                                 if str(o.get("kind", "")).startswith("allow")),
                                opts[0] if opts else None)
                    self.send({"jsonrpc": "2.0", "id": msg["id"], "result": {
                        "outcome": {"outcome": "selected",
                                    "optionId": (pick or {}).get("optionId")}}})
                else:
                    self.send({"jsonrpc": "2.0", "id": msg["id"],
                               "error": {"code": -32601,
                                         "message": "not supported by probe"}})
            elif msg.get("method") == "session/update":
                p = msg.get("params") or {}
                u = p.get("update") or {}
                if u.get("sessionUpdate") == "agent_message_chunk":
                    # Route by sessionId: one process now serves several
                    # sessions, so a single shared buffer would blend two
                    # lanes' answers together and both would look truncated.
                    sink = self.sinks.get(p.get("sessionId"))
                    if sink is not None:
                        sink.append((u.get("content") or {}).get("text") or "")
        self.dead = self.proc.poll()


class Lane:
    def __init__(self, n, conn):
        self.n = n
        self.conn = conn
        self.chunks = []
        self.session = None

    def open(self):
        got = self.conn.call("session/new", {"cwd": CWD, "mcpServers": []})
        self.session = got.get("sessionId")
        self.conn.sinks[self.session] = self.chunks
        for method in ("session/set_model", "session/setModel"):
            try:
                self.conn.call(method, {"sessionId": self.session,
                                        "modelId": MODEL})
                break
            except Exception:
                continue

    def turn(self, n, text):
        self.chunks.clear()
        t0 = time.time()
        row = {"lane": self.n, "conn": self.conn.n, "turn": n,
               "at": time.strftime("%H:%M:%S"), "t0": round(t0, 3)}
        try:
            res = self.conn.call("session/prompt",
                                 {"sessionId": self.session,
                                  "prompt": [{"type": "text", "text": text}]},
                                 timeout=TURN_TIMEOUT)
            body = "".join(self.chunks)
            row.update(secs=round(time.time() - t0, 1), chars=len(body),
                       stop=res.get("stopReason"), ok=True)
            if not body.strip():
                row.update(ok=False, error="empty stream (no content)")
            elif res.get("stopReason") not in (None, "end_turn"):
                row.update(ok=False, error=f"stopReason={res.get('stopReason')}")
            elif len(body) < 200:
                # ~150 words is ~900 chars. Far under that means the stream was
                # cut - how a soft throttle appears when nobody sends a 429.
                row.update(ok=False, error=f"short stream ({len(body)}ch)")
        except Exception as exc:
            row.update(secs=round(time.time() - t0, 1), chars=0, ok=False,
                       error=str(exc)[:400])
        row["t1"] = round(time.time(), 3)
        if self.conn.dead is not None:
            row["error"] = (row.get("error", "") +
                            f" | process exited {self.conn.dead}").strip(" |")
            row["ok"] = False
        log(row)


PROMPTS = [
    "In about 150 words, explain why bread dough needs to rest between "
    "kneading and shaping. No code.",
    "In about 150 words, describe how a bicycle stays upright while moving.",
    "In about 150 words, explain what makes a good index in a library's card "
    "catalogue.",
    "In about 150 words, describe why cast iron pans are seasoned.",
    "In about 150 words, explain how a lock and dam lets a boat change "
    "elevation on a river.",
]


def run(lane, barrier, deadline):
    n = 0
    while time.time() < deadline and not abort.is_set():
        n += 1
        start = time.time()
        try:
            barrier.wait(timeout=TURN_TIMEOUT + 30)
        except Exception:
            pass
        lane.turn(n, PROMPTS[(n - 1) % len(PROMPTS)])
        gap = CADENCE - (time.time() - start)
        while gap > 0 and not abort.is_set():
            time.sleep(min(gap, 2))
            gap -= 2


def watchdog(deadline):
    """Bail out before the OOM killer does, so a verdict still gets written."""
    while time.time() < deadline and not abort.is_set():
        free = available_gb()
        if free < MIN_FREE_GB:
            print(f"\n*** ABORTING: only {free:.1f} GB available "
                  f"(floor {MIN_FREE_GB} GB). Writing the verdict with what "
                  f"we have.", flush=True)
            abort.set()
            return
        time.sleep(10)


def max_overlap():
    """The most turns in flight at once - proof the test was concurrent."""
    edges = []
    for r in rows:
        if "t0" in r and "t1" in r:
            edges.append((r["t0"], 1))
            edges.append((r["t1"], -1))
    edges.sort()
    cur = best = 0
    for _, d in edges:
        cur += d
        best = max(best, cur)
    return best


def report():
    total = len(rows)
    bad = [r for r in rows if not r.get("ok")]
    limits = [r for r in bad if LIMIT.search(r.get("error", ""))]
    lat = sorted(r["secs"] for r in rows if r.get("ok"))
    def pct(p):
        return lat[min(int(len(lat) * p), len(lat) - 1)] if lat else 0
    seen = len({r["lane"] for r in rows}) or 1
    per_lane = total / seen
    span = (max(r["t1"] for r in rows) - min(r["t0"] for r in rows)) if rows else 0
    actual = (span / per_lane) if per_lane else 0
    overlap = max_overlap()

    L = ["# OpenCode free tier: does it hold under four concurrent lanes?\n"]
    L.append(f"Model: `{MODEL}`  ")
    L.append(f"{PROCS} `opencode acp` processes x {PER_PROC} sessions = "
             f"**{LANES} concurrent lanes**, held in lockstep.  ")
    L.append(f"Ran {span/60:.1f} min"
             f"{' (ABORTED EARLY - see below)' if abort.is_set() else ''}.  ")
    L.append(f"Measured cadence: a turn every **{actual:.0f}s** per lane "
             f"({per_lane:.0f} turns each). The fleet's measured cadence is "
             f"138s per lane, so this ran at **{138/actual if actual else 0:.1f}x** "
             f"the real load.\n")
    L.append(f"**Requests really did overlap: up to {overlap} in flight at "
             f"once** (of {LANES} lanes). If this said 1, opencode would be "
             f"serialising and the test would prove nothing about "
             f"concurrency.\n")
    L.append(f"- turns attempted: **{total}**")
    L.append(f"- failed: **{len(bad)}**"
             f"{f' ({100*len(bad)/total:.1f}%)' if total else ''}")
    L.append(f"- failures that look like a LIMIT: **{len(limits)}**")
    if lat:
        L.append(f"- latency of successful turns: median **{pct(0.5):.1f}s**, "
                 f"p90 **{pct(0.9):.1f}s**, max **{lat[-1]:.1f}s**")
    L.append("")

    if total == 0:
        L.append("## Verdict: NO DATA\n")
        L.append("Not one turn completed. Something is wrong with the probe or "
                 "the lane, not necessarily with the free tier.")
    elif not bad:
        L.append("## Verdict: no limit reached\n")
        L.append(f"Nothing was refused, truncated or throttled across {total} "
                 f"turns with up to {overlap} requests in flight at once.")
        L.append("")
        L.append("**What this does NOT prove.** The run was "
                 f"{span/60:.0f} minutes. A 14-hour overnight window is "
                 f"{14*60/(span/60) if span else 0:.0f}x longer, so a daily "
                 f"cap, a rolling-window cap or a slow tightening would not "
                 f"appear here. InferX also published no limit and died after "
                 f"an hour at four lanes. Treat this as 'no per-minute or "
                 f"per-concurrency limit at fleet load', not as 'safe "
                 f"unattended all night'.")
    else:
        L.append("## Verdict: it broke\n")
        for r in bad[:25]:
            L.append(f"- lane{r['lane']} (proc {r.get('conn')}) turn "
                     f"{r['turn']} at {r['at']}: `{r.get('error','')[:200]}`")
        if len(bad) > 25:
            L.append(f"- ... and {len(bad)-25} more, in `{OUT}`")
        first = min(r["at"] for r in bad)
        same = len({r["lane"] for r in bad if r["at"][:5] == first[:5]})
        L.append(f"\nFirst failure **{first}**; **{same}** of {LANES} lanes "
                 f"failed inside that minute. All lanes at once points at an "
                 f"ACCOUNT limit - the InferX failure mode. One lane alone "
                 f"points at that connection.")

    L.append("\n## Per lane\n")
    L.append("| lane | process | turns | failed |")
    L.append("|---|---|---|---|")
    for i in range(LANES):
        mine = [r for r in rows if r["lane"] == i]
        L.append(f"| {i} | {mine[0].get('conn') if mine else '-'} | "
                 f"{len(mine)} | {len([r for r in mine if not r.get('ok')])} |")

    L.append("\n## How to read this\n")
    L.append("Each lane is a separate ACP session, but they share "
             f"{PROCS} processes rather than one each, because this box has "
             "llama-server holding 47 GB and a full swap - four separate "
             "processes were OOM-killed on the first attempt. A per-ACCOUNT "
             "limit behaves the same either way; a per-CONNECTION limit would "
             "not, and this test cannot tell you about that one.")
    L.append(f"\nRaw rows: `{OUT}`\n")
    open(REPORT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    if "--from-jsonl" in sys.argv:
        for line in open(OUT):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        print(f"rebuilding the verdict from {len(rows)} recorded turns")
        report()
        return 0
    free = available_gb()
    print(f"available memory: {free:.1f} GB", flush=True)
    if free < MIN_FREE_GB + 2:
        print(f"refusing to start: {free:.1f} GB available, need "
              f"{MIN_FREE_GB + 2:.0f} GB", file=sys.stderr)
        return 1
    conns, lanes = [], []
    for p in range(PROCS):
        try:
            c = Conn(p)
            c.call("initialize", {
                "protocolVersion": 1,
                "clientCapabilities": {
                    "fs": {"readTextFile": False, "writeTextFile": False},
                    "terminal": False}})
        except Exception as exc:
            print(f"process {p} would not start: {exc}", file=sys.stderr)
            continue
        conns.append(c)
        for s in range(PER_PROC):
            ln = Lane(len(lanes), c)
            try:
                ln.open()
            except Exception as exc:
                print(f"lane {ln.n} would not open: {exc}", file=sys.stderr)
                continue
            lanes.append(ln)
            print(f"lane{ln.n} up on proc{p}, session {ln.session}", flush=True)
    if not lanes:
        print("no lane opened - nothing to measure", file=sys.stderr)
        report()
        return 1
    deadline = time.time() + MINUTES * 60
    threading.Thread(target=watchdog, args=(deadline,), daemon=True).start()
    barrier = threading.Barrier(len(lanes))
    threads = [threading.Thread(target=run, args=(ln, barrier, deadline))
               for ln in lanes]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for c in conns:
        try:
            c.proc.terminate()
        except Exception:
            pass
    report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
