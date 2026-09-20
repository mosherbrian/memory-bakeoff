#!/usr/bin/env python3
"""Second-driver re-derivation of PrecisionMemBench's session table.

Reads the shipped test-results/baseline/session-retrieval-report-*.json from
github.com/tenurehq/precisionMemBench and recomputes, per provider, the values
the README publishes: turns passed / pass rate, mean drift, mean precision, and
session p50/p95 latency (nearest-rank), comparing each to the report's own
`retrieval` aggregate where one exists.

Note: the report's p50/p95 use the nearest-rank convention
(ceil(p * n)-th smallest), not the interpolated median. Drift has no aggregate
field in the report, so its per-case mean is reported, not matched.

Usage: python3 verify_session.py <dir>
$0, stdlib only.
"""
import json
import math
import statistics
import sys
from pathlib import Path


def nearest_rank(vals, p):
    v = sorted(vals)
    k = min(max(math.ceil(p * len(v)), 1), len(v))
    return v[k - 1]


def main(root: Path) -> int:
    files = sorted(root.glob("session-retrieval-report-*.json"))
    ok = 0
    print(f"{'provider':22} {'pass/12':>7} {'rate':>7} {'drift':>7} {'prec':>7} "
          f"{'p50':>9} {'p95':>10} {'match':>5}")
    for path in files:
        d = json.loads(path.read_text())
        r, cs, prov = d["retrieval"], d["cases"], d["provider"]
        passed = sum(1 for c in cs if c["passed"])
        rate = passed / len(cs)
        ds = [c["driftScore"] for c in cs if c.get("driftScore") is not None]
        ps = [c["retrievalPrecision"] for c in cs if c.get("retrievalPrecision") is not None]
        la = [c["retrievalLatencyMs"] for c in cs if c.get("retrievalLatencyMs") is not None]
        drift = statistics.fmean(ds) if ds else float("nan")
        prec = statistics.fmean(ps) if ps else float("nan")
        p50, p95 = nearest_rank(la, 0.5), nearest_rank(la, 0.95)
        match = math.isclose(rate, r["passRate"], abs_tol=1e-4)
        match = match and math.isclose(p50, r["p50LatencyMs"], abs_tol=0.01)
        match = match and math.isclose(p95, r["p95LatencyMs"], abs_tol=0.01)
        if prec == prec:  # not NaN
            match = match and math.isclose(prec, r["meanPrecision"], abs_tol=5e-5)
        ok += match
        print(f"{prov:22} {passed:7} {rate:7.4f} {drift:7.4f} {prec:7.4f} "
              f"{p50:9.2f} {p95:10.2f} {str(bool(match)):>5}")
    print(f"\nsession table reproduced for {ok}/{len(files)} providers "
          f"(p50/p95 = nearest-rank; gbrain precision is null by design)")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
