#!/usr/bin/env python3
"""Gate for QUEUE row S7-1 (declared stopword prefilter, S6-2 bm25 arm re-run).

plumb-fable, row S7-1G, 2026-09-17. Written FROM ROW S7-1's TEXT ALONE, while
`team/S7-BM25-PREFILTER/` did not exist. Read for this gate: the board row, and
the PRIOR measurement the row cites (team/S6-SELECTIVITY: corpus, manifest,
results schema). The interface below is declared by the gate, not fitted to a
document; every finding names what it wants.

This gate is an INSTRUMENT. It trusts no number in the artifact: it recomputes
the prior from team/S6-SELECTIVITY and the re-run from results.jsonl, and it
checks the VALUES the prefilter produced, not a claim that it ran.

Declared interface (ROOT = team/S7-BM25-PREFILTER, PRIOR = team/S6-SELECTIVITY)
  declaration.json  {declared_at (ISO), stopwords: [lowercase words],
                    source (where the list came from, written down so the list
                    is chosen for provenance, not for fit),
                    addresses (names PRIOR/review.json, the recorded deviation),
                    corpus_sha256, manifest_sha256 (the PRIOR files, frozen),
                    rule: {artifact_if_abstain_at_least: N}}
  results.jsonl     one row per line, IN RUN ORDER: {ts (ISO), arm, case_id,
                    retrieved_ids, query_tokens (the tokens bm25 really scored),
                    declaration_sha256}. Arms `bm25-nofilter` (control) and
                    `bm25-prefilter`. Other arms are allowed and only bound.
  verdict.json      {verdict: "artifact-confirmed" | "artifact-refuted", finding,
                    prior: {source, mean_f1, retrieve_correct, abstain_correct},
                    rerun: {mean_f1, retrieve_correct, abstain_correct}}
                    This is the file rank 2 reads.

What the row turns on (marker in brackets)
  (a) The prefilter is DECLARED BEFORE the re-run, so nobody can suspect
      post-run tuning. declared_at precedes every result
      [DECLARED-AFTER-RESULTS]; every result row embeds the sha256 of the
      declaration bytes, so one edited stopword after the run breaks the chain
      [RESULTS-NOT-BOUND]; the list is real and sourced [PREFILTER-UNDECLARED]
      [PREFILTER-UNSOURCED]; the verdict rule is fixed in the declaration, not
      after the numbers [RULE-UNDECLARED]; corpus and manifest are the PRIOR
      ones, byte for byte [CORPUS-NOT-FROZEN] [MANIFEST-NOT-FROZEN]; the
      recorded deviation is named [DEVIATION-NOT-CITED].
  (b) It re-measures EXACTLY that arm. The unfiltered control runs first
      [CONTROL-NOT-FIRST] and reproduces the prior bm25 retrieval per case
      [CONTROL-NOT-REPRODUCED]; else a difference is harness drift, not the
      prefilter. Both arms cover every case once [ARM-MISSING] [ARM-INCOMPLETE]
      with ids from the case's store [UNKNOWN-ID].
  (c) The prefilter really ran, shown by values. Per case the prefilter arm's
      query_tokens equal the control's tokens minus the declared stopwords
      [PREFILTER-NOT-APPLIED]; at least one query loses a token, else the
      tokenizer question was never tested [PREFILTER-VACUOUS]; no query is
      filtered to nothing, because an abstention made by deleting the question
      is not selectivity [QUERY-EMPTIED].
  (d) The verdict follows from the numbers. The gate recomputes, per arm, mean
      set-F1 against the PRIOR manifest (an abstain case scores 1 only on an
      empty retrieval), retrieve_correct (retrieve cases whose helpful set is
      fully retrieved) and abstain_correct (abstain cases with nothing
      retrieved). verdict.json must cite the prior [PRIOR-NOT-CITED], quote it
      as recomputed [PRIOR-MISQUOTED], report the re-run as recomputed
      [NUMBERS-DISAGREE], and hold the verdict the declared rule gives:
      confirmed if and only if abstain_correct >= N [VERDICT-CONTRADICTS-RULE],
      with a finding [VERDICT-NO-FINDING]. `artifact-refuted` is a PASS: an
      honest negative is a completed result.
  other  [MISSING-FILE] [BAD-JSON] [SCHEMA] [VERDICT-INVALID] [PRIOR-UNREADABLE]

Limits, stated on purpose: timestamps and query_tokens are self-reported and a
hash chain can be rebuilt by someone who sets out to. The gate cannot tell if
the stopword list was fitted to these ten queries, or that the run cost $0 and
stayed local. Those stay with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S7-1 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT] [--prior DIR]
  python3 check.py --selftest  # proves the gate can fail, and can pass
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("declaration.json", "results.jsonl", "verdict.json")
CONTROL, FILTERED = "bm25-nofilter", "bm25-prefilter"
VERDICTS = ("artifact-confirmed", "artifact-refuted")
NUMS = ("mean_f1", "retrieve_correct", "abstain_correct")


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


def _score(cases: dict, helpful: dict, got: dict) -> dict:
    return {
        "mean_f1": sum(_f1(helpful[c], set(got[c])) for c in cases) / len(cases),
        "retrieve_correct": sum(1 for c, v in cases.items() if v["expect"] ==
                                "retrieve" and helpful[c] <= set(got[c])),
        "abstain_correct": sum(1 for c, v in cases.items() if v["expect"] ==
                               "abstain" and not got[c]),
    }


def _same(claimed: dict, real: dict) -> bool:
    return (abs(claimed["mean_f1"] - real["mean_f1"]) < 0.0006
            and claimed["retrieve_correct"] == real["retrieve_correct"]
            and claimed["abstain_correct"] == real["abstain_correct"])


def _fmt(s: dict) -> str:
    return (f"mean set-F1 {s['mean_f1']:.3f}, retrieve_correct "
            f"{s['retrieve_correct']}, abstain_correct {s['abstain_correct']}")


def _prior(prior: Path):
    """The prior measurement, re-derived: (cases, helpful, bm25 ids per case)."""
    corpus = _load(prior / "corpus.jsonl", lines=True)
    cases = {c["case_id"]: {"expect": c["expect"],
                            "store": {r["id"] for r in c["store"]}}
             for c in corpus}
    helpful = {c: set(_load(prior / "manifest.json")["helpful"][c])
               for c in cases}
    got = {r["case_id"]: list(r["retrieved_ids"])
           for r in _load(prior / "results.jsonl", lines=True)
           if r.get("arm") == "bm25"}
    if not cases or set(got) != set(cases):
        raise ValueError("prior bm25 arm does not cover the prior corpus")
    return cases, helpful, got


def _schema(decl, rows, verdict, prior: Path) -> list[tuple[str, str]]:
    f: list[tuple[str, str]] = []
    if not isinstance(decl, dict):
        return [("SCHEMA", "declaration.json must be an object")]
    if _ts(decl.get("declared_at")) is None:
        f.append(("SCHEMA", "declaration.json needs declared_at (ISO time)"))
    sw = decl.get("stopwords")
    if not _strs(sw) or not sw or any(not w or w != w.lower().strip()
                                      for w in sw):
        f.append(("PREFILTER-UNDECLARED", "declaration.json needs stopwords: a "
                  "non-empty list of lowercase words, the list itself and not "
                  "a pointer to it"))
    if not isinstance(decl.get("source"), str) or len(decl["source"].strip()) < 8:
        f.append(("PREFILTER-UNSOURCED", "declaration.json needs source: where "
                  "the stopword list came from (file, version or hash)"))
    if f"{prior.name}/review.json" not in str(decl.get("addresses", "")):
        f.append(("DEVIATION-NOT-CITED", "declaration.json needs addresses, "
                  f"naming {prior.name}/review.json where the deviation is "
                  "recorded"))
    for k in ("corpus_sha256", "manifest_sha256"):
        if not isinstance(decl.get(k), str):
            f.append(("SCHEMA", f"declaration.json needs {k}"))
    rule = decl.get("rule")
    n = rule.get("artifact_if_abstain_at_least") if isinstance(rule, dict) else None
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        f.append(("RULE-UNDECLARED", "declaration.json needs rule: "
                  "{artifact_if_abstain_at_least: N}, N a whole number >= 1, "
                  "fixed before the run"))

    if not isinstance(rows, list) or not rows:
        f.append(("SCHEMA", "results.jsonl has no rows"))
    else:
        for i, r in enumerate(rows, 1):
            if not (isinstance(r, dict) and _ts(r.get("ts"))
                    and isinstance(r.get("arm"), str)
                    and isinstance(r.get("case_id"), str)
                    and _strs(r.get("retrieved_ids"))
                    and _strs(r.get("query_tokens"))
                    and isinstance(r.get("declaration_sha256"), str)):
                f.append(("SCHEMA", f"results.jsonl row {i} needs ts, arm, "
                          "case_id, retrieved_ids, query_tokens, "
                          "declaration_sha256"))
                break

    if not isinstance(verdict, dict):
        return f + [("SCHEMA", "verdict.json must be an object")]
    if verdict.get("verdict") not in VERDICTS:
        f.append(("VERDICT-INVALID", f"verdict.json verdict must be one of "
                  f"{' / '.join(VERDICTS)}"))
    if not isinstance(verdict.get("finding"), str) \
            or len(verdict["finding"].strip()) < 20:
        f.append(("VERDICT-NO-FINDING", "verdict.json needs finding: one "
                  "sentence that rank 2 can act on"))
    for k in ("prior", "rerun"):
        v = verdict.get(k)
        if not (isinstance(v, dict)
                and isinstance(v.get("mean_f1"), (int, float))
                and all(isinstance(v.get(x), int) for x in NUMS[1:])
                and not any(isinstance(v.get(x), bool) for x in NUMS)):
            f.append(("SCHEMA", f"verdict.json needs {k}: {{mean_f1, "
                      "retrieve_correct, abstain_correct}"))
    return f


def check(root: Path, prior: Path) -> tuple[list[tuple[str, str]], str]:
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
    f = _schema(decl, rows, verdict, prior)
    if f:
        return f, ""

    # (a) declared before the re-run, and frozen
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
    n_abstain = sum(1 for v in cases.values() if v["expect"] == "abstain")
    need = decl["rule"]["artifact_if_abstain_at_least"]
    if need > n_abstain:
        f.append(("RULE-UNDECLARED", f"rule asks for {need} abstentions and "
                  f"the corpus has {n_abstain} abstain cases: it cannot be met"))

    # (b) exactly that arm: both arms complete, control first and reproducing
    arm: dict[str, dict] = {}
    for name in (CONTROL, FILTERED):
        mine = [r for r in rows if r["arm"] == name]
        if not mine:
            f.append(("ARM-MISSING", f"results.jsonl has no `{name}` rows"))
            continue
        seen = Counter(r["case_id"] for r in mine)
        if set(seen) != set(cases) or max(seen.values()) > 1:
            f.append(("ARM-INCOMPLETE", f"`{name}` must hold each of the "
                      f"{len(cases)} prior cases exactly once"))
            continue
        arm[name] = {r["case_id"]: r for r in mine}
        stray = [r["case_id"] for r in mine
                 if not set(r["retrieved_ids"]) <= cases[r["case_id"]]["store"]]
        if stray:
            f.append(("UNKNOWN-ID", f"`{name}` retrieved ids outside the "
                      f"case's store: {', '.join(sorted(stray))}"))
    if len(arm) < 2:
        return f, ""
    order = [r["arm"] for r in rows]
    last_control = len(order) - 1 - order[::-1].index(CONTROL)
    if last_control > order.index(FILTERED):
        f.append(("CONTROL-NOT-FIRST", f"every `{CONTROL}` row must come "
                  f"before the first `{FILTERED}` row"))
    drift = sorted(c for c in cases if set(arm[CONTROL][c]["retrieved_ids"])
                   != set(prior_got[c]))
    if drift:
        f.append(("CONTROL-NOT-REPRODUCED", f"`{CONTROL}` differs from the "
                  f"prior bm25 retrieval on {', '.join(drift)}: a change in "
                  f"the re-run cannot be put on the prefilter"))

    # (c) the prefilter really ran, by the values it produced
    stop = set(decl["stopwords"])
    unfiltered = sorted(
        c for c in cases if arm[FILTERED][c]["query_tokens"]
        != [t for t in arm[CONTROL][c]["query_tokens"] if t.lower() not in stop])
    if unfiltered:
        f.append(("PREFILTER-NOT-APPLIED", f"`{FILTERED}` query_tokens are not "
                  f"the `{CONTROL}` tokens minus the declared stopwords on "
                  f"{', '.join(unfiltered)}"))
    elif all(arm[FILTERED][c]["query_tokens"] == arm[CONTROL][c]["query_tokens"]
             for c in cases):
        f.append(("PREFILTER-VACUOUS", "no query lost a token: the declared "
                  "list touches nothing, so the tokenizer question is untested"))
    emptied = sorted(c for c in cases if not arm[FILTERED][c]["query_tokens"])
    if emptied:
        f.append(("QUERY-EMPTIED", f"the prefilter deleted the whole query on "
                  f"{', '.join(emptied)}: that abstention is not selectivity"))

    # (d) the verdict follows from the recomputed numbers
    was = _score(cases, helpful, prior_got)
    now = _score(cases, helpful,
                 {c: arm[FILTERED][c]["retrieved_ids"] for c in cases})
    if f"{prior.name}/results.jsonl" not in str(verdict["prior"].get("source", "")):
        f.append(("PRIOR-NOT-CITED", f"verdict.json prior.source must name "
                  f"{prior.name}/results.jsonl"))
    if not _same(verdict["prior"], was):
        f.append(("PRIOR-MISQUOTED", f"verdict.json prior does not match the "
                  f"prior as recomputed: {_fmt(was)}"))
    if not _same(verdict["rerun"], now):
        f.append(("NUMBERS-DISAGREE", f"verdict.json rerun does not match "
                  f"`{FILTERED}` as recomputed: {_fmt(now)}"))
    rightful = VERDICTS[0] if now["abstain_correct"] >= need else VERDICTS[1]
    if verdict["verdict"] != rightful:
        f.append(("VERDICT-CONTRADICTS-RULE", f"abstain_correct is "
                  f"{now['abstain_correct']} and the declared rule needs "
                  f"{need}: the verdict must be {rightful}"))
    return f, (f"{rightful}; prior {_fmt(was)}; `{FILTERED}` {_fmt(now)}")


def run(root: Path, prior: Path) -> int:
    findings, summary = check(root, prior)
    for marker, msg in findings:
        print(f"[{marker}] {msg}")
    if findings:
        print(f"S7-1 gate findings: {len(findings)}")
        return 1
    print(f"S7-1 gate: clean ({summary})")
    return 0


# ---- selftest: prove the gate can fail, and can pass ----

_T0 = datetime(2026, 9, 18, 17, 0, tzinfo=timezone.utc)
_Q = {"c1": ("retrieve", ["what", "is", "the", "port"], ["c1-r2"], ["c1-r2"]),
      "c2": ("retrieve", ["which", "is", "the", "owner"], ["c2-r1"], ["c2-r1"]),
      "c3": ("abstain", ["what", "is", "the", "warranty"], [], ["c3-r1"]),
      "c4": ("abstain", ["who", "is", "the", "florist"], [], ["c4-r3"])}


def _fixture(confirmed: bool = True) -> dict:
    """Four cases; the prior bm25 retrieves on all four, so it never abstains."""
    fx = {
        "decl": {"declared_at": _T0.isoformat(),
                 "stopwords": ["what", "which", "who", "is", "the"],
                 "source": "fixture stoplist v1, sha 0123abcd",
                 "addresses": "deviation recorded in S6-SELECTIVITY/review.json",
                 "corpus_sha256": "AUTO", "manifest_sha256": "AUTO",
                 "rule": {"artifact_if_abstain_at_least": 1}},
        "rows": [], "raw": {}, "edit_after_run": False,
        "verdict": {"verdict": VERDICTS[0 if confirmed else 1],
                    "finding": "bm25 abstains once stopwords are removed, so "
                               "the failure was a tokenizer artifact."
                    if confirmed else
                    "bm25 still retrieves on every abstain case under the "
                    "declared prefilter, so it is not a tokenizer artifact.",
                    "prior": {"source": "team/S6-SELECTIVITY/results.jsonl",
                              "mean_f1": 0.5, "retrieve_correct": 2,
                              "abstain_correct": 0},
                    "rerun": {"mean_f1": 1.0 if confirmed else 0.5,
                              "retrieve_correct": 2,
                              "abstain_correct": 2 if confirmed else 0}},
    }
    for name in (CONTROL, FILTERED):
        for c, (expect, toks, _, got) in _Q.items():
            fx["rows"].append({
                "arm": name, "case_id": c, "query_tokens": list(toks),
                "retrieved_ids": [] if (name == FILTERED and confirmed
                                        and expect == "abstain") else list(got)})
    return fx


def _write(td: Path, fx: dict) -> tuple[Path, Path]:
    prior, root = td / "S6-SELECTIVITY", td / "S7-BM25-PREFILTER"
    prior.mkdir()
    root.mkdir()
    (prior / "corpus.jsonl").write_text("".join(json.dumps({
        "case_id": c, "query": " ".join(toks), "expect": expect,
        "store": [{"id": f"{c}-r{i}", "text": "x"} for i in (1, 2, 3)]}) + "\n"
        for c, (expect, toks, _, _) in _Q.items()))
    (prior / "manifest.json").write_text(json.dumps(
        {"helpful": {c: h for c, (_, _, h, _) in _Q.items()}}))
    (prior / "results.jsonl").write_text("".join(json.dumps(
        {"arm": "bm25", "case_id": c, "retrieved_ids": got}) + "\n"
        for c, (_, _, _, got) in _Q.items()))
    decl = fx["decl"]
    for k, name in (("corpus_sha256", "corpus.jsonl"),
                    ("manifest_sha256", "manifest.json")):
        if decl.get(k) == "AUTO":
            decl[k] = _sha(prior / name)
    (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    sha = _sha(root / "declaration.json")
    stop = set(decl.get("stopwords") or [])
    out = []
    for i, r in enumerate(fx["rows"], 1):
        r = dict(r)
        r.setdefault("ts", (_T0 + timedelta(seconds=i)).isoformat())
        r.setdefault("declaration_sha256", sha)
        if r["arm"] == FILTERED and not r.pop("keep_tokens", False):
            r["query_tokens"] = [t for t in r["query_tokens"] if t not in stop]
        out.append(json.dumps(r) + "\n")
    (root / "results.jsonl").write_text("".join(out))
    (root / "verdict.json").write_text(json.dumps(fx["verdict"]))
    if fx["edit_after_run"]:  # one more stopword, after the numbers were seen
        decl["stopwords"] = decl["stopwords"] + ["warranty"]
        (root / "declaration.json").write_text(json.dumps(decl, indent=1))
    for name, text in fx["raw"].items():
        if text is None:
            (root / name).unlink()
        else:
            (root / name).write_text(text)
    return root, prior


def _rows(fx, arm, case=None):
    return [r for r in fx["rows"] if r["arm"] == arm and case in (None, r["case_id"])]


def _m_late(fx): fx["decl"]["declared_at"] = (_T0 + timedelta(hours=1)).isoformat()
def _m_edit(fx): fx["edit_after_run"] = True
def _m_nolist(fx): fx["decl"]["stopwords"] = []
def _m_pointer(fx): fx["decl"]["stopwords"] = "see index.ts"
def _m_nosource(fx): fx["decl"]["source"] = ""
def _m_nodev(fx): fx["decl"]["addresses"] = "the known deviation"
def _m_norule(fx): del fx["decl"]["rule"]
def _m_rule_big(fx): fx["decl"]["rule"]["artifact_if_abstain_at_least"] = 9
def _m_corpus(fx): fx["decl"]["corpus_sha256"] = "0" * 64
def _m_manifest(fx): fx["decl"]["manifest_sha256"] = "0" * 64
def _m_noarm(fx): fx["rows"] = _rows(fx, FILTERED)
def _m_short(fx): fx["rows"].remove(_rows(fx, FILTERED, "c4")[0])
def _m_twice(fx): fx["rows"].append(dict(_rows(fx, FILTERED, "c4")[0]))
def _m_stray(fx): _rows(fx, FILTERED, "c1")[0]["retrieved_ids"] = ["c9-r1"]
def _m_order(fx): fx["rows"].reverse()
def _m_drift(fx): _rows(fx, CONTROL, "c3")[0]["retrieved_ids"] = ["c3-r2"]
def _m_unapplied(fx): _rows(fx, FILTERED, "c3")[0]["keep_tokens"] = True
def _m_vacuous(fx): fx["decl"]["stopwords"] = ["zzz"]
def _m_emptied(fx): fx["decl"]["stopwords"] += ["warranty"]
def _m_uncited(fx): fx["verdict"]["prior"]["source"] = "an earlier run"
def _m_misquote(fx): fx["verdict"]["prior"]["mean_f1"] = 0.3
def _m_numbers(fx): fx["verdict"]["rerun"]["abstain_correct"] = 1
def _m_flip(fx): fx["verdict"]["verdict"] = VERDICTS[1]
def _m_maybe(fx): fx["verdict"]["verdict"] = "promising"
def _m_nofinding(fx): fx["verdict"]["finding"] = ""
def _m_badjson(fx): fx["raw"]["verdict.json"] = "{not json"
def _m_hostile(fx): fx["raw"]["results.jsonl"] = "[1, 2]\n\"x\"\nnull\n"
def _m_nofile(fx): fx["raw"]["declaration.json"] = None


def _m_receipts(fx):  # every file exists and says nothing
    fx["raw"] = {n: "{}\n" for n in FILES}


def _m_claimed_win(fx):  # honest data, a confirmed verdict written over it
    fx.update(copy.deepcopy(_fixture(confirmed=False)), verdict=fx["verdict"])


# name -> (mutation, markers that must be EXACTLY the ones raised)
_MUTANTS = {
    "declared after the run": (_m_late, {"DECLARED-AFTER-RESULTS"}),
    "stopword added after the run": (_m_edit, {"RESULTS-NOT-BOUND",
                                               "PREFILTER-NOT-APPLIED"}),
    "empty stopword list": (_m_nolist, {"PREFILTER-UNDECLARED"}),
    "list is a pointer": (_m_pointer, {"PREFILTER-UNDECLARED"}),
    "list has no source": (_m_nosource, {"PREFILTER-UNSOURCED"}),
    "deviation not named": (_m_nodev, {"DEVIATION-NOT-CITED"}),
    "no verdict rule": (_m_norule, {"RULE-UNDECLARED"}),
    "rule cannot be met": (_m_rule_big, {"RULE-UNDECLARED",
                                         "VERDICT-CONTRADICTS-RULE"}),
    "other corpus": (_m_corpus, {"CORPUS-NOT-FROZEN"}),
    "other manifest": (_m_manifest, {"MANIFEST-NOT-FROZEN"}),
    "no control arm": (_m_noarm, {"ARM-MISSING"}),
    "a case dropped": (_m_short, {"ARM-INCOMPLETE"}),
    "a case run twice": (_m_twice, {"ARM-INCOMPLETE"}),
    "id from another store": (_m_stray, {"UNKNOWN-ID", "NUMBERS-DISAGREE"}),
    "control after the re-run": (_m_order, {"CONTROL-NOT-FIRST"}),
    "control drifts from prior": (_m_drift, {"CONTROL-NOT-REPRODUCED"}),
    "prefilter not applied": (_m_unapplied, {"PREFILTER-NOT-APPLIED"}),
    "prefilter touches nothing": (_m_vacuous, {"PREFILTER-VACUOUS"}),
    "query filtered to nothing": (_m_emptied, {"QUERY-EMPTIED"}),
    "prior not cited": (_m_uncited, {"PRIOR-NOT-CITED"}),
    "prior misquoted": (_m_misquote, {"PRIOR-MISQUOTED"}),
    "re-run numbers wrong": (_m_numbers, {"NUMBERS-DISAGREE"}),
    "verdict against the rule": (_m_flip, {"VERDICT-CONTRADICTS-RULE"}),
    "win claimed over refuting data": (_m_claimed_win,
                                       {"NUMBERS-DISAGREE",
                                        "VERDICT-CONTRADICTS-RULE"}),
    "verdict not in vocabulary": (_m_maybe, {"VERDICT-INVALID"}),
    "verdict without finding": (_m_nofinding, {"VERDICT-NO-FINDING"}),
    "broken json": (_m_badjson, {"BAD-JSON"}),
    "hostile results": (_m_hostile, {"SCHEMA"}),
    "file missing": (_m_nofile, {"MISSING-FILE"}),
}


def _cli(root: Path, prior: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, __file__, str(root), "--prior",
                        str(prior)], capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout + p.stderr


def _selftest() -> int:
    import re
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
                                   or "S7-1 gate findings: " not in text):
            bad.append(f"{name}: wrong rejection, got exit {rc} {sorted(got)}")

    case("conforming, artifact confirmed", _fixture(True), None)
    case("conforming, honestly refuted", _fixture(False), None)
    receipts = _fixture()
    _m_receipts(receipts)
    case("receipts only: all files present, no substance", receipts,
         lambda got: len(got) >= 3 and "MISSING-FILE" not in got)
    for name, (mutate, want) in _MUTANTS.items():
        fx = _fixture()
        mutate(fx)
        case(name, fx, lambda got, want=want: got == want)
    with tempfile.TemporaryDirectory() as td:
        root, prior = _write(Path(td), _fixture())
        (prior / "results.jsonl").write_text("")
        rc, text = _cli(root, prior)
        if rc != 1 or "[PRIOR-UNREADABLE]" not in text or "Traceback" in text:
            bad.append(f"unreadable prior: got exit {rc}")

    for b in bad:
        print(f"selftest FAIL: {b}")
    if bad:
        return 1
    print(f"selftest: PASS (2 conforming fixtures accepted, one of them an "
          f"honest refutation; a receipts-only directory, an unreadable prior "
          f"and {len(_MUTANTS)} mutants each rejected by exactly their own "
          f"markers, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S7-1")
    ap.add_argument("root", nargs="?", default=str(HERE))
    ap.add_argument("--prior", default=str(HERE.parent / "S6-SELECTIVITY"))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    return run(Path(a.root), Path(a.prior))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:  # the contract: a verdict, never a traceback
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S7-1 gate findings: 1")
        raise SystemExit(1)
