#!/usr/bin/env python3
"""Standard-tier firing run on the validated row-36 trigger harness (S3-1).

Runs the standard corpus (60 scenarios) per scenario in an isolated agent dir,
exactly as the validated smoke runner does, then computes the SHIPPING metric
definitions (CORVID-S3-1-VERIFY-CHECKLIST.md):
  FBMR_topic, FalseFire (filler_plain only) with fresh_rate/gap_rate beside it,
  NearMissFire (never folded into FalseFire), FirePrecision.

Controls on the SAME corpus: --control never (trigger kill switch) and
--control always (topics file that matches every prompt) must separate.

Usage: run_standard.py [--control system|never|always] [--out DIR]
"""
import json
import os
import select
import subprocess
import sys
import tempfile
import time

PI = "/home/bmosher/.bun/bin/pi"
LIVE_AGENT_DIR = "/home/bmosher/acp-pi/.pi-agent"
EXT = "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-change-trigger"
import os as _os
CORPUS = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "corpus.jsonl")  # S4-10: local v3 corpus, was hardcoded to v2
MODEL = "night/qwen3.8-27b-code"
LINE_TIMEOUT = 180
ALWAYS_SUMMARY = ("list open tickets assigned staging service port focused test convention "
                  "portable mode prohibition deploy target host branch naming rule default "
                  "timeout value marketing newsletter welcome vendor backup archive changelog")


def tokens_of(text, stop):
    import re
    toks = re.findall(r"[a-z0-9][a-z0-9-]{3,}", text.lower())
    return [t for t in toks if t not in stop]


def load_stopwords():
    import re
    src = open(os.path.join(EXT, "index.ts")).read()
    m = re.search(r"const STOPWORDS = new Set\(\[(.*?)\]\)", src, re.S)
    return set(re.findall(r'"([^"]+)"', m.group(1)))


def make_agent_dir(workdir, control):
    import shutil
    adir = os.path.join(workdir, "agent")
    os.makedirs(adir, exist_ok=True)
    topics = os.path.join(workdir, "topics.jsonl")
    firelog = os.path.join(workdir, "firelog.jsonl")
    settings = {
        "enableInstallTelemetry": False,
        "packages": ([EXT] if control != "never" else [EXT]),
        "changeTrigger": {"enabled": control != "never", "gapMinutes": 30,
                          "topicsFile": topics, "fireLog": firelog},
    }
    with open(os.path.join(adir, "settings.json"), "w") as f:
        json.dump(settings, f)
    for name in ("auth.json", "models.json", "models-store.json"):
        src, dst = os.path.join(LIVE_AGENT_DIR, name), os.path.join(adir, name)
        if os.path.exists(src) and not os.path.exists(dst):
            os.symlink(src, dst)
    return adir, topics, firelog


def run_scenario(scen, adir, topics_path, firelog_path, control):
    if control == "always":
        recs = [{"summary": ALWAYS_SUMMARY}]
    else:
        recs = [{"summary": r["summary"]} for r in scen["records"]]
    with open(topics_path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    env = dict(os.environ, PI_CODING_AGENT_DIR=adir)
    if control == "never":
        env["PI_CHANGE_TRIGGER"] = "0"
    proc = subprocess.Popen([PI, "--mode", "rpc", "--no-session", "--model", MODEL],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, text=True, bufsize=1,
                            cwd=os.path.dirname(adir))

    def rpc(cmd):
        proc.stdin.write(json.dumps(cmd) + "\n"); proc.stdin.flush()

    def wait_line(n):
        deadline = time.time() + LINE_TIMEOUT
        while time.time() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"rpc died rc={proc.returncode}")
            if os.path.isfile(firelog_path) and sum(1 for _ in open(firelog_path)) >= n:
                return
            r, _, _ = select.select([proc.stdout], [], [], 0.5)
            if not r:
                continue
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("rpc stdout closed early")
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "response" and not ev.get("success"):
                raise RuntimeError(f"command rejected: {ev}")
        raise RuntimeError(f"no firelog line {n} in {LINE_TIMEOUT}s")
    try:
        turns = scen["turns"]
        for i, turn in enumerate(turns, 1):
            rpc({"id": f"p{i}", "type": "prompt", "message": turn["text"]})
            if control == "never":
                time.sleep(4)  # no firelog expected: the extension is not registered
            else:
                wait_line(i)
            if i < len(turns):
                rpc({"type": "abort"}); time.sleep(2)
    finally:
        try: proc.stdin.close()
        except Exception: pass
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill()
    if control == "never":
        if os.path.isfile(firelog_path) and sum(1 for _ in open(firelog_path)) > 0:
            raise RuntimeError("fire-never control wrote a firelog line")
        return [{"fired": False, "reasons": [], "matched_tokens": []} for _ in scen["turns"]]
    lines = [json.loads(l) for l in open(firelog_path) if l.strip()]
    return lines


def metrics(scenarios, results, stop):
    # results: list of (scenario, turn_type, line)
    fb, ff_den, ff_num, nm_den, nm_num, fr_num, fr_den, gp_num, all_fires, good_fires = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    topic_den = 0
    for sc in scenarios:
        m_texts = sc["turns"]
        for t in m_texts:
            pass
    per = list(results)
    # index by (sid, turn)
    for sid, ttype, line in per:
        fired = line["fired"]
        reasons = set(line["reasons"])
        if ttype == "filler_plain":
            ff_den += 1
            if fired and "topic" in reasons:
                ff_num += 1
            if "fresh" in reasons:
                fr_num += 1
            fr_den += 1
            if "gap" in reasons:
                gp_num += 1
        elif ttype == "moment_topic":
            topic_den += 1
            if fired and "topic" in reasons:
                fb += 1
        elif ttype == "moment_offtopic":
            pass
        elif ttype == "filler_near_miss":
            nm_den += 1
            if fired and "topic" in reasons:
                nm_num += 1
        if fired:
            all_fires += 1
            # Pre-registered FirePrecision (CORVID-S3-1-VERIFY-CHECKLIST §2):
            # numerator = topic fires on labeled load-bearing moments only;
            # near-miss (F2) fires lower it by design, fresh/gap/offtopic too.
            is_good = (ttype == "moment_topic") and "topic" in reasons
            if is_good:
                good_fires += 1
    return {
        "FBMR_topic": (fb, topic_den),
        "FalseFire": (ff_num, ff_den),
        "fresh_rate": (fr_num, fr_den),
        "gap_rate": (gp_num, fr_den),
        "NearMissFire": (nm_num, nm_den),
        "FirePrecision": (good_fires, all_fires),
    }


def main():
    args = sys.argv[1:]
    control, outdir = "system", None
    while args:
        if args[0] == "--control": control = args[1]; args = args[2:]
        elif args[0] == "--out": outdir = args[1]; args = args[2:]
        else: sys.exit(f"unknown arg {args[0]}")
    stop = load_stopwords()
    scenarios = [json.loads(l) for l in open(CORPUS) if l.strip()]
    outdir = os.path.abspath(outdir or tempfile.mkdtemp(prefix=f"standard-{control}-"))
    os.makedirs(outdir, exist_ok=True)
    results, failures = [], []
    for sc in scenarios:
        sid = sc["scenario_id"]
        workdir = os.path.join(outdir, sid); os.makedirs(workdir, exist_ok=True)
        adir, topics, firelog = make_agent_dir(workdir, control)
        t0 = time.time()
        try:
            lines = run_scenario(sc, adir, topics, firelog, control)
            for turn, line in zip(sc["turns"], lines):
                results.append((sid, turn["type"], line))
        except Exception as e:
            failures.append(f"{sid}: {e}")
        print(f"[{sid}] {time.time()-t0:.0f}s", flush=True)
    summary = metrics(scenarios, results, stop)
    with open(os.path.join(outdir, "results.jsonl"), "w") as f:
        for sid, ttype, line in results:
            f.write(json.dumps({"scenario": sid, "turn_type": ttype, **line}) + "\n")
    out = {"control": control, "n_scenarios": len(scenarios), "n_turns": len(results),
           "failures": failures, "metrics": {k: {"num": v[0], "den": v[1]} for k, v in summary.items()}}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
