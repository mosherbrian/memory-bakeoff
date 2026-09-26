"""R68 operator preflight: python preflight.py LABEL -> writes operator/preflight-LABEL.json, exit 0 only if every check passes.
First call writes operator/source-manifest.json (full closure); later calls re-verify it unchanged."""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
L = sys.argv[1]; P = "/var/home/bmosher/memory-bake-off/campaign4/packages"; R67 = f"{P}/R67-identity-boundary-validation"; R68 = f"{P}/R68-context-preference-trial"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest(); fails = []
files = [f"{R67}/completion-claim.json", f"{R67}/acceptance.json"] + [f"{R67}/operator/{x}" for x in ("run-arm.sh", "freeze.sh", "finalize.py")] + sorted(
    glob.glob(f"{R67}/launch/*") + glob.glob(f"{R67}/templates/*") + glob.glob(f"{R67}/fixture/*")) + [
    f"{P}/R63-context-evidence-gate/{x}" for x in ("gate.py", "contract.md", "contract-addendum-1.md")] + [
    f"{P}/R56-context-runner-readiness/scanner/scan.py", f"{P}/R56-context-runner-readiness/scanner/operator/scan_gate.py", f"{P}/R54-memory-dependent-task-design/events.py"]
b = os.path.realpath("/var/home/bmosher/.local/bin/claude")
cur = {"files": {os.path.relpath(f, P): h(f) for f in files}, "binary": {"path": b, "sha256": h(b)}}
mp = f"{R68}/operator/source-manifest.json"
if os.path.exists(mp):
    old = json.load(open(mp))
    if old["files"] != cur["files"] or old["binary"] != cur["binary"]: fails.append("source manifest changed")
else:
    c = json.load(open(f"{R67}/completion-claim.json"))
    bad = [f for f, v in c["files_sha256"].items() if h(os.path.join(R67, f)) != v]
    if bad: fails.append(f"R67 claim pins changed {bad}")
    json.dump({**cur, "at": datetime.now(timezone.utc).isoformat()}, open(mp, "w"), indent=1)
seams = [k for k in ("STUB_BIN", "DRY", "TEST_PROJECTS", "TEST_PRECREATE", "TEST_MUTATE_BETWEEN", "TEST_TIMEOUT", "GATE", "EVENTS", "OPROOT", "EVIDENCE_DIR", "R67_TEST_PROJECTS") if k in os.environ]
if seams: fails.append(f"seams set {seams}")
if os.path.exists(f"{R67}/evidence/{L}"): fails.append("native label exists")
anc, q = set(), os.getpid()
while q > 1: anc.add(q); q = int(open(f"/proc/{q}/stat").read().rsplit(")", 1)[1].split()[1])
rows = [l.split(None, 1) for l in subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout.splitlines()]
busy = [r[1][:120] for r in rows if len(r) == 2 and int(r[0]) not in anc and re.search(r"run-arm\.sh|claude -p |session\.sh", r[1])]
if busy: fails.append(f"participant or driver running {busy}")
env = {"HOME": "/var/home/bmosher", "PATH": "/var/home/bmosher/.local/bin:/usr/bin:/bin"}
au = json.loads(subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, env=env).stdout)
if (au.get("authMethod"), au.get("apiProvider"), au.get("subscriptionType")) != ("claude.ai", "firstParty", "max"): fails.append("route not Max")
ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, env=env).stdout.strip()
if not ver.startswith("2.1.283"): fails.append(f"version {ver}")
cap = subprocess.run(["/var/home/bmosher/.config/agent-deck/fleet-spend-stop", "--status"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
m = re.search(r"\$([0-9.]+) left of \$60", cap)
if not m or float(m.group(1)) <= 0: fails.append("Go pool exhausted or unknown")
out = {"label": L, "at": datetime.now(timezone.utc).isoformat(), "pass": not fails, "fails": fails, "manifest_sha256": h(mp), "version": ver,
       "route": {k: au.get(k) for k in ("authMethod", "apiProvider", "subscriptionType")}, "capacity": cap + "; daily cap advisory; no paid overflow", "seams_unset": not seams}
json.dump(out, open(f"{R68}/operator/preflight-{L}.json", "w"), indent=1); print(json.dumps(out, indent=1)); sys.exit(1 if fails else 0)
