#!/usr/bin/env python3
"""Gate for QUEUE row S7-2 (compose attempt: bm25 retrieval behind pi-lcm's
abstention gate).

plumb-fable, row S7-2G, 2026-09-17. Written FROM ROW S7-2's TEXT ALONE, while
`team/S7-COMPOSE/` did not exist. Read for this gate: the board row, and the
PRIOR measurement the row cites (team/S6-SELECTIVITY: corpus, manifest, results
schema). The interface below is declared by the gate, not fitted to a document;
every finding names what it wants.

This gate is an INSTRUMENT. It trusts no number in the artifact. It recomputes
the prior, both re-measured arms, the composition itself, the two-by-two table
that shows complementarity, and the verdict the pre-declared rule gives.

Declared interface (ROOT = team/S7-COMPOSE, PRIOR = team/S6-SELECTIVITY,
PREFILTER = team/S7-BM25-PREFILTER, the row this one depends on)
  declaration.json  {declared_at (ISO), corpus_sha256, manifest_sha256 (the
                    PRIOR files, frozen), bm25_variant: "prior" | "prefilter",
                    s7_1_verdict: "not-landed" | "artifact-confirmed" |
                    "artifact-refuted",
                    rule: {complementary_if_gain_at_least: margin > 0}}
  results.jsonl     one row per line, IN RUN ORDER: {ts (ISO), arm, case_id,
                    retrieved_ids, declaration_sha256}. Arms `bm25`,
                    `pi_lcm_toollevel_sel` (the PRIOR names) and `compose`.
  verdict.json      {verdict: "complementary" | "not-complementary", finding,
                    feeds (names roadmap R-PF, Decision Gate F option B),
                    prior: {source, bm25: S, pi_lcm: S},
                    rerun: {bm25: S, pi_lcm: S, compose: S},
                    overlap: {both, only_bm25, only_pi_lcm, neither}}
                    S = {mean_f1, retrieve_correct, abstain_correct}

What the row turns on (marker in brackets)
  (a) Not argued from taste. The rule that turns numbers into a verdict is
      fixed BEFORE the run [RULE-UNDECLARED]: declared_at precedes every result
      [DECLARED-AFTER-RESULTS], and every result row embeds the sha256 of the
      declaration bytes, so a margin moved after the run breaks the chain
      [RESULTS-NOT-BOUND]. Same frozen corpus and manifest, byte for byte
      [CORPUS-NOT-FROZEN] [MANIFEST-NOT-FROZEN].
  (b) Both arms are re-measured, not quoted. Each of bm25 and pi-lcm covers
      every case once [ARM-MISSING] [ARM-INCOMPLETE] [UNKNOWN-ID] and, with no
      LLM on a frozen corpus, reproduces its reference retrieval per case
      [ARM-NOT-REPRODUCED]; else a compose gain is harness drift. The bm25
      reference is the PRIOR bm25 arm, or row S7-1's `bm25-prefilter` arm when
      bm25_variant is "prefilter". The dependency on S7-1 is checked: the
      prefilter variant needs an S7-1 verdict of artifact-confirmed on disk, a
      quoted S7-1 verdict must match the file, and a confirmed artifact may not
      be composed on unfiltered [BM25-VARIANT-UNJUSTIFIED].
  (c) The compose arm IS the composition. Components run first
      [COMPONENTS-NOT-FIRST]; per case, compose retrieves nothing where pi-lcm
      retrieved nothing, and exactly the bm25 ids where pi-lcm fired
      [COMPOSE-NOT-COMPOSED]. A hand-improved compose arm is not evidence.
  (d) Complementary rather than ranked. A case is correct when a retrieve case
      has its whole helpful set retrieved, or an abstain case has nothing
      retrieved. verdict.json must show the two-by-two table of bm25 against
      pi-lcm correctness as recomputed [OVERLAP-DISAGREE]; cite the prior
      [PRIOR-NOT-CITED] and quote both prior arms as recomputed
      [PRIOR-MISQUOTED]; report all three re-run arms as recomputed
      [NUMBERS-DISAGREE]; hold the verdict the rule gives: complementary if and
      only if compose mean set-F1 minus the better single arm >= the declared
      margin [VERDICT-CONTRADICTS-RULE]; give a finding [VERDICT-NO-FINDING]
      that does not rank the engines [RANKING-LANGUAGE]; and name the decision
      it feeds [GATE-F-NOT-NAMED]. `not-complementary` is a PASS: an honest
      negative is the evidence Decision Gate F asked for.
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [VERDICT-INVALID] [PRIOR-UNREADABLE]

Limits, stated on purpose: timestamps are self-reported and a hash chain can be
rebuilt by someone who sets out to. "pi-lcm fired" is read as "pi-lcm retrieved
at least one id", the only signal the PRIOR schema holds. The gate cannot tell
that the run was local, $0 and free of LLM calls, or what ten cases can carry
for adopt-vs-build. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S7-2 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--prior DIR] [--prefilter DIR]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import copy
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
FILES = ("declaration.json", "results.jsonl", "verdict.json")
BM25, PI, COMPOSE = "bm25", "pi_lcm_toollevel_sel", "compose"
KEY = {BM25: "bm25", PI: "pi_lcm", COMPOSE: "compose"}  # verdict.json names
VERDICTS = ("complementary", "not-complementary")
VARIANTS = ("prior", "prefilter")
S71 = ("not-landed", "artifact-confirmed", "artifact-refuted")
OVERLAP = ("both", "only_bm25", "only_pi_lcm", "neither")
RANKING = re.compile(r"\b(beats?|outperforms?|winner|wins|leaderboard|ranked|"
                     r"ranking|better than|worse than|best engine)\b", re.I)


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


def _strs(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _load(path: Path, lines: bool = False):
    text = path.read_text(encoding="utf-8", errors="replace")
    if lines:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def _f1(helpful: set, got: set) -> float:
    if not helpful:
        return 0.0 if got else 1.0
    hit = len(helpful & got)
    return 2 * hit / (len(helpful) + len(got)) if hit else 0.0


def _correct(case: dict, helpful: set, got) -> bool:
    return not got if case["expect"] == "abstain" else helpful <= set(got)


def _score(cases: dict, helpful: dict, got: dict) -> dict:
    return {
        "mean_f1": sum(_f1(helpful[c], set(got[c])) for c in cases) / len(cases),
        "retrieve_correct": sum(1 for c, v in cases.items() if v["expect"] ==
                                "retrieve" and _correct(v, helpful[c], got[c])),
        "abstain_correct": sum(1 for c, v in cases.items() if v["expect"] ==
                               "abstain" and _correct(v, helpful[c], got[c])),
    }


def _is_score(v) -> bool:
    return (isinstance(v, dict) and isinstance(v.get("mean_f1"), (int, float))
            and not isinstance(v.get("mean_f1"), bool)
            and _int(v.get("retrieve_correct")) and _int(v.get("abstain_correct")))


def _same(claimed: dict, real: dict) -> bool:
    return (abs(claimed["mean_f1"] - real["mean_f1"]) < 0.0006
            and claimed["retrieve_correct"] == real["retrieve_correct"]
            and claimed["abstain_correct"] == real["abstain_correct"])


def _fmt(s: dict) -> str:
    return (f"mean set-F1 {s['mean_f1']:.3f}, retrieve_correct "
            f"{s['retrieve_correct']}, abstain_correct {s['abstain_correct']}")


def _arm(rows: list, name: str) -> dict:
    return {r["case_id"]: list(r["retrieved_ids"]) for r in rows
            if isinstance(r, dict) and r.get("arm") == name}


def _prior(prior: Path):
    """The prior, re-derived: (cases, helpful, {arm: ids per case})."""
    cases = {c["case_id"]: {"expect": c["expect"],
                            "store": {r["id"] for r in c["store"]}}
             for c in _load(prior / "corpus.jsonl", lines=True)}
    helpful = {c: set(_load(prior / "manifest.json")["helpful"][c])
               for c in cases}
    rows = _load(prior / "results.jsonl", lines=True)
    got = {name: _arm(rows, name) for name in (BM25, PI)}
    if not cases or any(set(g) != set(cases) for g in got.values()):
        raise ValueError(f"prior arms {BM25} and {PI} must cover the prior corpus")
    return cases, helpful, got


def _schema(decl, rows, verdict) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if _ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    for k in ("corpus_sha256", "manifest_sha256"):
        if not isinstance(decl.get(k), str):
            f.append(("SCHEMA", f"declaration.json needs {k}"))
    if decl.get("bm25_variant") not in VARIANTS:
        f.append(("SCHEMA", f"declaration.json needs bm25_variant: "
                  f"{' | '.join(VARIANTS)}"))
    if decl.get("s7_1_verdict") not in S71:
        f.append(("SCHEMA", f"declaration.json needs s7_1_verdict: "
                  f"{' | '.join(S71)}"))
    rule = decl.get("rule")
    m = rule.get("complementary_if_gain_at_least") if isinstance(rule, dict) else None
    if not isinstance(m, (int, float)) or isinstance(m, bool) or not 0 < m <= 1:
        f.append(("RULE-UNDECLARED", "declaration.json needs rule: "
                  "{complementary_if_gain_at_least: margin}, 0 < margin <= 1, "
                  "fixed before the run"))

    if not isinstance(rows, list) or not rows:
        f.append(("SCHEMA", "results.jsonl has no rows"))
    else:
        for i, r in enumerate(rows, 1):
            if not (isinstance(r, dict) and _ts(r.get("ts"))
                    and isinstance(r.get("arm"), str)
                    and isinstance(r.get("case_id"), str)
                    and _strs(r.get("retrieved_ids"))
                    and isinstance(r.get("declaration_sha256"), str)):
                f.append(("SCHEMA", f"results.jsonl row {i} needs ts, arm, "
                          "case_id, retrieved_ids, declaration_sha256"))
                break

    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if verdict.get("verdict") not in VERDICTS:
        f.append(("VERDICT-INVALID", f"verdict.json verdict must be one of "
                  f"{' / '.join(VERDICTS)}"))
    finding = verdict.get("finding")
    if not isinstance(finding, str) or len(finding.strip()) < 20:
        f.append(("VERDICT-NO-FINDING", "verdict.json needs finding: one "
                  "sentence that Decision Gate F can act on"))
    elif RANKING.search(finding):
        f.append(("RANKING-LANGUAGE", f"verdict.json finding ranks the engines "
                  f"({RANKING.search(finding).group(0)!r}). The row asks if the "
                  f"arms are complementary, not which one is ahead"))
    if "R-PF" not in str(verdict.get("feeds", "")):
        f.append(("GATE-F-NOT-NAMED", "verdict.json needs feeds, naming roadmap "
                  "R-PF (Decision Gate F option B)"))
    for k, arms in (("prior", (BM25, PI)), ("rerun", (BM25, PI, COMPOSE))):
        v = verdict.get(k)
        if not (isinstance(v, dict) and all(_is_score(v.get(KEY[a])) for a in arms)):
            f.append(("SCHEMA", f"verdict.json needs {k}: "
                      f"{{{', '.join(KEY[a] for a in arms)}}}, each {{mean_f1, "
                      "retrieve_correct, abstain_correct}"))
    o = verdict.get("overlap")
    if not (isinstance(o, dict) and all(_int(o.get(k)) for k in OVERLAP)):
        f.append(("SCHEMA", f"verdict.json needs overlap: "
                  f"{{{', '.join(OVERLAP)}}}, whole numbers of cases"))
    return f


def _bm25_reference(decl: dict, prefilter: Path, cases: dict, prior_bm25: dict):
    """(reference ids per case, finding or None) for the declared variant."""
    on_disk = None
    try:
        on_disk = _load(prefilter / "verdict.json").get("verdict")
    except Exception:
        pass
    variant, quoted = decl["bm25_variant"], decl["s7_1_verdict"]
    why = None
    if quoted != "not-landed" and quoted != on_disk:
        why = (f"s7_1_verdict says {quoted} and {prefilter.name}/verdict.json "
               f"says {on_disk}")
    elif variant == "prefilter" and on_disk != "artifact-confirmed":
        why = (f"bm25_variant prefilter needs {prefilter.name}/verdict.json to "
               f"say artifact-confirmed; it says {on_disk}")
    elif variant == "prior" and quoted == "artifact-confirmed":
        why = ("row S7-1 confirmed the abstention failure is a tokenizer "
               "artifact, so composing on the unfiltered arm composes on the "
               "artifact; use bm25_variant prefilter")
    ref = prior_bm25
    if variant == "prefilter" and not why:
        try:
            ref = _arm(_load(prefilter / "results.jsonl", lines=True),
                       "bm25-prefilter")
        except Exception:
            ref = {}
        if set(ref) != set(cases):
            why = (f"{prefilter.name}/results.jsonl has no complete "
                   f"`bm25-prefilter` arm to reproduce")
            ref = prior_bm25
    return ref, (("BM25-VARIANT-UNJUSTIFIED", why) if why else None)


def check(root: Path, prior: Path, prefilter: Path):
    try:
        cases, helpful, prior_got = _prior(prior)
    except Exception as e:
        return [("PRIOR-UNREADABLE", f"{prior}: {type(e).__name__}: {e}")], ""
    missing = [n for n in FILES if not (root / n).is_file()]
    if missing:
        return [("MISSING-FILE", f"{root}/{n}") for n in missing], ""
    try:
        decl = _load(root / "declaration.json")
        rows = _load(root / "results.jsonl", lines=True)
        verdict = _load(root / "verdict.json")
    except ValueError as e:
        return [("BAD-JSON", str(e))], ""
    f = _schema(decl, rows, verdict)
    if f:
        return f, ""

    # (a) the rule was fixed before the run, on the frozen corpus
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
    own = root / "corpus.jsonl"
    if decl["corpus_sha256"] != _sha(prior / "corpus.jsonl") or (
            own.is_file() and _sha(own) != decl["corpus_sha256"]):
        f.append(("CORPUS-NOT-FROZEN", f"corpus_sha256 must be the sha256 of "
                  f"{prior.name}/corpus.jsonl, and a local corpus.jsonl must "
                  f"be the same bytes"))
    if decl["manifest_sha256"] != _sha(prior / "manifest.json"):
        f.append(("MANIFEST-NOT-FROZEN", f"manifest_sha256 must be the sha256 "
                  f"of {prior.name}/manifest.json"))

    # (b) both arms re-measured and reproducing
    got: dict[str, dict] = {}
    for name in (BM25, PI, COMPOSE):
        mine = [r for r in rows if r["arm"] == name]
        if not mine:
            f.append(("ARM-MISSING", f"results.jsonl has no `{name}` rows"))
            continue
        seen = Counter(r["case_id"] for r in mine)
        if set(seen) != set(cases) or max(seen.values()) > 1:
            f.append(("ARM-INCOMPLETE", f"`{name}` must hold each of the "
                      f"{len(cases)} prior cases exactly once"))
            continue
        got[name] = _arm(mine, name)
        stray = sorted(c for c, ids in got[name].items()
                       if not set(ids) <= cases[c]["store"])
        if stray:
            f.append(("UNKNOWN-ID", f"`{name}` retrieved ids outside the "
                      f"case's store: {', '.join(stray)}"))
    if len(got) < 3:
        return f, ""
    bm25_ref, unjustified = _bm25_reference(decl, prefilter, cases,
                                            prior_got[BM25])
    if unjustified:
        f.append(unjustified)
    for name, ref in ((BM25, bm25_ref), (PI, prior_got[PI])):
        drift = sorted(c for c in cases if set(got[name][c]) != set(ref[c]))
        if drift:
            f.append(("ARM-NOT-REPRODUCED", f"`{name}` differs from its "
                      f"reference retrieval on {', '.join(drift)}: a compose "
                      f"gain cannot be told from harness drift"))

    # (c) the compose arm is the composition, and nothing else
    order = [r["arm"] for r in rows]
    if order.index(COMPOSE) < max(len(order) - 1 - order[::-1].index(a)
                                  for a in (BM25, PI)):
        f.append(("COMPONENTS-NOT-FIRST", f"every `{BM25}` and `{PI}` row must "
                  f"come before the first `{COMPOSE}` row"))
    wrong = sorted(c for c in cases if set(got[COMPOSE][c]) !=
                   (set(got[BM25][c]) if got[PI][c] else set()))
    if wrong:
        f.append(("COMPOSE-NOT-COMPOSED", f"on {', '.join(wrong)} `{COMPOSE}` "
                  f"is not: nothing where `{PI}` retrieved nothing, else "
                  f"exactly the `{BM25}` ids"))

    # (d) complementary rather than ranked, and the verdict the rule gives
    was = {a: _score(cases, helpful, prior_got[a]) for a in (BM25, PI)}
    now = {a: _score(cases, helpful, got[a]) for a in (BM25, PI, COMPOSE)}
    if f"{prior.name}/results.jsonl" not in str(verdict["prior"].get("source", "")):
        f.append(("PRIOR-NOT-CITED", f"verdict.json prior.source must name "
                  f"{prior.name}/results.jsonl"))
    for a in (BM25, PI):
        if not _same(verdict["prior"][KEY[a]], was[a]):
            f.append(("PRIOR-MISQUOTED", f"verdict.json prior.{KEY[a]} does not "
                      f"match the prior as recomputed: {_fmt(was[a])}"))
    for a in (BM25, PI, COMPOSE):
        if not _same(verdict["rerun"][KEY[a]], now[a]):
            f.append(("NUMBERS-DISAGREE", f"verdict.json rerun.{KEY[a]} does "
                      f"not match `{a}` as recomputed: {_fmt(now[a])}"))
    ok = {a: {c for c in cases if _correct(cases[c], helpful[c], got[a][c])}
          for a in (BM25, PI)}
    real = {"both": len(ok[BM25] & ok[PI]), "only_bm25": len(ok[BM25] - ok[PI]),
            "only_pi_lcm": len(ok[PI] - ok[BM25]),
            "neither": len(set(cases) - ok[BM25] - ok[PI])}
    if {k: verdict["overlap"][k] for k in OVERLAP} != real:
        f.append(("OVERLAP-DISAGREE", f"verdict.json overlap does not match "
                  f"the recomputed table of correct cases: {real}"))
    margin = decl["rule"]["complementary_if_gain_at_least"]
    gain = now[COMPOSE]["mean_f1"] - max(now[BM25]["mean_f1"], now[PI]["mean_f1"])
    rightful = VERDICTS[0] if gain >= margin - 1e-9 else VERDICTS[1]
    if verdict["verdict"] != rightful:
        f.append(("VERDICT-CONTRADICTS-RULE", f"compose gains {gain:+.3f} mean "
                  f"set-F1 over the better single arm and the declared margin "
                  f"is {margin}: the verdict must be {rightful}"))
    return f, (f"{rightful}, gain {gain:+.3f}; compose {_fmt(now[COMPOSE])}; "
               f"overlap {real}")


def run(root: Path, prior: Path, prefilter: Path) -> int:
    findings, summary = check(root, prior, prefilter)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S7-2 gate findings: {len(findings)}")
        return 1
    print(f"S7-2 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)
# case -> (expect, helpful, prior bm25 ids, prior pi-lcm ids)
_Q = {"c1": ("retrieve", ["c1-r2"], ["c1-r2"], ["c1-r2"]),
      "c2": ("retrieve", ["c2-r1"], ["c2-r1"], ["c2-r3"]),
      "c3": ("abstain", [], ["c3-r1"], []),
      "c4": ("abstain", [], ["c4-r3"], [])}


def _s(mean, r, a):
    return {"mean_f1": mean, "retrieve_correct": r, "abstain_correct": a}


def _fixture(complementary: bool = True) -> dict:
    """bm25 never abstains. pi-lcm always abstains rightly; on c2 it fires on
    the wrong record (compose can rescue it) or, in the honest negative, does
    not fire at all (compose inherits the miss)."""
    pi = {c: list(q[3]) for c, q in _Q.items()}
    if not complementary:
        pi["c2"] = []
    fx = {
        "decl": {"declared_at": _T0.isoformat(), "corpus_sha256": "AUTO",
                 "manifest_sha256": "AUTO", "bm25_variant": "prior",
                 "s7_1_verdict": "not-landed",
                 "rule": {"complementary_if_gain_at_least": 0.1}},
        "pi": pi, "s71": None, "raw": {}, "edit_after_run": False, "rows": [],
        "verdict": {
            "verdict": VERDICTS[0 if complementary else 1],
            "finding": "pi-lcm fires on the wrong record where bm25 has the "
                       "right one, so the composition recovers that case."
            if complementary else
            "pi-lcm does not fire where bm25 is right, so the composition "
            "adds nothing over pi-lcm alone on this corpus.",
            "feeds": "roadmap R-PF, Decision Gate F option B",
            "prior": {"source": "team/S6-SELECTIVITY/results.jsonl",
                      "bm25": _s(0.5, 2, 0), "pi_lcm": _s(0.75, 1, 2)},
            "rerun": {"bm25": _s(0.5, 2, 0), "pi_lcm": _s(0.75, 1, 2),
                      "compose": _s(1.0 if complementary else 0.75,
                                    2 if complementary else 1, 2)},
            "overlap": {"both": 1, "only_bm25": 1, "only_pi_lcm": 2,
                        "neither": 0}},
    }
    for name in (BM25, PI, COMPOSE):
        for c, q in _Q.items():
            ids = {BM25: q[2], PI: pi[c], COMPOSE: q[2] if pi[c] else []}[name]
            fx["rows"].append({"arm": name, "case_id": c,
                               "retrieved_ids": list(ids)})
    return fx


def _write(td: Path, fx: dict) -> tuple[Path, Path, Path]:
    prior, root = td / "S6-SELECTIVITY", td / "S7-COMPOSE"
    pre = td / "S7-BM25-PREFILTER"
    prior.mkdir()
    root.mkdir()
    (prior / "corpus.jsonl").write_text("".join(json.dumps({
        "case_id": c, "query": "q", "expect": q[0],
        "store": [{"id": f"{c}-r{i}", "text": "x"} for i in (1, 2, 3)]}) + "\n"
        for c, q in _Q.items()))
    (prior / "manifest.json").write_text(json.dumps(
        {"helpful": {c: q[1] for c, q in _Q.items()}}))
    (prior / "results.jsonl").write_text("".join(
        json.dumps({"arm": a, "case_id": c, "retrieved_ids": ids}) + "\n"
        for a, col in ((BM25, {c: q[2] for c, q in _Q.items()}), (PI, fx["pi"]))
        for c, ids in col.items()))
    if fx["s71"]:
        pre.mkdir()
        (pre / "verdict.json").write_text(json.dumps({"verdict": fx["s71"]}))
        (pre / "results.jsonl").write_text("".join(json.dumps(
            {"arm": "bm25-prefilter", "case_id": c,
             "retrieved_ids": [] if q[0] == "abstain" else q[2]}) + "\n"
            for c, q in _Q.items()))
    decl = fx["decl"]
    for k, name in (("corpus_sha256", "corpus.jsonl"),
                    ("manifest_sha256", "manifest.json")):
        if decl.get(k) == "AUTO":
            decl[k] = _sha(prior / name)
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = _sha(root / "declaration.json")
    out = []
    for i, r in enumerate(fx["rows"], 1):
        r = dict(r)
        r.setdefault("ts", (_T0 + timedelta(seconds=i)).isoformat())
        r.setdefault("declaration_sha256", sha)
        out.append(json.dumps(r) + "\n")
    (root / "results.jsonl").write_text("".join(out))
    (root / "verdict.json").write_text(json.dumps(fx["verdict"]))
    if fx["edit_after_run"]:  # the margin moved once the numbers were seen
        decl["rule"]["complementary_if_gain_at_least"] = 0.2
        (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, prior, pre


def _row(fx, arm, case):
    return next(r for r in fx["rows"] if r["arm"] == arm and r["case_id"] == case)


def _prefiltered(fx, verdict="artifact-confirmed"):
    """A conforming run on row S7-1's prefiltered bm25 arm."""
    fx["s71"] = verdict
    fx["decl"].update(bm25_variant="prefilter", s7_1_verdict=verdict)
    for c in ("c3", "c4"):
        _row(fx, BM25, c)["retrieved_ids"] = []
    fx["verdict"].update(verdict=VERDICTS[1], finding="with the prefilter bm25 "
                         "already abstains, so the composition adds nothing "
                         "over bm25 alone on this corpus.")
    fx["verdict"]["rerun"]["bm25"] = _s(1.0, 2, 2)
    fx["verdict"]["overlap"] = {"both": 3, "only_bm25": 1, "only_pi_lcm": 0,
                                "neither": 0}


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_edit(fx): fx["edit_after_run"] = True
def _m_norule(fx): del fx["decl"]["rule"]
def _m_zero(fx): fx["decl"]["rule"]["complementary_if_gain_at_least"] = 0
def _m_corpus(fx): fx["decl"]["corpus_sha256"] = "0" * 64
def _m_manifest(fx): fx["decl"]["manifest_sha256"] = "0" * 64
def _m_quoted(fx): fx["rows"] = [r for r in fx["rows"] if r["arm"] != PI]
def _m_short(fx): fx["rows"].remove(_row(fx, COMPOSE, "c4"))
def _m_twice(fx): fx["rows"].append(dict(_row(fx, COMPOSE, "c4")))
def _m_order(fx): fx["rows"].reverse()
def _m_drift(fx): _row(fx, BM25, "c3")["retrieved_ids"] = ["c3-r2"]
def _m_uncited(fx): fx["verdict"]["prior"]["source"] = "an earlier run"
def _m_misquote(fx): fx["verdict"]["prior"]["pi_lcm"] = _s(0.9, 2, 2)
def _m_numbers(fx): fx["verdict"]["rerun"]["compose"]["retrieve_correct"] = 1
def _m_overlap(fx): fx["verdict"]["overlap"].update(both=4, only_bm25=0,
                                                    only_pi_lcm=0)
def _m_flip(fx): fx["verdict"]["verdict"] = VERDICTS[1]
def _m_maybe(fx): fx["verdict"]["verdict"] = "promising"
def _m_nofinding(fx): fx["verdict"]["finding"] = ""
def _m_ranked(fx): fx["verdict"]["finding"] = ("pi-lcm beats bm25 on this "
                                               "corpus, so adopt pi-lcm.")
def _m_nofeeds(fx): del fx["verdict"]["feeds"]
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["declaration.json"] = None
def _m_variant_alone(fx): _prefiltered(fx); fx["s71"] = None
def _m_variant_refuted(fx): _prefiltered(fx, "artifact-refuted")
def _m_s71_misquoted(fx): fx["s71"] = "artifact-confirmed"; \
    fx["decl"]["s7_1_verdict"] = "artifact-refuted"
def _m_s71_ignored(fx): fx["s71"] = "artifact-confirmed"; \
    fx["decl"]["s7_1_verdict"] = "artifact-confirmed"


def _m_stray(fx):
    _row(fx, PI, "c2")["retrieved_ids"] = ["c9-r1"]


def _m_improved(fx):  # compose hand-edited away from the composition
    _row(fx, COMPOSE, "c4")["retrieved_ids"] = ["c4-r3"]


def _m_receipts(fx):  # every file exists and says nothing
    fx["raw"] = {n: "{}\n" for n in FILES}


def _m_claimed_win(fx):  # honest negative data, a win written over it
    fx.update(copy.deepcopy(_fixture(complementary=False)), verdict=fx["verdict"])


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "margin moved after the run": (_m_edit, {"RESULTS-NOT-BOUND"}),
    "no verdict rule": (_m_norule, {"RULE-UNDECLARED"}),
    "margin of zero": (_m_zero, {"RULE-UNDECLARED"}),
    "other corpus": (_m_corpus, {"CORPUS-NOT-FROZEN"}),
    "other manifest": (_m_manifest, {"MANIFEST-NOT-FROZEN"}),
    "pi-lcm quoted, not re-measured": (_m_quoted, {"ARM-MISSING"}),
    "a case dropped": (_m_short, {"ARM-INCOMPLETE"}),
    "a case run twice": (_m_twice, {"ARM-INCOMPLETE"}),
    "id from another store": (_m_stray, {"UNKNOWN-ID", "ARM-NOT-REPRODUCED"}),
    "compose before its components": (_m_order, {"COMPONENTS-NOT-FIRST"}),
    "bm25 drifts from prior": (_m_drift, {"ARM-NOT-REPRODUCED"}),
    "compose hand-edited": (_m_improved, {"COMPOSE-NOT-COMPOSED",
                                          "NUMBERS-DISAGREE",
                                          "VERDICT-CONTRADICTS-RULE"}),
    "prior not cited": (_m_uncited, {"PRIOR-NOT-CITED"}),
    "prior misquoted": (_m_misquote, {"PRIOR-MISQUOTED"}),
    "re-run numbers wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "overlap table wrong": (_m_overlap, {"OVERLAP-DISAGREE"}),
    "verdict against the rule": (_m_flip, {"VERDICT-CONTRADICTS-RULE"}),
    "win claimed over negative data": (_m_claimed_win,
                                       {"NUMBERS-DISAGREE",
                                        "VERDICT-CONTRADICTS-RULE"}),
    "verdict not in vocabulary": (_m_maybe, {"VERDICT-INVALID"}),
    "verdict without finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "finding ranks the engines": (_m_ranked, {"RANKING-LANGUAGE"}),
    "decision not named": (_m_nofeeds, {"GATE-F-NOT-NAMED"}),
    "prefilter variant, no S7-1 verdict": (_m_variant_alone,
                                           {"BM25-VARIANT-UNJUSTIFIED",
                                            "ARM-NOT-REPRODUCED"}),
    "prefilter variant, S7-1 refuted": (_m_variant_refuted,
                                        {"BM25-VARIANT-UNJUSTIFIED",
                                         "ARM-NOT-REPRODUCED"}),
    "S7-1 verdict misquoted": (_m_s71_misquoted, {"BM25-VARIANT-UNJUSTIFIED"}),
    "S7-1 confirmed, composed unfiltered": (_m_s71_ignored,
                                            {"BM25-VARIANT-UNJUSTIFIED"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _cli(root: Path, prior: Path, pre: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, __file__, str(root), "--prior",
                        str(prior), "--prefilter", str(pre)],
                       capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr


def _selftest() -> int:
    marker = re.compile(r"^\[([A-Z][A-Z0-9-]+)\]", re.M)
    bad: list[str] = []

    def case(name, fx, want):
        with tempfile.TemporaryDirectory() as td:
            rc, text = _cli(*_write(Path(td), fx))
        got = set(marker.findall(text))
        if "Traceback (most recent call last)" in text:
            bad.append(f"{name}: traceback")
        elif want is None and (rc != 0 or got or "gate findings" in text):
            bad.append(f"{name}: should be ACCEPTED, got exit {rc} {sorted(got)}")
        elif want is not None and (rc != 1 or not want(got)
                                   or "S7-2 gate findings: " not in text):
            bad.append(f"{name}: wrong rejection, got exit {rc} {sorted(got)}")

    case("conforming, complementary", _fixture(True), None)
    case("conforming, honestly not complementary", _fixture(False), None)
    pre = _fixture(True)
    _prefiltered(pre)
    case("conforming, on the S7-1 prefiltered arm", pre, None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, lambda got, want=want: got == want)
    with tempfile.TemporaryDirectory() as td:
        root, prior, pre_dir = _write(Path(td), _fixture())
        (prior / "results.jsonl").write_text("")
        rc, text = _cli(root, prior, pre_dir)
        if rc != 1 or "[PRIOR-UNREADABLE]" not in text or "Traceback" in text:
            bad.append(f"unreadable prior: got exit {rc}")

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (3 conforming fixtures accepted, one of them an "
          f"honest negative; a receipts-only directory, an unreadable prior "
          f"and {len(_MUTANTS)} mutants each rejected by exactly their own "
          f"markers, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S7-2")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--prior", default=str(HERE.parent / "S6-SELECTIVITY"))
    ap.add_argument("--prefilter", default=str(HERE.parent / "S7-BM25-PREFILTER"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.prior), Path(a.prefilter))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S7-2 gate findings: 1")
        raise SystemExit(1)
