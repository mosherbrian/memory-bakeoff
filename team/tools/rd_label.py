#!/usr/bin/env python3
"""Stage one of the R&D index: locate and describe. Nothing more.

WHAT STAGE ONE IS. Per file: one factual sentence of subject, the roles the
document plays, and an exact supporting quote for each role. No claim
extraction, no supersession judgement, no relationship chasing - those are
stages two and three, and each has to earn trust on its own. Tern, 2026-09-19,
correcting an over-packed first schema: "keep the schema as the destination,
make quotes and roles the first deliverable, and require each stage to earn
trust independently. That catches misunderstandings before they become hundreds
of well-formed records."

WHAT THE MECHANICAL CHECK DOES AND DOES NOT PROVE. Every quote is verified to
appear verbatim in the file, and its line span is computed here rather than
taken from the model. That is PROVENANCE validation, not label validation - a
perfectly copied sentence can still support the wrong role, and only a human
reading the file can tell. The distinction is Tern's, and it is the reason the
20-file review happens before the overnight run rather than after it.

Restartable: one record per file, written as it completes, keyed by content
hash. Re-running skips files whose hash already has a record, so a kill costs
one file.

    rd_label.py --hard              the 20 review files
    rd_label.py --all               everything not yet labelled
    rd_label.py --report            what has been labelled, and what failed
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

TEAM = Path(os.environ.get("RD_TEAM", Path.home() / "memory-bake-off/team"))
OUT = Path(os.environ.get("RD_LABELS", TEAM / "tools/rd-labels.jsonl"))
ENDPOINT = os.environ.get("RD_ENDPOINT", "http://strix-halo:8080/v1/chat/completions")
MODEL = os.environ.get("RD_MODEL", "qwen3.8-27b-code")
EXTRACTOR = "stage1/2026-09-19f"

ROLES = ["research_intake", "measurement_report", "protocol", "proposal",
         "decision_record", "verification", "synthesis", "operations",
         "implementation", "other", "unknown"]

PROMPT = """You are indexing one document from a research project's archive.
Describe it. Do NOT judge whether its claims are true, do not decide what
supersedes what, and do not summarise its findings.

Answer in EXACTLY this shape, and nothing else:

SUBJECT: <one factual sentence saying what this document is>
UNCERTAIN: <one sentence, or leave blank: what you could not tell>
ROLE: <one role from the vocabulary below>
<<<QUOTE
the sentence or short span copied exactly from the document
QUOTE>>>
ROLE: <another role, if one genuinely applies>
<<<QUOTE
its supporting passage
QUOTE>>>

CLASSIFY THE DOCUMENT'S FUNCTION, not every kind of sentence in it. A number
on the page does not make it a measurement report; a citation on the page does
not make it research intake. Ask what the document is FOR.

ROLE VOCABULARY - use only these, and use as many as genuinely apply:
  research_intake     the document's purpose is to bring in an outside paper,
                      benchmark or tool. Merely comparing to an external result
                      inside some other kind of document is NOT intake.
  measurement_report  reports a quantitative observation produced in the work
                      described - a census, a latency, resource usage, an
                      experiment result. Re-executing checks, constructing
                      mutants, and recording their acceptance or rejection are
                      VERIFICATION activities; those alone do not establish
                      this role. A document may hold both roles when it also
                      reports a distinct quantitative observation. Restating
                      earlier results is synthesis; checking someone else's
                      published figures is verification; an inherited baseline
                      does not make a pre-registration a measurement report.
                      Example of evidence that DOES establish it:
                        "Real census: 106 completed, 54 uncited, advisory rc 0."
  protocol            an OPERATIVE or FROZEN procedure. An amendment that has
                      not been accepted is a proposal, however it is worded.
  proposal            proposes work or a change that is not yet in force
  decision_record     records a decision taken, including a rejection, a
                      selection between options, or an explicit deferral or
                      prohibition ("do not build yet" is a DECISION). Wording
                      that merely points at the future does not make it a
                      proposal.
  verification        checks an identifiable claim or artifact against evidence
                      and records the outcome. Choosing which ideas are worth
                      pursuing is a DECISION, not a verification. A checker's
                      PASS/FAIL, or a deliberately broken fixture being
                      rejected, is verification evidence - not a measurement.
  synthesis           pulls several results together
  operations          fleet mechanics, scheduling, seats, infrastructure
  implementation      describes code that was written
  other               none of the above fits
  unknown             you genuinely cannot tell from the text

RULES:
- AT MOST 4 ROLES. A document has a few roles, not a dozen. Choose the ones
  that matter and stop.
- Every quote must be copied CHARACTER FOR CHARACTER from the document. Do not
  paraphrase, do not fix typos, do not splice noncontiguous passages. A quote
  that does not appear verbatim causes the whole record to be rejected.
- A quote may be ONE SENTENCE OR A SHORT CONTIGUOUS SPAN - two or three
  sentences, or a table row - when the surrounding words are what justify the
  role. It must be contiguous and copied exactly; under 400 characters.
- IDENTIFY THE DOCUMENT'S FUNCTIONS FIRST, then find evidence for each. For a
  candidate role, search the whole supplied text for the STRONGEST passage. If
  the first passage you find describes only method, scope or policy, LOOK
  ELSEWHERE for the actual observation or disposition - do NOT drop the role
  just because the first passage was unsuitable. Emit the role only if
  supporting evidence exists. Before finishing, check for a secondary function
  you have not recorded that does have explicit evidence. If the evidence is
  ambiguous, or lies outside the excerpt you were given, say so in "uncertain"
  rather than inventing support.
- ONE ROLE IS ENOUGH. Do not add roles for balance.
- AN IMPERATIVE INSIDE A PROPOSAL IS STILL A RECOMMENDATION. "Choose the middle
  approach", "this should be a standing gate", "we must do X" are proposal
  language. `decision_record` needs the document to record an adoption, a
  rejection, or a decision TAKEN - not advice about what ought to be done.
- A STATUS OBSERVATION IS NOT A DECISION. "It is not net-new, and still has no
  card" reports a state of affairs. Something must have been decided.
- FIXTURE OUTPUTS ARE VERIFICATION EVIDENCE EVEN WHEN NUMERIC. Expected values
  from a canonical fixture, parity counts, a mutant being rejected - all
  verification. `measurement_report` needs a quantity produced as a measurement
  in its own right.
- CODE THAT PERFORMS CHECKS IS `implementation`, and possibly `protocol` for the
  contract it declares. Its EXISTENCE does not establish that a verification
  ran. Use `verification` for a checker file only when the document records an
  execution outcome.
- A PROSE ARTIFACT IS NOT CODE. "This turn's artifact is this file" does not
  make a document `implementation`, and a persona or role block is not evidence
  that anything was installed.
- END THE QUOTE AT A COMPLETE CLAUSE. Never cut mid-word or mid-number.
- DO NOT INFER a project name, an authority, or a completion from a filename or
  from the seat that wrote the document. If the text does not name the project,
  your subject must not name it either. A seat is an author, not a project.
- "unknown" is a legitimate answer and is better than a guess.
- Answer with the JSON object and nothing before or after it.

DOCUMENT: <<PATH>>
---
<<BODY>>
"""


def head_tail(body, cap=40000):
    """A 992 KB board does not become clearer at 35,000 tokens of table rows.
    Measured 2026-09-19: asked one plain question, the model described QUEUE.md
    correctly in 96 tokens from that same input - so the size was never what
    stopped it. This keeps the beginning and the end, which is where a document
    says what it is and what became of it, and marks the cut."""
    if len(body) <= cap:
        return body
    h = cap * 3 // 4
    return (body[:h] + "\n\n[... " + str(len(body) - cap) +
            " characters omitted from the middle ...]\n\n" + body[-(cap - h):])


def call(prompt, timeout=300):
    # THE BUDGET COVERS THINKING. First run died on file one with
    # finish_reason=length: the server pins reasoning_effort medium in its env,
    # so the model spent the 2,000-token budget reasoning about a 992 KB
    # inventory and never reached its answer. This is extraction, not
    # judgement - there is nothing here worth thinking hard about - so effort
    # goes down and the budget goes up. The same shape cost the Flash-Next arm
    # a whole round earlier today.
    body = json.dumps({"model": MODEL, "temperature": 0.1, "max_tokens": 10000,
                       "chat_template_kwargs": {"reasoning_effort": "low"},
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    r = urllib.request.Request(ENDPOINT, data=body,
                               headers={"content-type": "application/json"})
    d = json.load(urllib.request.urlopen(r, timeout=timeout))
    ch = d["choices"][0]
    if ch.get("finish_reason") == "length":
        raise RuntimeError("TRUNCATED: the model ran out of budget mid-answer")
    return ch["message"].get("content") or ""


def parse(raw):
    """Marker-delimited, so a quote containing quotes cannot break the format.

    WHY NOT JSON. Measured on a random 60: two documents failed with
    "Expecting ',' delimiter" because a copied passage contained a double quote
    the model did not escape - 3%, about 24 records lost across the corpus. No
    amount of asking for valid JSON fixes a format whose payload is arbitrary
    document text.

    AND WHY THAT EXPLANATION LIVES HERE RATHER THAN IN THE PROMPT. The first
    version of this fix put the reasoning, measurement and all, at the top of
    the prompt. On RD-TRACKS.md the model then labelled THE PROMPT: subject
    "records a decision to use marker-delimited quotes instead of
    JSON-embedded quotes", with both quotes lifted from the instructions. The
    quote check caught it - neither passage is in that file - which is exactly
    the failure provenance-checking exists for. A rationale in the context is
    a document the model can index. Instructions tell it what to do; the why
    belongs in the source."""
    txt = re.sub(r"```(?:json|text)?", "", raw)
    subj = re.search(r"^SUBJECT:\s*(.+)$", txt, re.M)
    # HORIZONTAL WHITESPACE ONLY. `\s*` after an EMPTY uncertain field eats the
    # newline and captures the next line, so several records carry
    # "ROLE: verification" as their uncertainty note. Found by the Director in
    # the validation tranche, 2026-09-19; fixed by reparsing preserved replies,
    # no model re-run.
    unc = re.search(r"^UNCERTAIN:[ \t]*(.*)$", txt, re.M)
    roles = []
    for m in re.finditer(r"^ROLE:\s*(\S+)[^\n]*\n+<<<QUOTE\s*\n(.*?)\n?QUOTE>>>",
                         txt, re.S | re.M):
        roles.append({"role": m.group(1).strip().strip('",`'),
                      "quote": m.group(2).strip()})
    # a role with no quote block at all is still a role the model named;
    # "unknown" legitimately has nothing to quote.
    for m in re.finditer(r"^ROLE:\s*(unknown)\s*$", txt, re.M | re.I):
        if not any(r["role"].lower() == "unknown" for r in roles):
            roles.append({"role": "unknown", "quote": ""})
    if not subj and not roles:
        # ACCEPT JSON TOO. Moving quotes out of JSON fixed a 3% escaping
        # failure and introduced a 27% one: 3 of 11 replies came back as
        # well-formed JSON anyway, because that is what the model reaches for.
        # Fighting the preference is the wrong move when both formats are
        # parseable - markers are tried first because they cannot break on a
        # quote inside a quote, and JSON is accepted when it arrives intact.
        # A THIRD SHAPE, AND THE DANGEROUS ONE. The model sometimes merges the
        # two formats: JSON syntax carrying the MARKER field names, with ROLE
        # and QUOTE repeated at the top level rather than in a roles array -
        #   {"SUBJECT":"...","ROLE":"protocol","QUOTE":"...","ROLE":"operations",...}
        # json.loads accepts that and SILENTLY KEEPS ONLY THE LAST duplicate
        # key, so it parsed fine and returned zero roles. Lossy without an
        # error, which is the failure class this project exists to catch. The
        # pairs are pulled out by regex, in order, before json.loads can eat
        # them.
        pairs = re.findall(r'"ROLE"\s*:\s*"([^"]+)"\s*,\s*"QUOTE"\s*:\s*'
                           r'"((?:[^"\\]|\\.)*)"', txt)
        if pairs:
            sj = re.search(r'"SUBJECT"\s*:\s*"((?:[^"\\]|\\.)*)"', txt)
            uj = re.search(r'"UNCERTAIN"\s*:\s*"((?:[^"\\]|\\.)*)"', txt)
            # MOJIBAKE. `x.encode().decode("unicode_escape")` gives UTF-8
            # bytes to a Latin-1 decoder, so every em-dash in a quote came back
            # as "â\x80\x94" and then failed the presence check - four
            # rejections on the validation tranche that looked like the model
            # fabricating and were this line. json.loads on the quoted string
            # handles \n, \" and \uXXXX without touching the encoding.
            def unesc(x):
                try:
                    return json.loads(f'"{x}"')
                except Exception:                       # noqa: BLE001
                    return x
            return {"subject": unesc(sj.group(1)) if sj else "",
                    "uncertain": unesc(uj.group(1)) if uj else "",
                    "roles": [{"role": r.strip(), "quote": unesc(q)}
                              for r, q in pairs]}
        m = re.search(r"\{.*\}", txt, re.S)
        if m:
            try:
                d = json.loads(m.group(0))
                d = {k.lower(): v for k, v in d.items()}
                rs = []
                for r in d.get("roles") or []:
                    r = {k.lower(): v for k, v in r.items()}
                    if r.get("role"):
                        rs.append({"role": str(r["role"]).strip(),
                                   "quote": str(r.get("quote") or "")})
                if d.get("subject") or rs:
                    return {"subject": str(d.get("subject") or "").strip(),
                            "uncertain": str(d.get("uncertain") or "").strip(),
                            "roles": rs}
            except Exception:                           # noqa: BLE001
                pass
        raise ValueError(f"neither markers nor JSON in the reply: {txt[:120]!r}")
    return {"subject": subj.group(1).strip() if subj else "",
            "uncertain": unc.group(1).strip() if unc else "",
            "roles": roles}


# MARKDOWN IS FORMATTING, NOT CONTENT. Measured on the 20-file review,
# 2026-09-19: every one of the four rejected quotes was a real sentence from
# the file with its emphasis markers dropped - "- **Source:** HaluMem ..."
# came back as "Source: HaluMem ...". Four for four, zero fabrications. Run
# over 774 files this matcher would have produced roughly 150 false
# rejections and the conclusion "the local model invents quotes" would have
# been wrong every time - a guard that cries wolf, which is the failure this
# project removed from the model-substitution check the same morning.
#
# The guarantee is PROVENANCE: is this sentence really in the document. So
# emphasis markers and list bullets are stripped from both sides and the word
# sequence must still match exactly - a paraphrase still fails, which is the
# whole point of checking at all.
def _flat(s):
    s = re.sub(r"(?m)^\s*[-*+]\s+", "", s)
    s = re.sub(r"[*`_]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def locate(body, quote):
    """Line span of an exact quote, or None. Whitespace is normalised on BOTH
    sides because models reflow long lines; nothing else is forgiven."""
    if not quote.strip():
        return None
    fb, fq = _flat(body), _flat(quote)
    if fq not in fb:
        return None
    # map back to a line number by finding the first line that starts the quote
    head = fq[:40]
    for i, line in enumerate(body.split("\n"), 1):
        if head in _flat(line) or _flat(line)[:40] == head:
            return i
    return 0                 # present, but spans lines we could not pin


def label_one(path, retry=False):
    body = (TEAM / path).read_text(errors="ignore")
    sha = hashlib.sha256(body.encode()).hexdigest()[:12]
    sent = head_tail(body)
    prompt = PROMPT.replace("<<PATH>>", path).replace("<<BODY>>", sent)
    rec = {"path": path, "content_sha": sha, "extractor": EXTRACTOR,
           "model": MODEL, "at": int(time.time()),
           "prompt_sha": hashlib.sha256(PROMPT.encode()).hexdigest()[:12],
           # PARTIAL INPUT IS NOT AN ABSENT ROLE. Tern, 2026-09-19: record
           # coverage "so missing roles are not mistaken for absent roles".
           "input_coverage": ("full" if len(sent) == len(body)
                              else f"partial {len(sent)}/{len(body)} chars")}
    t0 = time.time()
    try:
        raw_reply = call(prompt)
        d = parse(raw_reply)
    except Exception as e:                              # noqa: BLE001
        # A PARSE FAILURE RETURNS EARLY, so the later raw-capture never ran and
        # the evidence for every error record was thrown away. Capture here too.
        # ONE BOUNDED RETRY, and both attempts are kept. The four parse
        # failures on the random 60 all succeeded on a re-run with no code
        # change, so the malformed shapes are stochastic. Tern, 2026-09-19:
        # "Preserve both attempts, record first-attempt and eventual success
        # separately, and apply the same provenance checks to the retry. Four
        # successful retries demonstrate recoverability, not a reliable
        # failure-rate estimate." So first_attempt is recorded whatever happens
        # and the rate stays measurable.
        first = {"status": f"error: {type(e).__name__}: {str(e)[:120]}",
                 "raw": (locals().get("raw_reply") or "")[:4000]}
        if retry:
            rec.update(processing_status=first["status"], raw=first["raw"],
                       first_attempt=first, attempts=2)
            return rec
        rec2 = label_one(path, retry=True)
        rec2["first_attempt"] = first
        rec2["attempts"] = 2
        return rec2
    rec["subject"] = (d.get("subject") or "").strip()
    rec["uncertain"] = (d.get("uncertain") or "").strip()
    roles, bad = [], []
    for r in d.get("roles") or []:
        name, quote = (r.get("role") or "").strip(), (r.get("quote") or "")
        line = locate(body, quote)
        entry = {"role": name, "quote": quote, "line": line,
                 "in_vocabulary": name in ROLES, "chars": len(quote)}
        # "unknown" IS THE ONE ROLE WITH NOTHING TO QUOTE. The prompt says
        # unknown is a legitimate answer and better than a guess; the validator
        # then required a supporting quote for every role, so a model that
        # honestly said "I cannot tell" had its whole record scored
        # no_valid_roles. Third time today this checker punished honest
        # behaviour - after the markdown emphasis and the complete-clause cut.
        # A check that fails good work is worse than no check.
        if name == "unknown":
            ok = True
        else:
            # 600, NOT 400. The 400 was MY number, not the Director's - it
            # asked for "a short contiguous evidence span, including a table
            # row or two sentences". S6-ROADMAP/check.py quoted a declared
            # interface block that is genuinely in the file and genuinely the
            # evidence for `protocol`, and it was thrown out for being SEVEN
            # characters over. Fifth time today a threshold of mine rejected
            # honest work. Still bounded, because an unbounded cap lets the
            # model quote the document back.
            ok = line is not None and name in ROLES and len(quote) <= 600
        (roles if ok else bad).append(entry)
    # DEDUPE. The parser tries several shapes and two can match the same reply,
    # which put the identical role/quote pair in the record twice.
    def uniq(rs):
        seen, out = set(), []
        for r in rs:
            k = (r["role"], r["quote"][:200])
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out
    rec["roles"] = uniq(roles)
    rec["rejected_roles"] = uniq(bad)
    rec["secs"] = round(time.time() - t0)
    # PROVENANCE, NOT CORRECTNESS. This says every surviving quote is really in
    # the file. It says nothing about whether the role is the right one.
    rec["processing_status"] = ("ok" if roles and not bad else
                                "needs_review" if roles else "no_valid_roles")
    # KEEP THE REPLY WHEN NOTHING SURVIVED. Three parser patches today were made
    # by re-running one file and printing its answer, because the record kept
    # only the verdict and not the evidence for it. A failure you cannot read is
    # a failure you fix by guessing.
    if not roles:
        rec["raw"] = (locals().get("raw_reply") or "")[:4000]
    return rec


def done_hashes():
    if not OUT.exists():
        return set()
    out = set()
    for line in OUT.open():
        try:
            d = json.loads(line)
        except Exception:                               # noqa: BLE001
            continue
        # KEYED ON THE EXTRACTOR TOO. Keying on content alone meant a repaired
        # prompt would skip every file it had already labelled badly, so the
        # repair would never reach them.
        if d.get("processing_status") == "ok":
            out.add((d["path"], d["content_sha"], d.get("extractor"),
                     d.get("prompt_sha")))
    return out


def targets(which):
    p = subprocess.run(["python3", str(TEAM / "tools/rd_index.py"), "--hard"],
                       capture_output=True, text=True, timeout=300)
    hard = [l.split()[0] for l in p.stdout.split("\n")
            if l.startswith("      ") and l.strip()]
    if which == "hard":
        return hard
    rows = [json.loads(l) for l in (TEAM / "tools/rd-index.jsonl").open()]
    return [r["path"] for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hard", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    # THE RANDOM TRANCHE, WITH A RECORDED SEED. Tern moved this ahead of the
    # bulk run: "The difficult set can show that we repaired known mistakes;
    # the random set tests whether those repairs work beyond the examples we
    # supplied." The seed is printed and stored so the draw can be re-made.
    ap.add_argument("--random", type=int, metavar="N")
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("paths", nargs="*", help="relabel just these files")
    a = ap.parse_args()

    if a.report:
        recs = [json.loads(l) for l in OUT.open()] if OUT.exists() else []
        by = {}
        for r in recs:
            by[r["processing_status"].split(":")[0]] = \
                by.get(r["processing_status"].split(":")[0], 0) + 1
        print(f"{len(recs)} record(s) in {OUT}")
        for k, v in sorted(by.items()):
            print(f"  {k:<16} {v}")
        bad = [r for r in recs if r.get("rejected_roles")]
        if bad:
            print(f"\n{len(bad)} record(s) had a quote that is not in the file:")
            for r in bad[:8]:
                for e in r["rejected_roles"][:1]:
                    why = "not in vocabulary" if not e["in_vocabulary"] else "quote not found"
                    print(f"  {r['path'][:44]:44} {e['role'][:18]:18} {why}")
        return 0

    which = ("these" if a.paths else "hard" if a.hard else "all" if a.all
             else "random" if a.random else None)
    if not which:
        ap.print_help()
        return 0
    done = done_hashes()
    if which == "random":
        import random
        # EXCLUDE EVERYTHING ALREADY REVIEWED, not just the difficult set. The
        # first draw here took "all minus hard", which could re-draw files from
        # the reviewed 60 - the very files whose boundaries the prompt was
        # tuned against. A validation sample that can contain tuned-against
        # files cannot test what it is for. Exclusions are read from the frozen
        # manifest so the draw is reproducible from a file, not from whatever
        # the label log happened to hold.
        import json as _j
        frozen = _j.loads((TEAM / "tools/rd-freeze-20260919.json").read_text())
        excl = set(frozen["excluded_difficult_set"]) | set(frozen["excluded_random_60"])
        pool = sorted(set(targets("all")) - excl)
        random.Random(a.seed).shuffle(pool)
        todo = pool[:a.random]
        print(f"random tranche: {len(todo)} of {len(pool)} unseen files, "
              f"seed {a.seed}, excluding {len(excl)} already-reviewed "
              f"(20 difficult + 60 tranche)", flush=True)
    elif which == "these":
        todo = a.paths
    else:
        todo = targets(which)
    print(f"{len(todo)} file(s) selected; {len(done)} already labelled", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for i, path in enumerate(todo, 1):
        try:
            sha = hashlib.sha256(
                (TEAM / path).read_bytes()).hexdigest()[:12]
        except OSError:
            continue
        if (path, sha, EXTRACTOR,
                hashlib.sha256(PROMPT.encode()).hexdigest()[:12]) in done:
            continue
        rec = label_one(path)
        with OUT.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"  {i}/{len(todo)} {path[:46]:46} {rec['processing_status'][:28]:28}"
              f" roles={len(rec.get('roles', []))} "
              f"rejected={len(rec.get('rejected_roles', []))}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
