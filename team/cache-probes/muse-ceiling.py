#!/usr/bin/env python3
"""Find the concurrency OpenCode's free tier actually supports.

The 2026-09-14 probe passed at 4 lanes and the fleet broke at 13, so the
ceiling is between. This walks N up until the limit bites and reports the
highest N that stayed clean.

TWO THINGS THE EARLIER PROBE GOT WRONG, fixed here:

1. It used TOOL-FREE prompts. A tool-using turn is several model calls, not
   one - the agent calls, reads a file, calls again - so the fleet's request
   rate per turn was far higher than the probe's and the probe understated the
   load per lane. These prompts read a file.

2. It inferred failure from hangs. A rate-limited call arrives as a STREAM
   ERROR inside opencode: nothing propagates to ACP, the turn just stops, and
   acp-worker waits out its 600 s stall timeout. So the probe saw a timeout
   and could not say why. This reads opencode's own log, which records
   `AI_APICallError: Rate limit exceeded` against the model id - ground truth
   instead of a symptom.

Caveat kept in the report: the limit looks ROLLING, so each step spends
allowance the next step inherits. Steps are spaced by COOLDOWN to drain it,
and a ceiling found walking upward is a floor on the true ceiling, not an
exact value.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time

LEVELS = [int(x) for x in os.environ.get("LEVELS", "2,4,6,8,10,12,14").split(",")]
ROUNDS = int(os.environ.get("ROUNDS", 3))
COOLDOWN = float(os.environ.get("COOLDOWN", 75))
TURN_TIMEOUT = 240
MODEL = "opencode/muse-spark-1.3-contributor-free"
LOG = os.path.expanduser("~/.local/share/opencode/log/opencode.log")
OUT = os.environ.get("OUT", os.path.expanduser("~/muse-ceiling.jsonl"))
REPORT = os.environ.get("REPORT", os.path.expanduser("~/muse-ceiling.md"))
CWD = os.path.expanduser("~/.cache")
RATE = re.compile(r"muse-spark.*Rate limit exceeded", re.I)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "mp", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "muse-probe2.py"))
mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mp)

results = []


def log_size():
    try:
        return os.path.getsize(LOG)
    except OSError:
        return 0


def new_rate_errors(since):
    """Rate-limit lines appended to opencode's log since byte offset `since`."""
    try:
        with open(LOG, errors="ignore") as fh:
            fh.seek(since)
            return sum(1 for line in fh if RATE.search(line))
    except OSError:
        return 0


class Conn(mp.Conn):
    """mp.Conn but spawning the renamed shim the fleet now uses."""

    def __init__(self, n):
        self.n = n
        self.next_id = 1
        self.io = threading.Lock()
        self.replies, self.events, self.sinks = {}, {}, {}
        self.dead = None
        self.proc = subprocess.Popen(
            ["muse-engine", "acp"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            bufsize=1, cwd=CWD, env=dict(os.environ))
        threading.Thread(target=self.reader, daemon=True).start()


PROMPT = ("Use your tools to read the file ./muse-ceiling-fixture.txt in the "
          "current directory and reply with the single word it contains. "
          "Nothing else.")


def run_level(n):
    """n concurrent sessions, ROUNDS simultaneous rounds. Returns a row."""
    conn = Conn(0)
    conn.call("initialize", {
        "protocolVersion": 1,
        "clientCapabilities": {
            "fs": {"readTextFile": False, "writeTextFile": False},
            "terminal": False}})
    lanes = []
    for i in range(n):
        ln = mp.Lane(i, conn)
        try:
            ln.open()
            lanes.append(ln)
        except Exception as exc:
            print(f"  lane {i} would not open: {exc}", flush=True)
    if not lanes:
        conn.proc.terminate()
        return {"n": n, "opened": 0, "error": "no lanes opened"}

    mark = log_size()
    turns, fails, lats = 0, 0, []
    lock = threading.Lock()

    def one(ln, rnd):
        nonlocal turns, fails
        ln.chunks.clear()
        t0 = time.time()
        ok, err = True, ""
        try:
            r = conn.call("session/prompt",
                          {"sessionId": ln.session,
                           "prompt": [{"type": "text", "text": PROMPT}]},
                          timeout=TURN_TIMEOUT)
            body = "".join(ln.chunks)
            if not body.strip():
                ok, err = False, "empty stream"
            elif r.get("stopReason") not in (None, "end_turn"):
                ok, err = False, f"stopReason={r.get('stopReason')}"
        except Exception as exc:
            ok, err = False, str(exc)[:120]
        with lock:
            turns += 1
            if ok:
                lats.append(time.time() - t0)
            else:
                fails += 1
                print(f"  n={n} r{rnd} lane{ln.n}: {err}", flush=True)

    for rnd in range(1, ROUNDS + 1):
        ts = [threading.Thread(target=one, args=(ln, rnd)) for ln in lanes]
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    # The log is written by the opencode process; give it a moment to flush
    # before counting, or a real error lands after the read and reads as clean.
    time.sleep(4)
    rl = new_rate_errors(mark)
    conn.proc.terminate()
    lats.sort()
    row = {"n": len(lanes), "turns": turns, "failed": fails,
           "rate_limit_errors": rl,
           "median_s": round(lats[len(lats) // 2], 1) if lats else None,
           "max_s": round(lats[-1], 1) if lats else None,
           "clean": fails == 0 and rl == 0}
    with open(OUT, "a") as fh:
        fh.write(json.dumps(row) + "\n")
    print(f"  => n={row['n']}: {turns} turns, {fails} failed, "
          f"{rl} rate-limit errors, median {row['median_s']}s "
          f"{'CLEAN' if row['clean'] else 'DIRTY'}", flush=True)
    return row


def report():
    clean = [r for r in results if r.get("clean")]
    ceiling = max((r["n"] for r in clean), default=0)
    first_bad = min((r["n"] for r in results if not r.get("clean")), default=None)
    L = ["# OpenCode free tier: the real concurrency ceiling\n"]
    L.append(f"Model: `{MODEL}`  ")
    L.append(f"Levels tried: {', '.join(str(r['n']) for r in results)} · "
             f"{ROUNDS} simultaneous rounds each · tool-using prompts · "
             f"{COOLDOWN:.0f}s between levels\n")
    L.append("| lanes | turns | failed | rate-limit errors | median | verdict |")
    L.append("|---|---|---|---|---|---|")
    for r in results:
        L.append(f"| {r['n']} | {r.get('turns','-')} | {r.get('failed','-')} | "
                 f"{r.get('rate_limit_errors','-')} | "
                 f"{r.get('median_s','-')}s | "
                 f"{'clean' if r.get('clean') else 'LIMITED'} |")
    L.append("")
    if ceiling and first_bad:
        L.append(f"## Highest clean concurrency: **{ceiling}** "
                 f"(first limited at {first_bad})\n")
        L.append(f"Set the fleet's gate to **{ceiling}** concurrent Muse "
                 f"turns. Lanes above that wait for a slot instead of being "
                 f"refused, because a refusal costs a full stall timeout.")
    elif ceiling:
        L.append(f"## No limit reached up to **{ceiling}** lanes\n")
        L.append("The ceiling is above the highest level tried.")
    else:
        L.append("## Limited at every level tried\n")
        L.append("Even the lowest concurrency saw refusals - suspect the "
                 "account allowance is spent, not the concurrency.")
    L.append("\n**Why a ceiling found this way is a FLOOR, not an exact "
             "number.** The limit is rolling: each level spends allowance the "
             f"next inherits, and {COOLDOWN:.0f}s between levels may not fully "
             "drain it. Walking upward therefore finds the lowest N that "
             "breaks under accumulated pressure, which is the safe direction "
             "to be wrong in.")
    L.append(f"\nRaw rows: `{OUT}`\n")
    open(REPORT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    os.makedirs(CWD, exist_ok=True)
    with open(os.path.join(CWD, "muse-ceiling-fixture.txt"), "w") as fh:
        fh.write("chandlery\n")
    for i, n in enumerate(LEVELS):
        print(f"=== level {n} lanes", flush=True)
        row = run_level(n)
        results.append(row)
        # Stop climbing once the limit bites: higher levels only confirm it and
        # they spend allowance that makes the next run less honest.
        if not row.get("clean"):
            print(f"  limit reached at {n}; not climbing further", flush=True)
            break
        if i + 1 < len(LEVELS):
            time.sleep(COOLDOWN)
    report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
