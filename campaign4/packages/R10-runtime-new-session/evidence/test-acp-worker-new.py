#!/usr/bin/env python3
"""R10: /new over the real socket of a real acp-worker process, against a stub
ACP engine. No network, no model, no fleet seat. Exit 0 clean, 1 with findings.

    python test-acp-worker-new.py [path/to/acp-worker]
"""
import json, os, socket, subprocess, sys, tempfile, threading, time

WORKER = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "acp-worker")
PASS = FAIL = 0

STUB = r'''
import json, os, sys, time
log = open(os.environ["STUB_LOG"], "a")
mode = os.environ.get("STUB_NEW_MODE", "")
n = 0
def out(o):
    sys.stdout.write(json.dumps(o) + "\n"); sys.stdout.flush()
for line in sys.stdin:
    try:
        m = json.loads(line)
    except Exception:
        continue
    mid, meth, p = m.get("id"), m.get("method"), m.get("params") or {}
    if meth:
        log.write(json.dumps({"t": time.time(), "method": meth, "params": p}) + "\n"); log.flush()
    if meth == "initialize":
        res = {"protocolVersion": 1, "agentCapabilities": {}, "agentInfo": {"name": "stub", "version": "0"}}
    elif meth == "session/new":
        n += 1
        if n > 1 and os.environ.get("STUB_NEW_DELAY"):
            time.sleep(float(os.environ["STUB_NEW_DELAY"]))
        if n > 1 and mode == "fail":
            out({"jsonrpc": "2.0", "id": mid, "error": {"code": -32000, "message": "stub refuses"}}); continue
        sid = "stub-1" if (n > 1 and mode == "same") else f"stub-{n}"
        res = {} if (n > 1 and mode == "none") else {"sessionId": sid, "modes": {"availableModes": [{"id": "build"}]}}
    elif meth == "session/prompt":
        text = p["prompt"][0]["text"]
        if "SLOW" in text:
            time.sleep(3)
        out({"jsonrpc": "2.0", "method": "session/update", "params": {"sessionId": p["sessionId"],
             "update": {"sessionUpdate": "agent_message_chunk", "content": {"type": "text", "text": "ok " + p["sessionId"]}}}})
        res = {"stopReason": "end_turn"}
    else:
        res = {}
    if mid is not None:
        out({"jsonrpc": "2.0", "id": mid, "result": res})
'''


def ok(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  pass  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


class Seat:
    def __init__(self, name, **env):
        self.d = tempfile.mkdtemp(prefix=f"r10-{name}-")
        open(f"{self.d}/stub.py", "w").write(STUB)
        self.log = f"{self.d}/stub.log"
        e = dict(os.environ, ACP_STATE_HOME=self.d, AGENTDECK_INSTANCE_ID=f"t-{name}", STUB_LOG=self.log,
                 ACP_MODEL="stub/model-x", **env)
        e.pop("ACP_RESUME", None) if "ACP_RESUME" not in env else None
        self.p = subprocess.Popen([sys.executable, WORKER, sys.executable, f"{self.d}/stub.py"], env=e, cwd=self.d,
                                  stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.sock = f"{self.d}/acp-sock/t-{name}.sock"
        self.hist = f"{self.d}/acp-history/t-{name}.jsonl"
        self.state = f"{self.d}/acp-sessions/t-{name}.json"
        for _ in range(80):
            try:
                if self.send("/ping", 2).get("status") == "idle":
                    break
            except OSError:
                pass
            time.sleep(0.25)

    def send(self, text, timeout=30):
        s = socket.socket(socket.AF_UNIX)
        s.settimeout(timeout)
        s.connect(self.sock)
        s.sendall((json.dumps({"text": text}) + "\n").encode())
        buf = b""
        while not buf.endswith(b"\n"):
            c = s.recv(65536)
            if not c:
                break
            buf += c
        s.close()
        return json.loads(buf)

    def calls(self, method):
        return [json.loads(l) for l in open(self.log) if json.loads(l)["method"] == method]

    def wait_idle(self, secs=15):
        end = time.time() + secs
        while time.time() < end:
            if self.send("/ping", 5)["status"] == "idle":
                return True
            time.sleep(0.2)
        return False

    def history(self):
        return [json.loads(l) for l in open(self.hist)] if os.path.exists(self.hist) else []

    def close(self):
        self.p.kill(); self.p.wait()


def main():
    print(f"worker: {WORKER}")
    print("case: idle /new gives a new, different id, a history boundary, and model/mode re-applied")
    s = Seat("idle")
    s.send("warm"); s.wait_idle()
    ok("first session answered and persisted", json.load(open(s.state)).get("sessionId") == "stub-1")
    r = s.send("/new")
    st = r.get("status", "")
    ok("reply is ok and names a new id", r.get("ok") and st.startswith("new stub-2"), r)
    ok("exactly one extra session/new", len(s.calls("session/new")) == 2)
    b = [h for h in s.history() if h["text"].startswith("[new session] stub-1 -> stub-2")]
    ok("history has one old -> new boundary", len(b) == 1, s.history())
    models = [c["params"].get("sessionId") for c in s.calls("session/set_model") + s.calls("session/unstable_setSessionModel")]
    ok("model pinned on the new session", "stub-2" in models, models)
    ok("mode applied on the new session", "stub-2" in [c["params"]["sessionId"] for c in s.calls("session/set_mode")])
    ok("unproven new id is not persisted", json.load(open(s.state)).get("sessionId") is None)
    ok("no prompt was sent by /new", len(s.calls("session/prompt")) == 1)
    print("case: normal prompt and /ping still work, on the new session")
    ok("prompt starts", s.send("hello")["status"] == "started")
    ok("turn ends idle", s.wait_idle())
    ok("prompt ran on stub-2", [c["params"]["sessionId"] for c in s.calls("session/prompt")] == ["stub-1", "stub-2"])
    ok("answered session is now persisted", json.load(open(s.state)).get("sessionId") == "stub-2")
    s.close()

    print("case: busy and queued refuse, with no effect")
    s = Seat("busy")
    s.send("SLOW one")
    s.send("two")  # queued behind it
    r = s.send("/new")["status"]
    ok("refused while running + queued", r.startswith("new refused: seat busy") and "queued" in r, r)
    ok("no session/new was called", len(s.calls("session/new")) == 1)
    ok("queue untouched: both prompts run on stub-1", s.wait_idle() and s.wait_idle() and
       [c["params"]["sessionId"] for c in s.calls("session/prompt")] == ["stub-1", "stub-1"])
    s.close()

    print("case: /new and a prompt racing: the prompt waits, then runs on the new session")
    s = Seat("race", STUB_NEW_DELAY="1.5")
    res = {}
    t = threading.Thread(target=lambda: res.update(new=s.send("/new")["status"]))
    t.start(); time.sleep(0.3)
    res["p"] = s.send("after")["status"]
    t.join()
    ok("/new succeeded", res["new"].startswith("new stub-2"), res)
    ok("prompt admitted after /new", res["p"] == "started" and s.wait_idle(), res)
    ok("prompt used the new session", [c["params"]["sessionId"] for c in s.calls("session/prompt")] == ["stub-2"])
    print("case: two /new at once do not interleave")
    out = []
    ts = [threading.Thread(target=lambda: out.append(s.send("/new")["status"])) for _ in range(2)]
    [x.start() for x in ts]; [x.join() for x in ts]
    ok("one switched, one refused", sorted(o.split()[1] for o in out) == ["refused:", "stub-3"], out)
    s.close()

    for mode, want in (("fail", "adapter refused"), ("same", "the same session id"), ("none", "no session id")):
        print(f"case: adapter {mode}: never a success, old session kept")
        s = Seat(mode, STUB_NEW_MODE=mode)
        r = s.send("/new")["status"]
        ok(f"{mode}: reported as failure", r.startswith("new failed") and want in r and "still on stub-1" in r, r)
        ok(f"{mode}: no boundary written", not [h for h in s.history() if h["text"].startswith("[new session]")])
        s.send("x"); s.wait_idle()
        ok(f"{mode}: next prompt still on stub-1", [c["params"]["sessionId"] for c in s.calls("session/prompt")] == ["stub-1"])
        s.close()

    print("case: a lane pinned with ACP_RESUME refuses /new")
    s = Seat("resume", ACP_RESUME="pinned-conv")
    r = s.send("/new")["status"]
    ok("refused, naming ACP_RESUME", r.startswith("new refused") and "ACP_RESUME" in r, r)
    ok("no extra session/new", len(s.calls("session/new")) == 1)
    s.close()

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
