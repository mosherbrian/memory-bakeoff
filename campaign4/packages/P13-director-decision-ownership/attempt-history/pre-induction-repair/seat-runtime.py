#!/usr/bin/env python3
# INJECTED ACP seat runtime (TEST ONLY, never live proof). One unix socket per fixture seat at
# $HOME/.config/agent-deck/acp-sock/<id>.sock (where the REAL wake connects). It answers like acp-worker
# ({"status": "started"}), then performs the task text AS A SEAT WOULD: writes the artifact, runs the
# claim CLI line exactly as given, and then the RUNTIME (this double, not the task) records the turn
# start/end in $STREAMS/<id>.jsonl. Director/duty seats only log what they received.
import json, os, re, shlex, socket, subprocess, sys, threading, time
home = os.environ["HOME"]; streams = os.environ["STREAMS"]; log = open(os.environ["INJ"] + "/seat-runtime.log", "a", buffering=1)
ids = sys.argv[1:]
def turn(sid, text):
    item = "i%d" % int(time.time() * 1000)
    bad = [w for w in ("decision-turn", "<bound-stream>", ".jsonl") if w in text]
    log.write("%s RECV %s %d bytes anti-stub=%s\n" % (time.strftime("%H:%M:%S"), sid, len(text), bad or "clean"))
    open(os.environ["INJ"] + "/recv-" + sid + ".txt", "a").write(text + "\n----\n")
    if os.environ.get("SEAT_DIRECTOR_DECIDES") == "1" and "verifier PASS" in text:
        d = re.search(r"(/\S+/agent-loop) decide --config (\S+) --qid (\S+)", text)
        if d:
            r = subprocess.run([d.group(1), "decide", "--config", d.group(2), "--qid", d.group(3), "--kind", "question_answered", "--ref", "neg-early", "--reason", "injected early decision"], capture_output=True, text=True)
            log.write("%s EARLY-DECIDE %s rc=%d\n" % (time.strftime("%H:%M:%S"), sid, r.returncode))
    m = re.search(r'Write the single line "(.+?)" to the file (\S+?)\.\n', text)
    if m: open(m.group(2), "w").write(m.group(1) + "\n")
    v = re.search(r'Check that (\S+) contains exactly "(.+?)"', text); o = re.search(r'Write one line to (\S+?): ', text)
    if v and o:
        ok = open(v.group(1)).read().strip() == v.group(2); open(o.group(1), "w").write(("PASS" if ok else "FAIL") + "\n")
    c = [l.strip() for l in text.splitlines() if l.strip().startswith("/") and " claim --config " in l]
    if c:
        r = subprocess.run(shlex.split(c[0]), capture_output=True, text=True)
        log.write("%s CLAIM %s rc=%d %s %s\n" % (time.strftime("%H:%M:%S"), sid, r.returncode, c[0], (r.stdout + r.stderr).strip()[:200]))
        with open(os.path.join(streams, sid + ".jsonl"), "a") as f:
            f.write(json.dumps({"t": "start", "item": item}) + "\n" + json.dumps({"t": "end", "item": item}) + "\n")
def serve(sid):
    p = os.path.join(home, ".config/agent-deck/acp-sock", sid + ".sock")
    try: os.remove(p)
    except OSError: pass
    s = socket.socket(socket.AF_UNIX); s.bind(p); s.listen(8)
    while True:
        c, _ = s.accept(); buf = b""
        while b"\n" not in buf:
            ch = c.recv(65536)
            if not ch: break
            buf += ch
        c.sendall(b'{"status": "started"}\n'); c.close()
        try: text = json.loads(buf.decode()).get("text", "")
        except Exception: text = ""
        # The loop's wake text is itself a JSON envelope {kind, package, action, execution, text};
        # the seat reads the task in its "text" (as an ACP runtime hands it to the model).
        try: text = json.loads(text).get("text", text) if text.lstrip().startswith("{") else text
        except Exception: pass
        threading.Thread(target=turn, args=(sid, text), daemon=True).start()
os.makedirs(os.path.join(home, ".config/agent-deck/acp-sock"), exist_ok=True); os.makedirs(streams, exist_ok=True)
for i in ids: threading.Thread(target=serve, args=(i,), daemon=True).start()
while True: time.sleep(3600)
