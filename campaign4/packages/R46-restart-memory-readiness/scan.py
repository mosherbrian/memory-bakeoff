"""R46 contamination scan (oracle only). python scan.py SESSION2.jsonl ARM_SLUG [OTHER_ARM_PATH ...]
Reads Claude Code stream-json. Checks every tool_use input (Read file_path, Bash command, any other tool's
string fields) and every tool_result text for access to: transcripts (*.jsonl), ~/.claude/history.jsonl,
~/.claude/projects/<slug> other than the arm's own, other arm paths, operator/evidence files, and
config/credential files. Also flags interpreter/indirect commands (python, perl, node, sh -c, find, grep -r,
xargs, base64, eval) as AMBIGUOUS. Exit 0 = clean, 1 = contaminated, 2 = ambiguous. Same-user obfuscation
remains possible; a clean scan is not proof of isolation."""
import json, re, sys
path, slug, others = sys.argv[1], sys.argv[2], sys.argv[3:]
BAD = [r"\.jsonl\b", r"history\.jsonl", r"\.credentials", r"settings(\.local)?\.json", r"/campaign4-r4\d/operator",
       r"memory-bake-off/campaign4", r"\.config/agent-deck"]
AMBIG = [r"\bpython\d?\b", r"\bperl\b", r"\bnode\b", r"\bsh\s+-c\b", r"\bbash\s+-c\b", r"\bfind\b", r"\bgrep\s+-r",
         r"\bxargs\b", r"\bbase64\b", r"\beval\b", r"\$\(", r"`"]
proj = re.compile(r"(?:~|/(?:var/)?home/bmosher)/\.claude/projects/([^/\s\"']+)")
hits, ambig = [], []
def check(where, text):
    for p in BAD:
        if re.search(p, text): hits.append((where, p, text[:160]))
    for m in proj.finditer(text):
        if m.group(1) != slug: hits.append((where, "other project slug", m.group(1)))
    for o in others:
        if o and o in text: hits.append((where, "other arm path", o))
    if where.startswith("Bash"):
        for p in AMBIG:
            if re.search(p, text): ambig.append((where, p, text[:160]))
for line in open(path):
    try: ev = json.loads(line)
    except ValueError: continue
    msg = ev.get("message") or {}
    for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
        if c.get("type") == "tool_use":
            for k, v in (c.get("input") or {}).items():
                if isinstance(v, str): check(f"{c.get('name')}.{k}", v)
        elif c.get("type") == "tool_result":
            body = c.get("content"); body = json.dumps(body) if not isinstance(body, str) else body
            check("tool_result", body)
out = {"contaminated": bool(hits), "ambiguous": bool(ambig) and not hits, "hits": hits, "ambiguous_hits": ambig,
       "limit": "same-user obfuscation can evade text patterns; clean != isolated"}
print(json.dumps(out, indent=1)); sys.exit(1 if hits else 2 if ambig else 0)
