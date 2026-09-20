#!/usr/bin/env python3
"""Gate for QUEUE row S10-1 (door rung 2: a harsher, query-adjacent pressure
load on the same five frozen items and adapters).

plumb-fable, row S10-1G, 2026-09-18. Written FROM ROW S10-1's TEXT ALONE, while
`team/S9-DOOR-RUNG2/` did not exist. Read for this gate: the board row, and of
the verified rung-1 prior (team/S8-DOOR) only its key names and declared
parameters. The interface below is declared by the gate, not fitted to a
document; every finding names what it wants.

The row reuses the S8-DOOR harness, gate and declaration machinery, and so does
this gate: the two scoring rules are IMPORTED from team/S8-DOOR/check.py, so
old and new are scored by one definition and cannot drift apart.

This gate is an INSTRUMENT. It recomputes both numbers from the delivered
text, re-derives whether the load ever REACHED the door, re-checks the
no-helpful-evidence assertion on every chunk, and reads the rung-1 cells from
the prior itself rather than from the new verdict's account of them.

Declared interface (ROOT = team/S9-DOOR-RUNG2, PRIOR = team/S8-DOOR)
  declaration.json       as rung 1: {declared_at, budget_chars, scoring,
                         items_sha256, adapters} and pressure:
                         {tool_output_bytes, chunks_sha256}. It may not
                         mention results in any way.
  items.jsonl            the rung-1 file, byte for byte
  pressure_chunks.jsonl  the declared load, one line per item:
                         {item_id, chunks: [text]}
  results.jsonl          as rung 1: {ts, adapter, condition, item_id,
                         delivered_text, competing_bytes, declaration_sha256}
  verdict.json           {finding, prior (names PRIOR's verdict.json or
                         results.jsonl), budget_chars, per_adapter: {adapter:
                         {rung1: {normal: N, pressure: N},
                          rung2: {normal: N, pressure: N},
                          load_reached_door: items (0..n)}}}
                         N = the two rung-1 numbers, nothing blended.

What the row turns on (marker in brackets)
  (a) ONLY THE LOAD CHANGES. Items are the rung-1 bytes, adapters, budget and
      scoring are rung 1's [ONLY-THE-LOAD-MAY-CHANGE]; the unloaded condition
      reproduces rung 1's `normal` cells, or the harness moved
      [NORMAL-NOT-REPRODUCED].
  (b) The load is HARSHER and QUERY-ADJACENT, and declared before any run.
      Every item has chunks [LOAD-INCOMPLETE]; every chunk shares vocabulary
      with its item's query [LOAD-NOT-QUERY-ADJACENT]; no chunk carries any
      item's helpful evidence - the pre-run assertion, recomputed
      [LOAD-CARRIES-EVIDENCE]; the declared bytes are not below rung 1's
      [LOAD-NOT-HARSHER]; the declaration pins the chunk file
      [LOAD-NOT-FROZEN]; declared_at precedes every result
      [DECLARED-AFTER-RESULTS]; the declaration says nothing of results
      [DECLARATION-REFERENCES-RESULTS]; every row embeds its sha256
      [RESULTS-NOT-BOUND].
  (c) DID IT REACH THE DOOR. Rung 1 held because no tool chunk reached any
      top-k. The gate re-derives, per adapter, on how many items a piece of
      the load appears in the delivered text [REACH-DISAGREE]; where that is
      zero the finding must say the load never reached the door, so "held" is
      not read as "pressure never matters" [NEVER-REACHED-UNSAID].
  (d) OLD VS NEW, SIDE BY SIDE. rung1 cells equal PRIOR's verdict
      [PRIOR-MISQUOTED], the prior is named [PRIOR-NOT-CITED]; rung2 cells
      equal the recomputation [NUMBERS-DISAGREE]; both numbers in every cell
      [NUMBER-MISSING], nothing blended [BLENDED-SCORE].
  (e) As rung 1: both conditions for every adapter and item
      [CONDITION-MISSING] [ARM-INCOMPLETE]; load applied under pressure and
      absent under normal [PRESSURE-NOT-APPLIED]; the budget binds
      [BUDGET-EXCEEDED].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [PRIOR-UNREADABLE]
         [S8-GATE-UNREADABLE]

Limits, stated on purpose: delivered_text and competing_bytes are what the
harness wrote down. "Shares vocabulary" is two query words of four letters or
more (all of them when the query has fewer); whether the chunks compete HARD
ENOUGH stays with the named verifier. Reach is detected by 40-character
windows of a chunk in the delivered text, so a chunk rewritten by a summariser
would not be seen.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S10-1 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--prior DIR] [--s8-gate FILE]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "S8-DOOR"
FILES = ("declaration.json", "items.jsonl", "pressure_chunks.jsonl",
         "results.jsonl", "verdict.json")
STOP = {"what", "which", "when", "where", "does", "that", "this", "with",
        "from", "have", "will", "should", "would", "there", "their", "about"}
WINDOW = 40
NEVER = re.compile(r"(never|not|n't|no chunk)[^.]{0,40}reach", re.I)


def _s8(path: Path):
    spec = importlib.util.spec_from_file_location("_s8_door_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _words(text: str) -> set:
    return set(re.findall(r"[a-z0-9][a-z0-9-]{3,}", text.lower())) - STOP


def _reached(s8, chunks: list[str], delivered: str) -> bool:
    d = s8._norm(delivered)
    for c in chunks:
        n = s8._norm(c)
        if any(n[i:i + WINDOW] in d for i in
               range(0, max(len(n) - WINDOW, 0) + 1, WINDOW // 2)):
            return True
    return False


def _cells_ok(s8, cell) -> bool:
    return isinstance(cell, dict) and s8._num(cell.get(s8.PRESENCE)) \
        and s8._num(cell.get(s8.BYTES))


def _same(s8, a: dict, b: dict) -> bool:
    return abs(a[s8.PRESENCE] - b[s8.PRESENCE]) < 0.0006 \
        and abs(a[s8.BYTES] - b[s8.BYTES]) < 0.5


def _schema(s8, decl, items, chunks, rows, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    pr = decl.get("pressure") if isinstance(decl, dict) else None
    if not (isinstance(decl, dict) and s8._ts(decl.get("declared_at"))
            and s8._int(decl.get("budget_chars"))
            and isinstance(decl.get("scoring"), dict)
            and isinstance(decl.get("items_sha256"), str)
            and isinstance(decl.get("adapters"), list) and decl["adapters"]
            and isinstance(pr, dict) and s8._int(pr.get("tool_output_bytes"))
            and isinstance(pr.get("chunks_sha256"), str)):
        f.append(("SCHEMA", "declaration.json needs declared_at, budget_chars, "
                  "scoring, items_sha256, adapters and pressure: "
                  "{tool_output_bytes, chunks_sha256}"))
    if not (isinstance(items, list) and items and all(
            isinstance(i, dict) and isinstance(i.get("item_id"), str)
            and isinstance(i.get("query"), str)
            and isinstance(i.get("helpful_evidence"), list)
            and all(isinstance(h, str) for h in i["helpful_evidence"])
            for i in items)):
        f.append(("SCHEMA", "items.jsonl needs {item_id, query, "
                  "helpful_evidence: [strings]} per line"))
    if not (isinstance(chunks, list) and all(
            isinstance(c, dict) and isinstance(c.get("item_id"), str)
            and isinstance(c.get("chunks"), list)
            and all(isinstance(t, str) for t in c["chunks"]) for c in chunks)):
        f.append(("SCHEMA", "pressure_chunks.jsonl needs {item_id, chunks: "
                  "[strings]} per line"))
    if not isinstance(rows, list) or not rows or not all(
            isinstance(r, dict) and s8._ts(r.get("ts"))
            and isinstance(r.get("adapter"), str)
            and r.get("condition") in s8.CONDITIONS
            and isinstance(r.get("item_id"), str)
            and isinstance(r.get("delivered_text"), str)
            and s8._int(r.get("competing_bytes"))
            and isinstance(r.get("declaration_sha256"), str) for r in rows):
        f.append(("SCHEMA", "results.jsonl rows need ts, adapter, condition "
                  "(normal | pressure), item_id, delivered_text, "
                  "competing_bytes, declaration_sha256"))
    if not (isinstance(verdict, dict)
            and isinstance(verdict.get("per_adapter"), dict)
            and isinstance(verdict.get("finding"), str)
            and len(verdict["finding"].strip()) >= 20):
        f.append(("SCHEMA", "verdict.json needs finding (a sentence) and "
                  "per_adapter: {adapter: {rung1, rung2, load_reached_door}}"))
    return f


def check(root: Path, prior: Path, s8_gate: Path) -> tuple[list, str]:
    try:
        s8 = _s8(s8_gate)
        s8.score, s8._cell, s8.BLEND, s8.SCORING  # the machinery reused
    except Exception as e:
        return [("S8-GATE-UNREADABLE", f"{s8_gate}: {type(e).__name__}: {e}")], ""
    try:
        p_decl = s8._load(prior / "declaration.json")
        p_cells = s8._load(prior / "verdict.json")["per_adapter"]
        p_items_sha = s8._sha(prior / "items.jsonl")
        p_load = p_decl["pressure"]["tool_output_bytes"]
        if not all(_cells_ok(s8, p_cells[a][c]) for a in p_decl["adapters"]
                   for c in s8.CONDITIONS):
            raise ValueError("prior verdict cells incomplete")
    except Exception as e:
        return [("PRIOR-UNREADABLE", f"{prior}: {type(e).__name__}: {e}")], ""
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = s8._load(root / "declaration.json")
        item_list = s8._load(root / "items.jsonl", lines=True)
        chunk_list = s8._load(root / "pressure_chunks.jsonl", lines=True)
        rows = s8._load(root / "results.jsonl", lines=True)
        verdict = s8._load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(s8, decl, item_list, chunk_list, rows, verdict)
    if f:
        return f, ""

    # (a) only the load changes
    same = {"items": s8._sha(root / "items.jsonl") == p_items_sha
            and decl["items_sha256"] == p_items_sha,
            "adapters": decl["adapters"] == p_decl["adapters"],
            "budget_chars": decl["budget_chars"] == p_decl["budget_chars"],
            "scoring": decl["scoring"] == p_decl["scoring"] == s8.SCORING}
    moved = [k for k, ok in same.items() if not ok]
    if moved:
        f.append(("ONLY-THE-LOAD-MAY-CHANGE", f"differs from rung 1 "
                  f"({prior.name}): {', '.join(moved)}. The row re-measures "
                  f"exactly those cells; only the pressure load is new"))

    # (b) the load: declared, frozen, harsher, adjacent, evidence-free
    decl_text = (root / "declaration.json").read_text(encoding="utf-8",
                                                      errors="replace")
    if re.search(r"result", decl_text, re.I):
        f.append(("DECLARATION-REFERENCES-RESULTS", "declaration.json mentions "
                  "results; a declaration written before the run has nothing "
                  "to say about them"))
    sha = s8._sha(root / "declaration.json")
    unbound = sum(1 for r in rows if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RESULTS-NOT-BOUND", f"{unbound} of {len(rows)} result rows "
                  f"do not carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]})"))
    first = min(s8._ts(r["ts"]) for r in rows)
    if s8._ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RESULTS", f"declared_at {decl['declared_at']} "
                  f"is not before the first result {first.isoformat()}"))
    load = decl["pressure"]["tool_output_bytes"]
    if decl["pressure"]["chunks_sha256"] != s8._sha(root / "pressure_chunks.jsonl"):
        f.append(("LOAD-NOT-FROZEN", "pressure.chunks_sha256 is not the sha256 "
                  "of pressure_chunks.jsonl: the load changed after it was "
                  "declared"))
    if load < p_load:
        f.append(("LOAD-NOT-HARSHER", f"declared load {load} bytes is below "
                  f"rung 1's {p_load}"))
    items = {i["item_id"]: i for i in item_list}
    chunks = {c["item_id"]: [t for t in c["chunks"] if t.strip()]
              for c in chunk_list}
    bare = sorted(i for i in items if not chunks.get(i))
    if bare:
        f.append(("LOAD-INCOMPLETE", f"no pressure chunks for: {', '.join(bare)}"))
    evidence = [s8._norm(h) for i in items.values() for h in i["helpful_evidence"]
                if h.strip()]
    far, leaky = [], []
    for iid, texts in chunks.items():
        q = _words(items[iid]["query"]) if iid in items else set()
        need = min(2, len(q))
        for n, t in enumerate(texts):
            if iid in items and len(q & _words(t)) < need:
                far.append(f"{iid}#{n}")
            if any(h in s8._norm(t) for h in evidence):
                leaky.append(f"{iid}#{n}")
    if far:
        f.append(("LOAD-NOT-QUERY-ADJACENT", f"{len(far)} chunk(s) share fewer "
                  f"than two words with their item's query "
                  f"({', '.join(far[:5])}); rung 1's load never competed for "
                  f"relevance, which is what rung 2 is for"))
    if leaky:
        f.append(("LOAD-CARRIES-EVIDENCE", f"{len(leaky)} chunk(s) contain "
                  f"helpful evidence ({', '.join(leaky[:5])}); the load must "
                  f"compete, not help"))

    # (e) both conditions, every adapter and item
    budget = decl["budget_chars"]
    adapters = [a for a in decl["adapters"] if isinstance(a, str)]
    got: dict[tuple[str, str], dict] = {}
    for a in adapters:
        for c in s8.CONDITIONS:
            mine = [r for r in rows if r["adapter"] == a and r["condition"] == c]
            if not mine:
                f.append(("CONDITION-MISSING", f"`{a}` has no `{c}` rows"))
                continue
            seen = Counter(r["item_id"] for r in mine)
            if set(seen) != set(items) or max(seen.values()) > 1:
                f.append(("ARM-INCOMPLETE", f"`{a}`/{c} must hold each of the "
                          f"{len(items)} items exactly once"))
                continue
            got[(a, c)] = {r["item_id"]: r["delivered_text"] for r in mine}
            if any(r["competing_bytes"] < load if c == "pressure"
                   else r["competing_bytes"] != 0 for r in mine):
                f.append(("PRESSURE-NOT-APPLIED", f"`{a}`/{c}: competing_bytes "
                          f"must be >= {load} under pressure and 0 under normal"))
            if any(len(r["delivered_text"]) > budget for r in mine):
                f.append(("BUDGET-EXCEEDED", f"`{a}`/{c}: delivered text over "
                          f"the declared {budget}-character budget"))

    # (a) (c) (d) the cells, the reach, old against new
    helpful = {i: items[i]["helpful_evidence"] for i in items}
    if not re.search(rf"{re.escape(prior.name)}/(verdict\.json|results\.jsonl)",
                     json.dumps(verdict.get("prior", ""))):
        f.append(("PRIOR-NOT-CITED", f"verdict.json prior must name "
                  f"{prior.name}/verdict.json or {prior.name}/results.jsonl"))
    said = verdict["per_adapter"]
    if sorted(said) != sorted(adapters):
        f.append(("NUMBERS-DISAGREE", f"verdict.json per_adapter must hold "
                  f"exactly the declared adapters: {', '.join(adapters)}"))
    unreached = []
    for a in adapters:
        entry = said.get(a) if isinstance(said.get(a), dict) else {}
        blended = sorted(k for k in entry if s8.BLEND.search(str(k))) + sorted(
            f"{r}.{c}.{k}" for r in ("rung1", "rung2")
            if isinstance(entry.get(r), dict) for c in s8.CONDITIONS
            if isinstance(entry[r].get(c), dict) for k in entry[r][c]
            if s8.BLEND.search(str(k)))
        if blended:
            f.append(("BLENDED-SCORE", f"`{a}`: {', '.join(blended)} - report "
                      f"{s8.PRESENCE} and {s8.BYTES} and nothing that blends "
                      f"them"))
        for rung in ("rung1", "rung2"):
            for c in s8.CONDITIONS:
                cell = (entry.get(rung) or {}).get(c) \
                    if isinstance(entry.get(rung), dict) else None
                if not _cells_ok(s8, cell):
                    f.append(("NUMBER-MISSING", f"`{a}`.{rung}.{c}: needs BOTH "
                              f"{s8.PRESENCE} and {s8.BYTES}; old and new sit "
                              f"side by side"))
                elif rung == "rung1" and not _same(s8, cell, p_cells[a][c]) \
                        if a in p_cells else False:
                    f.append(("PRIOR-MISQUOTED", f"`{a}`.rung1.{c} is not the "
                              f"cell in {prior.name}/verdict.json"))
                elif rung == "rung2" and (a, c) in got and not _same(
                        s8, cell, s8._cell(helpful, got[(a, c)])):
                    real = s8._cell(helpful, got[(a, c)])
                    f.append(("NUMBERS-DISAGREE", f"`{a}`.rung2.{c}: recomputed "
                              f"{real[s8.PRESENCE]:.3f} / {real[s8.BYTES]:.1f}"))
        if (a, "normal") in got and a in p_cells and not _same(
                s8, s8._cell(helpful, got[(a, "normal")]), p_cells[a]["normal"]):
            f.append(("NORMAL-NOT-REPRODUCED", f"`{a}`: the unloaded condition "
                      f"does not reproduce rung 1's normal cell; a rung-2 "
                      f"change cannot then be put on the load"))
        if (a, "pressure") in got:
            reach = sum(1 for i in items if _reached(
                s8, chunks.get(i, []), got[(a, "pressure")][i]))
            if entry.get("load_reached_door") != reach:
                f.append(("REACH-DISAGREE", f"`{a}`: load_reached_door must be "
                          f"{reach}, the items where a piece of the load is in "
                          f"the delivered text"))
            if reach == 0:
                unreached.append(a)
    if unreached and not NEVER.search(verdict["finding"]):
        f.append(("NEVER-REACHED-UNSAID", f"the load reached the door on no "
                  f"item for {', '.join(unreached)}; the finding must say it "
                  f"never reached the door, so `held` is not read as "
                  f"`pressure never matters`"))
    return f, (f"{len(adapters)} adapters x 2 conditions x {len(items)} items; "
               f"load {load} bytes, query-adjacent, evidence-free; rung 1 and "
               f"rung 2 side by side")


def run(root: Path, prior: Path, s8_gate: Path) -> int:
    findings, summary = check(root, prior, s8_gate)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S10-1 gate findings: {len(findings)}")
        return 1
    print(f"S10-1 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 19, 17, 0, tzinfo=timezone.utc)
_ITEMS = [{"item_id": f"d{i}", "query": f"Which port does tenant{i} staging use?",
           "helpful_evidence": [f"tenant{i} staging listens on {6000 + i}"]}
          for i in range(5)]
_FILL = "lunch is at noon today. "


def _chunk(i: int) -> str:
    return (f"tool output: tenant{i} staging port scan finished with no "
            f"anomalies across the staging subnet, scan id {i}.")


def _fixture(s8) -> dict:
    """bm25 keeps the evidence and lets a load chunk in under pressure;
    quiet never sees the load at all."""
    def text(adapter, cond, item):
        n = int(item["item_id"][1:])
        ev = item["helpful_evidence"][0]
        if adapter == "bm25" and cond == "pressure":
            return ev + " " + _chunk(n)
        return ev + " " + _FILL
    items = [dict(i) for i in _ITEMS]
    helpful = {i["item_id"]: i["helpful_evidence"] for i in items}
    normal = s8._cell(helpful, {i["item_id"]: text("quiet", "normal", i)
                                for i in items})
    return {
        "s8": s8, "items": items, "text": text,
        "chunks": [{"item_id": i["item_id"],
                    "chunks": [_chunk(int(i["item_id"][1:]))]} for i in items],
        "p_decl": {"declared_at": "2026-09-17T00:00:00+00:00",
                   "budget_chars": 400, "scoring": dict(s8.SCORING),
                   "pressure": {"tool_output_bytes": 20000},
                   "items_sha256": "AUTO", "adapters": ["bm25", "quiet"]},
        "p_cells": {a: {"normal": dict(normal), "pressure": dict(normal)}
                    for a in ("bm25", "quiet")},
        "decl": {"declared_at": _T0.isoformat(), "budget_chars": 400,
                 "scoring": dict(s8.SCORING),
                 "pressure": {"tool_output_bytes": 40000, "chunks_sha256": "AUTO"},
                 "items_sha256": "AUTO", "adapters": ["bm25", "quiet"]},
        "conditions": list(s8.CONDITIONS), "drop_last": False, "raw": {},
        "after": None, "own_items": None,
        "verdict": {"finding": "under the query-adjacent load bm25 lets a tool "
                               "chunk through the door on every item; the load "
                               "never reached the door for quiet.",
                    "prior": "team/S8-DOOR/verdict.json", "budget_chars": 400,
                    "per_adapter": "AUTO"},
    }


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    s8 = fx["s8"]
    prior, root = td / "S8-DOOR", td / "S9-DOOR-RUNG2"
    prior.mkdir()
    root.mkdir()
    lines = "".join(json.dumps(i) + "\n" for i in _ITEMS)
    (prior / "items.jsonl").write_text(lines)
    fx["p_decl"]["items_sha256"] = s8._sha(prior / "items.jsonl")
    (prior / "declaration.json").write_text(json.dumps(fx["p_decl"]))
    (prior / "verdict.json").write_text(json.dumps({"per_adapter": fx["p_cells"]}))
    (root / "items.jsonl").write_text(
        lines if fx["own_items"] is None else fx["own_items"])
    (root / "pressure_chunks.jsonl").write_text(
        "".join(json.dumps(c) + "\n" for c in fx["chunks"]))
    decl = fx["decl"]
    if decl.get("items_sha256") == "AUTO":
        decl["items_sha256"] = s8._sha(root / "items.jsonl")
    if decl["pressure"].get("chunks_sha256") == "AUTO":
        decl["pressure"]["chunks_sha256"] = s8._sha(root / "pressure_chunks.jsonl")
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = s8._sha(root / "declaration.json")
    helpful = {i["item_id"]: i["helpful_evidence"] for i in fx["items"]}
    load = {c["item_id"]: c["chunks"] for c in fx["chunks"]}
    out, n, per = [], 0, {}
    for a in decl["adapters"]:
        per[a] = {"rung1": fx["p_cells"].get(a, {}), "rung2": {}}
        for c in fx["conditions"]:
            cell = {}
            for item in fx["items"]:
                n += 1
                cell[item["item_id"]] = fx["text"](a, c, item)
                out.append(json.dumps({
                    "ts": (_T0 + timedelta(seconds=n)).isoformat(),
                    "adapter": a, "condition": c, "item_id": item["item_id"],
                    "delivered_text": cell[item["item_id"]],
                    "competing_bytes": decl["pressure"]["tool_output_bytes"]
                    if c == "pressure" else 0,
                    "declaration_sha256": sha}) + "\n")
            per[a]["rung2"][c] = s8._cell(helpful, cell)
            if c == "pressure":
                per[a]["load_reached_door"] = sum(
                    1 for i in helpful
                    if _reached(s8, load.get(i, []), cell[i]))
    (root / "results.jsonl").write_text("".join(out[:-1] if fx["drop_last"]
                                                else out))
    v = fx["verdict"]
    if v.get("per_adapter") == "AUTO":
        v["per_adapter"] = per
    (root / "verdict.json").write_text(json.dumps(v))
    if fx["after"]:
        fx["after"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, prior


def _patch(root, fn):
    p = root / "verdict.json"
    v = json.loads(p.read_text())
    fn(v)
    p.write_text(json.dumps(v))


def _after_chunks(root, decl):  # the load softened once the numbers were seen
    p = root / "pressure_chunks.jsonl"
    p.write_text(p.read_text().replace("no anomalies", "no real anomalies"))


def _after_note(root, decl):
    decl["note"] = "load confirmed adequate"
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_refs(fx): fx["decl"]["note"] = "load tuned against results.jsonl"
def _m_edit(fx): fx["after"] = _after_note
def _m_load_moved(fx): fx["after"] = _after_chunks
def _m_budget(fx): fx["decl"]["budget_chars"] = 2400
def _m_adapters(fx): fx["decl"]["adapters"] = ["bm25"]
def _m_softer(fx): fx["decl"]["pressure"]["tool_output_bytes"] = 5000
def _m_easy_only(fx): fx["conditions"] = ["normal"]
def _m_dropped(fx): fx["drop_last"] = True
def _m_prior_uncited(fx): fx["verdict"]["prior"] = "the first door run"
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["pressure_chunks.jsonl"] = None
def _m_receipts(fx): fx["raw"] = {n: "{}\n" for n in FILES}


def _m_other_items(fx):
    fx["items"] = [dict(i, query=i["query"] + " ") for i in _ITEMS]
    fx["own_items"] = "".join(json.dumps(i) + "\n" for i in fx["items"])


def _m_unrelated_load(fx):  # rung 1 again: bytes that never compete
    for c in fx["chunks"]:
        c["chunks"] = ["tool output: the weekly cafeteria menu has been "
                       "refreshed for all floors."]


def _m_leaky_load(fx):
    fx["chunks"][0]["chunks"].append(
        "tool output: tenant0 staging listens on 6000, confirmed by port scan.")


def _m_no_chunks(fx): fx["chunks"][4]["chunks"] = []


def _m_harness_moved(fx):
    base = fx["text"]
    fx["text"] = lambda a, c, i: base(a, c, i) + (_FILL if c == "normal" else "")


def _m_prior_misquoted(fx):
    fx["after"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                            ["bm25"]["rung1"]["pressure"].update(
                                                {fx["s8"].PRESENCE: 0.2}))


def _m_new_only(fx):
    fx["after"] = lambda root, decl: _patch(root, lambda v: [
        e.pop("rung1") for e in v["per_adapter"].values()])


def _m_numbers(fx):
    fx["after"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                            ["bm25"]["rung2"]["pressure"].update(
                                                {fx["s8"].BYTES: 1.0}))


def _m_blended(fx):
    fx["after"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                            ["bm25"].update(door_score=0.9))


def _m_reach(fx):
    fx["after"] = lambda root, decl: _patch(root, lambda v: v["per_adapter"]
                                            ["quiet"].update(load_reached_door=5))


def _m_never_matters(fx):
    fx["verdict"]["finding"] = ("bm25 lets a tool chunk through; quiet held "
                                "under pressure, so pressure does not matter "
                                "for it.")


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "declaration references results": (_m_refs,
                                       {"DECLARATION-REFERENCES-RESULTS"}),
    "declaration edited after the run": (_m_edit, {"RESULTS-NOT-BOUND"}),
    "load softened after the run": (_m_load_moved, {"LOAD-NOT-FROZEN"}),
    "other items than rung 1": (_m_other_items, {"ONLY-THE-LOAD-MAY-CHANGE"}),
    "other budget than rung 1": (_m_budget, {"ONLY-THE-LOAD-MAY-CHANGE"}),
    "an adapter left out": (_m_adapters, {"ONLY-THE-LOAD-MAY-CHANGE"}),
    "load lighter than rung 1": (_m_softer, {"LOAD-NOT-HARSHER"}),
    "load unrelated to the queries": (_m_unrelated_load,
                                      {"LOAD-NOT-QUERY-ADJACENT"}),
    "load carries the answer": (_m_leaky_load, {"LOAD-CARRIES-EVIDENCE"}),
    "an item with no load": (_m_no_chunks, {"LOAD-INCOMPLETE"}),
    "only the easy condition": (_m_easy_only, {"CONDITION-MISSING",
                                               "NUMBER-MISSING"}),
    "a row dropped": (_m_dropped, {"ARM-INCOMPLETE"}),
    "unloaded condition drifted from rung 1": (_m_harness_moved,
                                               {"NORMAL-NOT-REPRODUCED"}),
    "rung 1 misquoted": (_m_prior_misquoted, {"PRIOR-MISQUOTED"}),
    "new numbers only, no side by side": (_m_new_only, {"NUMBER-MISSING"}),
    "prior not named": (_m_prior_uncited, {"PRIOR-NOT-CITED"}),
    "rung 2 numbers wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "a blended score": (_m_blended, {"BLENDED-SCORE"}),
    "reach overstated": (_m_reach, {"REACH-DISAGREE"}),
    "held read as pressure never matters": (_m_never_matters,
                                            {"NEVER-REACHED-UNSAID"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest(s8_gate: Path) -> int:
    try:
        s8 = _s8(s8_gate)
    except Exception as e:
        print(f"[S8-GATE-UNREADABLE] {s8_gate}: {type(e).__name__}: {e}")
        print("S10-1 gate findings: 1")
        return 1
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want, gate=s8_gate):
        with tempfile.TemporaryDirectory() as td:
            root, prior = _write(Path(td), fx)
            r = subprocess.run([sys.executable, __file__, str(root), "--prior",
                                str(prior), "--s8-gate", str(gate)],
                               capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        got = set(marker.findall(out))
        ok = want(got) if callable(want) else got == want
        if "Traceback (most recent call last)" in out:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not ok
                                   or "S10-1 gate findings: " not in out):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming", _fixture(s8), None)
    receipts = _fixture(s8)
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: bool(got) and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture(s8)
        mutate(fx)
        case(name, fx, want)
    case("rung-1 gate missing", _fixture(s8), {"S8-GATE-UNREADABLE"},
         gate=Path("/nonexistent/check.py"))

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming run accepted; a receipts-only "
          f"directory, a missing rung-1 gate and {len(_MUTANTS)} mutants each "
          f"rejected by exactly their own markers - an unrelated load, a load "
          f"that carries the answer and `held` read as `never matters` among "
          f"them; no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S10-1")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--prior", default=str(PRIOR))
    ap.add_argument("--s8-gate", default=str(PRIOR / "check.py"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest(Path(a.s8_gate))
    return run(Path(a.root), Path(a.prior), Path(a.s8_gate))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S10-1 gate findings: 1")
        raise SystemExit(1)
