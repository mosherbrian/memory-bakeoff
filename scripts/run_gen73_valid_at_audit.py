#!/usr/bin/env python3
"""Gen73: audit what `valid_at` is actually given. No engine is run.

The Perseus adapter derives BOTH `as_of_unix_ms` and `valid_at` from the same
call, `TimeBase.store_instant(event_time)`, which maps a calendar instant onto a
STORE WRITE INSTANT by bisecting ingestion times. That is a transaction-time
coordinate. Asking `valid_at` with it means asking "what did the store contain
at the write instant nearest this date", not "what was valid on this date".

Where event time and ingestion time nearly coincide the two are
indistinguishable. Where they diverge - which is exactly what a backfill is -
the resolved instant falls BEFORE the backfilled fact was written, so the fact
cannot be returned however well the engine works.
"""
from __future__ import annotations

import json, sys
from bisect import bisect_right
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.backfill import (BACKFILL_DEPTH, build_backfill_fixture,   # noqa: E402
                                     backfill_sha256)
from memory_bakeoff.longitudinal import build_longitudinal_fixture             # noqa: E402

OUT = ROOT / "results" / "backfill_gen73"


def store_instant(isos, instants, iso):
    """The adapter's mapping, reproduced exactly."""
    index = bisect_right(isos, iso)
    if index == 0:
        return instants[0] - 1
    if index >= len(instants):
        return instants[-1] + 1
    return (instants[index - 1] + instants[index]) // 2


def audit(fixture, label):
    isos = [o.ingestion_time.isoformat() for o in fixture.observations]
    instants = [1000 + 100 * i for i in range(len(isos))]
    rows = []
    for observation in fixture.observations:
        lag_days = (observation.ingestion_time - observation.event_time).days
        resolved = store_instant(isos, instants, observation.event_time.isoformat())
        written = instants[observation.ingestion_order - 1]
        rows.append({
            "observation": observation.id,
            "event_time": observation.event_time.isoformat(),
            "ingestion_order": observation.ingestion_order,
            "arrival_lag_days": lag_days,
            "valid_at_resolves_to": resolved,
            "actually_written_at": written,
            "unreachable_by_construction": resolved < written and lag_days > 0,
            "is_backfill": observation.id in BACKFILL_DEPTH or observation.historical_only,
        })
    broken = [r for r in rows if r["unreachable_by_construction"]]
    return {"fixture": label, "rows": rows,
            "unreachable_count": len(broken),
            "unreachable": [r["observation"] for r in broken]}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    backfill = audit(build_backfill_fixture(), "backfill-v1")
    original = audit(build_longitudinal_fixture(), "longitudinal-v1")
    payload = {
        "defect": "the Perseus adapter passes a TRANSACTION-time instant to "
                  "`valid_at`; both temporal operations are derived from "
                  "TimeBase.store_instant(event_time), which bisects INGESTION "
                  "times",
        "consequence": "for any observation whose event time precedes its arrival, "
                       "`valid_at` resolves to an instant before that observation "
                       "was written, so it cannot be returned regardless of engine "
                       "behaviour",
        "why_it_hid": "in longitudinal-v1 every observation but one is ingested "
                      "about a minute after its event, so the two clocks coincide "
                      "and the substitution is invisible",
        "backfill_v1_sha256": backfill_sha256(),
        "audits": [backfill, original],
        "engines_run": 0,
    }
    (OUT / "valid_at_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    for entry in payload["audits"]:
        print(f"{entry['fixture']}: {entry['unreachable_count']} observation(s) "
              f"unreachable by construction -> {entry['unreachable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
