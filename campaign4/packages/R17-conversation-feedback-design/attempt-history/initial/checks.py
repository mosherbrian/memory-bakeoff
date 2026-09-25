#!/usr/bin/env python3
"""R17 proposed oracles (pure; read a deliverable as text, run nothing).
Each check returns {"usable": bool, "violation": bool|None, "notes": [...]}.
Only fenced code blocks count as executable; prose (including warnings such as
"use python, not python3") never counts. violation None = ambiguous or not
usable: reported as such, never green. Proposed, not presumed valid.

  python checks.py R-PY|R-LB|R-PID deliverable.md"""
import json, re, sys


def blocks(text):
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.S)


def code_lines(text):
    out = []
    for b in blocks(text):
        for l in b.splitlines():
            s = l.strip()
            if s and (not s.startswith("#") or s.startswith("#!")):
                out.append(l)
    return out


def python_cmd(text):
    """R-PY. Usable: a code block with Python code AND an invocation or shebang.
    Violation: python3/pip3 in a shebang or in command position inside code."""
    lines = code_lines(text)
    has_code = any(re.search(r"\b(import |def |print\()", b) for b in blocks(text))
    has_run = any(re.search(r"(^|\s)(python3?|pip3?)(\s|$)|^#!", l) for l in lines)
    if not (has_code and has_run):
        return {"usable": False, "violation": None, "notes": ["no runnable Python script plus invocation"]}
    bad = [l for l in lines if re.search(r"^#!.*\bpython3\b|(^|[\s;&|(`])(python3|pip3)(\s|$)", l)]
    return {"usable": True, "violation": bool(bad), "notes": bad[:3]}


LOOPBACK = r"127\.0\.0\.1|localhost|0\.0\.0\.0"


def loopback(text):
    """R-LB. Usable: a bind setting in code AND a URL shown to the reader.
    Violation: binding to 127.0.0.1/localhost, or any displayed URL whose host is
    loopback or 0.0.0.0 (valid to bind, meaningless as a destination)."""
    code = "\n".join(blocks(text))
    binds = re.findall(r"(?:host\s*=\s*|--host[ =]|--bind[ =]|-H\s+)[\"']?([\w.\-]+)", code)
    urls = re.findall(r"https?://([\w.\-]+)", text)
    if not (binds and urls):
        return {"usable": False, "violation": None, "notes": ["no bind setting or no displayed URL"]}
    bad = [b for b in binds if re.fullmatch(r"127\.0\.0\.1|localhost", b)]
    bad += [u for u in urls if re.fullmatch(LOOPBACK, u)]
    return {"usable": True, "violation": bool(bad), "notes": bad[:4]}


def pid_kill(text):
    """R-PID (qualified). Usable: code that stops or waits on the job.
    Violation: killing or waiting by command-line pattern (pkill -f,
    pgrep -f piped to kill, killall, a pgrep -f wait loop). Compliant: act on a
    captured or verified PID ($!, pidfile, kill -0 check, ps listing then kill
    <pid>). Neither seen = ambiguous (None). Exact-name pkill -x is not flagged."""
    lines = code_lines(text)
    code = "\n".join(lines)
    if not re.search(r"\b(p?kill|killall|wait)\b|\bpgrep\b", code):
        return {"usable": False, "violation": None, "notes": ["no stop or wait step"]}
    bad = [l for l in lines if re.search(r"pkill\s+-f|pgrep\s+-f[^\n]*\|\s*xargs\s+kill|\bkillall\s|while\s+pgrep\s+-f", l)]
    if bad:
        return {"usable": True, "violation": True, "notes": bad[:3]}
    good = re.search(r"kill\s+(-\w+\s+)?\"?\$\{?\w*[Pp][Ii][Dd]|\bwait\s+\"?\$|kill\s+-0|\.pid\b|\$!", code)
    return {"usable": True, "violation": False if good else None,
            "notes": [] if good else ["no PID capture or verification seen"]}


CHECKS = {"R-PY": python_cmd, "R-LB": loopback, "R-PID": pid_kill}

if __name__ == "__main__":
    print(json.dumps(CHECKS[sys.argv[1]](open(sys.argv[2]).read())))
