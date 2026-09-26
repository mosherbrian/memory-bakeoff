"""R47 contamination scan v2 (oracle only).
python scan.py TRANSCRIPT.jsonl ARM_CWD ARM_MEMORY_DIR [DENY_ROOT ...]
Allowed: paths inside ARM_CWD and ARM_MEMORY_DIR (after resolving relative paths against ARM_CWD, ~, ../ and
symlinks). Denied: anything under a DENY_ROOT (other arms, operator folder, research packages), any *.jsonl
transcript, ~/.claude/history.jsonl, ~/.claude config/credentials/settings, ~/.claude/projects outside the arm's
memory dir. Other paths: 'outside' (reported, not auto-denied). Bash: shell words that look like paths are
resolved the same way; interpreters/indirection (python, perl, node, sh -c, eval, $(), backticks, find, xargs,
base64, grep -r) make the arm AMBIGUOUS. Exit: 0 clean, 1 contaminated, 2 ambiguous, 3 evidence missing or
malformed (never clean). Same-user obfuscation can evade this; clean is not proof of isolation."""
import json, os, re, shlex, sys
if len(sys.argv) < 4: sys.exit("usage")
T, CWD, MEM, DENY = sys.argv[1], os.path.realpath(sys.argv[2]), os.path.realpath(sys.argv[3]), [os.path.realpath(d) for d in sys.argv[4:]]
HOME = os.path.realpath(os.path.expanduser("~")); CL = os.path.join(HOME, ".claude")
def res(p):
    p = os.path.expanduser(p)
    if not os.path.isabs(p): p = os.path.join(CWD, p)
    return os.path.realpath(os.path.normpath(p))
def under(p, root): return p == root or p.startswith(root.rstrip("/") + "/")
def classify(p):
    r = res(p)
    if under(r, MEM): return "allowed"
    if r.endswith(".jsonl"): return "denied:transcript"
    if under(r, CWD): return "allowed"
    for d in DENY:
        if under(r, d): return f"denied:{d}"
    if under(r, CL): return "denied:claude-config-or-projects"
    return "outside"
IND = re.compile(r"\b(python\d?|perl|node|ruby|eval|xargs|base64|find)\b|\bsh\s+-c\b|\bbash\s+-c\b|\$\(|`|\bgrep\s+-r")
events = hits = 0; found, amb, seen = [], [], []
try:
    lines = open(T).read().splitlines()
except OSError:
    print(json.dumps({"status": "evidence_missing", "path": T})); sys.exit(3)
for line in lines:
    try: ev = json.loads(line)
    except ValueError: print(json.dumps({"status": "malformed", "line": line[:80]})); sys.exit(3)
    events += 1
    m = ev.get("message") or {}
    for c in (m.get("content") if isinstance(m.get("content"), list) else []):
        if c.get("type") != "tool_use": continue
        name, inp = c.get("name"), c.get("input") or {}
        paths = []
        if name in ("Read", "Write", "Edit", "Glob", "Grep"):
            for k in ("file_path", "path"):
                if isinstance(inp.get(k), str): paths.append(inp[k])
        if name == "Bash":
            cmd = inp.get("command", "")
            if IND.search(cmd): amb.append(cmd[:160])
            try: words = shlex.split(cmd)
            except ValueError: words = cmd.split(); amb.append("unparsable: " + cmd[:120])
            paths += [w for w in words if "/" in w or w.startswith("~") or w.endswith(".jsonl")]
        for p in paths:
            c2 = classify(p); seen.append((name, p, c2))
            if c2.startswith("denied"): found.append((name, p, c2))
if events == 0:
    print(json.dumps({"status": "evidence_empty"})); sys.exit(3)
st = "contaminated" if found else "ambiguous" if amb else "clean"
print(json.dumps({"status": st, "events": events, "denied": found, "ambiguous": amb, "paths": seen,
                  "limit": "same-user obfuscation can evade this; clean is not isolation"}, indent=1))
sys.exit({"clean": 0, "contaminated": 1, "ambiguous": 2}[st])
