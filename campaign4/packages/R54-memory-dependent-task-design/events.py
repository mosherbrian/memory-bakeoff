"""R54 memory-event accounting (offline, not a contamination scanner).
python events.py TRANSCRIPT.jsonl MEMORY_DIR [MANIFEST] -> JSON rows
Links each tool_use to its tool_result / permission_denied by id. Memory events:
  file_read_ok        Read of a file under MEMORY_DIR with a non-error result (file present in MANIFEST if given)
  file_read_failed    Read of a MEMORY_DIR file with an error result
  cat_read_ok / cat_read_failed   Bash whose ONLY command is `cat <memory file>` (optionally after `cd X &&`/`;`)
  dir_listing         Bash `ls [-flags] <MEMORY_DIR>` (a listing is never a file read)
  denied              any memory-mentioning call with a permission denial
  unresolved          memory-mentioning call with no result and no denial
  unsupported_shell   Bash mentioning MEMORY_DIR in any other form (manual review; never counted as a read)
  inert_mention       Write/other tool whose input only mentions MEMORY_DIR in prose/content
A path string alone never proves retrieval; index injection and causal use are never inferred here."""
import json, os, re, shlex, sys
def run(T, MEM, MAN=None):
    MEM = MEM.rstrip("/")
    present = None
    if MAN and os.path.exists(MAN):
        txt = open(MAN).read().strip()
        present = set() if txt in ("", "ABSENT") else {l.split()[-1].lstrip("./") for l in txt.splitlines()}
    uses, res, den, total = {}, {}, set(), 0
    for line in open(T):
        if not line.strip(): continue
        e = json.loads(line)
        if not isinstance(e, dict): continue
        if e.get("type") == "system" and e.get("subtype") == "permission_denied" and e.get("tool_use_id"): den.add(e["tool_use_id"])
        m = e.get("message")
        if not isinstance(m, dict) or not isinstance(m.get("content"), list): continue
        for c in m["content"]:
            if not isinstance(c, dict): continue
            if c.get("type") == "tool_use": uses[c["id"]] = (c.get("name"), c.get("input") or {}); total += 1
            elif c.get("type") == "tool_result": res[c.get("tool_use_id")] = bool(c.get("is_error"))
    rows = []
    for i, (name, inp) in uses.items():
        s = json.dumps(inp)
        if MEM not in s: continue
        r = {"id": i, "tool": name}
        if i in den: r["event"] = "denied"
        elif i not in res: r["event"] = "unresolved"
        elif name == "Read":
            fp = inp.get("file_path", ""); r["path"] = fp; ok = not res[i]
            if present is not None and fp.startswith(MEM + "/") and os.path.basename(fp) not in present and ok: r["note"] = "ok result but file absent from snapshot"
            r["event"] = "file_read_ok" if ok else "file_read_failed"
        elif name == "Bash":
            cmd = inp.get("command", ""); parts = [p.strip() for p in re.split(r"&&|;|\n", cmd) if p.strip()]
            mem_parts = [p for p in parts if MEM in p]
            try: w = shlex.split(mem_parts[0]) if len(mem_parts) == 1 else []
            except ValueError: w = []
            if w and w[0] == "ls" and any(x.rstrip("/") == MEM for x in w[1:]): r["event"] = "dir_listing"   # ls naming the memory dir (other dirs may be listed too)
            elif w and w[0] == "cat" and len(w) == 2 and w[1].startswith(MEM + "/"): r["event"] = "cat_read_failed" if res[i] else "cat_read_ok"; r["path"] = w[1]
            else: r["event"] = "unsupported_shell"; r["command"] = cmd[:200]
        else: r["event"] = "inert_mention"
        rows.append(r)
    counts = {}
    for r in rows: counts[r["event"]] = counts.get(r["event"], 0) + 1
    return {"tool_uses": total, "memory_events": rows, "counts": counts}
if __name__ == "__main__":
    print(json.dumps(run(*sys.argv[1:4]), indent=1))
