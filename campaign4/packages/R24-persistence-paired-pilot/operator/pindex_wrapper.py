"""R24 operator capture wrapper, installed in each arm as pindex_cli.py.

Runs the frozen R22 CLI unchanged with the same arguments. It removes
PINDEX_TEST_NOW from the environment so the host clock is used, and records
host start/end, exact argv, stdout, stderr, exit code and sha256 of every out/
file in a capture area outside the arm. The participant chooses the action;
the wrapper never chooses or adds one. Same-user writable: a declared limit."""
import hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone

FROZEN = "/var/home/bmosher/memory-bake-off/campaign4/packages/R22-persistence-trial-preparation/pindex_cli.py"
CAPTURE = os.environ.get("R24_CAPTURE_ROOT", "/var/home/bmosher/r24-capture") + "/" + os.path.basename(os.getcwd())


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    env = {k: v for k, v in os.environ.items() if k != "PINDEX_TEST_NOW"}
    os.makedirs(CAPTURE, exist_ok=True)
    n = len([d for d in os.listdir(CAPTURE) if d.startswith("call-")]) + 1
    rec = {"call": n, "cwd": os.getcwd(), "argv": [sys.executable, FROZEN] + sys.argv[1:],
           "frozen_sha256": hashlib.sha256(open(FROZEN, "rb").read()).hexdigest(), "capture_started_at": now()}
    p = subprocess.run(rec["argv"], capture_output=True, text=True, env=env)
    rec.update(capture_ended_at=now(), exit=p.returncode, stdout=p.stdout, stderr=p.stderr)
    out = None
    if "--out" in sys.argv:
        out = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    files = {}
    if out and os.path.isdir(out):
        for f in sorted(os.listdir(out)):
            fp = os.path.join(out, f)
            if os.path.isfile(fp):
                files[f] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
    rec["out_sha256"] = files
    d = os.path.join(CAPTURE, f"call-{n}")
    os.makedirs(d)
    for f in files:
        with open(os.path.join(out, f), "rb") as src, open(os.path.join(d, f), "wb") as dst:
            dst.write(src.read())
    json.dump(rec, open(os.path.join(d, "capture.json"), "w"), indent=1)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
