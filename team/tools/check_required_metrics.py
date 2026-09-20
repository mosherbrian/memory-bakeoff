#!/usr/bin/env python3
"""U2 selective-metric omission guard — adopted from Assay's prototype.

Prototype author: Assay (`worker-glm-dsh2`), 2026-09-13, sha
`e6b50c25f9aa…` (`team/ASSAY-U2-REQUIRED-METRICS-PROTOTYPE.md`). Adopted into
Corvid's checker suite unchanged in rule, with attribution and an extended
self-test.

Closes the coverage map's top unguarded class (U2, Muse batch-4 ACCEPT 4.5): a
result summary can cite only the metrics that pass while a required harm/context
metric (`prohibited@5`, exact context size) is silently absent. AGENTS requires
"always report exact returned context size and harmful/prohibited presence; do
not rely on prohibited fraction alone."

A small schema index says which columns a benchmark `summary.csv` must expose; a
missing required column is a finding unless the result dir carries an explicit
waiver (`METRIC-WAIVER.json`). Static, $0, no model. Verified smoke: 0 findings
on `repo-glm-dsh3` (106 summaries, 1 skipped) and canonical `implementer/repo`
(102 summaries).

Usage:
  python3 check_required_metrics.py [results_dir] [--schema SCHEMA.json]
  python3 check_required_metrics.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import tempfile
from pathlib import Path

# Candidate index (bundled). The canonical home would be results/SCHEMA.json.
DEFAULT_SCHEMA = {
    "schema_version": 1,
    "kinds": {
        "run_summary": {
            "glob": "*/summary.csv",
            "recognized_columns": ["hit@5", "prohibited@5", "mean_context_chars"],
            "required_columns": ["hit@5", "prohibited@5", "mean_context_chars"],
            "waiver_file": "METRIC-WAIVER.json",
            # Leakage-field contract delta (G-B; Corvid 2026-09-14): declared
            # trigger, legacy floor, whole-cell ``leakage@<int>`` matcher.
            "leakage_marker": "LEAKAGE-REQUIRED.json",
            "leakage_column_pattern": "leakage@\\d+",
        }
    },
}

LEAKAGE_METRIC_RE = re.compile(r"leakage@\d+", re.IGNORECASE)


def _leakage_metric_present(header: list[str], pattern: str) -> bool:
    rx = re.compile(pattern, re.IGNORECASE)
    return any(rx.fullmatch((c or "").strip()) for c in header)


def _leakage_waived(path: Path) -> bool:
    """B1: exact token membership in guard 14's ``{"waived": [...]}``; a waiver
    for a different metric whose reason says "leakage" must not suppress it."""
    if not path.is_file():
        return False
    try:
        waiver = json.loads(path.read_text())
    except Exception:                                    # noqa: BLE001
        return False
    if not isinstance(waiver, dict):
        return False
    tokens = waiver.get("waived", [])
    if not isinstance(tokens, list):
        return False
    return any(isinstance(t, str) and
               (t.strip().lower() == "leakage"
                or re.fullmatch(r"leakage@\d+", t.strip(), re.IGNORECASE))
               for t in tokens)


def _validate_schema(schema: dict) -> str | None:
    """Type-check the schema shape so a malformed index cannot traceback or
    silently skip every summary (Alice 2026-09-13)."""
    kind = schema["kinds"]["run_summary"]
    if not isinstance(kind, dict):
        return "kinds.run_summary is not an object"
    required = kind.get("required_columns")
    if (not isinstance(required, list) or not required
            or not all(isinstance(x, str) and x for x in required)):
        return "required_columns must be a non-empty list of strings"
    recognized = kind.get("recognized_columns", required)
    if not isinstance(recognized, list) or not all(isinstance(x, str) for x in recognized):
        return "recognized_columns must be a list of strings"
    for key in ("waiver_file", "glob", "leakage_marker", "leakage_column_pattern"):
        if key in kind and (not isinstance(kind[key], str) or not kind[key]):
            return f"{key} must be a non-empty string"
    return None


def _load_schema_file(p: Path):
    """Guarded reader shared by the explicit and canonical local schema paths.

    Returns (schema, findings). A malformed/empty/unreadable schema must be a
    structured finding, never an uncaught traceback (Assay/Alice 2026-09-13).
    """
    if not p.is_file():
        return None, [{"finding": f"missing prerequisite: {p} (not a file)", "got": "absent"}]
    if not os.access(p, os.R_OK):
        return None, [{"finding": f"unreadable prerequisite: {p}", "got": "unreadable"}]
    try:
        schema = json.loads(p.read_text())
    except Exception as exc:                          # noqa: BLE001
        return None, [{"finding": f"malformed schema: {p}: {exc}", "got": "unparseable"}]
    if not isinstance(schema, dict) or not isinstance(schema.get("kinds"), dict) \
            or "run_summary" not in schema["kinds"]:
        return None, [{"finding": f"malformed schema: {p}: missing kinds.run_summary",
                       "got": "malformed"}]
    problem = _validate_schema(schema)
    if problem:
        return None, [{"finding": f"malformed schema: {p}: {problem}", "got": "malformed"}]
    return schema, []


def _read_schema(results: Path, schema_path: Path | None):
    if schema_path is not None:
        return _load_schema_file(schema_path)
    local = results / "SCHEMA.json"
    if local.exists():
        return _load_schema_file(local)
    return DEFAULT_SCHEMA, []


def check(results: Path, schema_path: Path | None = None):
    findings: list[dict] = []
    if not results.is_dir():
        return [{"finding": f"missing prerequisite: {results} (results dir)", "got": "absent"}], {}
    schema, pre = _read_schema(results, schema_path)
    if pre:
        return pre, {}
    kind = schema["kinds"]["run_summary"]
    required = kind["required_columns"]
    recognized = kind.get("recognized_columns", required)
    waiver_name = kind.get("waiver_file", "METRIC-WAIVER.json")

    summaries = sorted(results.glob(kind.get("glob", "*/summary.csv")))
    if not summaries:
        return [{"finding": "missing prerequisite: results/*/summary.csv "
                            "(no scannable summaries)", "got": "absent"}], {"n_summaries": 0, "skipped": 0, "waived": 0}

    skipped = waived = 0
    for p in summaries:
        rel = p.relative_to(results)
        if not p.is_file():
            findings.append({"finding": f"missing prerequisite: {rel} (not a file)",
                             "got": "absent"})
            continue
        if not os.access(p, os.R_OK):
            findings.append({"finding": f"unreadable prerequisite: {rel}", "got": "unreadable"})
            continue
        try:
            with open(p, newline="") as fh:
                header = next(csv.reader(fh))
        except Exception as exc:                      # noqa: BLE001
            findings.append({"finding": f"unreadable prerequisite: {rel}: {exc}",
                             "got": "unreadable"})
            continue
        # Leakage-field contract (declared trigger; legacy floor). Runs BEFORE
        # the recognized-column skip so a declared run cannot be silently
        # skipped (Alice's G2) and is required iff it declares itself.
        marker_name = kind.get("leakage_marker")
        if marker_name:
            marker = p.parent / marker_name
            if marker.is_file():
                decl = None
                unparseable = None
                try:
                    decl = json.loads(marker.read_text())
                except Exception as exc:                  # noqa: BLE001
                    unparseable = exc
                if unparseable is not None or not isinstance(decl, dict):
                    findings.append({
                        "finding": f"malformed leakage declaration: {rel.parent / marker_name}",
                        "result": str(rel.parent), "got": "unparseable" if unparseable else "malformed"})
                elif decl.get("leakage_required") is True:
                    pattern = kind.get("leakage_column_pattern", LEAKAGE_METRIC_RE.pattern)
                    if not _leakage_metric_present(header, pattern) \
                            and not _leakage_waived(p.parent / waiver_name):
                        findings.append({
                            "finding": f"required metric not reported: {rel}",
                            "result": str(rel.parent), "metric": "leakage@k",
                            "got": "absent", "want": "present"})
                # leakage_required false/absent -> explicit legacy floor
        if not any(c in header for c in recognized):
            skipped += 1                                  # not a benchmark summary
            continue
        waived_metrics: set[str] = set()
        w = p.parent / waiver_name
        if w.is_file():
            try:
                waived_metrics = set(json.loads(w.read_text()).get("waived", []))
            except Exception:                             # noqa: BLE001
                findings.append({"finding": f"unreadable prerequisite: {rel.parent / waiver_name}",
                                 "got": "unreadable"})
        for metric in required:
            if metric in header:
                continue
            if metric in waived_metrics:
                waived += 1
            else:
                findings.append({"finding": f"required metric not reported: {rel}",
                                 "result": str(rel.parent), "metric": metric,
                                 "got": "absent", "want": "present"})
    return findings, {"n_summaries": len(summaries), "skipped": skipped, "waived": waived}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good"; good.mkdir()
        (good / "summary.csv").write_text("provider,hit@5,prohibited@5,mean_context_chars\nx,0.5,0.1,100\n")
        assert check(root) == ([], check(root)[1]), check(root)
        bad = root / "bad"; bad.mkdir()
        (bad / "summary.csv").write_text("provider,hit@5,prohibited@5\nx,0.5,0.1\n")
        f, _ = check(root)
        assert len(f) == 1 and f[0]["metric"] == "mean_context_chars", f
        (bad / "METRIC-WAIVER.json").write_text(json.dumps({"waived": ["mean_context_chars"]}))
        assert check(root)[0] == [], check(root)

        # An unknown-schema summary is skipped, not failed.
        (root / "odd").mkdir()
        (root / "odd" / "summary.csv").write_text("foo,bar\n1,2\n")
        assert check(root)[0] == [], check(root)

        # Structured prerequisites, matching the suite dialect.
        missing = check(root / "nope")[0]
        assert missing and "missing prerequisite" in missing[0]["finding"], missing
        empty = root / "empty"; empty.mkdir()
        no_sum = check(empty)[0]
        assert no_sum and "no scannable summaries" in no_sum[0]["finding"], no_sum
        explicit = check(root, schema_path=root / "no-schema.json")[0]
        assert explicit and "missing prerequisite" in explicit[0]["finding"], explicit

        # Canonical local schema is read through the same guarded reader.
        for bad_text, token in (("{not json", "malformed schema"), ("{}", "malformed schema")):
            (root / "SCHEMA.json").write_text(bad_text)
            f = check(root)[0]
            assert f and token in f[0]["finding"], (bad_text, f)
        (root / "SCHEMA.json").unlink()
        # Schema shape: a bad type must not traceback or silently skip.
        for bad_obj in ({"kinds": {"run_summary": {}}},
                        {"kinds": {"run_summary": {"required_columns": "hit@5"}}},
                        {"kinds": {"run_summary": {"required_columns": []}}},
                        {"kinds": {"run_summary": {"required_columns": ["hit@5"], "waiver_file": 1}}},
                        {"kinds": {"run_summary": {"required_columns": ["hit@5"], "glob": 1}}}):
            (root / "SCHEMA.json").write_text(json.dumps(bad_obj))
            f = check(root)[0]
            assert f and "malformed schema" in f[0]["finding"], (bad_obj, f)
        (root / "SCHEMA.json").unlink()
        # A directory at */summary.csv is structured, not silently skipped.
        (root / "dirsum").mkdir()
        (root / "dirsum" / "summary.csv").mkdir()
        f = check(root)[0]
        assert any("not a file" in x["finding"] for x in f), f
        (root / "dirsum" / "summary.csv").rmdir()

        # Unreadable canonical schema (no-op under root).
        (root / "SCHEMA.json").write_text("{}")
        os.chmod(root / "SCHEMA.json", 0)
        if not os.access(root / "SCHEMA.json", os.R_OK):
            f = check(root)[0]
            assert f and "unreadable prerequisite" in f[0]["finding"], f
        os.chmod(root / "SCHEMA.json", 0o644)
        (root / "SCHEMA.json").unlink()

    # Leakage-field contract controls (B1-B3 pinned), asserted per case (G1).
    with tempfile.TemporaryDirectory() as td2:
        root2 = Path(td2)

        def mk(name, cols, decl=None, waiver=None):
            d = root2 / name
            d.mkdir()
            (d / "summary.csv").write_text("provider," + ",".join(cols) + "\n"
                                           + "x," + ",".join("0" for _ in cols) + "\n")
            if decl is not None:
                (d / "LEAKAGE-REQUIRED.json").write_text(decl)
            if waiver is not None:
                (d / "METRIC-WAIVER.json").write_text(waiver)

        base = ["hit@5", "prohibited@5", "mean_context_chars"]
        mk("legacy", base)
        mk("declared_present", base + ["leakage@5"], '{"leakage_required": true}')
        mk("declared_missing", base, '{"leakage_required": true}')
        mk("declared_false", base, '{"leakage_required": false}')
        mk("waived", base, '{"leakage_required": true}', '{"waived": ["leakage"]}')
        mk("waiver_wrong_metric", base, '{"leakage_required": true}',
           '{"waived": ["hit@5"], "reason": "leakage"}')
        mk("col_not_leakage", base + ["not_leakage"], '{"leakage_required": true}')
        mk("decl_malformed", base, "{not json")
        mk("decl_list", base, "[]")
        mk("unknown_cols_declared", ["foo"], '{"leakage_required": true}')
        found = check(root2)[0]
        by: dict[str, list[dict]] = {}
        for x in found:
            by.setdefault(x.get("result", "").rsplit("/", 1)[-1], []).append(x)

        def leaked(name):
            return any(x.get("metric") == "leakage@k" for x in by.get(name, []))

        def malformed(name):
            return any("malformed leakage declaration" in x["finding"] for x in by.get(name, []))

        assert leaked("declared_missing"), by
        assert leaked("unknown_cols_declared"), by        # G2: marker precedes skip
        assert leaked("col_not_leakage"), by              # B3: whole-cell matcher
        assert leaked("waiver_wrong_metric"), by          # B1: no reason-substring waiver
        assert not by.get("legacy"), by
        assert not by.get("declared_present"), by
        assert not by.get("declared_false"), by           # B2: boolean trigger
        assert not by.get("waived"), by
        assert malformed("decl_malformed"), by
        assert malformed("decl_list"), by                 # B2: non-object fails closed

    print("self-test: PASS (complete clean; missing metric flagged; waiver suppresses; "
          "unknown schema skipped; missing results/schema and zero summaries structured; "
          "malformed/unreadable local schema and directory summary are structured; "
          "leakage-field controls: declared-missing/unknown-cols/not_leakage/wrong-metric-waiver "
          "flagged, legacy/false/present/waived clean, malformed/non-object fails closed)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="?", default="results")
    ap.add_argument("--schema", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    findings, stats = check(Path(args.results).resolve(), args.schema)
    print(f"=== {args.results}\n    required-metric findings: {len(findings)}  "
          f"(summaries {stats.get('n_summaries')}, skipped {stats.get('skipped')}, "
          f"waived {stats.get('waived')})")
    for f in findings:
        print(f"    {f}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
