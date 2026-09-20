#!/usr/bin/env python3
"""Probe: run.json records must carry an in-vocabulary experiment_class.

AGENTS non-negotiable: preserve the distinction between `baseline`,
`controlled_core`, `raw_product`, and `product`. This probe checks every
provider record in `results/*/run.json`:

  * HARD FAIL (rc 1) on a class value outside the four-value vocabulary.
  * ADVISORY on a record with no `experiment_class` (coverage gap; frozen
    pre-schema dirs are expected to be sparse until a new-run requirement lands).

Not wired into the suite yet (`probe_*` convention; adoption is an owner/QUEUE
decision). Usage: probe_experiment_class_schema.py [--results DIR] [--self-test]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEF_RESULTS = os.path.join(REPO, "results")
VOCAB = {"baseline", "controlled_core", "raw_product", "product"}


def scan(results_dir):
    files = records = have = missing = 0
    bad = []
    for name in sorted(os.listdir(results_dir)):
        rj = os.path.join(results_dir, name, "run.json")
        if not os.path.isfile(rj):
            continue
        try:
            data = json.load(open(rj, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, list):
            continue
        files += 1
        for rec in data:
            if not isinstance(rec, dict):
                continue
            records += 1
            if "experiment_class" not in rec:
                missing += 1
                continue
            have += 1
            val = rec["experiment_class"]
            if val not in VOCAB:
                bad.append(f"{name}/{rec.get('provider')}: {val!r}")
    return {"files": files, "records": records, "have": have,
            "missing": missing, "bad": bad}


def self_test():
    import tempfile
    d = tempfile.mkdtemp()
    good = os.path.join(d, "good"); os.makedirs(good)
    open(os.path.join(good, "run.json"), "w").write(json.dumps(
        [{"provider": "bm25", "experiment_class": "baseline"}]))
    bad = os.path.join(d, "bad"); os.makedirs(bad)
    open(os.path.join(bad, "run.json"), "w").write(json.dumps(
        [{"provider": "x", "experiment_class": "production"},
         {"provider": "y"}]))
    r = scan(d)
    assert r["records"] == 3 and r["have"] == 2 and r["missing"] == 1, r
    assert len(r["bad"]) == 1 and "production" in r["bad"][0], r
    print("self-test: PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=DEF_RESULTS)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not os.path.isdir(a.results):
        print(f"missing prerequisite: {a.results}")
        return 1
    r = scan(a.results)
    print(f"=== {a.results}")
    print(f"    run.json lists={r['files']}  records={r['records']}  "
          f"with class={r['have']}  missing class={r['missing']}  "
          f"out-of-vocab={len(r['bad'])}")
    for x in r["bad"]:
        print(f"    out-of-vocabulary experiment_class: {x}")
    if r["missing"]:
        print(f"    advisory: {r['missing']} record(s) carry no experiment_class "
              f"(frozen pre-schema dirs; see team/CORVID-EXPERIMENT-CLASS-CENSUS.md)")
    return 1 if r["bad"] else 0


if __name__ == "__main__":
    sys.exit(main())
