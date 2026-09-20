#!/usr/bin/env python3
"""Gate for QUEUE row S8-7 (the door: score what the model was HANDED).

plumb-fable, row S8-7G, 2026-09-17. Written FROM ROW S8-7's TEXT ALONE, while
`team/S8-DOOR/` did not exist (and no S7-DOOR existed either). Read for this
gate: the board row and the candidate card the row names
(team/EXTERNAL-ADEBENCH-20260917.md). The interface below is declared by the
gate, not fitted to a document; every finding names what it wants.

This gate is an INSTRUMENT. It does not take the two numbers on trust: every
result row carries the exact text the adapter delivered into the prompt, and
the gate recomputes both numbers from that text against the frozen items.

Declared interface (ROOT = team/S8-DOOR)
  declaration.json  {declared_at (ISO), budget_chars (int > 0),
                    scoring: {presence: "all-helpful-substrings",
                              irrelevant_bytes: "delivered-minus-helpful"},
                    pressure: {tool_output_bytes: int > 0},
                    items_sha256, adapters: [names]}
                    It may not mention results in any way.
  items.jsonl       one item per line: {item_id, query, helpful_evidence:
                    [non-empty strings the model must be handed]}
  results.jsonl     one row per line, IN RUN ORDER: {ts (ISO), adapter,
                    condition: "normal" | "pressure", item_id, delivered_text
                    (the exact text handed to the prompt), competing_bytes
                    (0 under normal; >= declared under pressure),
                    declaration_sha256}
  verdict.json      {finding, prior (states none exists), card (names the
                    ADEBench card), budget_chars,
                    per_adapter: {adapter: {normal: N, pressure: N}}}
                    N = {helpful_evidence_presence (0..1),
                         irrelevant_delivered_bytes (mean)} and NOTHING that
                    blends them.

The scoring, fixed here so it can be recomputed:
  presence          1 for an item when every helpful string appears in the
                    delivered text (whitespace collapsed, case-blind), else 0;
                    reported as the mean over items.
  irrelevant bytes  UTF-8 bytes of the delivered text minus the bytes of each
                    helpful string counted ONCE; a repeated chunk is
                    irrelevant, which is the card's own finding. Mean over
                    items.

What the row turns on (marker in brackets)
  (a) Declared BEFORE the results. declared_at precedes every result row
      [DECLARED-AFTER-RESULTS]; the declaration text nowhere references
      results [DECLARATION-REFERENCES-RESULTS]; every result row embeds the
      sha256 of the declaration bytes, so a budget or rule moved afterwards
      breaks the chain [RESULTS-NOT-BOUND]; budget, scoring and pressure are
      all declared [BUDGET-UNDECLARED] [SCORING-UNDECLARED]
      [PRESSURE-UNDECLARED]; the items are frozen [ITEMS-NOT-FROZEN].
  (b) TWO numbers, SEPARATELY. Each adapter-condition cell carries both
      [NUMBER-MISSING] and no blended, combined, overall or scored figure
      [BLENDED-SCORE]; each equals the recomputation [NUMBERS-DISAGREE];
      verdict budget equals the declared one [BUDGET-MISMATCH].
  (c) BOTH conditions. Every adapter is measured under `normal` AND
      `pressure` on every item [CONDITION-MISSING] [ARM-INCOMPLETE]; pressure
      rows carry competing bytes at least the declared amount and normal rows
      none [PRESSURE-NOT-APPLIED]; at least one adapter [NO-ADAPTER] and 5
      items [TOO-FEW-ITEMS].
  (d) The budget BINDS: no delivered text exceeds it [BUDGET-EXCEEDED].
  (e) No prior implied [PRIOR-NOT-STATED]; the card named [CARD-NOT-CITED];
      no upstream number or winner imported [SCORE-IMPORTED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA]

Limits, stated on purpose: delivered_text and competing_bytes are what the
harness wrote down; the gate cannot see the prompt itself. Whether the helpful
strings are the RIGHT evidence for each query stays with the named verifier.
Timestamps are self-reported and a hash chain can be rebuilt by someone who
sets out to.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S8-7 gate findings: N`, never a traceback.

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
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = "EXTERNAL-ADEBENCH-20260917.md"
FILES = ("declaration.json", "items.jsonl", "results.jsonl", "verdict.json")
CONDITIONS = ("normal", "pressure")
PRESENCE, BYTES = "helpful_evidence_presence", "irrelevant_delivered_bytes"
SCORING = {"presence": "all-helpful-substrings",
           "irrelevant_bytes": "delivered-minus-helpful"}
MIN_ITEMS = 5
BLEND = re.compile(r"score|overall|blend|combin|composite|total|index|rank|"
                   r"grade", re.I)
NO_PRIOR = re.compile(r"none exists?|no prior|no previous|never (been )?"
                      r"measured|first measurement", re.I)
IMPORTED = re.compile(r"\b(gbrain|ade ?brain)\b[^.\n]{0,60}\d"
                      r"|\d[^.\n]{0,60}\b(gbrain|ade ?brain)\b|\bwinner\b", re.I)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ts(v):
    if not isinstance(v, str):
        return None
    try:
        t = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def score(delivered: str, helpful: list[str]) -> tuple[int, int]:
    """(presence 0/1, irrelevant bytes) for one delivered text."""
    d = _norm(delivered)
    matched = [h for h in helpful if _norm(h) in d]
    irrelevant = len(delivered.encode("utf-8")) - sum(
        len(h.encode("utf-8")) for h in matched)
    return int(len(matched) == len(helpful)), max(irrelevant, 0)


def _cell(items: dict, rows: dict) -> dict:
    p, b = zip(*(score(rows[i], items[i]) for i in items))
    return {PRESENCE: sum(p) / len(p), BYTES: sum(b) / len(b)}


def _schema(decl, items, rows, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if _ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    if not (_int(decl.get("budget_chars")) and decl["budget_chars"] > 0):
        f.append(("BUDGET-UNDECLARED", "declaration.json needs budget_chars: "
                  "a whole number > 0, the door size, fixed before the run"))
    if decl.get("scoring") != SCORING:
        f.append(("SCORING-UNDECLARED", f"declaration.json needs scoring: "
                  f"{json.dumps(SCORING)}, the two rules this gate recomputes, "
                  f"fixed before the run"))
    pr = decl.get("pressure")
    if not (isinstance(pr, dict) and _int(pr.get("tool_output_bytes"))
            and pr["tool_output_bytes"] > 0):
        f.append(("PRESSURE-UNDECLARED", "declaration.json needs pressure: "
                  "{tool_output_bytes: whole number > 0}, the competing "
                  "tool-output load, fixed before the run"))
    if not isinstance(decl.get("items_sha256"), str):
        f.append(("SCHEMA", "declaration.json needs items_sha256"))
    if not (isinstance(decl.get("adapters"), list) and decl["adapters"]
            and all(isinstance(a, str) for a in decl["adapters"])):
        f.append(("NO-ADAPTER", "declaration.json needs adapters: [at least "
                  "one memory adapter name]"))

    ok = isinstance(items, list) and items and all(
        isinstance(i, dict) and isinstance(i.get("item_id"), str)
        and isinstance(i.get("helpful_evidence"), list) and i["helpful_evidence"]
        and all(isinstance(h, str) and h.strip() for h in i["helpful_evidence"])
        for i in items)
    if not ok or len({i["item_id"] for i in items}) != len(items):
        f.append(("SCHEMA", "items.jsonl needs one {item_id, query, "
                  "helpful_evidence: [non-empty strings]} per line, item_id "
                  "unique"))

    if not isinstance(rows, list) or not rows:
        f.append(("SCHEMA", "results.jsonl has no rows"))
    else:
        for n, r in enumerate(rows, 1):
            if not (isinstance(r, dict) and _ts(r.get("ts"))
                    and isinstance(r.get("adapter"), str)
                    and r.get("condition") in CONDITIONS
                    and isinstance(r.get("item_id"), str)
                    and isinstance(r.get("delivered_text"), str)
                    and _int(r.get("competing_bytes"))
                    and isinstance(r.get("declaration_sha256"), str)):
                f.append(("SCHEMA", f"results.jsonl row {n} needs ts, adapter, "
                          "condition (normal | pressure), item_id, "
                          "delivered_text, competing_bytes, "
                          "declaration_sha256"))
                break

    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if not isinstance(verdict.get("per_adapter"), dict):
        f.append(("SCHEMA", "verdict.json needs per_adapter: {adapter: "
                  "{normal: {...}, pressure: {...}}}"))
    if not isinstance(verdict.get("finding"), str) \
            or len(verdict["finding"].strip()) < 20:
        f.append(("SCHEMA", "verdict.json needs finding: one sentence"))
    return f


def check(root: Path) -> tuple[list[tuple[str, str]], str]:
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = _load(root / "declaration.json")
        items_list = _load(root / "items.jsonl", lines=True)
        rows = _load(root / "results.jsonl", lines=True)
        verdict = _load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(decl, items_list, rows, verdict)
    if f:
        return f, ""

    # (a) declared before the results
    decl_text = (root / "declaration.json").read_text(encoding="utf-8",
                                                      errors="replace")
    if re.search(r"result", decl_text, re.I):
        f.append(("DECLARATION-REFERENCES-RESULTS", "declaration.json mentions "
                  "results; a declaration written before the run has nothing "
                  "to say about them"))
    sha = _sha(root / "declaration.json")
    unbound = sum(1 for r in rows if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RESULTS-NOT-BOUND", f"{unbound} of {len(rows)} result rows "
                  f"do not carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]}): the declaration changed after the run, or "
                  f"the run never read it"))
    first = min(_ts(r["ts"]) for r in rows)
    if _ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RESULTS", f"declared_at {decl['declared_at']} "
                  f"is not before the first result {first.isoformat()}"))
    if decl["items_sha256"] != _sha(root / "items.jsonl"):
        f.append(("ITEMS-NOT-FROZEN", "items_sha256 is not the sha256 of "
                  "items.jsonl: the items or their helpful evidence changed "
                  "after they were declared"))
    items = {i["item_id"]: i["helpful_evidence"] for i in items_list}
    if len(items) < MIN_ITEMS:
        f.append(("TOO-FEW-ITEMS", f"{len(items)} items; the gate needs at "
                  f"least {MIN_ITEMS}"))

    # (c) both conditions, every adapter, every item
    budget, load = decl["budget_chars"], decl["pressure"]["tool_output_bytes"]
    adapters = list(decl["adapters"])
    stray = sorted({r["adapter"] for r in rows} - set(adapters))
    if stray:
        f.append(("NO-ADAPTER", f"result rows for adapters not declared: "
                  f"{', '.join(stray)}"))
    got: dict[tuple[str, str], dict] = {}
    for a in adapters:
        for c in CONDITIONS:
            mine = [r for r in rows if r["adapter"] == a and r["condition"] == c]
            if not mine:
                f.append(("CONDITION-MISSING", f"`{a}` has no `{c}` rows; the "
                          f"row asks for normal AND under-pressure, not the "
                          f"easy one alone"))
                continue
            seen = Counter(r["item_id"] for r in mine)
            if set(seen) != set(items) or max(seen.values()) > 1:
                f.append(("ARM-INCOMPLETE", f"`{a}`/{c} must hold each of the "
                          f"{len(items)} items exactly once"))
                continue
            got[(a, c)] = {r["item_id"]: r["delivered_text"] for r in mine}
            wrong = [r["item_id"] for r in mine if (
                r["competing_bytes"] < load if c == "pressure"
                else r["competing_bytes"] != 0)]
            if wrong:
                f.append(("PRESSURE-NOT-APPLIED", f"`{a}`/{c}: competing_bytes "
                          f"must be >= {load} under pressure and 0 under "
                          f"normal; wrong on {', '.join(wrong[:4])}"))
            over = [r["item_id"] for r in mine if len(r["delivered_text"]) > budget]
            if over:
                f.append(("BUDGET-EXCEEDED", f"`{a}`/{c}: delivered text over "
                          f"the declared {budget}-character budget on "
                          f"{', '.join(over[:4])}; the budget did not bind"))

    # (b) two numbers, separately, as recomputed
    if verdict.get("budget_chars") != budget:
        f.append(("BUDGET-MISMATCH", f"verdict.json budget_chars must be the "
                  f"declared {budget}"))
    said = verdict["per_adapter"]
    if sorted(said) != sorted(adapters):
        f.append(("NUMBERS-DISAGREE", f"verdict.json per_adapter must hold "
                  f"exactly the declared adapters: {', '.join(adapters)}"))
    for a in adapters:
        cells = said.get(a) if isinstance(said.get(a), dict) else {}
        blended = sorted(k for k in cells if BLEND.search(str(k))) + sorted(
            f"{c}.{k}" for c in CONDITIONS if isinstance(cells.get(c), dict)
            for k in cells[c] if BLEND.search(str(k)))
        if blended:
            f.append(("BLENDED-SCORE", f"`{a}`: {', '.join(blended)} - a single "
                      f"figure hides which of the two numbers moved; report "
                      f"{PRESENCE} and {BYTES} and nothing that blends them"))
        for c in CONDITIONS:
            cell = cells.get(c)
            if not isinstance(cell, dict) or not (_num(cell.get(PRESENCE))
                                                  and _num(cell.get(BYTES))):
                f.append(("NUMBER-MISSING", f"`{a}`/{c}: needs BOTH {PRESENCE} "
                          f"and {BYTES}, each its own number"))
                continue
            if (a, c) not in got:
                continue
            real = _cell(items, got[(a, c)])
            if abs(cell[PRESENCE] - real[PRESENCE]) >= 0.0006 or abs(
                    cell[BYTES] - real[BYTES]) >= 0.5:
                f.append(("NUMBERS-DISAGREE", f"`{a}`/{c}: reported "
                          f"{cell[PRESENCE]:.3f} / {cell[BYTES]:.1f}; "
                          f"recomputed from delivered_text "
                          f"{real[PRESENCE]:.3f} / {real[BYTES]:.1f}"))

    # (e) prior, card, no import
    if not NO_PRIOR.search(str(verdict.get("prior", ""))):
        f.append(("PRIOR-NOT-STATED", "verdict.json needs prior, saying in "
                  "words that no prior measurement of this exists"))
    if CARD not in str(verdict.get("card", "")):
        f.append(("CARD-NOT-CITED", f"verdict.json needs card, naming "
                  f"team/{CARD}"))
    prose = " ".join(str(v) for k, v in verdict.items()
                     if isinstance(v, str) and k != "card")
    hit = IMPORTED.search(prose)
    if hit:
        f.append(("SCORE-IMPORTED", f"verdict.json carries an upstream number "
                  f"or winner ({hit.group(0)!r}); the card says its ranking "
                  f"is not evidence"))
    return f, (f"{len(adapters)} adapters x 2 conditions x {len(items)} items, "
               f"budget {budget} chars, both numbers recomputed from the "
               f"delivered text")


def run(root: Path) -> int:
    findings, summary = check(root)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S8-7 gate findings: {len(findings)}")
        return 1
    print(f"S8-7 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)
_ITEMS = [{"item_id": f"d{i}", "query": f"question {i}",
           "helpful_evidence": [f"the port for tenant {i} is {6000 + i}"]}
          for i in range(6)]
_FILL = "unrelated note about lunch. "


def _fixture() -> dict:
    """bm25 hands the evidence with a little filler; pi_lcm hands it under
    normal load and drops it under pressure, with more filler."""
    def text(adapter, cond, item):
        ev = item["helpful_evidence"][0]
        if adapter == "pi_lcm" and cond == "pressure":
            return _FILL * 6
        return ev + " " + _FILL * (2 if adapter == "bm25" else 4)
    return {
        "decl": {"declared_at": _T0.isoformat(), "budget_chars": 400,
                 "scoring": dict(SCORING),
                 "pressure": {"tool_output_bytes": 20000},
                 "items_sha256": "AUTO", "adapters": ["bm25", "pi_lcm"]},
        "items": [dict(i) for i in _ITEMS],
        "text": text, "raw": {}, "after_run": None, "drop_last": False,
        "conditions": list(CONDITIONS),
        "verdict": {"finding": "pi_lcm keeps the evidence under normal load "
                               "and loses it under tool-output pressure.",
                    "prior": "none exists: this is the first door measurement",
                    "card": f"team/{CARD}", "budget_chars": 400,
                    "per_adapter": "AUTO"},
    }


def _write(td: Path, fx: dict) -> Path:
    root = td / "S8-DOOR"
    root.mkdir()
    (root / "items.jsonl").write_text(
        "".join(json.dumps(i) + "\n" for i in fx["items"]))
    decl = fx["decl"]
    if decl.get("items_sha256") == "AUTO":
        decl["items_sha256"] = _sha(root / "items.jsonl")
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = _sha(root / "declaration.json")
    out, n, per = [], 0, {}
    for a in decl.get("adapters", []):
        per[a] = {}
        for c in fx["conditions"]:
            cell = {}
            for item in fx["items"]:
                n += 1
                t = fx["text"](a, c, item)
                cell[item["item_id"]] = t
                out.append(json.dumps({
                    "ts": (_T0 + timedelta(seconds=n)).isoformat(),
                    "adapter": a, "condition": c, "item_id": item["item_id"],
                    "delivered_text": t,
                    "competing_bytes": 20000 if c == "pressure" else 0,
                    "declaration_sha256": sha}) + "\n")
            per[a][c] = _cell({i["item_id"]: i["helpful_evidence"]
                               for i in fx["items"]}, cell)
    (root / "results.jsonl").write_text("".join(out[:-1] if fx["drop_last"]
                                                else out))
    v = fx["verdict"]
    if v.get("per_adapter") == "AUTO":
        v["per_adapter"] = per
    (root / "verdict.json").write_text(json.dumps(v))
    if fx["after_run"]:
        fx["after_run"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root


def _after_note(root, decl):  # any edit after the run breaks the chain
    decl["note"] = "budget confirmed adequate"
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _after_items(root, decl):  # evidence relaxed once the numbers were seen
    p = root / "items.jsonl"
    p.write_text(p.read_text().replace("is 6005", "is"))


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_refs(fx): fx["decl"]["note"] = "budget chosen to match results.jsonl"
def _m_edit(fx): fx["after_run"] = _after_note
def _m_items(fx): fx["after_run"] = _after_items
def _m_nobudget(fx): del fx["decl"]["budget_chars"]
def _m_scoring(fx): fx["decl"]["scoring"] = {"presence": "judged by a model"}
def _m_nopressure(fx): del fx["decl"]["pressure"]
def _m_noadapter(fx): fx["decl"]["adapters"] = []
def _m_few(fx): fx["items"] = fx["items"][:3]
def _m_easy_only(fx): fx["conditions"] = ["normal"]
def _m_dropped(fx): fx["drop_last"] = True
def _m_budget_mismatch(fx): fx["verdict"]["budget_chars"] = 2400
def _m_prior(fx): fx["verdict"]["prior"] = "consistent with earlier runs"
def _m_card(fx): fx["verdict"]["card"] = "the intel feed"
def _m_import(fx): fx["verdict"]["finding"] += " gbrain reached 0.91 upstream."
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["items.jsonl"] = None


def _m_pressure_unapplied(fx):
    fx["after_run"] = lambda root, decl: (root / "results.jsonl").write_text(
        (root / "results.jsonl").read_text().replace('"competing_bytes": 20000',
                                                     '"competing_bytes": 0'))


def _m_over_budget(fx):
    base = fx["text"]
    fx["text"] = lambda a, c, i: base(a, c, i) + _FILL * 20


def _m_blended(fx):
    fx["after_run"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                                ["bm25"]["normal"].update(
                                                    door_score=0.83))


def _m_single_score(fx):
    fx["after_run"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                                .update(bm25={
                                                    "normal": {"door_score": 0.9},
                                                    "pressure": {"door_score": 0.7}}))


def _m_presence_only(fx):
    fx["after_run"] = lambda root, decl: _patch(root, lambda v: [
        cell.pop(BYTES) for a in v["per_adapter"].values() for cell in a.values()])


def _m_numbers(fx):
    fx["after_run"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                                ["pi_lcm"]["pressure"].update(
                                                    {PRESENCE: 1.0}))


def _m_receipts(fx):
    fx["raw"] = {n: "{}\n" for n in FILES}


def _patch(root, fn):
    p = root / "verdict.json"
    v = json.loads(p.read_text())
    fn(v)
    p.write_text(json.dumps(v))


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "declaration references results": (_m_refs,
                                       {"DECLARATION-REFERENCES-RESULTS"}),
    "declaration edited after the run": (_m_edit, {"RESULTS-NOT-BOUND"}),
    "evidence relaxed after the run": (_m_items, {"ITEMS-NOT-FROZEN",
                                                  "NUMBERS-DISAGREE"}),
    "no budget": (_m_nobudget, {"BUDGET-UNDECLARED"}),
    "scoring not the declared rules": (_m_scoring, {"SCORING-UNDECLARED"}),
    "pressure undeclared": (_m_nopressure, {"PRESSURE-UNDECLARED"}),
    "no adapter": (_m_noadapter, {"NO-ADAPTER", "SCHEMA"}),
    "three items": (_m_few, {"TOO-FEW-ITEMS"}),
    "only the easy condition": (_m_easy_only, {"CONDITION-MISSING",
                                               "NUMBER-MISSING"}),
    "a row dropped": (_m_dropped, {"ARM-INCOMPLETE"}),
    "pressure rows without load": (_m_pressure_unapplied,
                                   {"PRESSURE-NOT-APPLIED"}),
    "budget did not bind": (_m_over_budget, {"BUDGET-EXCEEDED"}),
    "verdict budget differs": (_m_budget_mismatch, {"BUDGET-MISMATCH"}),
    "a blended score beside the two": (_m_blended, {"BLENDED-SCORE"}),
    "a single blended score instead": (_m_single_score, {"BLENDED-SCORE",
                                                         "NUMBER-MISSING"}),
    "presence only": (_m_presence_only, {"NUMBER-MISSING"}),
    "numbers wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "prior implied": (_m_prior, {"PRIOR-NOT-STATED"}),
    "card not cited": (_m_card, {"CARD-NOT-CITED"}),
    "upstream number imported": (_m_import, {"SCORE-IMPORTED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([sys.executable, __file__, str(_write(Path(td), fx))],
                               capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S8-7 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming", _fixture(), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, want)
    # the scorer itself: a repeated chunk is irrelevant, a paraphrase is absent
    p, b = score("The PORT for tenant 1 is 6001. the port for tenant 1 is 6001.",
                 ["the port for tenant 1 is 6001"])
    if (p, b) != (1, 32):
        bad.append(f"scorer: repeated chunk gave {(p, b)}, expected (1, 32)")
    if score("tenant 1 listens on 6001", ["the port for tenant 1 is 6001"])[0]:
        bad.append("scorer: a paraphrase counted as present")

    for b_ in bad:
        print(f"selftest FAIL: {b_}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming run accepted; a receipts-only "
          f"directory and {len(_MUTANTS)} mutants each rejected by exactly "
          f"their own markers - an easy-only run, a blended score and a "
          f"post-run declaration among them; scorer checked; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S8-7")
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
        print("S8-7 gate findings: 1")
        raise SystemExit(1)
