#!/usr/bin/env python3
"""Gate for QUEUE row S6-2 (an invocation instrument that can REJECT
indiscriminate retrieval).

plumb-fable, row S6-2G, 2026-09-17. Written FROM ROW S6-2's TEXT ALONE, before
any S6-2 artifact existed (`team/S6-SELECTIVITY/` was absent). The interface
below is declared by the gate, not fitted to a document; every finding names what
it wants, so the author can conform without reading this source.

Declared interface
  corpus.jsonl   one case per line: {case_id, query, expect: "retrieve"|"abstain",
                 store: [{id, text}, ...]}
  manifest.json  {declared_at (ISO), corpus_sha256, truncation (int|null),
                 separation_margin (>0), helpful: {case_id: [record ids]}}
  results.jsonl  one row per line, IN RUN ORDER: {ts (ISO), arm, case_id,
                 retrieved_ids, manifest_sha256}; engine rows add
                 adaptations: [labels]. Control arms are named return-nothing,
                 return-everything, bm25, oracle; any other arm is an engine.
  decision.json  {verdict: "stop"|"continue", finding (required on stop)}
  review.json    {reviewer, author, verdict}
  design.md      cites team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md and carries one
                 line `KnowledgeDrift choice: reuse-abstention | frozen-worlds |
                 build-own` (build-own needs a stated reason)

The three properties the row turns on (marker in brackets):
  (a) the manifest declares which records should help BEFORE results exist.
      declared_at precedes every result [DECLARED-AFTER-RESULTS]; the manifest
      does not reference results [MANIFEST-DERIVED]; and every result row embeds
      the sha256 of the manifest bytes, so the manifest existed, byte for byte,
      when each result was written [RESULTS-NOT-BOUND]. The manifest in turn
      pins the corpus [CORPUS-NOT-FROZEN]. Chain: corpus -> manifest -> results.
  (b) the corpus holds cases whose correct answer is to retrieve NOTHING, and
      they are labelled [NO-ABSTAIN-CASES] [CASE-UNLABELLED] [ABSTAIN-MISMATCH];
      stores hold several records [SINGLE-RECORD-STORE] with distractors
      [NO-DISTRACTORS], or return-everything still guarantees a hit.
  (c) the controls ran FIRST [CONTROLS-NOT-FIRST], all four are present and
      cover every case [CONTROL-ARM-MISSING] [CONTROL-INCOMPLETE], and each
      delivered what its name says [CONTROL-ARM-WRONG]. The gate RECOMPUTES the
      separation (mean set-F1 against the manifest; an abstain case scores 1
      only on an empty retrieval): if bm25 does not beat return-everything by
      the pre-declared margin, the verdict must be "stop" [CONTINUED-ANYWAY].
      A stop verdict is a PASS - an honestly shown limit is a completed result -
      but it needs its finding [STOP-WITHOUT-FINDING] and no engine rows
      [STOP-BUT-ENGINES-RAN]. Engine rows label every adaptation
      [ADAPTATION-UNLABELLED].
  citation  [CITATION-MISSING] [CHOICE-UNNAMED] [CHOICE-UNREASONED]
  other     [MISSING-FILE] [BAD-JSON] [SCHEMA] [MANIFEST-UNKNOWN-ID]
            [MARGIN-UNDECLARED] [TRUNCATION-UNDECLARED] [DECISION-INVALID]
            [REVIEW-INCOMPLETE] [REVIEW-NOT-INDEPENDENT]

Limit, stated on purpose: timestamps are self-reported and a hash chain can be
rebuilt by someone who sets out to. This stops a manifest written from results by
accident or convenience; whether the distractors are PLAUSIBLE, and whether the
citation supports the choice, stays with the named verifier.

Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a
named marker and the line `S6-2 gate findings: N`, never a traceback.

Usage:
  python3 check.py [ROOT]      # ROOT defaults to this directory
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
from datetime import datetime, timezone
from pathlib import Path

FILES = ("design.md", "corpus.jsonl", "manifest.json", "results.jsonl",
         "decision.json", "review.json")
CONTROLS = ("return-nothing", "return-everything", "bm25", "oracle")
CARD = "EXTERNAL-KNOWLEDGEDRIFT-20260916.md"
CHOICES = ("reuse-abstention", "frozen-worlds", "build-own")
MIN_STORE = 3  # "several records per store"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ts(v):
    if not isinstance(v, str):
        return None
    try:
        t = datetime.fromisoformat(v.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def _arm(v) -> str:
    return re.sub(r"[_\s]+", "-", v.strip().lower()) if isinstance(v, str) else ""


def _ids(v):
    ok = isinstance(v, list) and all(isinstance(x, str) for x in v)
    return set(v) if ok else None


def _read(root: Path, name: str, findings: list, lines: bool = False):
    text = (root / name).read_text(encoding="utf-8", errors="replace")
    try:
        if not lines:
            return json.loads(text)
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    except ValueError as e:
        findings.append(("BAD-JSON", f"{name}: {e}"))
        return None


def _f1(helpful: set, got: set) -> float:
    if not helpful:
        return 0.0 if got else 1.0
    tp = len(helpful & got)
    return 2 * tp / (len(helpful) + len(got)) if tp else 0.0


def _check_design(text: str, findings: list) -> None:
    if CARD not in text:
        findings.append(("CITATION-MISSING", f"design.md does not cite team/{CARD}"))
    named = set(re.findall(r"(?im)knowledgedrift choice\W*?[:=]\W*([a-z][a-z-]*)", text))
    if len(named) != 1 or not named <= set(CHOICES):
        findings.append(("CHOICE-UNNAMED", "design.md needs exactly one line "
                         f"`KnowledgeDrift choice: <{' | '.join(CHOICES)}>`, "
                         f"found {sorted(named)}"))
    elif named == {"build-own"} and not re.search(
            r"\b(?:because|reason|do(?:es)? not fit|doesn't fit)\b", text, re.I):
        findings.append(("CHOICE-UNREASONED", "build-own needs a stated reason "
                         "KnowledgeDrift's construction does not fit"))


def _check_review(obj, findings: list) -> None:
    def s(*keys):
        for k in keys:
            v = obj.get(k) if isinstance(obj, dict) else None
            if isinstance(v, str) and v.strip():
                return v.strip()
    who, author = s("reviewer", "verifier", "reviewed_by"), s("author")
    if not (who and author and s("verdict", "status", "result")):
        findings.append(("REVIEW-INCOMPLETE",
                         "review.json needs reviewer, author and verdict"))
    elif who.lower() == author.lower():
        findings.append(("REVIEW-NOT-INDEPENDENT",
                         f"reviewer and author are both {who!r}"))


def _structure(corpus, manifest, results, decision, findings: list) -> None:
    """Shape only. Semantics run on a root that passes this, so they can index
    without guarding every access."""
    def bad(msg):
        findings.append(("SCHEMA", msg))

    seen = set()
    for i, c in enumerate(corpus):
        if not (isinstance(c, dict) and isinstance(c.get("case_id"), str)
                and isinstance(c.get("query"), str) and isinstance(c.get("store"), list)
                and all(isinstance(r, dict) and isinstance(r.get("id"), str)
                        and isinstance(r.get("text"), str) for r in c["store"])):
            bad(f"corpus.jsonl line {i + 1}: need case_id, query, store[{{id, text}}]")
        elif c["case_id"] in seen:
            bad(f"corpus.jsonl: duplicate case_id {c['case_id']!r}")
        else:
            seen.add(c["case_id"])
            if c.get("expect") not in ("retrieve", "abstain"):
                findings.append(("CASE-UNLABELLED", f"case {c['case_id']!r}: expect "
                                 'must be "retrieve" or "abstain"'))
    if not corpus:
        bad("corpus.jsonl holds no cases")

    if not isinstance(manifest, dict):
        return bad("manifest.json must be an object")
    if _ts(manifest.get("declared_at")) is None:
        bad("manifest.json: declared_at must be an ISO timestamp")
    h = manifest.get("helpful")
    if not (isinstance(h, dict) and all(_ids(v) is not None for v in h.values())):
        bad("manifest.json: helpful must map case_id -> [record ids]")
    m = manifest.get("separation_margin")
    if not (isinstance(m, (int, float)) and not isinstance(m, bool) and m > 0):
        findings.append(("MARGIN-UNDECLARED", "manifest.json: separation_margin > 0 "
                         "must be declared before the runs, not chosen after"))
    t = manifest.get("truncation", 0)
    if "truncation" not in manifest or not (
            t is None or (isinstance(t, int) and not isinstance(t, bool) and t > 0)):
        findings.append(("TRUNCATION-UNDECLARED", "manifest.json: truncation (int or "
                         'null) must be declared so "everything" is reproducible'))

    for i, r in enumerate(results):
        if not (isinstance(r, dict) and _ts(r.get("ts")) and _arm(r.get("arm"))
                and isinstance(r.get("case_id"), str)
                and _ids(r.get("retrieved_ids")) is not None):
            bad(f"results.jsonl line {i + 1}: need ts, arm, case_id, retrieved_ids")
    if not results:
        bad("results.jsonl holds no rows")

    if not (isinstance(decision, dict)
            and str(decision.get("verdict", "")).strip().lower() in ("stop", "continue")):
        findings.append(("DECISION-INVALID",
                         'decision.json: verdict must be "stop" or "continue"'))


def _semantics(root: Path, corpus, manifest, results, decision, findings: list):
    add = lambda marker, msg: findings.append((marker, msg))
    cases = {c["case_id"]: c for c in corpus}
    store = {k: {r["id"] for r in c["store"]} for k, c in cases.items()}
    helpful = {k: set(v) for k, v in manifest["helpful"].items()}

    # (b) abstention cases exist and are labelled; stores can embarrass a firehose
    if set(helpful) != set(cases):
        add("MANIFEST-UNKNOWN-ID", "manifest.helpful keys differ from corpus case "
            f"ids: {sorted(set(helpful) ^ set(cases))}")
        return None
    for k, c in cases.items():
        if helpful[k] - store[k]:
            add("MANIFEST-UNKNOWN-ID",
                f"case {k!r}: helpful ids not in its store {sorted(helpful[k] - store[k])}")
        if len(store[k]) < MIN_STORE:
            add("SINGLE-RECORD-STORE", f"case {k!r} holds {len(store[k])} record(s); "
                f"the row wants several (>= {MIN_STORE})")
        if (c["expect"] == "abstain") != (not helpful[k]):
            add("ABSTAIN-MISMATCH", f"case {k!r} is labelled {c['expect']!r} but the "
                f"manifest declares {len(helpful[k])} helpful record(s)")
        elif helpful[k] and helpful[k] == store[k]:
            add("NO-DISTRACTORS", f"case {k!r}: every record is helpful, so "
                "return-everything is a perfect answer")
    labels = [c["expect"] for c in corpus]
    if "abstain" not in labels or "retrieve" not in labels:
        add("NO-ABSTAIN-CASES", "corpus needs at least one case labelled abstain "
            f"and one labelled retrieve; labels seen: {sorted(set(labels))}")

    # (a) corpus -> manifest -> results, in that order
    if manifest.get("corpus_sha256") != _sha(root / "corpus.jsonl"):
        add("CORPUS-NOT-FROZEN", "manifest.corpus_sha256 is not the sha256 of "
            "corpus.jsonl: the corpus changed after the declaration, or was never pinned")
    raw = (root / "manifest.json").read_text(encoding="utf-8", errors="replace")
    if re.search(r"results?\.jsonl|derived[_ -]?from", raw, re.I):
        add("MANIFEST-DERIVED", "manifest.json references results or a derivation; "
            "the declaration must stand on its own")
    declared, msha = _ts(manifest["declared_at"]), _sha(root / "manifest.json")
    early = [i + 1 for i, r in enumerate(results) if _ts(r["ts"]) <= declared]
    if early:
        add("DECLARED-AFTER-RESULTS", f"{len(early)} result row(s) are not later than "
            f"manifest.declared_at, first at line {early[0]}")
    unbound = [i + 1 for i, r in enumerate(results) if r.get("manifest_sha256") != msha]
    if unbound:
        add("RESULTS-NOT-BOUND", f"{len(unbound)} result row(s) do not carry the sha256 "
            f"of manifest.json ({msha[:12]}...), first at line {unbound[0]}")

    # (c) controls first, complete, and honest about what they delivered
    if any(r["case_id"] not in cases for r in results):
        add("MANIFEST-UNKNOWN-ID", "results.jsonl names a case_id not in the corpus")
        return None
    by_arm: dict[str, dict[str, set]] = {}
    for r in results:
        by_arm.setdefault(_arm(r["arm"]), {})[r["case_id"]] = set(r["retrieved_ids"])
    for arm in CONTROLS:
        if arm not in by_arm:
            add("CONTROL-ARM-MISSING", f"no {arm} rows in results.jsonl")
        elif set(by_arm[arm]) != set(cases):
            add("CONTROL-INCOMPLETE", f"{arm} skips case(s) "
                f"{sorted(set(cases) - set(by_arm[arm]))}")
    is_ctl = [_arm(r["arm"]) in CONTROLS for r in results]
    engines = [r for r, c in zip(results, is_ctl) if not c]
    if engines:
        ctl_ts = [_ts(r["ts"]) for r, c in zip(results, is_ctl) if c]
        if (True in is_ctl[is_ctl.index(False):]
                or (ctl_ts and max(ctl_ts) >= min(_ts(r["ts"]) for r in engines))):
            add("CONTROLS-NOT-FIRST", "an engine row precedes a control row, by file "
                "order or by timestamp")
    trunc = manifest.get("truncation")
    for k in cases:
        want_n = len(store[k]) if not isinstance(trunc, int) else min(trunc, len(store[k]))
        for arm, ok, want in (
                ("return-nothing", lambda g: not g, "nothing"),
                ("return-everything",
                 lambda g: g <= store[k] and len(g) == want_n, f"{want_n} store records"),
                ("oracle", lambda g: g == helpful[k], "exactly the declared helpful set")):
            got = by_arm.get(arm, {}).get(k)
            if got is not None and not ok(got):
                add("CONTROL-ARM-WRONG",
                    f"{arm} on case {k!r} delivered {sorted(got)}, expected {want}")
    for i, r in enumerate(results):
        a = r.get("adaptations")
        if not is_ctl[i] and not (isinstance(a, list)
                                  and all(isinstance(x, str) and x.strip() for x in a)):
            add("ADAPTATION-UNLABELLED", f"results.jsonl line {i + 1} ({r['arm']}): engine "
                "rows need adaptations: [labels], [] if none")
            break

    # the verdict must follow from the controls, recomputed here
    if any(m in ("CONTROL-ARM-MISSING", "CONTROL-INCOMPLETE", "MARGIN-UNDECLARED")
           for m, _ in findings):
        return None
    score = {a: sum(_f1(helpful[k], by_arm[a][k]) for k in cases) / len(cases)
             for a in ("bm25", "return-everything")}
    gap = score["bm25"] - score["return-everything"]
    separated = gap > manifest["separation_margin"]
    detail = (f"bm25 {score['bm25']:.3f} vs return-everything "
              f"{score['return-everything']:.3f}, gap {gap:.3f}, declared margin "
              f"{manifest['separation_margin']}")
    verdict = str(decision["verdict"]).strip().lower()
    if verdict == "continue" and not separated:
        add("CONTINUED-ANYWAY", "return-everything is indistinguishable from selective "
            f"retrieval ({detail}); the row says STOP and report that")
    if verdict == "stop":
        f = decision.get("finding")
        if not (isinstance(f, str) and len(f.split()) >= 5):
            add("STOP-WITHOUT-FINDING", "a stop verdict must carry its finding in "
                "decision.json (a sentence, not a flag)")
        if engines:
            add("STOP-BUT-ENGINES-RAN", f"verdict is stop but {len(engines)} engine "
                "row(s) exist: the comparison was run anyway")
    return f"verdict {verdict}; {detail}"


def check(root: Path) -> tuple[list[tuple[str, str]], str]:
    findings: list[tuple[str, str]] = []
    missing = [f for f in FILES
               if not (root / f).is_file() or not (root / f).stat().st_size]
    for f in missing:
        findings.append(("MISSING-FILE", f"{f} (absent or empty)"))
    if "design.md" not in missing:
        _check_design((root / "design.md").read_text(encoding="utf-8", errors="replace"),
                      findings)
    if "review.json" not in missing:
        obj = _read(root, "review.json", findings)
        if obj is not None:
            _check_review(obj, findings)
    core = ("corpus.jsonl", "manifest.json", "results.jsonl", "decision.json")
    if any(f in missing for f in core):
        return findings, ""
    loaded = [_read(root, f, findings, lines=f.endswith(".jsonl")) for f in core]
    if any(x is None for x in loaded):
        return findings, ""
    before = len(findings)
    _structure(*loaded, findings)
    if any(m in ("SCHEMA", "CASE-UNLABELLED", "DECISION-INVALID")
           for m, _ in findings[before:]):
        return findings, ""
    return findings, _semantics(root, *loaded, findings) or ""


# ---- selftest: the gate must be able to fail, and able to pass ----

_DESIGN = (f"# Selectivity diagnostic\n\nCited before the corpus was built: team/{CARD}\n\n"
           "KnowledgeDrift choice: build-own\n\nWe build our own because its frozen "
           "worlds do not use our store-per-scenario shape. We adopt its abstention "
           "structure and re-derive every score.\n")


def _fixture() -> dict:
    def case(cid, expect):
        return {"case_id": cid, "query": f"q-{cid}", "expect": expect,
                "store": [{"id": f"{cid}-r{i}", "text": f"record {i}"} for i in range(3)]}
    return {
        "design": _DESIGN,
        "corpus": [case("c1", "retrieve"), case("c2", "retrieve"), case("c3", "abstain")],
        "manifest": {"declared_at": "2026-09-17T10:00:00Z", "truncation": None,
                     "separation_margin": 0.1,
                     "helpful": {"c1": ["c1-r0"], "c2": ["c2-r1"], "c3": []}},
        "decision": {"verdict": "continue"},
        "review": {"reviewer": "corvid-dsh", "author": "kiln-flash", "verdict": "pass"},
        # knobs for the results generator
        "bm25": "selective", "engines": True, "engines_first": False,
        "everything_short": False, "drop_arm": None, "adaptations": True,
        "corpus_sha": None, "bind_sha": None,
    }


def _write(root: Path, fx: dict) -> None:
    (root / "design.md").write_text(fx["design"], encoding="utf-8")
    (root / "corpus.jsonl").write_text(
        "".join(json.dumps(c) + "\n" for c in fx["corpus"]), encoding="utf-8")
    man = dict(fx["manifest"])
    man["corpus_sha256"] = fx["corpus_sha"] or _sha(root / "corpus.jsonl")
    (root / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    msha = fx["bind_sha"] or _sha(root / "manifest.json")

    helpful = fx["manifest"].get("helpful", {})
    blocks = {a: [] for a in (*CONTROLS, "engine-x")}
    for c in fx["corpus"]:
        k, ids = c["case_id"], [r["id"] for r in c.get("store", [])]
        sel = list(helpful.get(k, [])) or ids[:1]  # bm25 over-fires on abstain cases
        blocks["return-nothing"].append((k, []))
        blocks["return-everything"].append((k, ids[:1] if fx["everything_short"] else ids))
        blocks["bm25"].append((k, sel if fx["bm25"] == "selective" else ids))
        blocks["oracle"].append((k, list(helpful.get(k, []))))
        blocks["engine-x"].append((k, sel))
    order = [a for a in CONTROLS if a != fx["drop_arm"]]
    if fx["engines"]:
        order = ["engine-x", *order] if fx["engines_first"] else [*order, "engine-x"]
    rows, n = [], 0
    for arm in order:
        for k, got in blocks[arm]:
            row = {"ts": f"2026-09-17T11:00:{n:02d}Z", "arm": arm, "case_id": k,
                   "retrieved_ids": got, "manifest_sha256": msha}
            if arm == "engine-x" and fx["adaptations"]:
                row["adaptations"] = ["top_k raised from 1 to 5"]
            rows.append(row)
            n += 1
    (root / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (root / "decision.json").write_text(json.dumps(fx["decision"]), encoding="utf-8")
    (root / "review.json").write_text(json.dumps(fx["review"]), encoding="utf-8")


_STOP = {"verdict": "stop", "finding": "return-everything scores the same as bm25, so "
         "the instrument cannot separate a selective retriever from a firehose"}


def _honest_stop(fx):  # the instrument fails to separate, and the row says so
    fx.update(bm25="firehose", engines=False, decision=dict(_STOP))


def _mut(**kw):
    return lambda fx: fx.update(kw)


def _man(**kw):
    return lambda fx: fx["manifest"].update(kw)


def _case(i, **kw):
    return lambda fx: fx["corpus"][i].update(kw)


# one defect each, so every check is shown to fail on its own
_MUTANTS = {
    "CONTINUED-ANYWAY": _mut(bm25="firehose"),
    "STOP-BUT-ENGINES-RAN": _mut(decision=dict(_STOP)),
    "STOP-WITHOUT-FINDING": lambda fx: (_honest_stop(fx),
                                        fx.update(decision={"verdict": "stop"})),
    "DECISION-INVALID": _mut(decision={"verdict": "proceed"}),
    "DECLARED-AFTER-RESULTS": _man(declared_at="2026-09-17T12:00:00Z"),
    "RESULTS-NOT-BOUND": _mut(bind_sha="0" * 64),
    "MANIFEST-DERIVED": _man(derived_from="results.jsonl"),
    "CORPUS-NOT-FROZEN": _mut(corpus_sha="0" * 64),
    "NO-ABSTAIN-CASES": lambda fx: (fx["corpus"].pop(), fx["manifest"]["helpful"].pop("c3")),
    "CASE-UNLABELLED": lambda fx: fx["corpus"][2].pop("expect"),
    "ABSTAIN-MISMATCH": lambda fx: fx["manifest"]["helpful"].update(c3=["c3-r0"]),
    "SINGLE-RECORD-STORE": lambda fx: fx["corpus"][0].update(
        store=fx["corpus"][0]["store"][:1]),
    "NO-DISTRACTORS": lambda fx: fx["manifest"]["helpful"].update(
        c1=["c1-r0", "c1-r1", "c1-r2"]),
    "MANIFEST-UNKNOWN-ID": lambda fx: fx["manifest"]["helpful"].update(c1=["nope"]),
    "CONTROL-ARM-MISSING": _mut(drop_arm="return-everything"),
    "CONTROL-ARM-WRONG": _mut(everything_short=True),
    "CONTROLS-NOT-FIRST": _mut(engines_first=True),
    "ADAPTATION-UNLABELLED": _mut(adaptations=False),
    "MARGIN-UNDECLARED": lambda fx: fx["manifest"].pop("separation_margin"),
    "TRUNCATION-UNDECLARED": lambda fx: fx["manifest"].pop("truncation"),
    "CITATION-MISSING": _mut(design=_DESIGN.replace(CARD, "a benchmark Brian found")),
    "CHOICE-UNNAMED": _mut(design=_DESIGN.replace("KnowledgeDrift choice: build-own", "")),
    "CHOICE-UNREASONED": _mut(design=f"See team/{CARD}.\nKnowledgeDrift choice: build-own\n"),
    "REVIEW-NOT-INDEPENDENT": _mut(review={"reviewer": "kiln-flash",
                                           "author": "kiln-flash", "verdict": "pass"}),
    "SCHEMA": lambda fx: fx["corpus"][0].pop("store"),
}
_MARKER = re.compile(r"S6-2 gate findings: [1-9]")


def _selftest() -> int:
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        def root(name, *edits):
            d = Path(td) / name
            d.mkdir()
            fx = copy.deepcopy(_fixture())
            for e in edits:
                e(fx)
            _write(d, fx)
            return d

        good, stop = root("good"), root("stop", _honest_stop)
        for label, d in (("conforming continue", good), ("honest STOP", stop)):
            got, _ = check(d)
            if got:
                fails.append(f"{label} fixture REJECTED: {got}")

        for marker, edit in _MUTANTS.items():
            got = {m for m, _ in check(root(marker, edit))[0]}
            if marker not in got:
                fails.append(f"mutant for [{marker}] was ACCEPTED or mis-named: {sorted(got)}")

        for f in FILES:  # every declared file is required, one at a time
            d = root(f"no-{f}")
            (d / f).unlink()
            if ("MISSING-FILE", f"{f} (absent or empty)") not in check(d)[0]:
                fails.append(f"fixture without {f} was ACCEPTED")

        # the real command line, both ways, plus a root that tries to crash it
        bad = root("bad", _mut(bm25="firehose"), _man(declared_at="2026-09-17T12:00:00Z"))
        crash = root("crash")
        (crash / "corpus.jsonl").write_text('[1]\n"x"\n{"case_id": 3}\n')
        (crash / "manifest.json").write_text("[]")
        (crash / "results.jsonl").write_text('{"ts": 5, "arm": null}\n')
        (crash / "decision.json").write_text("null")
        (crash / "review.json").unlink()
        (crash / "review.json").mkdir()
        for label, d, want in (("clean", good, 0), ("stop", stop, 0), ("dirty", bad, 1),
                               ("hostile", crash, 1)):
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), str(d)],
                               capture_output=True, text=True, timeout=60)
            text = p.stdout + p.stderr
            if p.returncode != want:
                fails.append(f"CLI [{label}]: exit {p.returncode}, expected {want}")
            if "Traceback (most recent call last)" in text:
                fails.append(f"CLI [{label}]: traceback instead of a verdict")
            if bool(_MARKER.search(text)) != bool(want):
                fails.append(f"CLI [{label}]: finding marker "
                             f"{'absent' if want else 'printed on a clean root'}")
    for f in fails:
        print(f"[SELFTEST-FAIL] {f}")
    if fails:
        print(f"S6-2 gate selftest findings: {len(fails)}")
        return 1
    print(f"selftest: PASS (conforming continue AND honest STOP accepted; {len(_MUTANTS)} "
          f"single-defect mutants, {len(FILES)} missing-file roots, and the dirty and "
          "hostile CLI roots all rejected by name, no traceback)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate for QUEUE row S6-2")
    ap.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--selftest", "--self-test", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    findings, summary = check(Path(a.root))
    for marker, detail in findings:
        print(f"[{marker}] {detail}")
    if findings:
        print(f"S6-2 gate findings: {len(findings)}")
        return 1
    print(f"S6-2 gate: clean ({summary})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as e:  # a crash must still read as a finding, not a trace
        print(f"[GATE-ERROR] {type(e).__name__}: {e}")
        print("S6-2 gate findings: 1")
        raise SystemExit(1)
