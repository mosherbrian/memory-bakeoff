"""P6-r8 executable controlled-fault onset capture (stdlib only).

`mark` writes an onset marker file {onset_at (host gmtime), provenance,
uncertainty_s, case/action/execution} at the moment the operator (or test
fault injector) injects the declared fixture fault. `read` prints it back.
The live plan declares per case whether onset comes from an operator marker
(this tool) or a producer-recorded sidecar, with limitations:

- An operator marker stamps the INJECTION command time, not producer time;
  its uncertainty must cover human/transport delay (explicit, finite, >=0).
- A producer sidecar stamps the producer's append time; it shares the host
  clock but is still producer-observed, not harness-observed.
- Witness observation delay is bounded separately by the witness tool.
- Missing/unbounded onset is INCOMPLETE, never acceptance.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time


class OnsetFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _now_z():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def mark(path, case, action, execution, provenance, uncertainty_s):
    try:
        unc = float(uncertainty_s)
    except (TypeError, ValueError):
        raise OnsetFault("E_UNCERTAINTY", "uncertainty not a number")
    if not math.isfinite(unc) or unc < 0:
        raise OnsetFault("E_UNCERTAINTY",
                         "uncertainty must be finite and nonnegative")
    if not provenance:
        raise OnsetFault("E_PROVENANCE", "provenance required")
    rec = {"onset_at": _now_z(), "provenance": provenance,
           "uncertainty_s": unc, "case": case, "action": action,
           "execution": execution,
           "limitation": "injection-command time, not producer time; "
                         "uncertainty covers human/transport delay"}
    with open(path, "w") as fh:
        json.dump(rec, fh, sort_keys=True, indent=1)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r8 fault onset capture")
    sub = ap.add_subparsers(dest="cmd", required=True)
    mk = sub.add_parser("mark")
    mk.add_argument("--out", required=True)
    mk.add_argument("--case", required=True)
    mk.add_argument("--action", required=True)
    mk.add_argument("--execution", required=True)
    mk.add_argument("--provenance", required=True)
    mk.add_argument("--uncertainty-s", required=True)
    rd = sub.add_parser("read")
    rd.add_argument("--path", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "mark":
        print(json.dumps(mark(args.out, args.case, args.action,
                              args.execution, args.provenance,
                              args.uncertainty_s), sort_keys=True))
        return 0
    print(json.dumps(json.load(open(args.path)), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OnsetFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
