#!/usr/bin/env python3
"""Gate for board row S11-3: pi-lcm NATIVE supersession on broader histories.

Written FROM THE ROW TEXT ALONE, before the artifact existed. The row demands:
mechanically extend the S7-3 trial generation with a BEFORE-THE-RUN declaration
(more distractor families, longer streams, the documented agentmemory 92.9%
distractor shape, unfitted), run the NATIVE pi-lcm arm only (no layer code),
and report old-vs-new against the prior measurement in
team/S7-STATELAYER/verdict.json (row-stated prior: native 0/32 false
supersession, 12/12 updates). A null is acceptable evidence; a fake null is not.

The trap: a null is cheap. A corpus that is not actually broader repeats the
prior null; a corpus with no distractor trials or no update trials cannot fail
and calls that a pass; reported counts that disagree with the per-trial record
are prose, not measurement. So this gate trusts no reported number: it
recounts the native arm from the per-trial records and checks the corpus
against the frozen declaration by hash.

DECLARED INTERFACE (this gate declares it; ROOT = team/S10-PI-LCM-HIST):
  ROOT/declaration.json   written before the run, frozen thereafter:
      { "declared_at": <non-empty str>,
        "baseline":  { "source": <str naming S7-3>,
                       "distractor_families": <int>,
                       "stream_length_max": <int> },
        "broader":   { "distractor_families": [<str>, ...],   # strictly more
                       "stream_length_min": <int>,             # strictly longer
                       "distractor_share_pct": <number>,       # the declared shape
                       "shape_source": <str naming agentmemory 92.9>,
                       "fitted_to_results": false } }
  ROOT/trials.jsonl       one object per trial, the NATIVE arm only:
      { "trial_id": <str, unique>, "arm": "pi-lcm-native",
        "kind": "distractor" | "update", "family": <str, in the declared set>,
        "stream_len": <int >= declared minimum>,
        "superseded": <bool> }   # original treated as superseded at stream end
  ROOT/verdict.json       the report, bound to the frozen declaration:
      { "row": "S11-3", "arm": "pi-lcm-native", "no_layer_code": true,
        "declaration_sha256": <sha256 of declaration.json bytes>,
        "counts":  { "false_superseded": n, "distractor_trials": d,
                     "missed_updates": m, "update_trials": u },
        "failures": [trial_id, ...],
        "old_vs_new": { "prior": { "source": <str>,
                                   "false_supersession": [n, d],
                                   "missed_updates": [m, u] },
                        "new":   { "false_supersession": [n, d],
                                   "missed_updates": [m, u] } },
        "verdict": "native-null" | "native-failure",
        "finding": <non-empty str> }

Semantics (same as the prior's controls): a distractor trial whose original is
marked superseded is a FALSE SUPERSESSION; an update trial whose original is
NOT marked superseded is a MISSED UPDATE. Counts, failures, old-vs-new and the
verdict label are all recomputed from trials.jsonl here and must match.

Usage:
  python3 check.py              # gate the real ROOT
  python3 check.py --selftest   # prove the gate can fail (fixtures in tmp)
  python3 check.py --root DIR --prior PATH   # fixture/alternate paths
Exit: 0 clean; 1 with one "FINDING <CODE>: ..." line per named finding;
never a traceback. Stdlib only, no network, no LLM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

PRIOR_ROW_PATH = Path("team") / "S7-STATELAYER" / "verdict.json"


def _f(findings, code, detail):
    findings.append("FINDING %s: %s" % (code, detail))


def _load_json(path, code, findings):
    if not path.is_file():
        _f(findings, "MISSING", "required file not found: %s" % path)
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _f(findings, code, "%s is not valid JSON (%s)" % (path.name, exc))
        return None
    if not isinstance(obj, dict):
        _f(findings, code, "%s must be a JSON object" % path.name)
        return None
    return obj


def _load_jsonl(path, code, findings):
    rows = []
    if not path.is_file():
        _f(findings, "MISSING", "required file not found: %s" % path)
        return rows
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            _f(findings, code, "trials.jsonl line %d is not valid JSON (%s)" % (ln, exc))
            continue
        if not isinstance(obj, dict):
            _f(findings, code, "trials.jsonl line %d is not an object" % ln)
            continue
        rows.append(obj)
    if not rows:
        _f(findings, code, "trials.jsonl holds no trial records")
    return rows


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _check_declaration(decl, findings):
    if decl is None:
        return None
    if not str(decl.get("declared_at", "")).strip():
        _f(findings, "DECL", "declaration.json lacks non-empty declared_at")
    base = decl.get("baseline")
    broad = decl.get("broader")
    if not isinstance(base, dict) or not isinstance(broad, dict):
        _f(findings, "DECL", "declaration.json needs baseline and broader objects")
        return None
    if "S7-3" not in str(base.get("source", "")):
        _f(findings, "DECL", "baseline.source must name the S7-3 generation it extends")
    fam_b = base.get("distractor_families")
    len_b = base.get("stream_length_max")
    if not _is_int(fam_b) or not _is_int(len_b) or fam_b < 1 or len_b < 1:
        _f(findings, "DECL", "baseline.distractor_families and baseline.stream_length_max must be positive ints")
        return None
    fam_n = broad.get("distractor_families")
    len_n = broad.get("stream_length_min")
    share = broad.get("distractor_share_pct")
    if not isinstance(fam_n, list) or not fam_n or not all(isinstance(x, str) and x.strip() for x in fam_n):
        _f(findings, "DECL", "broader.distractor_families must be a non-empty list of names")
        return None
    if len(set(fam_n)) != len(fam_n):
        _f(findings, "DECL", "broader.distractor_families contains duplicate names")
        return None
    if len(fam_n) <= fam_b:
        _f(findings, "BREADTH", "declared corpus not broader: %d families vs baseline %d (row demands MORE)" % (len(fam_n), fam_b))
    if not _is_int(len_n) or len_n <= len_b:
        _f(findings, "BREADTH", "declared stream_length_min %r must be an int > baseline max %d (row demands LONGER streams)" % (len_n, len_b))
    shape = str(broad.get("shape_source", ""))
    if "agentmemory" not in shape.lower() or "92.9" not in shape:
        _f(findings, "SHAPE", "shape_source must cite the documented agentmemory 92.9%% distractor shape")
    if broad.get("fitted_to_results") is not False:
        _f(findings, "SHAPE", "fitted_to_results must be false — the shape is declared unfitted, before the run")
    if not isinstance(share, (int, float)) or isinstance(share, bool):
        _f(findings, "SHAPE", "broader.distractor_share_pct must be a number")
        share = None
    return {"families": set(fam_n), "stream_min": len_n if _is_int(len_n) else None, "share": share}


def _read_prior(prior_path, findings):
    prior = _load_json(prior_path, "PRIOR", findings)
    if prior is None:
        return None
    arms = prior.get("arms")
    native = None
    if isinstance(arms, dict):
        for name, block in arms.items():
            if "native" in str(name).lower() and isinstance(block, dict):
                native = block
                break
    if native is None:
        _f(findings, "PRIOR", "prior verdict.json has no native arm block: %s" % prior_path)
        return None
    got = tuple(native.get(k) for k in ("false_superseded", "distractor_trials", "missed_updates", "update_trials"))
    if not all(_is_int(x) for x in got):
        _f(findings, "PRIOR", "prior verdict.json native arm missing count fields")
        return None
    want = (0, 32, 0, 12)  # the row-text-stated prior: 0/32 false supersession, 12/12 updates
    if got != want:
        _f(findings, "PRIOR", "prior file says native %d/%d false supersession, %d/%d updates; row text states %d/%d, %d/%d" % (*got, *want))
    return {"false_supersession": [got[0], got[1]], "missed_updates": [got[2], got[3]]}


def check_dir(root, prior_path):
    findings = []
    decl = _load_json(root / "declaration.json", "DECL", findings)
    spec = _check_declaration(decl, findings)
    trials = _load_jsonl(root / "trials.jsonl", "TRIALS", findings)
    ver = _load_json(root / "verdict.json", "VERDICT", findings)
    prior = _read_prior(prior_path, findings)

    seen_ids = set()
    dist = 0
    upd = 0
    fs = 0
    mu = 0
    fail_ids = []
    fams_seen = set()
    for i, t in enumerate(trials):
        where = "trial %d (%s)" % (i, t.get("trial_id", "?"))
        tid = t.get("trial_id")
        if not isinstance(tid, str) or not tid.strip():
            _f(findings, "TRIALS", "%s missing trial_id" % where)
            continue
        if tid in seen_ids:
            _f(findings, "TRIALS", "duplicate trial_id %s" % tid)
            continue
        seen_ids.add(tid)
        arm = str(t.get("arm", ""))
        if "layer" in arm.lower():
            _f(findings, "ARM", "trial %s ran a layer arm %r — the row allows the native arm only, no layer code" % (tid, arm))
        elif arm != "pi-lcm-native":
            _f(findings, "ARM", "trial %s arm must be pi-lcm-native, got %r" % (tid, arm))
        kind = t.get("kind")
        if kind not in ("distractor", "update"):
            _f(findings, "TRIALS", "trial %s kind must be distractor|update, got %r" % (tid, kind))
            continue
        fam = t.get("family")
        if not isinstance(fam, str) or not fam.strip():
            _f(findings, "TRIALS", "trial %s missing family" % tid)
        elif spec is not None and fam not in spec["families"]:
            _f(findings, "BREADTH", "trial %s uses family %r outside the declared set" % (tid, fam))
        else:
            fams_seen.add(fam)
        slen = t.get("stream_len")
        if not _is_int(slen) or slen < 1:
            _f(findings, "TRIALS", "trial %s stream_len must be a positive int" % tid)
        elif spec is not None and spec["stream_min"] is not None and slen < spec["stream_min"]:
            _f(findings, "BREADTH", "trial %s stream_len %d is shorter than the declared minimum %d" % (tid, slen, spec["stream_min"]))
        sup = t.get("superseded")
        if not isinstance(sup, bool):
            _f(findings, "TRIALS", "trial %s superseded must be a bool" % tid)
            continue
        if kind == "distractor":
            dist += 1
            if sup:
                fs += 1
                fail_ids.append(tid)
        else:
            upd += 1
            if not sup:
                mu += 1
                fail_ids.append(tid)

    total = dist + upd
    if trials:
        if dist == 0 or upd == 0:
            _f(findings, "NONVACUOUS", "corpus has %d distractor / %d update trials — both kinds must exist or a 0/0 null is unmeasured" % (dist, upd))
        if prior is not None:
            if dist < prior["false_supersession"][1]:
                _f(findings, "NONVACUOUS", "%d distractor trials is fewer than the prior's %d — the re-measurement must not shrink" % (dist, prior["false_supersession"][1]))
            if upd < prior["missed_updates"][1]:
                _f(findings, "NONVACUOUS", "%d update trials is fewer than the prior's %d — missed updates would be unmeasured" % (upd, prior["missed_updates"][1]))
        if spec is not None and total:
            share_obs = 100.0 * dist / total
            if not (92.4 <= share_obs <= 93.4):
                _f(findings, "SHAPE", "observed distractor share %.1f%% is not the documented agentmemory 92.9%% shape (92.4–93.4 band)" % share_obs)
            if spec["share"] is not None:
                if abs(share_obs - float(spec["share"])) > 0.15:
                    _f(findings, "SHAPE", "observed distractor share %.2f%% deviates from the declared %.2f%% — the shape was fitted, not unfitted" % (share_obs, float(spec["share"])))
            missing = {f for f in spec["families"]} - fams_seen
            if missing:
                _f(findings, "BREADTH", "declared distractor families never appear in the corpus: %s" % ", ".join(sorted(missing)))

    if ver is None:
        return findings
    if ver.get("row") != "S11-3":
        _f(findings, "VERDICT", 'verdict.json row must be "S11-3"')
    if ver.get("arm") != "pi-lcm-native":
        _f(findings, "ARM", "verdict.json arm must be pi-lcm-native (the native arm only)")
    if ver.get("no_layer_code") is not True:
        _f(findings, "ARM", "verdict.json must attest no_layer_code: true")
    if decl is not None:
        want_sha = hashlib.sha256((root / "declaration.json").read_bytes()).hexdigest()
        if ver.get("declaration_sha256") != want_sha:
            _f(findings, "VERDICT", "declaration_sha256 does not bind this declaration.json — the before-the-run declaration is not frozen to the report")
    counts = ver.get("counts")
    if not isinstance(counts, dict):
        _f(findings, "VERDICT", "verdict.json needs a counts object")
    else:
        got = tuple(counts.get(k) for k in ("false_superseded", "distractor_trials", "missed_updates", "update_trials"))
        want = (fs, dist, mu, upd)
        if not all(_is_int(x) for x in got):
            _f(findings, "VERDICT", "counts must all be ints")
        elif got != want:
            _f(findings, "COUNTS", "reported %d false supersession of %d, %d missed updates of %d — the per-trial record says %d of %d, %d of %d" % (*got, *want))
    failures = ver.get("failures")
    if not isinstance(failures, list):
        _f(findings, "VERDICT", "verdict.json needs a failures list of trial ids")
    elif sorted(str(x) for x in failures) != sorted(fail_ids):
        _f(findings, "VERDICT", "reported failures %s do not match the %d failing trial(s) in the record" % (sorted(str(x) for x in failures), len(fail_ids)))
    ovn = ver.get("old_vs_new")
    if not isinstance(ovn, dict):
        _f(findings, "OVN", "verdict.json must report old_vs_new (row: must report old-vs-new)")
    else:
        old = ovn.get("prior")
        new = ovn.get("new")
        if not isinstance(old, dict) or not isinstance(new, dict):
            _f(findings, "OVN", "old_vs_new needs prior and new blocks")
        else:
            if prior is not None:
                if old.get("false_supersession") != prior["false_supersession"] or old.get("missed_updates") != prior["missed_updates"]:
                    _f(findings, "OVN", "cited prior %r != team/S7-STATELAYER/verdict.json native arm (false_supersession %r, missed_updates %r)" % (
                        {k: old.get(k) for k in ("false_supersession", "missed_updates")}, prior["false_supersession"], prior["missed_updates"]))
            if new.get("false_supersession") != [fs, dist] or new.get("missed_updates") != [mu, upd]:
                _f(findings, "OVN", "cited new numbers do not match the recount: false_supersession %r, missed_updates %r expected" % ([fs, dist], [mu, upd]))
    label = ver.get("verdict")
    want_label = "native-failure" if (fs or mu) else "native-null"
    if label not in ("native-null", "native-failure"):
        _f(findings, "VERDICT", "verdict must be native-null or native-failure")
    elif label != want_label:
        _f(findings, "VERDICT", "verdict says %r but the record has %d false supersession and %d missed updates (expected %r)" % (label, fs, mu, want_label))
    if not str(ver.get("finding", "")).strip():
        _f(findings, "VERDICT", "verdict.json needs a non-empty finding sentence")
    return findings


def _fixture(tmp):
    """Minimal CONFORMING fixture; returns (root, prior_path)."""
    root = Path(tmp)
    root.mkdir(parents=True, exist_ok=True)
    fams = ["email", "calendar", "code", "files", "chat"]
    decl = {
        "declared_at": "2026-09-18T09:00:00Z",
        "baseline": {"source": "S7-3 trial generation (team/S7-STATELAYER)",
                     "distractor_families": 2, "stream_length_max": 6},
        "broader": {"distractor_families": fams, "stream_length_min": 9,
                    "distractor_share_pct": 92.9,
                    "shape_source": "agentmemory 92.9% distractor shape (documented, unfitted)",
                    "fitted_to_results": False},
    }
    dpath = root / "declaration.json"
    dpath.write_text(json.dumps(decl, sort_keys=True), encoding="utf-8")
    lines = []
    for i in range(157):  # 157/169 = 92.9% distractors, >= prior's 32
        lines.append({"trial_id": "d%03d" % i, "arm": "pi-lcm-native", "kind": "distractor",
                      "family": fams[i % len(fams)], "stream_len": 9 + (i % 3), "superseded": False})
    for i in range(12):
        lines.append({"trial_id": "u%03d" % i, "arm": "pi-lcm-native", "kind": "update",
                      "family": fams[i % len(fams)], "stream_len": 10, "superseded": True})
    (root / "trials.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
    ver = {
        "row": "S11-3", "arm": "pi-lcm-native", "no_layer_code": True,
        "declaration_sha256": hashlib.sha256(dpath.read_bytes()).hexdigest(),
        "counts": {"false_superseded": 0, "distractor_trials": 157, "missed_updates": 0, "update_trials": 12},
        "failures": [],
        "old_vs_new": {
            "prior": {"source": str(PRIOR_ROW_PATH), "false_supersession": [0, 32], "missed_updates": [0, 12]},
            "new": {"false_supersession": [0, 157], "missed_updates": [0, 12]}},
        "verdict": "native-null",
        "finding": "native pi-lcm on the broader declared corpus: 0/157 false supersession, 12/12 updates — null, as the Gate F record needs",
    }
    (root / "verdict.json").write_text(json.dumps(ver), encoding="utf-8")
    prior_path = Path(tmp) / "prior.json"
    prior_path.write_text(json.dumps({"arms": {"pi-lcm-native": {
        "false_superseded": 0, "distractor_trials": 32, "missed_updates": 0, "update_trials": 12}}}), encoding="utf-8")
    return root, prior_path


def _dirty_counts(tmp):
    root, prior = _fixture(tmp)
    lines = (root / "trials.jsonl").read_text(encoding="utf-8").splitlines()
    patched = []
    flipped = 0
    for ln in lines:
        obj = json.loads(ln)
        if obj["kind"] == "distractor" and flipped < 3:
            obj["superseded"] = True
            flipped += 1
        patched.append(json.dumps(obj))
    (root / "trials.jsonl").write_text("\n".join(patched) + "\n", encoding="utf-8")
    return root, prior, "COUNTS"


def _dirty_narrow(tmp):
    root, prior = _fixture(tmp)
    fams = ["email", "calendar"]
    decl = {
        "declared_at": "2026-09-18T09:00:00Z",
        "baseline": {"source": "S7-3 trial generation", "distractor_families": 2, "stream_length_max": 6},
        "broader": {"distractor_families": fams, "stream_length_min": 5,
                    "distractor_share_pct": 92.9,
                    "shape_source": "agentmemory 92.9% distractor shape", "fitted_to_results": False},
    }
    dpath = root / "declaration.json"
    dpath.write_text(json.dumps(decl, sort_keys=True), encoding="utf-8")
    lines = []
    for i in range(32):
        lines.append({"trial_id": "d%03d" % i, "arm": "pi-lcm-native", "kind": "distractor",
                      "family": fams[i % 2], "stream_len": 5, "superseded": False})
    for i in range(12):
        lines.append({"trial_id": "u%03d" % i, "arm": "pi-lcm-native", "kind": "update",
                      "family": fams[i % 2], "stream_len": 5, "superseded": True})
    (root / "trials.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
    vpath = root / "verdict.json"
    ver = json.loads(vpath.read_text(encoding="utf-8"))
    ver["declaration_sha256"] = hashlib.sha256(dpath.read_bytes()).hexdigest()
    ver["counts"] = {"false_superseded": 0, "distractor_trials": 32, "missed_updates": 0, "update_trials": 12}
    ver["old_vs_new"]["new"] = {"false_supersession": [0, 32], "missed_updates": [0, 12]}
    vpath.write_text(json.dumps(ver), encoding="utf-8")
    return root, prior, "BREADTH"


def _run_selftest():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        good_root, good_prior = _fixture(str(Path(tmp) / "good"))
        # accept the minimal conforming fixture
        good_findings = check_dir(good_root, good_prior)
    print("selftest conforming fixture: %s" % ("accepted" if not good_findings else "REJECTED"))
    for line in good_findings:
        print("  " + line)
    if good_findings:
        ok = False
    # reject each deliberately non-conforming fixture, on the intended finding
    for name, builder in (("counts-disagree-with-record", _dirty_counts), ("corpus-not-broader", _dirty_narrow)):
        with tempfile.TemporaryDirectory() as tmp:
            root, prior, expect = builder(str(Path(tmp) / "bad"))
            findings = check_dir(root, prior)
        hit = any(("FINDING %s:" % expect) in fline for fline in findings)
        print("selftest non-conforming fixture (%s): %s%s" % (name, "rejected" if findings else "ACCEPTED", "" if not hit else " [%s]" % expect))
        for line in findings:
            print("  " + line)
        if not findings or not hit:
            ok = False
    print("SELFTEST %s" % ("OK" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="S11-3 native-supersession-broader-histories gate")
    ap.add_argument("--root", type=Path, default=None, help="artifact dir (default: dir containing this file)")
    ap.add_argument("--prior", type=Path, default=None, help="prior verdict.json (default: team/S7-STATELAYER/verdict.json beside this gate)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        try:
            return _run_selftest()
        except Exception as exc:
            print("FINDING SELFTEST: gate selftest crashed (%s)" % exc)
            return 1
    root = args.root if args.root else Path(__file__).resolve().parent
    prior = args.prior if args.prior else root.parent / "S7-STATELAYER" / "verdict.json"
    try:
        findings = check_dir(root, prior)
    except Exception as exc:
        print("FINDING CRASH: gate errored without a verdict (%s)" % exc)
        return 1
    for line in findings:
        print(line)
    if findings:
        return 1
    print("PASS: S11-3 native arm re-measured on the declared broader corpus; old-vs-new verified against team/S7-STATELAYER/verdict.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
