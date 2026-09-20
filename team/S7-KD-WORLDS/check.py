#!/usr/bin/env python3
"""Gate for QUEUE row S7-4 (KnowledgeDrift frozen worlds as a second instrument).

plumb-fable, row S7-4G, 2026-09-17. Written FROM ROW S7-4's TEXT ALONE, while
`team/S7-KD-WORLDS/` did not exist. Read for this gate: the board row, and the
card the row cites (team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md). The upstream
repository and its task format were NOT opened, so the gate does not guess how
a task is judged. The interface below is declared by the gate, not fitted to a
document; every finding names what it wants.

This gate is an INSTRUMENT where it can be. It recounts every pass rate from
per-item receipts, re-hashes the frozen worlds, takes each item's family from
the frozen item list and never from a receipt, checks the caveat against the
card's own text, and scans the prose for the upstream leaderboard.

Declared interface (ROOT = team/S7-KD-WORLDS, CARD = the cited card)
  declaration.json  {declared_at (ISO), items_sha256,
                    worlds: {upstream_repo (names KnowledgeDrift), commit
                             (hex), license: "MIT", dir (has worlds/v2; under
                             ROOT or absolute), files: {relative path: sha256}},
                    engines: {name: {experiment_class: baseline |
                              controlled_core | raw_product | product}},
                    families_not_run: {family: reason}}
  items.jsonl       one task per line: {item_id, family, seed}
  results.jsonl     one receipt per line, IN RUN ORDER: {ts (ISO), engine,
                    item_id, passed (bool), expected, response,
                    declaration_sha256}. Controls `return-nothing` and
                    `oracle`; every other engine name is one of ours.
  verdict.json      {finding, lane: "external", feeds (names roadmap R-PE),
                    card (names the card file), caveat (a sentence quoted from
                    the card's caveat section), prior (states none exists),
                    per_family: {engine: {family: {passed, items, pass_rate}}}}

What the row turns on (marker in brackets)
  (a) FROZEN worlds, not home-grown ones. The declaration pins upstream repo
      and commit [UPSTREAM-UNPINNED], records the licence
      [LICENSE-NOT-RECORDED], points at worlds/v2 [NOT-V2-WORLDS], and lists
      world files whose sha256 the gate re-hashes [WORLDS-NOT-FROZEN]. More
      than one seed is run [SINGLE-SEED].
  (b) PER-FAMILY results, with no silent choice of family. Each of the eight
      scored families is either run or listed in families_not_run with a
      reason [FAMILY-UNACCOUNTED]; families are the card's [UNKNOWN-FAMILY];
      Abstention is run, since the row exists to stop more home-grown
      abstention fixtures [NO-ABSTENTION-FAMILY]; at least two families
      [SINGLE-FAMILY] of at least 10 items each [TOO-FEW-ITEMS].
  (c) Scores RE-DERIVED. One receipt per engine per item [ARM-INCOMPLETE], with
      the expected and the response kept beside the judgement [SCHEMA].
      Controls ran first [CONTROLS-NOT-FIRST] and did what their names say:
      `oracle` passes every item, `return-nothing` passes every Abstention item
      and no Retrieval item [CONTROL-ARM-WRONG] [ARM-MISSING]. At least one of
      our engines ran [NO-ENGINE], each declared with its evidence class
      [ENGINE-UNDECLARED] [ENGINE-CLASS]. verdict.json per_family must equal
      the recount, no engine or family more or less [NUMBERS-DISAGREE].
  (d) NO SCORE IMPORT. No prose in ROOT (verdict.json strings, *.md) carries
      an upstream leaderboard number, or an upstream system beside a number
      [SCORE-IMPORTED]. The card says: cite neither until it is explained.
  (e) The card's CAVEAT TRAVELS. verdict.json names the card
      [CARD-NOT-CITED] and quotes, word for word, at least 40 characters of
      its caveat section [CAVEAT-NOT-FROM-CARD]; an invented caveat fails.
  (f) A separate evidence class. lane is "external" and feeds names R-PE
      [LANE-NOT-NAMED]; the prior is stated as none [PRIOR-NOT-STATED]; a
      finding is given [VERDICT-NO-FINDING].
  (g) Declared before the run. declared_at precedes every receipt
      [DECLARED-AFTER-RESULTS]; each receipt embeds the sha256 of the
      declaration bytes [RESULTS-NOT-BOUND]; the declaration pins the item list
      [ITEMS-NOT-FROZEN].
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [CARD-UNREADABLE]

Limits, stated on purpose: `passed` is the author's judgement per item. The
gate recounts it and demands the evidence beside it, but does not re-judge a
task, because the upstream task format was not read. It cannot tell that the
world files ARE the upstream ones at that commit, or that the run was local and
$0. Timestamps are self-reported and a hash chain can be rebuilt by someone who
sets out to. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S7-4 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--card FILE]
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
CARD_NAME = "EXTERNAL-KNOWLEDGEDRIFT-20260916.md"
FILES = ("declaration.json", "items.jsonl", "results.jsonl", "verdict.json")
SCORED = ("Retrieval", "Abstention", "Currency", "Contradiction", "Drift",
          "Deletion", "Rationale", "Temporal")
FAMILIES = SCORED + ("Authority",)
NOTHING, ORACLE = "return-nothing", "oracle"
CLASSES = ("baseline", "controlled_core", "raw_product", "product")
MIN_ITEMS, MIN_QUOTE = 10, 40
NO_PRIOR = re.compile(r"none exists?|no prior|no previous|no run\b|never (been )?"
                      r"(run|measured)|first (run|measurement)", re.I)
# the upstream leaderboard, as the card records it: never to be cited
IMPORTED = re.compile(
    r"\b(718|580|359|348|459)\b"
    r"|\b(engram|mem0|memobase|vector rag)\b[^.\n]{0,60}\d"
    r"|\d[^.\n]{0,60}\b(engram|mem0|memobase|vector rag)\b", re.I)


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


def _text(v) -> bool:
    return isinstance(v, str) and len(v.strip()) >= 8


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _plain(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`\"“”]", "", s)).strip().lower()


def _caveat_section(card: str) -> str:
    m = re.search(r"^##[^\n]*caveat[^\n]*\n(.*?)(?=^## |\Z)", card,
                  re.I | re.M | re.S)
    return _plain(m.group(1)) if m else ""


def _strings(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values():
            yield from _strings(x)
    elif isinstance(v, list):
        for x in v:
            yield from _strings(x)


def _schema(decl, items, rows, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if _ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    if not isinstance(decl.get("items_sha256"), str):
        f.append(("SCHEMA", "declaration.json needs items_sha256"))
    w = decl.get("worlds") if isinstance(decl.get("worlds"), dict) else {}
    if "knowledgedrift" not in str(w.get("upstream_repo", "")).lower() \
            or not re.fullmatch(r"[0-9a-f]{7,40}", str(w.get("commit", ""))):
        f.append(("UPSTREAM-UNPINNED", "declaration.json worlds needs "
                  "upstream_repo (the KnowledgeDrift repository) and commit "
                  "(7 to 40 hex characters)"))
    if str(w.get("license", "")).strip().upper() != "MIT":
        f.append(("LICENSE-NOT-RECORDED", "declaration.json worlds needs "
                  "license: \"MIT\", the licence the row relies on"))
    files = w.get("files")
    if not (isinstance(w.get("dir"), str) and isinstance(files, dict) and files
            and all(isinstance(k, str) and isinstance(v, str)
                    for k, v in files.items())):
        f.append(("SCHEMA", "declaration.json worlds needs dir and files: "
                  "{relative path: sha256}, at least one file"))
    elif "worlds/v2" not in w["dir"].replace("\\", "/"):
        f.append(("NOT-V2-WORLDS", f"declaration.json worlds.dir {w['dir']!r} "
                  f"must point at the upstream worlds/v2 set the row names"))
    if not (isinstance(decl.get("engines"), dict)
            and isinstance(decl.get("families_not_run"), dict)):
        f.append(("SCHEMA", "declaration.json needs engines: {name: "
                  "{experiment_class}} and families_not_run: {family: reason}"))

    ok = isinstance(items, list) and items and all(
        isinstance(i, dict) and isinstance(i.get("item_id"), str)
        and isinstance(i.get("family"), str) and "seed" in i for i in items)
    if not ok or len({i["item_id"] for i in items}) != len(items):
        f.append(("SCHEMA", "items.jsonl needs one {item_id, family, seed} per "
                  "line, item_id unique"))

    if not isinstance(rows, list) or not rows:
        f.append(("SCHEMA", "results.jsonl has no rows"))
    else:
        for n, r in enumerate(rows, 1):
            if not (isinstance(r, dict) and _ts(r.get("ts"))
                    and isinstance(r.get("engine"), str)
                    and isinstance(r.get("item_id"), str)
                    and isinstance(r.get("passed"), bool)
                    and "expected" in r and "response" in r
                    and isinstance(r.get("declaration_sha256"), str)):
                f.append(("SCHEMA", f"results.jsonl row {n} needs ts, engine, "
                          "item_id, passed (true or false), expected, response "
                          "(the evidence beside the judgement), "
                          "declaration_sha256"))
                break

    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if not isinstance(verdict.get("per_family"), dict):
        f.append(("SCHEMA", "verdict.json needs per_family: {engine: {family: "
                  "{passed, items, pass_rate}}}"))
    return f


def _prose(root: Path, verdict, card_text: str, f: list) -> None:
    """(d) (e) (f): what the artifact SAYS."""
    if not isinstance(verdict.get("finding"), str) \
            or len(verdict["finding"].strip()) < 20:
        f.append(("VERDICT-NO-FINDING", "verdict.json needs finding: one "
                  "sentence on what the second instrument shows"))
    if verdict.get("lane") != "external" or "R-PE" not in str(verdict.get("feeds", "")):
        f.append(("LANE-NOT-NAMED", "verdict.json needs lane: \"external\" and "
                  "feeds naming roadmap R-PE: an external lane is a separate "
                  "evidence class, not more of our own instrument"))
    if not NO_PRIOR.search(str(verdict.get("prior", ""))):
        f.append(("PRIOR-NOT-STATED", "verdict.json needs prior, stating in "
                  "words that no run of our engines on these worlds exists "
                  "(`none exists`)"))
    if CARD_NAME not in str(verdict.get("card", "")):
        f.append(("CARD-NOT-CITED", f"verdict.json needs card, naming "
                  f"team/{CARD_NAME}"))
    quote = _plain(str(verdict.get("caveat", "")))
    if len(quote) < MIN_QUOTE or quote not in _caveat_section(card_text):
        f.append(("CAVEAT-NOT-FROM-CARD", f"verdict.json needs caveat: at "
                  f"least {MIN_QUOTE} characters quoted word for word from the "
                  f"card's caveat section. The card's caveat travels; a new "
                  f"one does not replace it"))
    texts = [("verdict.json", s) for s in _strings(verdict)]
    texts += [(p.name, p.read_text(encoding="utf-8", errors="replace"))
              for p in sorted(root.glob("*.md"))]
    hits = sorted({f"{name}: {m.group(0)!r}" for name, s in texts
                   for m in IMPORTED.finditer(s)})
    if hits:
        f.append(("SCORE-IMPORTED", f"upstream leaderboard content in the "
                  f"artifact ({'; '.join(hits[:4])}). The row says no score "
                  f"import; the card says cite neither"))


def check(root: Path, card: Path) -> tuple[list[tuple[str, str]], str]:
    try:
        card_text = card.read_text(encoding="utf-8", errors="replace")
        if not _caveat_section(card_text):
            raise ValueError("no caveat section")
    except (OSError, ValueError) as e:
        return [("CARD-UNREADABLE", f"{card}: {e}")], ""
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = _load(root / "declaration.json")
        items = _load(root / "items.jsonl", lines=True)
        rows = _load(root / "results.jsonl", lines=True)
        verdict = _load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(decl, items, rows, verdict)
    if f:
        return f, ""

    # (g) declared before the run
    sha = _sha(root / "declaration.json")
    unbound = sum(1 for r in rows if r["declaration_sha256"] != sha)
    if unbound:
        f.append(("RESULTS-NOT-BOUND", f"{unbound} of {len(rows)} receipts do "
                  f"not carry the sha256 of declaration.json as it stands "
                  f"({sha[:12]}): the declaration changed after the run, or "
                  f"the run never read it"))
    first = min(_ts(r["ts"]) for r in rows)
    if _ts(decl["declared_at"]) >= first:
        f.append(("DECLARED-AFTER-RESULTS", f"declared_at {decl['declared_at']} "
                  f"is not before the first receipt {first.isoformat()}"))
    if decl["items_sha256"] != _sha(root / "items.jsonl"):
        f.append(("ITEMS-NOT-FROZEN", "items_sha256 is not the sha256 of "
                  "items.jsonl: the item list, or an item's family, changed "
                  "after it was declared"))

    # (a) frozen worlds
    wdir = root / decl["worlds"]["dir"]
    moved = sorted(rel for rel, want in decl["worlds"]["files"].items()
                   if not (wdir / rel).is_file() or _sha(wdir / rel) != want)
    if moved:
        f.append(("WORLDS-NOT-FROZEN", f"world files absent or not matching "
                  f"their declared sha256: {', '.join(moved[:5])}"))
    if len({json.dumps(i["seed"]) for i in items}) < 2:
        f.append(("SINGLE-SEED", "items.jsonl holds one seed; the row asks for "
                  "the worlds/v2 seeds"))

    # (b) per-family, with no silent choice of family
    family = {i["item_id"]: i["family"] for i in items}
    size = Counter(family.values())
    unknown = sorted(set(size) - set(FAMILIES))
    if unknown:
        f.append(("UNKNOWN-FAMILY", f"items.jsonl families not in the card: "
                  f"{', '.join(unknown)}. Use {', '.join(FAMILIES)}"))
    not_run = decl["families_not_run"]
    silent = sorted(x for x in SCORED if x not in size
                    and not _text(not_run.get(x)))
    if silent:
        f.append(("FAMILY-UNACCOUNTED", f"scored families neither run nor "
                  f"listed in families_not_run with a reason: "
                  f"{', '.join(silent)}"))
    if "Abstention" not in size:
        f.append(("NO-ABSTENTION-FAMILY", "the Abstention family is not run; "
                  "it is the family the row exists for"))
    if len(size) < 2:
        f.append(("SINGLE-FAMILY", "one family is not per-family results"))
    small = sorted(x for x, n in size.items() if n < MIN_ITEMS)
    if small:
        f.append(("TOO-FEW-ITEMS", f"fewer than {MIN_ITEMS} items in: "
                  f"{', '.join(small)}"))

    # (c) scores re-derived from receipts
    engines = sorted({r["engine"] for r in rows} - {NOTHING, ORACLE})
    if not engines:
        f.append(("NO-ENGINE", "results.jsonl holds controls only; the row "
                  "asks for a run of OUR engines on these worlds"))
    passed: dict[str, dict] = {}
    for arm in (NOTHING, ORACLE, *engines):
        mine = [r for r in rows if r["engine"] == arm]
        if not mine:
            f.append(("ARM-MISSING", f"results.jsonl has no `{arm}` receipts"))
            continue
        seen = Counter(r["item_id"] for r in mine)
        if set(seen) != set(family) or max(seen.values()) > 1:
            f.append(("ARM-INCOMPLETE", f"`{arm}` must hold each of the "
                      f"{len(family)} items exactly once"))
            continue
        passed[arm] = {r["item_id"]: r["passed"] for r in mine}
    for e in engines:
        entry = decl["engines"].get(e)
        if not isinstance(entry, dict):
            f.append(("ENGINE-UNDECLARED", f"`{e}` has receipts and is not in "
                      f"declaration.json engines"))
        elif entry.get("experiment_class") not in CLASSES:
            f.append(("ENGINE-CLASS", f"declaration.json engines.{e} needs "
                      f"experiment_class: {' | '.join(CLASSES)}"))
    if len(passed) == 2 + len(engines) and engines:
        nothing_wrong = [i for i, fam in family.items()
                         if (fam == "Abstention" and not passed[NOTHING][i])
                         or (fam == "Retrieval" and passed[NOTHING][i])]
        if nothing_wrong or not all(passed[ORACLE].values()):
            f.append(("CONTROL-ARM-WRONG", f"`{ORACLE}` must pass every item; "
                      f"`{NOTHING}` must pass every Abstention item and no "
                      f"Retrieval item. If not, the scorer cannot be trusted "
                      f"on our engines"))
        order = [r["engine"] for r in rows]
        if max(i for i, a in enumerate(order) if a in (NOTHING, ORACLE)) > \
                min(i for i, a in enumerate(order) if a in engines):
            f.append(("CONTROLS-NOT-FIRST", "every control receipt must come "
                      "before the first engine receipt"))
        real = {e: {fam: {"passed": sum(1 for i, x in family.items()
                                        if x == fam and passed[e][i]),
                          "items": n} for fam, n in size.items()}
                for e in engines}
        said = verdict["per_family"]
        bad = sorted(set(said) ^ set(real))
        for e in set(said) & set(real):
            cells = said[e] if isinstance(said[e], dict) else {}
            bad += [f"{e}/{fam}" for fam in set(cells) ^ set(real[e])]
            for fam in set(cells) & set(real[e]):
                c, r = cells[fam], real[e][fam]
                if not (isinstance(c, dict) and c.get("passed") == r["passed"]
                        and c.get("items") == r["items"]
                        and isinstance(c.get("pass_rate"), (int, float))
                        and abs(c["pass_rate"] - r["passed"] / r["items"])
                        < 0.0006):
                    bad.append(f"{e}/{fam} (recount {r['passed']}/{r['items']})")
        if bad:
            f.append(("NUMBERS-DISAGREE", f"verdict.json per_family does not "
                      f"equal the receipts as recounted, no engine or family "
                      f"more or less: {', '.join(sorted(bad)[:6])}"))

    _prose(root, verdict, card_text, f)
    return f, (f"{len(engines)} engines, {len(size)} families, "
               f"{len(family)} items, per-family pass rates recounted")


def run(root: Path, card: Path) -> int:
    findings, summary = check(root, card)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S7-4 gate findings: {len(findings)}")
        return 1
    print(f"S7-4 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)
_CARD = ("# External benchmark card\n\n## What it is\n\n"
         "Eight scored families, plus an optional ninth, on worlds frozen under "
         "worlds/v2.\n\n## The caveat, which is the whole reason\n\n"
         "**The benchmark's author has a system in its own ranking, and it "
         "wins.** The repo lists \"reference Engram\" at 718, the top score.\n\n"
         "## What this changes\n\nNothing yet.\n")
_QUOTE = "The benchmark's author has a system in its own ranking, and it wins."


def _fixture() -> dict:
    items = [{"item_id": f"s{seed}-{fam[:3].lower()}-{i}", "family": fam,
              "seed": seed}
             for seed in (1, 2) for fam in ("Retrieval", "Abstention")
             for i in range(6)]
    ids = lambda fam: [i["item_id"] for i in items if i["family"] == fam]  # noqa: E731
    return {
        "decl": {"declared_at": _T0.isoformat(), "items_sha256": "AUTO",
                 "worlds": {"upstream_repo": "github.com/techtheist/KnowledgeDrift",
                            "commit": "0a1b2c3d4e5f", "license": "MIT",
                            "dir": "KnowledgeDrift/worlds/v2", "files": "AUTO"},
                 "engines": {"bm25": {"experiment_class": "baseline"},
                             "pi_lcm": {"experiment_class": "product"}},
                 "families_not_run": {x: "needs a judgement our retrieval "
                                         "engines do not produce"
                                      for x in SCORED[2:]}},
        "items": items, "order": [NOTHING, ORACLE, "bm25", "pi_lcm"],
        # engine -> the items it passed
        "pass": {NOTHING: set(ids("Abstention")),
                 ORACLE: {i["item_id"] for i in items},
                 "bm25": set(ids("Retrieval")),
                 "pi_lcm": set(ids("Abstention") + ids("Retrieval")[:2])},
        "verdict": {"finding": "on frozen external worlds bm25 passes "
                               "Retrieval and no Abstention item; pi_lcm the "
                               "reverse.",
                    "lane": "external", "feeds": "roadmap R-PE external lanes",
                    "card": f"team/{CARD_NAME}", "caveat": _QUOTE,
                    "prior": "none exists: no run of our engines on its worlds",
                    "per_family": "AUTO"},
        "md": {}, "raw": {}, "after_run": None, "drop_last": False,
        "strip_key": None,
    }


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    root, card = td / "S7-KD-WORLDS", td / CARD_NAME
    root.mkdir()
    card.write_text(_CARD)
    decl = fx["decl"]
    worlds = decl.get("worlds")
    if isinstance(worlds, dict) and worlds.get("files") == "AUTO":
        wdir = root / worlds["dir"]
        wdir.mkdir(parents=True)
        for seed in (1, 2):
            (wdir / f"seed{seed}.json").write_text(json.dumps({"seed": seed}))
        worlds["files"] = {p.name: _sha(p) for p in sorted(wdir.iterdir())}
    (root / "items.jsonl").write_text(
        "".join(json.dumps(i) + "\n" for i in fx["items"]))
    if decl.get("items_sha256") == "AUTO":
        decl["items_sha256"] = _sha(root / "items.jsonl")
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = _sha(root / "declaration.json")
    out, n = [], 0
    for engine in fx["order"]:
        for i in fx["items"]:
            n += 1
            r = {"ts": (_T0 + timedelta(seconds=n)).isoformat(),
                 "engine": engine, "item_id": i["item_id"],
                 "passed": i["item_id"] in fx["pass"][engine],
                 "expected": ["rec-1"] if i["family"] == "Retrieval" else [],
                 "response": [], "declaration_sha256": sha}
            r.pop(fx["strip_key"], None)
            out.append(json.dumps(r) + "\n")
    (root / "results.jsonl").write_text("".join(out[:-1] if fx["drop_last"]
                                                else out))
    v = fx["verdict"]
    if v.get("per_family") == "AUTO":
        size = Counter(i["family"] for i in fx["items"])
        v["per_family"] = {
            e: {fam: {"passed": (p := sum(1 for i in fx["items"]
                                          if i["family"] == fam
                                          and i["item_id"] in fx["pass"][e])),
                      "items": n_items, "pass_rate": p / n_items}
                for fam, n_items in size.items()}
            for e in fx["order"] if e not in (NOTHING, ORACLE)}
    (root / "verdict.json").write_text(json.dumps(v))
    for name, text in fx["md"].items():
        (root / name).write_text(text)
    if fx["after_run"]:
        fx["after_run"](root, decl)
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, card


def _after_decl(root, decl):  # a family quietly dropped once numbers were seen
    decl["families_not_run"]["Drift"] = "dropped after a poor first look"
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))


def _after_items(root, decl):  # an awkward Retrieval item relabelled
    p = root / "items.jsonl"
    p.write_text(p.read_text().replace(
        '{"item_id": "s2-ret-5", "family": "Retrieval"',
        '{"item_id": "s2-ret-5", "family": "Abstention"'))


def _after_world(root, decl):  # a world edited at home
    (root / decl["worlds"]["dir"] / "seed2.json").write_text('{"seed": 2, '
                                                             '"ours": true}')


def _only(fx, fam):
    fx["items"] = [dict(i, family=fam) for i in fx["items"]]
    fx["pass"][NOTHING] = ({i["item_id"] for i in fx["items"]}
                           if fam == "Abstention" else set())
    fx["decl"]["families_not_run"]["Abstention" if fam == "Retrieval"
                                   else "Retrieval"] = "not run, stated reason"


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_decl_moved(fx): fx["after_run"] = _after_decl
def _m_relabel(fx): fx["after_run"] = _after_items
def _m_world(fx): fx["after_run"] = _after_world
def _m_v1(fx): fx["decl"]["worlds"]["dir"] = "KnowledgeDrift/worlds/v1"
def _m_nocommit(fx): fx["decl"]["worlds"]["commit"] = "main"
def _m_homegrown(fx): fx["decl"]["worlds"]["upstream_repo"] = "ours, regenerated"
def _m_nolicense(fx): del fx["decl"]["worlds"]["license"]
def _m_silent(fx): del fx["decl"]["families_not_run"]["Drift"]
def _m_noreason(fx): fx["decl"]["families_not_run"]["Drift"] = ""
def _m_no_abstention(fx): _only(fx, "Retrieval")
def _m_oneseed(fx): fx["items"] = [dict(i, seed=1) for i in fx["items"]]
def _m_few(fx): fx["items"] = [i for i in fx["items"] if i["item_id"][-1] in "01"]
def _m_undeclared(fx): del fx["decl"]["engines"]["pi_lcm"]
def _m_class(fx): fx["decl"]["engines"]["bm25"]["experiment_class"] = "ours"
def _m_noengine(fx): fx["order"] = [NOTHING, ORACLE]
def _m_nocontrol(fx): fx["order"] = [NOTHING, "bm25", "pi_lcm"]
def _m_oracle(fx): fx["pass"][ORACLE].discard("s1-ret-0")
def _m_nothing(fx): fx["pass"][NOTHING].add("s1-ret-0")
def _m_dropped(fx): fx["drop_last"] = True
def _m_order(fx): fx["order"] = ["bm25", "pi_lcm", NOTHING, ORACLE]
def _m_noevidence(fx): fx["strip_key"] = "response"
def _m_lane(fx): fx["verdict"]["lane"] = "ours"
def _m_feeds(fx): fx["verdict"]["feeds"] = "the headline"
def _m_nocard(fx): fx["verdict"]["card"] = "the Reddit post"
def _m_prior(fx): fx["verdict"]["prior"] = "see the card"
def _m_nofinding(fx): fx["verdict"]["finding"] = ""
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["items.jsonl"] = None


def _m_vibes(fx):
    fx["items"] = [dict(i, family="Vibes") if i["family"] == "Retrieval" else i
                   for i in fx["items"]]
    fx["decl"]["families_not_run"]["Retrieval"] = "not run, stated reason"


def _m_numbers(fx):
    fx["verdict"]["per_family"] = {"bm25": {"Retrieval": {
        "passed": 12, "items": 12, "pass_rate": 1.0}}}


def _m_extra_engine(fx):  # a row of numbers with no receipts behind it
    fx["after_run"] = lambda root, decl: (root / "verdict.json").write_text(
        json.dumps(dict(fx["verdict"], per_family=dict(
            fx["verdict"]["per_family"], reference={"Retrieval": {
                "passed": 9, "items": 12, "pass_rate": 0.75}}))))


def _m_invented(fx):
    fx["verdict"]["caveat"] = ("External benchmarks can differ from ours in "
                               "scope, so results should be read with care.")


def _m_wrong_section(fx):
    fx["verdict"]["caveat"] = ("Eight scored families, plus an optional ninth, "
                               "on worlds frozen under worlds/v2.")


def _m_import_finding(fx):
    fx["verdict"]["finding"] += " Upstream has TF-IDF at 580 for comparison."


def _m_import_report(fx):
    fx["md"]["report.md"] = "# Report\n\nFor context, Engram Alpha scored 80%.\n"


def _m_import_caveat(fx):
    fx["verdict"]["caveat"] = ('The repo lists "reference Engram" at 718, the '
                               'top score.')


def _m_receipts(fx):  # every file exists and says nothing
    fx["raw"] = {n: "{}\n" for n in FILES}


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "family dropped after the run": (_m_decl_moved, {"RESULTS-NOT-BOUND"}),
    "item relabelled after the run": (_m_relabel, {"ITEMS-NOT-FROZEN",
                                                   "CONTROL-ARM-WRONG",
                                                   "NUMBERS-DISAGREE"}),
    "world edited at home": (_m_world, {"WORLDS-NOT-FROZEN"}),
    "not the v2 worlds": (_m_v1, {"NOT-V2-WORLDS"}),
    "upstream commit not pinned": (_m_nocommit, {"UPSTREAM-UNPINNED"}),
    "home-grown worlds": (_m_homegrown, {"UPSTREAM-UNPINNED"}),
    "licence not recorded": (_m_nolicense, {"LICENSE-NOT-RECORDED"}),
    "family silently skipped": (_m_silent, {"FAMILY-UNACCOUNTED"}),
    "family skipped with no reason": (_m_noreason, {"FAMILY-UNACCOUNTED"}),
    "family not in the card": (_m_vibes, {"UNKNOWN-FAMILY"}),
    "abstention not run": (_m_no_abstention, {"NO-ABSTENTION-FAMILY",
                                              "SINGLE-FAMILY"}),
    "one seed": (_m_oneseed, {"SINGLE-SEED"}),
    "four items per family": (_m_few, {"TOO-FEW-ITEMS"}),
    "engine not declared": (_m_undeclared, {"ENGINE-UNDECLARED"}),
    "engine class outside the vocabulary": (_m_class, {"ENGINE-CLASS"}),
    "controls only": (_m_noengine, {"NO-ENGINE"}),
    "oracle control missing": (_m_nocontrol, {"ARM-MISSING"}),
    "oracle fails an item": (_m_oracle, {"CONTROL-ARM-WRONG"}),
    "return-nothing passes retrieval": (_m_nothing, {"CONTROL-ARM-WRONG"}),
    "a receipt dropped": (_m_dropped, {"ARM-INCOMPLETE"}),
    "controls after the engines": (_m_order, {"CONTROLS-NOT-FIRST"}),
    "judgement without evidence": (_m_noevidence, {"SCHEMA"}),
    "per-family table thinned": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "engine with no receipts reported": (_m_extra_engine, {"NUMBERS-DISAGREE"}),
    "lane not external": (_m_lane, {"LANE-NOT-NAMED"}),
    "roadmap item not named": (_m_feeds, {"LANE-NOT-NAMED"}),
    "card not cited": (_m_nocard, {"CARD-NOT-CITED"}),
    "caveat invented": (_m_invented, {"CAVEAT-NOT-FROM-CARD"}),
    "caveat from another section": (_m_wrong_section, {"CAVEAT-NOT-FROM-CARD"}),
    "prior not stated": (_m_prior, {"PRIOR-NOT-STATED"}),
    "no finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "leaderboard number in the finding": (_m_import_finding, {"SCORE-IMPORTED"}),
    "leaderboard system in report.md": (_m_import_report, {"SCORE-IMPORTED"}),
    "caveat quote carries a score": (_m_import_caveat, {"SCORE-IMPORTED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want, lose_card=False):
        with tempfile.TemporaryDirectory() as td:
            root, card = _write(Path(td), fx)
            if lose_card:
                card.unlink()
            r = subprocess.run([sys.executable, __file__, str(root), "--card",
                                str(card)], capture_output=True, text=True,
                               timeout=60)
        text = r.stdout + r.stderr
        got = set(marker.findall(text))
        if "Traceback (most recent call last)" in text:
            bad.append(f"{name}: traceback")
        elif want is None and (r.returncode != 0 or got
                               or "gate findings" in text):
            bad.append(f"{name}: should be ACCEPTED, got exit {r.returncode} "
                       f"{sorted(got)}")
        elif want is not None and (r.returncode != 1 or not want(got)
                                   or "S7-4 gate findings: " not in text):
            bad.append(f"{name}: wrong rejection, got exit {r.returncode} "
                       f"{sorted(got)}")

    case("conforming", _fixture(), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    case("card missing", _fixture(), lambda got: got == {"CARD-UNREADABLE"},
         lose_card=True)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, lambda got, want=want: got == want)

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (the conforming fixture accepted; a receipts-only "
          f"directory, a missing card and {len(_MUTANTS)} mutants each "
          f"rejected by exactly their own markers, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S7-4")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--card", default=str(HERE.parent / CARD_NAME))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.card))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S7-4 gate findings: 1")
        raise SystemExit(1)
