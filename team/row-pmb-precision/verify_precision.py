#!/usr/bin/env python3
"""Second-driver re-derivation of PrecisionMemBench's published mean-precision column.

Reads the shipped per-case baseline reports from
github.com/tenurehq/precisionMemBench/test-results/baseline/ and recomputes
the `retrieval.meanPrecision` aggregate two ways:
  (a) over all cases with a non-null retrievalPrecision  -> matches the shipped aggregate
  (b) over the cases with a non-null retrievalRecall (the README's stated
      "43 cases that require active query-dependent retrieval")
and the recall mean over (b).

Usage:  python3 verify_precision.py <dir-with-retrieval-report-*.json>
$0, stdlib only.
"""
import json
import math
import statistics
import sys
from pathlib import Path


def main(root: Path) -> int:
    rows = []
    for path in sorted(root.glob("retrieval-report-*.json")):
        d = json.loads(path.read_text())
        r = d["retrieval"]
        cs = d["cases"]
        p = [c for c in cs if c.get("retrievalPrecision") is not None]
        rr = [c for c in cs if c.get("retrievalRecall") is not None]
        m70 = statistics.fmean(c["retrievalPrecision"] for c in p) if p else float("nan")
        p43 = [c for c in rr if c.get("retrievalPrecision") is not None]
        m43 = statistics.fmean(c["retrievalPrecision"] for c in p43) if p43 else float("nan")
        rec = statistics.fmean(c["retrievalRecall"] for c in rr) if rr else float("nan")
        rows.append((d["provider"], r["meanPrecision"], m70, m43, rec,
                     r["totalPassed"], r["activeRetrievalPasses"], len(p), len(rr),
                     math.isclose(m70, r["meanPrecision"], rel_tol=0, abs_tol=5e-5)))
    hdr = f"{'provider':22} {'shipped':>8} {'over-nP':>8} {'over-43':>8} {'recall':>8} {'nP':>4} {'nR':>4} {'match':>5}"
    print(hdr)
    bad = 0
    for prov, ship, m70, m43, rec, tp, ap, np_, nr, ok in rows:
        print(f"{prov:22} {ship:8.4f} {m70:8.4f} {m43:8.4f} {rec:8.4f} {np_:4} {nr:4} {str(ok):>5}")
        if not ok:
            bad += 1
    print(f"\nshipped meanPrecision == mean over all precision-bearing cases for "
          f"{len(rows)-bad}/{len(rows)} providers")
    print("README method note: 'Mean precision and recall are computed over the 43 "
          "cases that require active query-dependent retrieval.'")
    print("=> recall matches the 43-case set; precision does NOT where nP != 43.")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
