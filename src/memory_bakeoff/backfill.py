"""`backfill-v1`: several independent late-arriving facts, at different depths.

Gen72 found a mirror. Perseus retains superseded belief and cannot reach a fact
that arrived out of order; Hindsight places the backfill correctly and loses the
superseded belief. That rested on **one** correction and **one** backfilled
observation, which is far too thin to call an architectural pattern.

This fixture is built to break or confirm it. It varies the two things that
could each be doing the work:

**Backfill depth** - how far the event time sits behind the moment of arrival:

- `shallow` (B004): dated one day before the fact that arrived just before it
- `deep` (B006): dated eight days back, behind several intervening facts
- `very_deep` (B008): dated before the timeline's first observation

**What happens to the backfilled fact afterwards** - because a store that files
by arrival may cope with a backfill that is never revisited and fail one that is
later corrected, and those are different defects:

- `historical_only` - arrives late, is never revised (B004, B006)
- `later_corrected` - arrives late, then a correction lands on it (B008/B011)

It also carries two independent superseded beliefs, so belief retention is
measured more than once, and one correction whose effective time is backdated in
the same shape as `longitudinal-v1` so the two fixtures can be compared.

`longitudinal-v1` is untouched. This is a separate fixture with its own version
and its own hash; the frozen scorer reads both because the shapes are identical.
"""
from __future__ import annotations

from datetime import datetime, timezone

from memory_bakeoff.longitudinal import (
    Checkpoint, LongitudinalCase, LongitudinalFixture, LongitudinalObservation,
    TargetKind, Transition, canonical_json)

import hashlib

UTC = timezone.utc
FIXTURE_VERSION = "backfill-v1"

# Which backfill each observation is, and how deep. Evaluator-side only.
BACKFILL_DEPTH = {
    "B004": "shallow",      # one day behind the preceding fact
    "B006": "deep",         # eight days back, behind several facts
    "B008": "very_deep",    # before the first observation on the timeline
    "B011": "deep",         # eight days back, and later corrected
}
BACKFILL_FATE = {
    "B004": "historical_only",
    "B006": "historical_only",
    "B008": "later_corrected",
    "B011": "later_corrected",
}


def _t(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def build_backfill_fixture() -> LongitudinalFixture:
    O, C = LongitudinalObservation, LongitudinalCase
    observations = (
        # --- a live timeline, with two beliefs that later get superseded -------
        O("B001", "Alpha rig measured 10 units.", _t("2026-03-01T09:00"),
          _t("2026-03-01T09:00"), 1, _t("2026-03-01T09:01"), "rig:alpha", "v1",
          "synthetic_public", "throughput:alpha", Transition.ADD),
        O("B002", "Beta rig measured 20 units.", _t("2026-03-02T09:00"),
          _t("2026-03-02T09:00"), 2, _t("2026-03-02T09:01"), "rig:beta", "v1",
          "synthetic_public", "throughput:beta", Transition.ADD),
        O("B003", "Alpha rig now measures 12 units.", _t("2026-03-10T09:00"),
          _t("2026-03-10T09:00"), 3, _t("2026-03-10T09:01"), "rig:alpha", "v1",
          "synthetic_public", "throughput:alpha", Transition.SUPERSEDE_CURRENT,
          supersedes_id="B001"),

        # --- shallow backfill, never revised ----------------------------------
        O("B004", "Recovered log: Alpha read 11 units on 9 March.",
          _t("2026-03-09T09:00"), _t("2026-03-09T09:00"), 4, _t("2026-03-11T09:01"),
          "rig:alpha", "v1", "synthetic_public", "throughput:alpha",
          Transition.ADD, historical_only=True),

        # --- a second superseded belief, on an unrelated key -------------------
        O("B005", "Beta rig now measures 25 units.", _t("2026-03-12T09:00"),
          _t("2026-03-12T09:00"), 5, _t("2026-03-12T09:01"), "rig:beta", "v1",
          "synthetic_public", "throughput:beta", Transition.SUPERSEDE_CURRENT,
          supersedes_id="B002"),

        # --- deep backfill, never revised -------------------------------------
        O("B006", "Recovered log: Beta read 22 units on 4 March.",
          _t("2026-03-04T09:00"), _t("2026-03-04T09:00"), 6, _t("2026-03-13T09:01"),
          "rig:beta", "v1", "synthetic_public", "throughput:beta",
          Transition.ADD, historical_only=True),

        # --- a live fact, so the very-deep backfill has company ---------------
        O("B007", "Gamma rig measured 30 units.", _t("2026-03-14T09:00"),
          _t("2026-03-14T09:00"), 7, _t("2026-03-14T09:01"), "rig:gamma", "v1",
          "synthetic_public", "throughput:gamma", Transition.ADD),

        # --- very deep backfill, later corrected ------------------------------
        O("B008", "Recovered log: Gamma read 28 units on 25 February.",
          _t("2026-02-25T09:00"), _t("2026-02-25T09:00"), 8, _t("2026-03-15T09:01"),
          "rig:gamma", "v1", "synthetic_public", "throughput:gamma",
          Transition.ADD, historical_only=True),
        O("B009", "Audit corrected the recovered Gamma log: it was 29, not 28.",
          _t("2026-03-18T09:00"), _t("2026-02-25T09:00"), 9, _t("2026-03-18T09:01"),
          "rig:gamma", "v1", "synthetic_public", "throughput:gamma",
          Transition.CORRECTION, corrects_id="B008"),

        # --- a live fact and a deep backfill that is then corrected -----------
        O("B010", "Delta rig measured 40 units.", _t("2026-03-19T09:00"),
          _t("2026-03-19T09:00"), 10, _t("2026-03-19T09:01"), "rig:delta", "v1",
          "synthetic_public", "throughput:delta", Transition.ADD),
        O("B011", "Recovered log: Delta read 38 units on 11 March.",
          _t("2026-03-11T09:00"), _t("2026-03-11T09:00"), 11, _t("2026-03-20T09:01"),
          "rig:delta", "v1", "synthetic_public", "throughput:delta",
          Transition.ADD, historical_only=True),
        O("B012", "Audit corrected the recovered Delta log: it was 39, not 38.",
          _t("2026-03-22T09:00"), _t("2026-03-11T09:00"), 12, _t("2026-03-22T09:01"),
          "rig:delta", "v1", "synthetic_public", "throughput:delta",
          Transition.CORRECTION, corrects_id="B011"),
    )

    checkpoints = tuple(Checkpoint(f"BP{n:02d}", n, f"after ingestion {n}")
                        for n in (3, 4, 6, 8, 9, 11, 12))

    cases = (
        # belief retention, measured twice on independent keys
        C("BQ01", "BP04", TargetKind.HISTORICAL_BELIEF, "throughput:alpha",
          "What was Alpha's reading believed to be on 1 March?", ("B001",), ("B003",),
          event_time=_t("2026-03-01T09:00"), scope="rig:alpha", configuration="v1",
          rationale="superseded belief, first key"),
        C("BQ02", "BP06", TargetKind.HISTORICAL_BELIEF, "throughput:beta",
          "What was Beta's reading believed to be on 2 March?", ("B002",), ("B005",),
          event_time=_t("2026-03-02T09:00"), scope="rig:beta", configuration="v1",
          rationale="superseded belief, second key"),

        # shallow backfill, never revised
        C("BQ03", "BP04", TargetKind.LATE_HISTORY, "throughput:alpha",
          "What did the recovered log say Alpha read on 9 March?", ("B004",), (),
          event_time=_t("2026-03-09T09:00"), scope="rig:alpha", configuration="v1",
          rationale="shallow backfill, historical only"),
        C("BQ04", "BP06", TargetKind.AS_OF, "throughput:alpha",
          "What was Alpha's reading on 9 March?", ("B004",), ("B003",),
          event_time=_t("2026-03-09T09:00"), scope="rig:alpha", configuration="v1",
          rationale="shallow backfill must win at its own event time"),

        # deep backfill, never revised
        C("BQ05", "BP06", TargetKind.LATE_HISTORY, "throughput:beta",
          "What did the recovered log say Beta read on 4 March?", ("B006",), (),
          event_time=_t("2026-03-04T09:00"), scope="rig:beta", configuration="v1",
          rationale="deep backfill, historical only"),
        C("BQ06", "BP08", TargetKind.AS_OF, "throughput:beta",
          "What was Beta's reading on 4 March?", ("B006",), ("B005",),
          event_time=_t("2026-03-04T09:00"), scope="rig:beta", configuration="v1",
          rationale="deep backfill must win at its own event time"),

        # very deep backfill, later corrected
        C("BQ07", "BP08", TargetKind.LATE_HISTORY, "throughput:gamma",
          "What did the recovered log say Gamma read on 25 February?", ("B008",), (),
          event_time=_t("2026-02-25T09:00"), scope="rig:gamma", configuration="v1",
          rationale="very deep backfill, before the timeline starts"),
        C("BQ08", "BP09", TargetKind.CORRECTED_HISTORY, "throughput:gamma",
          "What was Gamma's corrected reading for 25 February?", ("B009",), ("B008",),
          event_time=_t("2026-02-25T09:00"), scope="rig:gamma", configuration="v1",
          rationale="a correction landing on a very deep backfill"),
        C("BQ09", "BP09", TargetKind.HISTORICAL_BELIEF, "throughput:gamma",
          "What did the recovered Gamma log say before the audit?", ("B008",), ("B009",),
          event_time=_t("2026-02-25T09:00"), scope="rig:gamma", configuration="v1",
          rationale="belief about a backfilled fact, before its correction"),

        # deep backfill, later corrected
        C("BQ10", "BP11", TargetKind.LATE_HISTORY, "throughput:delta",
          "What did the recovered log say Delta read on 11 March?", ("B011",), (),
          event_time=_t("2026-03-11T09:00"), scope="rig:delta", configuration="v1",
          rationale="deep backfill, about to be corrected"),
        C("BQ11", "BP12", TargetKind.CORRECTED_HISTORY, "throughput:delta",
          "What was Delta's corrected reading for 11 March?", ("B012",), ("B011",),
          event_time=_t("2026-03-11T09:00"), scope="rig:delta", configuration="v1",
          rationale="a correction landing on a deep backfill"),

        # current-truth controls, so the fixture is not only historical
        C("BQ12", "BP12", TargetKind.CURRENT, "throughput:alpha",
          "What does Alpha currently measure?", ("B003",), ("B001",),
          scope="rig:alpha", configuration="v1",
          rationale="control: current truth must not be the superseded value"),
        C("BQ13", "BP12", TargetKind.CURRENT, "throughput:delta",
          "What does Delta currently measure?", ("B010",), (),
          scope="rig:delta", configuration="v1",
          rationale="control: a backfill must not displace current truth"),
    )
    return LongitudinalFixture(observations, checkpoints, cases)


def backfill_payload(fixture: LongitudinalFixture | None = None) -> dict:
    fixture = fixture or build_backfill_fixture()
    return {
        "fixture_version": FIXTURE_VERSION,
        "observations": [o.truth_dict() for o in fixture.observations],
        "checkpoints": [{"id": c.id, "ingestion_order": c.ingestion_order,
                         "description": c.description} for c in fixture.checkpoints],
        "cases": [c.truth_dict() for c in fixture.cases],
        "backfill_depth": BACKFILL_DEPTH,
        "backfill_fate": BACKFILL_FATE,
    }


def backfill_sha256(fixture: LongitudinalFixture | None = None) -> str:
    return hashlib.sha256(canonical_json(backfill_payload(fixture)).encode()).hexdigest()
