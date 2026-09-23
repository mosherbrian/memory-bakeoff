"""Runtime source-time hook (stdlib only): trusted end-append receipts.

The model seat never types a clock. This module stamps host UTC at the
actual end-record append, bound to the runtime session/item, with
provenance, second-resolution uncertainty and clock-discontinuity
handling. Unknown/discontinuous time is flagged INCOMPLETE downstream —
never backfilled or guessed.

Source record format (versioned fields in the SAME end record; one
append, no unsynchronized sidecar)::

    {"t": "end", "item": "<id>",
     "src_v": 1, "src_at": "2026-09-23T01:00:05Z",
     "src_session": "<runtime session id>",
     "src_provenance": "runtime-end-append",
     "src_uncertainty_s": 1, "src_clock": "ok",
     "src_status": "ok"}

``src_clock`` is ``ok`` (trusted host UTC), ``discontinuous`` (wall vs
monotonic diverged past tolerance: stamp kept, flagged unusable) or
``test`` (fixture-only injected clock via ``ACP_SOURCE_TEST_NOW`` or the
explicit ``now`` argument — never set on live paths).

Failure semantics: the append is one ``write`` call. If it fails, this
module raises ``SourceWriteError`` AFTER a stderr notice; the runtime
caller keeps the turn alive (telemetry never kills model work) while the
evidence honestly records absence. Consumers treat missing/unreadable
source as INCOMPLETE, never PASS.
"""
from __future__ import annotations

import json
import os
import sys
import time

SRC_VERSION = 1
SRC_PROVENANCE = "runtime-end-append"
SRC_UNCERTAINTY_S = 1
DISCONTINUITY_THRESHOLD_S = 60

_TEST_NOW_ENV = "ACP_SOURCE_TEST_NOW"

_last = {"wall": None, "mono": None}


class SourceWriteError(OSError):
    pass


def _host_now():
    return time.time(), time.monotonic()


def _instant_str(epoch_s):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch_s))


def _clock_state(wall, mono):
    global _last
    prev_w, prev_m = _last["wall"], _last["mono"]
    _last["wall"], _last["mono"] = wall, mono
    if prev_w is None:
        return "ok"
    if abs((wall - prev_w) - (mono - prev_m)) > DISCONTINUITY_THRESHOLD_S:
        return "discontinuous"
    return "ok"


def source_fields(session, item, now=None):
    """Build the source receipt fields for one end append.

    ``now`` (epoch seconds) or ``ACP_SOURCE_TEST_NOW`` (UTC ISO Z) inject
    a fixture clock and mark the record ``test``; otherwise real host UTC
    (``ok``/``discontinuous``). Raises ValueError on empty session/item.
    """
    if not session or not isinstance(session, str):
        raise ValueError("source needs a nonempty session")
    if not item or not isinstance(item, str):
        raise ValueError("source needs a nonempty item")
    clock = "ok"
    if now is None:
        test_now = os.environ.get(_TEST_NOW_ENV)
        if test_now:
            from datetime import datetime, timezone
            try:
                now = datetime.strptime(
                    test_now, "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=timezone.utc).timestamp()
            except ValueError:
                raise ValueError("ACP_SOURCE_TEST_NOW malformed")
            clock = "test"
    if now is None:
        wall, mono = _host_now()
        now = wall
        clock = _clock_state(wall, mono)
    return {"src_v": SRC_VERSION, "src_at": _instant_str(now),
            "src_session": session, "src_provenance": SRC_PROVENANCE,
            "src_uncertainty_s": SRC_UNCERTAINTY_S, "src_clock": clock,
            "src_status": "ok"}


def emit_end(stream_path, session, item, extra=None, now=None):
    """Append one end record with its source receipt (single write).

    This is the shipped hook the instrumented runtime calls and tests
    execute in a subprocess. Returns the record dict. Raises
    SourceWriteError (after a stderr notice) when the append fails.
    """
    record = {"t": "end", "item": item}
    record.update(source_fields(session, item, now=now))
    if extra:
        record.update(extra)
    line = json.dumps(record, sort_keys=True) + "\n"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(stream_path)),
                    exist_ok=True)
        with open(stream_path, "a") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())
    except OSError as e:
        sys.stderr.write("source-time append failed: %s\n" % e)
        raise SourceWriteError(str(e))
    return record


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="runtime source-time hook")
    sub = ap.add_subparsers(dest="cmd")
    e = sub.add_parser("emit-end")
    e.add_argument("--stream", required=True)
    e.add_argument("--session", required=True)
    e.add_argument("--item", required=True)
    e.add_argument("--now", default=None)
    args = ap.parse_args(argv)
    if args.cmd != "emit-end":
        ap.print_usage(sys.stderr)
        return 2
    now = float(args.now) if args.now else None
    try:
        rec = emit_end(args.stream, args.session, args.item, now=now)
    except (SourceWriteError, ValueError) as exc:
        sys.stderr.write("emit-end failed: %s\n" % exc)
        return 3
    print(json.dumps(rec, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
