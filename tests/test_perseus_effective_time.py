"""The repaired adapter must separate the two clocks, and prove it before any run.

Sol's condition for Gen74 was deterministic adapter tests demonstrating the
divergence ahead of any engine call, so these run on the fixtures alone.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass

from memory_bakeoff import backfill as B
from memory_bakeoff.longitudinal import (TargetKind, build_longitudinal_fixture)
from memory_bakeoff.providers import perseus_effective_time as V2


@dataclass(frozen=True)
class FakeTimeBase:
    """The frozen adapter's mapping, reproduced so the two can be compared."""
    fixture_iso: tuple
    write_instants: tuple

    def store_instant(self, iso: str) -> int:
        index = bisect_right(self.fixture_iso, iso)
        if index == 0:
            return self.write_instants[0] - 1
        if index >= len(self.write_instants):
            return self.write_instants[-1] + 1
        return (self.write_instants[index - 1] + self.write_instants[index]) // 2


def base_for(fixture) -> FakeTimeBase:
    isos = tuple(o.ingestion_time.isoformat() for o in fixture.observations)
    return FakeTimeBase(isos, tuple(1000 + 100 * i for i in range(len(isos))))


def test_valid_at_now_carries_the_effective_time_not_a_store_instant():
    fixture = B.build_backfill_fixture()
    case = next(c for c in fixture.cases if c.target_kind is TargetKind.AS_OF)
    arguments = V2.recall_arguments(case, base_for(fixture), 5)
    assert arguments["valid_at"] == int(case.event_time.timestamp() * 1000)
    assert arguments["valid_at"] > 1_700_000_000_000  # a real calendar instant


def test_as_of_still_maps_through_ingestion_order():
    """Transaction time is a knowledge-time question; that mapping was correct."""
    fixture = B.build_backfill_fixture()
    case = next(c for c in fixture.cases
                if c.target_kind is TargetKind.HISTORICAL_BELIEF)
    time_base = base_for(fixture)
    arguments = V2.recall_arguments(case, time_base, 5)
    assert arguments["as_of_unix_ms"] == time_base.store_instant(
        case.event_time.isoformat())
    assert "valid_at" not in arguments


def test_the_two_clocks_diverge_on_every_backfill_case():
    fixture = B.build_backfill_fixture()
    time_base = base_for(fixture)
    diverged = 0
    for case in fixture.cases:
        if V2.native_operation(case) != "recall_hybrid_valid_at":
            continue
        both = V2.clocks_diverge(case, time_base)
        assert both["valid_at_v2"] != both["store_instant_v1"]
        diverged += 1
    assert diverged >= 4


def test_the_clocks_also_diverge_on_the_original_fixture():
    fixture = build_longitudinal_fixture()
    time_base = base_for(fixture)
    checked = [V2.clocks_diverge(c, time_base) for c in fixture.cases
               if V2.native_operation(c) == "recall_hybrid_valid_at"]
    assert checked
    assert all(b["valid_at_v2"] != b["store_instant_v1"] for b in checked)


def test_current_state_cases_carry_no_temporal_argument():
    fixture = B.build_backfill_fixture()
    case = next(c for c in fixture.cases if c.target_kind is TargetKind.CURRENT)
    arguments = V2.recall_arguments(case, base_for(fixture), 5)
    assert "valid_at" not in arguments and "as_of_unix_ms" not in arguments


def test_the_frozen_adapter_is_not_imported():
    source = open(V2.__file__).read()
    assert "perseus_longitudinal" not in source


def test_the_contract_records_the_measured_store_limitation():
    contract = V2.contract()
    assert "write instant regardless" in contract["measured_store_limitation"]
    assert contract["old_results_status"].startswith("retained as invalid")
