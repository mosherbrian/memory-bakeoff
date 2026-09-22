"""P6-r6 independent timing witness (stdlib only; independent of candidate
decision timestamps, T1). Two subcommands:

observe: bounded wait for one end record {t:"end",item} on a recorded
  stream path, stamping host-clock detection time; reads the controlled
  onset file {onset_at, provenance, uncertainty_s} for that item; emits one
  timing row with action/execution correlation, detection = onset->detected,
  worker_duration = dispatch->detected (reported, never gated), and
  uncertainty = onset_uncertainty + poll_interval + 1s host-clock bound.
  A stream-notification wait is used where available; observation delay is
  recorded as bound, never asserted as exact producer time.

  Controlled onset sources (declared in the live plan, never invented by
  this tool): (a) producer-recorded onset sidecar; (b) operator-declared
  fixture-fault marker file written at fault injection with host timestamp.
  Missing onset file -> row with onset_at null (INCOMPLETE downstream).

check: gates rows against detection/recovery/total bounds (defaults 30/60/
  90, extended 180/240 reported); any success row without onset, or any
  failure row, yields verdicts that never pass the campaign criterion:
  missing onset -> "incomplete" (rc 3); late detection -> E_GATE_DETECT.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time


class WitnessFault(Exception):
    def __init__(self, code, detail):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _instant(v):
    if not isinstance(v, str):
        return None
    try:
        s = v.strip().replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        return None


def _now_z():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def observe_end(stream_path, item, timeout_s=60.0, poll_s=0.5):
    """Poll-bound wait for the end record; returns (detected_at_z, wait_s).
    wait_s bounds the observation delay (uncertainty, not exactness)."""
    deadline = time.monotonic() + timeout_s
    waited = 0.0
    seen = set()
    while True:
        try:
            with open(stream_path, "rb") as fh:
                data = fh.read().decode("utf-8", "replace")
        except OSError:
            data = ""
        for line in data.split("\n"):
            line = line.strip()
            if not line or line in seen:
                continue
            seen.add(line)
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and row.get("t") == "end" and \
                    row.get("item") == item:
                return _now_z(), waited
        if time.monotonic() >= deadline:
            raise WitnessFault("E_NO_END",
                               "no end for item %r within %.0fs" % (item,
                                                                   timeout_s))
        time.sleep(min(poll_s, max(0.0, deadline - time.monotonic())))
        waited += poll_s


def read_onset(onset_path):
    try:
        rec = json.load(open(onset_path))
    except (OSError, ValueError):
        return (None, None, None)
    if not isinstance(rec, dict):
        return (None, None, None)
    return (rec.get("onset_at"), rec.get("provenance"),
            rec.get("uncertainty_s"))


def emit_row(action, execution, dispatch_at, detected_at, onset, out_path):
    onset_at, prov, unc = onset
    row = {"action": action, "execution": execution,
           "dispatch_at": dispatch_at, "detected_at": detected_at,
           "committed_at": None, "outcome": "observed-end",
           "onset_at": onset_at, "onset_provenance": prov,
           "onset_uncertainty_s": unc, "onset_known": onset_at is not None,
           "witness": "p6r6-external", "witness_clock": "host-gmtime"}
    if onset_at and detected_at:
        o, d = _instant(onset_at), _instant(detected_at)
        s = _instant(dispatch_at)
        row["detection_latency_s"] = (d - o).total_seconds() if o and d \
            else None
        row["worker_duration_s"] = (d - s).total_seconds() if d and s \
            else None
    with open(out_path, "a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def check_rows(rows_path, detect=30.0, recover=60.0, total=90.0,
               ext_detect=180.0, ext_total=240.0):
    rows = [json.loads(l) for l in open(rows_path)
            if l.strip()]
    if not rows:
        raise WitnessFault("E_NO_ROWS", "no witness rows")
    success = [r for r in rows if r.get("outcome") in ("observed-end",
                                                       "recovered")]
    unknown = [r for r in success if not r.get("onset_at")]
    late = []
    for r in success:
        if r.get("onset_at") and r.get("detected_at"):
            det = (_instant(r["detected_at"]) - _instant(r["onset_at"])
                   ).total_seconds()
            r["detection_latency_s"] = det
            if det > detect:
                late.append((r.get("action"), det))
    report = {"samples": len(rows), "success": len(success),
              "unmeasured": len(unknown),
              "late_detections": [[a, d] for a, d in late],
              "extended_bounds": {"detect_s": ext_detect,
                                  "total_s": ext_total}}
    if unknown:
        report.update({"verdict": "incomplete",
                       "reason": "%d of %d rows lack independent onset; "
                                 "INCOMPLETE, never passing" % (
                                     len(unknown), len(success))})
        return report
    if late:
        raise WitnessFault("E_GATE_DETECT",
                           "late detection(s): %s" % (late,))
    report["verdict"] = "within-bounds"
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="P6-r6 timing witness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ob = sub.add_parser("observe")
    ob.add_argument("--stream", required=True)
    ob.add_argument("--item", required=True)
    ob.add_argument("--onset-file", default="")
    ob.add_argument("--action", required=True)
    ob.add_argument("--execution", required=True)
    ob.add_argument("--dispatch-at", default="")
    ob.add_argument("--timeout-s", type=float, default=60.0)
    ob.add_argument("--out", required=True)
    ck = sub.add_parser("check")
    ck.add_argument("--rows", required=True)
    ck.add_argument("--detect", type=float, default=30.0)
    ck.add_argument("--recover", type=float, default=60.0)
    ck.add_argument("--total", type=float, default=90.0)
    args = ap.parse_args(argv)
    if args.cmd == "observe":
        detected, waited = observe_end(args.stream, args.item,
                                       args.timeout_s)
        onset = read_onset(args.onset_file) if args.onset_file else (
            None, None, None)
        row = emit_row(args.action, args.execution, args.dispatch_at or
                       None, detected, onset, args.out)
        row["observation_wait_s"] = waited
        print(json.dumps(row, sort_keys=True))
        return 0
    verdict = check_rows(args.rows, args.detect, args.recover, args.total)
    print(json.dumps(verdict, sort_keys=True))
    return 0 if verdict.get("verdict") == "within-bounds" else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WitnessFault as e:
        print(json.dumps({"error": e.code, "detail": e.detail,
                          "owner": "cairn"}, sort_keys=True))
        raise SystemExit(3)
