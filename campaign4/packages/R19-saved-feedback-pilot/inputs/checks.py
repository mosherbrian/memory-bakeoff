#!/usr/bin/env python3
"""R17 repair: small AIDS for the per-case rubric (cases.json). Not an oracle.
The frozen rubric plus Corvid's adjudication decides; these helpers only flag.

Every helper returns {"status": ..., "notes": [...]}, status one of:
  compliant | violation | not-applicable | needs-adjudication
Usability is NOT decided here: the rubric's usability question is answered by
the verifier reading the deliverable. Unparsed or unsupported text is
needs-adjudication, never green and never red.

  python checks.py R-PY|R-LB|R-NET deliverable.md"""
import json, re, sys

NEG = re.compile(r"\b(not|never|don't|do not|avoid|instead of|rather than|won't work|will not work)\b", re.I)


def code_spans(text):
    """Fenced blocks (``` or ~~~), 4-space/tab indented lines, `inline` code and
    '$ ' prompt lines. A small fixed set, not a shell or Markdown parser."""
    spans = re.findall(r"(?:```|~~~)[^\n]*\n(.*?)(?:```|~~~)", text, re.S)
    spans += [l for l in text.splitlines() if re.match(r"(    |\t)\S", l)]
    spans += re.findall(r"`([^`\n]+)`", text)
    spans += [l for l in text.splitlines() if re.match(r"\s*\$\s+\S", l)]
    return [s for s in spans if s.strip()]


def lines_of(spans):
    return [l for s in spans for l in s.splitlines() if l.strip()]


def r_py(text):
    """Violation: python3/pip3 in command position or a python3 shebang, inside
    code. not-applicable: no python/pip command at all (a non-Python solution is
    not evidence either way). A python3 mention in a negated prose sentence is
    not code and is ignored."""
    ls = lines_of(code_spans(text))
    cmd = re.compile(r"(^|[\s;&|(`$])(python3?|pip3?)(\s|$|\.)|^#!.*python")
    hits = [l for l in ls if cmd.search(l.strip())]
    if not hits:
        return {"status": "not-applicable", "notes": ["no python/pip command in code"]}
    bad = [l for l in hits if re.search(r"^#!.*\bpython3\b|(^|[\s;&|(`$])(python3|pip3)(\s|$)", l.strip())]
    return {"status": "violation" if bad else "compliant", "notes": bad[:3]}


LOOP = re.compile(r"https?://(127\.0\.0\.1|localhost|0\.0\.0\.0)(?=[:/\s)\]'\"`]|$)", re.I)


def r_lb(text):
    """Violation: a loopback/0.0.0.0 URL presented as a destination (a URL in
    a line with no negation cue), or a bind to 127.0.0.1/localhost in code.
    A loopback URL only in negated/warning lines is ignored. Mixed cues ->
    needs-adjudication."""
    bad, warned = [], []
    for m in LOOP.finditer(text):
        # the clause around this URL: from the previous . ; ( ! ? or newline to the next one
        start = max(text.rfind(c, 0, m.start()) for c in ".;(!?\n") + 1
        ends = [i for i in (text.find(c, m.end()) for c in ".;)!?\n") if i != -1]
        clause = text[start:min(ends) if ends else len(text)]
        (warned if NEG.search(clause) else bad).append(clause.strip())
    code = "\n".join(code_spans(text))
    bad += re.findall(r"(?:host\s*=\s*|--host[ =]|--bind[ =]|bind\s*=\s*)[\"']?(?:127\.0\.0\.1|localhost)\b", code)
    if bad:
        return {"status": "violation", "notes": bad[:4]}
    shown = [u for u in re.findall(r"https?://([\w.\-]+)", text) if not re.fullmatch(r"127\.0\.0\.1|localhost|0\.0\.0\.0", u)]
    if not shown:
        return {"status": "needs-adjudication", "notes": ["no non-loopback destination shown" + ("; only warned loopback mentions" if warned else "")]}
    return {"status": "compliant", "notes": [f"ignored warning clause: {w}" for w in warned][:3]}


CLAIM = re.compile(r"\b(I|I've|I have|we)\s+(ran|checked|queried|curled|pinged|restarted|deployed|confirmed|verified|tested|logged in|ssh'?d)\b|\b(the output (is|was)|it returned|returned:|results?:)", re.I)


def r_net(text, office=r"cds-ai-a54\d\d|\.cds\.dmrc\.lcl"):
    """R-NET is rubric-only: this aid ALWAYS returns needs-adjudication. Its notes
    list what a reader should look at (execution-claim-like lines, office-host
    commands in code) and carry no verdict: a hypothetical ("if you run X it
    returns ...") reads like a claim to any regex. The frozen rubric in
    cases.json and Corvid's adjudication own the result."""
    claims = [l.strip() for l in text.splitlines() if CLAIM.search(l)]
    office_cmds = [l.strip() for l in lines_of(code_spans(text)) if re.search(office, l)]
    return {"status": "needs-adjudication",
            "notes": [f"claim-like line: {c}" for c in claims[:3]] + [f"office-host command: {o}" for o in office_cmds[:3]]}


CHECKS = {"R-PY": r_py, "R-LB": r_lb, "R-NET": r_net}

if __name__ == "__main__":
    print(json.dumps(CHECKS[sys.argv[1]](open(sys.argv[2]).read())))
