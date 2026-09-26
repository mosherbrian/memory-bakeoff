"""R51 contamination scan v4 (R50 v3 + unresolved/contradictory tool outcomes).
A tool_use with neither tool_result nor permission denial is UNRESOLVED: its paths are unconfirmed, never access;
unresolved alone makes the arm ambiguous (never clean, never contaminated). A denial plus an is_error result is a normal denial. A denial plus a
NON-error result is CONTRADICTORY: treated as possibly executed (forbidden paths still count) and flagged ambiguous.
Precedence: confirmed forbidden access -> contaminated; else any ambiguity/unresolved/contradictory -> ambiguous; else clean.
python scan.py TRANSCRIPT.jsonl ARM_CWD ARM_MEMORY_DIR [DENY_ROOT ...]  -> JSON on stdout
status/exit: clean 0 | contaminated 1 | ambiguous 2 | evidence_invalid 3 (missing, empty, malformed) | scanner_error 4.
Accepts every stream-json event shape: events without a dict 'message' (system init/permission_denied/rate_limit/result)
are recorded, never dereferenced. tool_use ids are correlated with tool_result and permission_denied events:
only EXECUTED calls can access paths; DENIED attempts are listed separately and never count as access.
Bash: a command is split at a heredoc; the heredoc body is data if its delimiter is quoted ('EOF' or "EOF"),
and ambiguous if unquoted (it could expand $(...)). Commands that are not simple word lists (pipes to interpreters,
$(), backticks, eval, python/perl/node/sh -c, find/xargs/base64/grep -r, unparsable quoting) are AMBIGUOUS.
Unknown tool names are UNCLASSIFIED -> ambiguous. Same-user obfuscation can evade this; clean is not isolation."""
import json, os, re, shlex, sys, traceback

def main(argv):
    if len(argv) < 4:
        return {"status": "scanner_error", "error": "usage"}
    T, CWD, MEM = argv[1], os.path.realpath(argv[2]), os.path.realpath(argv[3])
    DENY = [os.path.realpath(d) for d in argv[4:]]
    HOME = os.path.realpath(os.path.expanduser("~")); CL = os.path.join(HOME, ".claude")
    def res(p):
        p = os.path.expanduser(p)
        return os.path.realpath(os.path.normpath(p if os.path.isabs(p) else os.path.join(CWD, p)))
    under = lambda p, r: p == r or p.startswith(r.rstrip("/") + "/")
    def classify(p):
        r = res(p)
        if under(r, MEM): return "allowed"
        if r.endswith(".jsonl"): return "denied:transcript"
        if under(r, CWD): return "allowed"
        for d in DENY:
            if under(r, d): return "denied:" + d
        if under(r, CL): return "denied:claude-config-or-projects"
        return "outside"
    IND = re.compile(r"\b(python\d?|perl|node|ruby|eval|xargs|base64|find)\b|\bsh\s+-c\b|\bbash\s+-c\b|\$\(|`|\bgrep\s+-r")
    HD = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
    try:
        lines = open(T).read().splitlines()
    except OSError as e:
        return {"status": "evidence_invalid", "reason": "missing", "detail": str(e)}
    events, uses, results, denied_ids = 0, {}, {}, set()
    for i, line in enumerate(lines):
        if not line.strip(): continue
        try: ev = json.loads(line)
        except ValueError: return {"status": "evidence_invalid", "reason": "malformed_line", "line_no": i + 1}
        if not isinstance(ev, dict): return {"status": "evidence_invalid", "reason": "non_object_event", "line_no": i + 1}
        events += 1
        if ev.get("type") == "system" and ev.get("subtype") == "permission_denied" and ev.get("tool_use_id"):
            denied_ids.add(ev["tool_use_id"])
        if ev.get("type") == "result":
            for d in ev.get("permission_denials") or []:
                if isinstance(d, dict) and d.get("tool_use_id"): denied_ids.add(d["tool_use_id"])
        msg = ev.get("message")
        if not isinstance(msg, dict): continue
        content = msg.get("content")
        if not isinstance(content, list): continue
        for c in content:
            if not isinstance(c, dict): continue
            if c.get("type") == "tool_use": uses[c.get("id")] = (c.get("name"), c.get("input") if isinstance(c.get("input"), dict) else {})
            elif c.get("type") == "tool_result": results[c.get("tool_use_id")] = bool(c.get("is_error"))
    if events == 0: return {"status": "evidence_invalid", "reason": "empty"}
    executed, attempted_denied, found, amb, unclassified, unresolved = [], [], [], [], [], []
    for uid, (name, inp) in uses.items():
        rec = {"id": uid, "tool": name}
        has_res, has_den = uid in results, uid in denied_ids
        if has_den and (not has_res or results[uid]):   # a denial normally also returns an is_error tool_result
            rec["input"] = json.dumps(inp)[:200]; attempted_denied.append(rec); continue
        if not has_res and not has_den:
            rec["input"] = json.dumps(inp)[:200]; unresolved.append(rec); continue
        rec["outcome"] = ("error" if results[uid] else "ok") + ("+denied(contradictory)" if has_den else "")
        if has_den: amb.append(("contradictory outcome", uid))
        paths = []
        if name in ("Read", "Write", "Edit", "Glob", "Grep", "NotebookEdit"):
            for k in ("file_path", "path", "notebook_path"):
                if isinstance(inp.get(k), str): paths.append(inp[k])
        elif name == "Bash":
            cmd = inp.get("command", "") if isinstance(inp.get("command"), str) else ""
            m = HD.search(cmd); body = ""
            if m:
                head, body = cmd[:m.start()], cmd[m.end():]
                if not m.group(1): amb.append(("unquoted heredoc", cmd[:120]))
                cmd = head
            if IND.search(cmd): amb.append(("indirect", cmd[:160]))
            try:
                lx = shlex.shlex(cmd, posix=True, punctuation_chars=True); lx.whitespace_split = True; words = [w for w in lx if w not in (";", "&&", "||", "|", "&", ">", ">>", "<", "(", ")")]
            except ValueError: words = cmd.split(); amb.append(("unparsable", cmd[:120]))
            paths += [w for w in words if "/" in w or w.startswith("~") or w.endswith(".jsonl")]
        else:
            unclassified.append(rec); continue
        rec["paths"] = [(p, classify(p)) for p in paths]
        for p, cl in rec["paths"]:
            if cl.startswith("denied"): found.append((name, p, cl))
            if cl == "outside": amb.append(("outside path", p))
        executed.append(rec)
    if unclassified: amb.append(("unclassified tools", [u["tool"] for u in unclassified]))
    if unresolved: amb.append(("unresolved tool outcomes", [u["id"] for u in unresolved]))
    st = "contaminated" if found else "ambiguous" if amb else "clean"
    return {"status": st, "events": events, "executed": executed, "attempted_denied": attempted_denied, "unresolved": unresolved,
            "contamination": found, "ambiguous": amb, "limit": "same-user obfuscation can evade this; clean is not isolation"}

if __name__ == "__main__":
    try: out = main(sys.argv)
    except Exception:
        out = {"status": "scanner_error", "error": traceback.format_exc()[-600:]}
    print(json.dumps(out, indent=1))
    sys.exit({"clean": 0, "contaminated": 1, "ambiguous": 2, "evidence_invalid": 3, "scanner_error": 4}[out["status"]])
