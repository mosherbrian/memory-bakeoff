#!/usr/bin/env python
"""Gate-writing with an AUTOMATABLE critique loop.

The critique is built only from MEASURED PROPERTIES OF THE MODEL'S OWN OUTPUT -
does it parse, does its selftest pass, how many distinct fixtures does that
selftest exercise, does it resolve paths the same from two working directories,
does it reject the unbuilt artifact. Nothing about the row's specific hazards is
fed back, because naming those would transplant another author's thinking and
the resulting gate would be mine, not the model's.

That constraint is also what makes this shippable: every signal here is one the
gate-batch driver could compute on its own.
"""
import json, os, re, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

S = Path("/tmp/claude-1000/-var-home-bmosher/09b5ba50-67c7-4535-b27c-5baa3e1c4fa8/scratchpad/gate-bakeoff")
BASE = (S / "muse-prompt.txt").read_text()
ART = "/home/bmosher/memory-bake-off/team/S10-PI-LCM-HIST"


def call_local(prompt, model="qwen3.8-27b-code"):
    body = json.dumps({"model": model, "max_tokens": 16000, "temperature": 0.2,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    r = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions",
                               data=body, headers={"content-type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=2400))["choices"][0]["message"]["content"]


def call_go(prompt, model):
    p = subprocess.run([os.path.expanduser("~/.config/agent-deck/muse")],
                       input=prompt, text=True, capture_output=True, timeout=1500,
                       env=dict(os.environ, MUSE_MODEL=model))
    return p.stdout


def extract(raw):
    clean = re.sub(r"\x1b\[[0-9;]*m", "", raw)
    m = re.search(r"```(?:python)?\n(.*?)```", clean, re.S)
    body = m.group(1) if m else clean
    lines = body.split("\n")
    i = next((i for i, l in enumerate(lines)
              if l.lstrip().startswith(("#!", "import ", "from ", '"""'))), 0)
    return "\n".join(lines[i:])


def run(path, args, cwd):
    try:
        p = subprocess.run([sys.executable, str(path)] + args, capture_output=True,
                           text=True, timeout=300, cwd=cwd)
        return p.returncode, (p.stdout + p.stderr)[:1500]
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


def measure(path):
    """Every signal the driver could compute for itself."""
    m = {}
    try:
        compile(path.read_text(), str(path), "exec")
        m["parses"] = True
    except SyntaxError as e:
        return {"parses": False, "error": str(e)[:200]}
    m["bytes"] = path.stat().st_size
    m["selftest_rc"], m["selftest_out"] = run(path, ["--selftest"], "/tmp")
    # how many distinct fixtures does the selftest actually exercise?
    src = path.read_text()
    m["fixtures"] = len(re.findall(r"(?i)\b(mutant|fixture|non[-_]?conform|deliberately)", src))
    m["home_rc"], m["home_out"] = run(path, [], os.path.expanduser("~"))
    m["tmp_rc"], m["tmp_out"] = run(path, [], "/tmp")
    m["path_stable"] = m["home_out"][:400] == m["tmp_out"][:400]
    return m


def critique(m, rnd):
    if not m.get("parses"):
        return f"Your file does not parse: {m.get('error')}. Return valid Python only."
    c = [f"ROUND {rnd} REVIEW of the file you just wrote. These are MEASURED "
         f"facts about your own output, nothing else.", ""]
    c.append(f"- it is {m['bytes']:,} bytes and parses.")
    c.append(f"- `--selftest` exited {m['selftest_rc']}. Its output was:\n"
             f"    {m['selftest_out'].strip()[:400]}")
    if m["selftest_rc"] != 0:
        c.append("  A selftest that does not exit 0 is a failed gate. Fix that first.")
    c.append(f"- run with no arguments against the real (unbuilt) artifact it "
             f"exited {m['home_rc']}: {m['home_out'].strip()[:220]}")
    if m["home_rc"] == 0:
        c.append("  THAT IS A DEFECT: the artifact does not exist yet, so a "
                 "clean exit means your check does not check anything.")
    if not m["path_stable"]:
        c.append(f"- RUN FROM A DIFFERENT DIRECTORY IT SAYS SOMETHING ELSE:\n"
                 f"    from $HOME: {m['home_out'].strip()[:150]}\n"
                 f"    from /tmp : {m['tmp_out'].strip()[:150]}\n"
                 "  A check must mean the same thing from every working "
                 "directory. Resolve every path absolutely.")
    else:
        c.append("- it resolves paths identically from two different working "
                 "directories. Keep that.")
    c.append("")
    c.append("THE ONE THING TO IMPROVE NOW: a gate's value is the failures it "
             "can still catch AFTER the obvious one. Your selftest currently "
             "proves it rejects a non-conforming fixture. Widen it: build "
             "SEVERAL distinct deliberately-wrong fixtures, each wrong in a "
             "different way that the row's own text makes possible, and reject "
             "each by its own named finding. Accept a conforming one. Exit 0 "
             "only if every one of those holds.")
    c.append("")
    c.append("Return the COMPLETE revised file. Python only, no commentary, no "
             "markdown fences.")
    return "\n".join(c)


def passk(out):
    """Fraction of rounds that produced a USABLE gate. Report this, not best-of.

    Adopted 2026-09-19 from IBM's Consistency Analyzer work (CANDIDATE-CARD-
    ALTK-EVOLVE.md). Its argument is that Mean@k hides unreliability - a ReAct
    agent scoring 77.4% average succeeded on all five repeats for only 53% of
    tasks. The gate bake-off filed the night before reported each author's BEST
    VALID round, which is exactly Mean@k. Re-scored: cairn produced a usable
    gate in 3 of 3 rounds, Flash-Next in 1 of 3. gate-batch dispatches ONCE and
    expects a gate, so 1-in-3 is the number that decides, and best-of-three is
    not.
    """
    scored = [r for r in out["rounds"] if "parses" in r]
    ok = [r for r in scored
          if r.get("parses") and r.get("selftest_rc") == 0
          and r.get("home_rc") == 1 and r.get("bytes", 0) > 0]
    return {"rounds_scored": len(scored), "usable": len(ok),
            "pass_k": (len(ok) / len(scored)) if scored else None}


def loop(name, caller, rounds=3):
    out = {"name": name, "rounds": []}
    prompt = BASE
    for r in range(1, rounds + 1):
        t0 = time.time()
        try:
            raw = caller(prompt)
        except Exception as e:
            out["rounds"].append({"round": r, "error": f"{type(e).__name__}: {e}"})
            break
        p = S / f"{name}-r{r}.py"
        p.write_text(extract(raw))
        m = measure(p)
        m["secs"] = round(time.time() - t0)
        out["rounds"].append({"round": r, **{k: v for k, v in m.items()
                                             if not k.endswith("_out")}})
        print(f"  {name} round {r}: {m['secs']}s, {m.get('bytes',0):,}B, "
              f"selftest rc={m.get('selftest_rc')}, unbuilt rc={m.get('home_rc')}, "
              f"path-stable={m.get('path_stable')}", flush=True)
        if r < rounds:
            prompt = (BASE + "\n\n=== YOUR PREVIOUS ATTEMPT ===\n"
                      + p.read_text()[:12000] + "\n\n=== " + critique(m, r))
    out["consistency"] = passk(out)
    print(f"  {name} Pass^k: {out['consistency']['usable']}/"
          f"{out['consistency']['rounds_scored']} rounds usable")
    return out


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "cairn":
        res = loop("cairn", lambda p: call_local(p))
    else:
        res = loop("muse", lambda p: call_go(p, "opencode-go/muse-spark-1.3-contributor"))
    (S / f"{which}-loop.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1)[-900:])


def call_zen(prompt, model):
    """PLAIN COMPLETION, the same treatment cairn gets.

    The first comparison was not apples to apples and the round-2 collapses
    were the tell. cairn was called through /v1/chat/completions - no tools,
    nothing but text in and text out - while the Go models went through
    `opencode run`, which is an AGENT: it has a filesystem, it reads things, it
    does work. DeepSeek proved that in round one by listing the real team/
    directory instead of writing a gate. Given a critique and its own previous
    file, an agent goes and DOES something; a completion endpoint answers.

    Judging a model's gate-writing on whether its agent harness stayed on task
    measures the harness. This routes every hosted model the way cairn is
    already routed, so the only difference left is the model.
    """
    import os, json, urllib.request
    key = base = None
    for line in open(os.path.expanduser("~/.config/agent-deck/dsh-keys.env")):
        line = line.strip().removeprefix("export ").strip()
        if line.startswith("OPENCODE_API_KEY="): key = line.split("=", 1)[1].strip('"\'')
        if line.startswith("OPENCODE_BASE_URL="): base = line.split("=", 1)[1].strip('"\'')
    body = json.dumps({"model": model.split("/", 1)[-1], "max_tokens": 16000,
                       "temperature": 0.2,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    r = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                               headers={"content-type": "application/json",
                                        "authorization": f"Bearer {key}",
                                        "user-agent": "opencode/1.0"})
    return json.load(urllib.request.urlopen(r, timeout=1800))["choices"][0]["message"]["content"]


HALOGEN_RECORD = []


def call_halogen(prompt, effort="medium", max_tok=16384):
    """Qwen3.8-Flash-Next on the local Halogen server.

    The same treatment cairn got - a plain completions endpoint, no tools - so
    this is the one model of its class that can be compared to cairn honestly.
    Every hosted candidate had to go through `opencode run`, which is an agent
    and wanders off task when handed a critique.

    THREE THINGS THIS SERVER DOES DIFFERENTLY, per its operator:
    - the token budget covers THINKING as well as the answer. Running out mid
      thought returns finish_reason "length", EMPTY content, and the partial
      trace in reasoning_content, which most clients never display. So the
      finish reason is recorded and an empty answer is reported as truncation,
      never as a model failure.
    - the shipped chat template hardcodes xhigh effort, which cost 10 points on
      TEB, so an effort is always sent explicitly.
    - 180 s of silence trips the engine watchdog and takes the container down:
      a stall appears as a dead endpoint, not a slow one.
    """
    import json, urllib.request
    body = json.dumps({
        "model": "halogen-qwen3.8-flash-next",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tok, "temperature": 0.2,
        "chat_template_kwargs": {"reasoning_effort": effort},
    }).encode()
    r = urllib.request.Request("http://strix-halo:8731/v1/chat/completions",
                               data=body, headers={"content-type": "application/json"})
    d = json.load(urllib.request.urlopen(r, timeout=1800))
    ch = d["choices"][0]
    fr = ch.get("finish_reason")
    txt = ch["message"].get("content") or ""
    u = d.get("usage", {}) or {}
    HALOGEN_RECORD.append({"finish_reason": fr, "content_chars": len(txt),
                           "completion_tokens": u.get("completion_tokens"),
                           "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens")})
    # ANY length finish is a truncation, not only an empty one. The operator's
    # warning named the empty case; the dangerous case is PARTIAL. At effort
    # high this model spent 13,952 of a 16,384 budget on reasoning and returned
    # 9,655 characters of an unfinished file - which parsed, whose selftest
    # exited 0, and which then PASSED an artifact that does not exist, because
    # the half of it that does the checking was never written. A truncated gate
    # is the worst possible object here: it looks like a clean pass.
    if fr == "length":
        raise RuntimeError(
            f"TRUNCATED: finish_reason=length after {u.get('completion_tokens')} "
            f"tokens of which {(u.get('completion_tokens_details') or {}).get('reasoning_tokens')} "
            f"were reasoning; budget was {max_tok}. {len(txt)} chars returned - "
            f"do not score a partial file.")
    return txt


SWIFT_RECORD = []


def call_swap(prompt, model, effort=None, max_tok=16384, host="strix-halo:8080"):
    """llama-swap, the endpoint cairn itself uses - so this is like-for-like.

    cairn's baseline in this bake-off (2 -> 7 -> 14 fixtures, 3 of 3 rounds
    usable) was measured through exactly this path against qwen3.8-27b-code.
    The server pins reasoning_effort medium in its own env, so nothing is sent
    here unless an effort is passed deliberately - which keeps the default run
    identical in treatment to cairn's and makes any difference the WEIGHTS.
    """
    import json, urllib.request
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tok, "temperature": 0.2}
    if effort:
        body["chat_template_kwargs"] = {"reasoning_effort": effort}
    r = urllib.request.Request(f"http://{host}/v1/chat/completions",
                               data=json.dumps(body).encode(),
                               headers={"content-type": "application/json"})
    d = json.load(urllib.request.urlopen(r, timeout=2400))
    ch = d["choices"][0]
    u = d.get("usage", {}) or {}
    SWIFT_RECORD.append({"model": model, "effort": effort,
                         "finish_reason": ch.get("finish_reason"),
                         "completion_tokens": u.get("completion_tokens"),
                         "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                         "content_chars": len(ch["message"].get("content") or "")})
    if ch.get("finish_reason") == "length":
        raise RuntimeError(f"TRUNCATED: {u.get('completion_tokens')} tokens, budget {max_tok}")
    return ch["message"].get("content") or ""
