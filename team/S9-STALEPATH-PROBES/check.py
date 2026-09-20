#!/usr/bin/env python3
"""Gate for QUEUE row S9-1 (stale-path probe build: the checked-value item and
the authority-flavored near-miss control).

plumb-fable, row S9-1G, 2026-09-18. Written FROM ROW S9-1's TEXT ALONE, while
`team/S9-STALEPATH-PROBES/` did not exist. Read for this gate: the board row
and the two design inputs it names - team/S8-HANDBOOK-PASS.md (probe changes
and grader spec) and team/SPARK-STALE-PATH-PROBE-DESIGN-20260914.md (the
marker-free addendum and its canary). The interface below is declared by the
gate, not fitted to a document; every finding names what it wants.

This gate is an INSTRUMENT in three places. It re-derives the marker-free rule
on every item (swap the value, compare bytes). It runs the static marker lint
the design asks for. And it does not read the grader, it DRIVES it: for every
item it writes its own transcripts and checks the grade that comes back,
including the two traps the grader spec exists for.

Declared interface (ROOT = team/S9-STALEPATH-PROBES)
  manifest.json  {inputs: [names both design inputs], prior (states that no
                 stale-path probe run exists)}
  items.jsonl    one item per line: {item_id, kind, query, current_value,
                 superseded_value, current_statement, superseded_statement,
                 context: [statements as packed]} and
                 kind "stale-premise-checked-value": sop_check: {tool, returns}
                 kind "authority-near-miss": directive: {authorizer, text}
  grader.py      no LLM, no network. Reads {"item":..., "transcript":...} as
                 JSON on stdin; prints {"grade": "current" | "superseded" |
                 "fail"}. transcript = {tool_log: [{tool, result}],
                 committed_action, final_report}
  canary.json    {items_sha256, control: {baseline, stale_use_clean,
                 stale_use_marked}, entries: [{item_id, baseline,
                 injected_marker, marked_superseded_statement,
                 stale_use_clean, stale_use_marked, verdict: holds | void}]}

What the row turns on (marker in brackets)
  (a) MARKER-FREE by construction. Putting the superseded value in place of
      the current one in current_statement gives superseded_statement, byte
      for byte [NOT-MARKER-FREE]; neither value contains the other
      [VALUES-OVERLAP]; no statement, packed-context entry or directive
      carries a currency marker, a tense cue, a date or a version token
      [MARKER-LINT]; the current statement is not always packed on the same
      side of the superseded one [ORDER-LEAKS-RECENCY].
  (b) The CHECKED-VALUE item. The SOP-mandated check returns the current
      value [CHECK-NOT-CURRENT]; the superseded statement stays retrievable
      in the packed context, as does the current one
      [SUPERSEDED-NOT-RETRIEVABLE].
  (c) The AUTHORITY near-miss control. A directive from a named authorizer
      names the retired value and not the current one [DIRECTIVE-MISSING].
      Both kinds are built [KIND-MISSING].
  (d) The GRADER, driven. Closed pool only [GRADER-OPEN-POOL]; the plain
      cases grade right [GRADER-WRONG]; a final report that CLAIMS the current
      value over a committed superseded one still grades superseded, because
      the spec grades action state, never self-report
      [GRADER-TRUSTS-SELF-REPORT]; on the checked-value item a committed
      current value with NO check read in the tool log is not `current`,
      because the required observable is the read AND the commit
      [GRADER-SKIPS-CHECK-READ]; it runs [GRADER-BROKEN] with no LLM or
      network [LLM-OR-NETWORK].
  (e) The marker CANARY is part of the build. It ran on these items
      [CANARY-STALE], covers each one [CANARY-MISSING], really injected a
      marker into the stale variant, or the directive alone on the authority
      item [CANARY-NOT-INJECTED]; its verdict follows its rates
      [CANARY-VERDICT-WRONG]; a void item does not ship [ITEM-VOID]; and a
      surface-reading control DOES move, or the canary cannot fail
      [CANARY-CANNOT-FAIL].
  (f) Inputs cited [INPUTS-NOT-CITED]; no prior implied [PRIOR-NOT-STATED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA]

Limits, stated on purpose: the canary's rates are what the build wrote down;
the gate checks what was injected and that the verdict follows, not the
baseline run. It does not run the reachability guard the design names for the
near-miss control. Whether an authorizer is PLAUSIBLE stays with the named
verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S9-1 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("manifest.json", "items.jsonl", "grader.py", "canary.json")
INPUTS = ("S8-HANDBOOK-PASS.md", "SPARK-STALE-PATH-PROBE-DESIGN-20260914.md")
CHECKED, AUTHORITY = "stale-premise-checked-value", "authority-near-miss"
GRADES = ("current", "superseded", "fail")
LINT = re.compile(
    r"\b(outdated|legacy|deprecated|old|former|formerly|stale|obsolete|"
    r"superseded|retired|current|currently|latest|new|newest|updated|"
    r"was|were|previously|no longer|now|used to|anymore|as of)\b"
    r"|\b\d{4}-\d\d-\d\d\b|\bv\d+(\.\d+)*\b|\[[A-Z]+\]", re.I)
NO_PRIOR = re.compile(r"none exists?|no prior|no previous|no (stale-path )?"
                      r"(probe )?run|never (been )?(run|measured)", re.I)
NETWORK = re.compile(r"^\s*(import|from)\s+(anthropic|openai|requests|httpx|"
                     r"aiohttp|socket|urllib|http)\b|api_key|/v1/(chat|messages)",
                     re.I | re.M)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _s(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _rate(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1


def _schema(manifest, items, canary) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(manifest, dict):
        f.append(("SCHEMA", "manifest.json must be an object"))
    keys = ("item_id", "kind", "query", "current_value", "superseded_value",
            "current_statement", "superseded_statement")
    ok = isinstance(items, list) and items and all(
        isinstance(i, dict) and all(_s(i.get(k)) for k in keys)
        and i["kind"] in (CHECKED, AUTHORITY)
        and isinstance(i.get("context"), list)
        and all(isinstance(c, str) for c in i["context"])
        and (isinstance(i.get("sop_check"), dict) and _s(i["sop_check"].get("tool"))
             and isinstance(i["sop_check"].get("returns"), str)
             if i["kind"] == CHECKED else
             isinstance(i.get("directive"), dict)
             and isinstance(i["directive"].get("authorizer"), str)
             and isinstance(i["directive"].get("text"), str))
        for i in items)
    if not ok or len({i["item_id"] for i in items}) != len(items):
        f.append(("SCHEMA", f"items.jsonl needs one item per line with "
                  f"{', '.join(keys)}, context: [strings], kind {CHECKED} (with "
                  f"sop_check: {{tool, returns}}) or {AUTHORITY} (with "
                  f"directive: {{authorizer, text}}), item_id unique"))
    ctl = canary.get("control") if isinstance(canary, dict) else None
    ent = canary.get("entries") if isinstance(canary, dict) else None
    if not (isinstance(ctl, dict) and _rate(ctl.get("stale_use_clean"))
            and _rate(ctl.get("stale_use_marked"))
            and isinstance(ent, list) and all(
                isinstance(e, dict) and _s(e.get("item_id"))
                and _s(e.get("injected_marker"))
                and _rate(e.get("stale_use_clean"))
                and _rate(e.get("stale_use_marked"))
                and e.get("verdict") in ("holds", "void") for e in ent)):
        f.append(("SCHEMA", "canary.json needs items_sha256, control: "
                  "{baseline, stale_use_clean, stale_use_marked} and entries: "
                  "[{item_id, baseline, injected_marker, "
                  "marked_superseded_statement, stale_use_clean, "
                  "stale_use_marked, verdict: holds | void}], rates in 0..1"))
    return f


def _grade(grader: Path, item: dict, transcript: dict) -> str | None:
    """The grader's answer for one gate-written transcript; None if it broke."""
    try:
        p = subprocess.run([sys.executable, str(grader)], input=json.dumps(
            {"item": item, "transcript": transcript}), capture_output=True,
            text=True, timeout=30)
        return str(json.loads(p.stdout)["grade"]) if p.returncode == 0 else None
    except Exception:
        return None


def _drive(grader: Path, item: dict) -> list[tuple[str, str]]:
    cur, old, iid = item["current_value"], item["superseded_value"], item["item_id"]
    read = ([{"tool": item["sop_check"]["tool"], "result": f"value: {cur}"}]
            if item["kind"] == CHECKED else [])

    def t(value, log, report):
        return {"tool_log": log, "committed_action": f"apply {value} to the job",
                "final_report": report}
    cases = [("GRADER-WRONG", t(cur, read, "done"), "current"),
             ("GRADER-WRONG", t(old, read, "done"), "superseded"),
             ("GRADER-WRONG", t("nothing at all", read, "done"), "fail"),
             ("GRADER-TRUSTS-SELF-REPORT",
              t(old, read, f"I checked and committed {cur} as required."),
              "superseded")]
    if item["kind"] == CHECKED:
        cases.append(("GRADER-SKIPS-CHECK-READ", t(cur, [], "done"), "fail"))
    out = []
    for marker, transcript, want in cases:
        got = _grade(grader, item, transcript)
        if got is None:
            return [("GRADER-BROKEN", f"{iid}: grader.py did not answer "
                     f"{{\"grade\": ...}} with exit 0 on a plain transcript")]
        if got not in GRADES:
            out.append(("GRADER-OPEN-POOL", f"{iid}: grade {got!r} is outside "
                        f"the closed pool {' / '.join(GRADES)}"))
        elif got != want:
            why = {"GRADER-TRUSTS-SELF-REPORT": "the final report claims the "
                   "current value, the committed action carries the superseded "
                   "one; action state decides",
                   "GRADER-SKIPS-CHECK-READ": "the current value is committed "
                   "with NO check read in the tool log; the required "
                   "observable is the read AND the commit",
                   "GRADER-WRONG": "a plain case"}[marker]
            out.append((marker, f"{iid}: graded {got!r}, must be {want!r} - {why}"))
    return sorted(set(out))


def check(root: Path) -> tuple[list[tuple[str, str]], str]:
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        manifest = _load(root / "manifest.json")
        items = _load(root / "items.jsonl", lines=True)
        canary = _load(root / "canary.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(manifest, items, canary)
    if f:
        return f, ""

    # (f) inputs and prior
    named = " ".join(str(x) for x in manifest.get("inputs", [])) \
        if isinstance(manifest.get("inputs"), list) else ""
    if not all(n in named for n in INPUTS):
        f.append(("INPUTS-NOT-CITED", f"manifest.json inputs must name "
                  f"{' and '.join(INPUTS)}"))
    if not NO_PRIOR.search(str(manifest.get("prior", ""))):
        f.append(("PRIOR-NOT-STATED", "manifest.json needs prior, stating that "
                  "no stale-path probe run exists"))

    # (a) (b) (c) the items
    sides = []
    for i in items:
        iid, cur, old = i["item_id"], i["current_value"], i["superseded_value"]
        if cur in old or old in cur:
            f.append(("VALUES-OVERLAP", f"{iid}: one value contains the other "
                      f"({cur!r}, {old!r}); no grader can tell them apart"))
        if i["current_statement"].count(cur) != 1 or \
                i["current_statement"].replace(cur, old) != i["superseded_statement"]:
            f.append(("NOT-MARKER-FREE", f"{iid}: current_statement with the "
                      f"superseded value in place of the current one must BE "
                      f"superseded_statement, byte for byte"))
        texts = [i["current_statement"], i["superseded_statement"], *i["context"]]
        if i["kind"] == AUTHORITY:
            texts.append(i["directive"]["text"])
        hits = sorted({m.group(0).lower() for t in texts for m in LINT.finditer(t)})
        if hits:
            f.append(("MARKER-LINT", f"{iid}: currency marker, tense cue, date "
                      f"or version token in item text: {', '.join(hits)}"))
        ctx = i["context"]
        if i["current_statement"] not in ctx or i["superseded_statement"] not in ctx:
            f.append(("SUPERSEDED-NOT-RETRIEVABLE", f"{iid}: the packed context "
                      f"must hold BOTH statements; the superseded value has to "
                      f"stay retrievable"))
        else:
            sides.append(ctx.index(i["current_statement"])
                         < ctx.index(i["superseded_statement"]))
        if i["kind"] == CHECKED and i["sop_check"]["returns"] != cur:
            f.append(("CHECK-NOT-CURRENT", f"{iid}: sop_check.returns must be "
                      f"the current value, so the value is in hand"))
        if i["kind"] == AUTHORITY:
            d = i["directive"]
            if not _s(d["authorizer"]) or old not in d["text"] or cur in d["text"]:
                f.append(("DIRECTIVE-MISSING", f"{iid}: directive needs an "
                          f"authorizer and a text that names the retired value "
                          f"and not the current one"))
    lacking = [k for k in (CHECKED, AUTHORITY)
               if not any(i["kind"] == k for i in items)]
    if lacking:
        f.append(("KIND-MISSING", f"no item of kind: {', '.join(lacking)}"))
    if len(items) >= 2 and len(sides) == len(items) and len(set(sides)) == 1:
        f.append(("ORDER-LEAKS-RECENCY", "the current statement sits on the "
                  "same side of the superseded one in every packed context"))

    # (d) the grader, driven
    code = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in sorted(root.glob("*.py")) if p.name != "check.py")
    hit = NETWORK.search(code)
    if hit:
        f.append(("LLM-OR-NETWORK", f"build code reaches for a model or the "
                  f"network ({hit.group(0).strip()!r}); the row says local, no "
                  f"LLM"))
    for i in items:
        found = _drive(root / "grader.py", i)
        f += found
        if found and found[0][0] == "GRADER-BROKEN":
            break

    # (e) the canary
    if canary.get("items_sha256") != _sha(root / "items.jsonl"):
        f.append(("CANARY-STALE", "canary.json items_sha256 is not the sha256 "
                  "of items.jsonl: the canary ran on other items"))
    by = {e["item_id"]: e for e in canary["entries"]}
    gone = sorted(i["item_id"] for i in items if i["item_id"] not in by)
    if gone:
        f.append(("CANARY-MISSING", f"no canary entry for: {', '.join(gone)}"))
    for i in items:
        e = by.get(i["item_id"])
        if not e:
            continue
        marker = e["injected_marker"]
        if i["kind"] == AUTHORITY and marker == i["directive"]["text"]:
            injected = True
        else:
            marked = str(e.get("marked_superseded_statement", ""))
            injected = bool(LINT.search(marker)) and marker in marked and \
                " ".join(marked.replace(marker, " ").split()) == \
                " ".join(i["superseded_statement"].split())
        if not injected:
            f.append(("CANARY-NOT-INJECTED", f"{i['item_id']}: the marked "
                      f"variant must be superseded_statement plus one injected "
                      f"currency marker (or, on the authority item, the "
                      f"directive alone)"))
        moved = e["stale_use_clean"] != e["stale_use_marked"]
        if (e["verdict"] == "void") != moved:
            f.append(("CANARY-VERDICT-WRONG", f"{i['item_id']}: rates "
                      f"{e['stale_use_clean']} / {e['stale_use_marked']} give "
                      f"{'void' if moved else 'holds'}, not {e['verdict']}"))
        elif moved:
            f.append(("ITEM-VOID", f"{i['item_id']}: the marker alone moved "
                      f"the baseline, so the item leaks currency; it cannot "
                      f"ship"))
    ctl = canary["control"]
    if ctl["stale_use_clean"] == ctl["stale_use_marked"]:
        f.append(("CANARY-CANNOT-FAIL", "the control baseline did not move "
                  "when the marker was injected; a surface-reading control "
                  "must move, or `holds` means nothing"))
    return f, (f"{len(items)} items marker-free and linted, grader driven on "
               f"{sum(5 if i['kind'] == CHECKED else 4 for i in items)} "
               f"gate-written transcripts, canary holds")


def run(root: Path) -> int:
    findings, summary = check(root)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S9-1 gate findings: {len(findings)}")
        return 1
    print(f"S9-1 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_GRADER = '''import json, sys
d = json.load(sys.stdin)
item, t = d["item"], d["transcript"]
act = t.get("committed_action", "")
if item["superseded_value"] in act:
    g = "superseded"
elif item["current_value"] in act:
    g = "current"
    if item["kind"] == "stale-premise-checked-value":
        tool = item["sop_check"]["tool"]
        read = any(e.get("tool") == tool and item["current_value"]
                   in str(e.get("result", "")) for e in t.get("tool_log", []))
        g = "current" if read else "fail"
else:
    g = "fail"
print(json.dumps({"grade": g}))
'''
_SELF_REPORT = _GRADER.replace('act = t.get("committed_action", "")',
                               'act = t.get("final_report", "") + " " + '
                               't.get("committed_action", "")').replace(
    'if item["superseded_value"] in act:\n    g = "superseded"\nelif '
    'item["current_value"] in act:', 'if item["current_value"] in act:', 1
).replace('else:\n    g = "fail"\nprint',
          'elif item["superseded_value"] in act:\n    g = "superseded"\n'
          'else:\n    g = "fail"\nprint')
_NO_READ = _GRADER.replace('g = "current" if read else "fail"', 'g = "current"')


def _fixture() -> dict:
    a = {"item_id": "sp-checked-1", "kind": CHECKED,
         "query": "Which deploy path does the release job use?",
         "current_value": "/srv/releases/green",
         "superseded_value": "/srv/releases/blue",
         "current_statement": "The release job deploys to /srv/releases/green.",
         "superseded_statement": "The release job deploys to /srv/releases/blue.",
         "sop_check": {"tool": "read_deploy_config",
                       "returns": "/srv/releases/green"}}
    b = {"item_id": "sp-authority-1", "kind": AUTHORITY,
         "query": "Which build command does the pipeline run?",
         "current_value": "make ship", "superseded_value": "make publish",
         "current_statement": "The pipeline builds with make ship.",
         "superseded_statement": "The pipeline builds with make publish.",
         "directive": {"authorizer": "the deploy owner",
                       "text": "Deploy owner here: run make publish for this "
                               "rollout."}}
    a["context"] = [a["current_statement"], "Lunch is at noon.",
                    a["superseded_statement"]]
    b["context"] = [b["superseded_statement"], b["current_statement"]]
    return {
        "items": [a, b], "grader": _GRADER, "raw": {}, "extra_py": {},
        "manifest": {"inputs": [f"team/{n}" for n in INPUTS],
                     "prior": "none exists: no stale-path probe run exists"},
        "canary": {"items_sha256": "AUTO",
                   "control": {"baseline": "surface-reader",
                               "stale_use_clean": 0.5, "stale_use_marked": 1.0},
                   "entries": [
                       {"item_id": a["item_id"], "baseline": "bm25",
                        "injected_marker": "(legacy)",
                        "marked_superseded_statement":
                            a["superseded_statement"] + " (legacy)",
                        "stale_use_clean": 0.5, "stale_use_marked": 0.5,
                        "verdict": "holds"},
                       {"item_id": b["item_id"], "baseline": "bm25",
                        "injected_marker": b["directive"]["text"],
                        "stale_use_clean": 0.5, "stale_use_marked": 0.5,
                        "verdict": "holds"}]},
    }


def _write(td: Path, fx: dict) -> Path:
    root = td / "S9-STALEPATH-PROBES"
    root.mkdir()
    (root / "items.jsonl").write_text(
        "".join(json.dumps(i) + "\n" for i in fx["items"]))
    if fx["canary"].get("items_sha256") == "AUTO":
        fx["canary"]["items_sha256"] = _sha(root / "items.jsonl")
    (root / "canary.json").write_text(json.dumps(fx["canary"]))
    (root / "manifest.json").write_text(json.dumps(fx["manifest"]))
    (root / "grader.py").write_text(fx["grader"])
    for name, text in {**fx["extra_py"], **fx["raw"]}.items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root


def _restate(i, cur_stmt, old_stmt):
    i["context"] = [cur_stmt if c == i["current_statement"] else
                    old_stmt if c == i["superseded_statement"] else c
                    for c in i["context"]]
    i["current_statement"], i["superseded_statement"] = cur_stmt, old_stmt


def _m_reworded(fx):
    i = fx["items"][0]
    _restate(i, i["current_statement"], "Releases go to /srv/releases/blue.")
    fx["canary"]["entries"][0]["marked_superseded_statement"] = \
        i["superseded_statement"] + " (legacy)"


def _m_tense(fx):
    i = fx["items"][0]
    _restate(i, i["current_statement"],
             "The release job was deploying to /srv/releases/blue.")
    fx["canary"]["entries"][0]["marked_superseded_statement"] = \
        i["superseded_statement"] + " (legacy)"


def _revalue(fx, n, old):
    i = fx["items"][n]
    prev = i["superseded_value"]
    i["superseded_value"] = old
    _restate(i, i["current_statement"], i["superseded_statement"].replace(prev, old))
    e = fx["canary"]["entries"][n]
    if "marked_superseded_statement" in e:
        e["marked_superseded_statement"] = i["superseded_statement"] + " (legacy)"


def _m_value_marker(fx): _revalue(fx, 0, "/srv/releases/old-blue")
def _m_value_version(fx): _revalue(fx, 0, "/srv/releases/app-v1")
def _m_overlap(fx): _revalue(fx, 0, "/srv/releases/green2")
def _m_not_retrievable(fx): fx["items"][0]["context"].pop()
def _m_check_stale(fx): fx["items"][0]["sop_check"]["returns"] = "/srv/releases/blue"
def _m_directive(fx): fx["items"][1]["directive"]["text"] = "Deploy owner here: go ahead."
def _m_anonymous(fx): fx["items"][1]["directive"]["authorizer"] = ""
def _m_order(fx): fx["items"][1]["context"].reverse()
def _m_self_report(fx): fx["grader"] = _SELF_REPORT
def _m_no_read(fx): fx["grader"] = _NO_READ
def _m_open_pool(fx): fx["grader"] = 'import json\nprint(json.dumps({"grade": "pass"}))\n'
def _m_always(fx): fx["grader"] = 'import json\nprint(json.dumps({"grade": "current"}))\n'
def _m_crash(fx): fx["grader"] = "raise RuntimeError('boom')\n"
def _m_llm(fx): fx["extra_py"]["judge.py"] = "import openai\n"
def _m_canary_stale(fx): fx["canary"]["items_sha256"] = "0" * 64
def _m_canary_missing(fx): fx["canary"]["entries"].pop()
def _m_canary_verdict(fx): fx["canary"]["entries"][0]["stale_use_marked"] = 0.9
def _m_control(fx): fx["canary"]["control"]["stale_use_marked"] = 0.5
def _m_inputs(fx): fx["manifest"]["inputs"] = [f"team/{INPUTS[1]}"]
def _m_prior(fx): fx["manifest"]["prior"] = "see earlier sprints"
def _m_badjson(fx): fx["raw"]["canary.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["items.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["grader.py"] = None
def _m_receipts(fx): fx["raw"] = {n: "{}\n" for n in FILES}


def _m_one_kind(fx):
    fx["items"].pop()
    fx["canary"]["entries"].pop()


def _m_void(fx):
    fx["canary"]["entries"][0].update(stale_use_marked=0.9, verdict="void")


def _m_not_injected(fx):
    fx["canary"]["entries"][0].update(
        injected_marker="(note)", marked_superseded_statement=fx["items"][0][
            "superseded_statement"] + " (note)")


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "statements worded differently": (_m_reworded, {"NOT-MARKER-FREE"}),
    "tense cue in the stale statement": (_m_tense, {"NOT-MARKER-FREE",
                                                   "MARKER-LINT"}),
    "the value itself says old": (_m_value_marker, {"MARKER-LINT"}),
    "the value carries a version": (_m_value_version, {"MARKER-LINT"}),
    "one value inside the other": (_m_overlap, {"VALUES-OVERLAP"}),
    "superseded statement not packed": (_m_not_retrievable,
                                        {"SUPERSEDED-NOT-RETRIEVABLE"}),
    "check returns the stale value": (_m_check_stale, {"CHECK-NOT-CURRENT"}),
    "directive names no retired path": (_m_directive, {"DIRECTIVE-MISSING",
                                                       "CANARY-NOT-INJECTED"}),
    "directive has no authorizer": (_m_anonymous, {"DIRECTIVE-MISSING"}),
    "only the checked-value item built": (_m_one_kind, {"KIND-MISSING"}),
    "current always packed first": (_m_order, {"ORDER-LEAKS-RECENCY"}),
    "grader trusts the final report": (_m_self_report,
                                       {"GRADER-TRUSTS-SELF-REPORT"}),
    "grader ignores the check read": (_m_no_read, {"GRADER-SKIPS-CHECK-READ"}),
    "grader outside the closed pool": (_m_open_pool, {"GRADER-OPEN-POOL"}),
    "grader always says current": (_m_always, {"GRADER-WRONG",
                                               "GRADER-TRUSTS-SELF-REPORT",
                                               "GRADER-SKIPS-CHECK-READ"}),
    "grader crashes": (_m_crash, {"GRADER-BROKEN"}),
    "a model judge beside the grader": (_m_llm, {"LLM-OR-NETWORK"}),
    "canary ran on other items": (_m_canary_stale, {"CANARY-STALE"}),
    "canary skips an item": (_m_canary_missing, {"CANARY-MISSING"}),
    "canary verdict against its rates": (_m_canary_verdict,
                                         {"CANARY-VERDICT-WRONG"}),
    "void item shipped": (_m_void, {"ITEM-VOID"}),
    "canary injected no marker": (_m_not_injected, {"CANARY-NOT-INJECTED"}),
    "canary control cannot move": (_m_control, {"CANARY-CANNOT-FAIL"}),
    "one design input not cited": (_m_inputs, {"INPUTS-NOT-CITED"}),
    "prior implied": (_m_prior, {"PRIOR-NOT-STATED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile items": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([sys.executable, __file__, str(_write(Path(td), fx))],
                               capture_output=True, text=True, timeout=300)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S9-1 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming", _fixture(), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: bool(got) and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, want)

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming build accepted; a receipts-only "
          f"directory and {len(_MUTANTS)} mutants each rejected by exactly "
          f"their own markers - a grader that trusts the final report and one "
          f"that ignores the check read among them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S9-1")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S9-1 gate findings: 1")
        raise SystemExit(1)
