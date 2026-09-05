"""`round2-reconciliation-gen88-v1`: the corrected retrieval-layer picture of Round 2.

Round 2 reported an eight-row table of clean counts per engine. Eleven
generations of audit have since established that several of its rows were not
what they appeared to be:

- two rows asked questions no retriever could answer (Gen83, Gen84), and are
  excluded here by the Gen87 layer boundary rather than by hand;
- the temporal rows rested on a coordinate error, and four claims were retracted,
  qualified or reattributed (Gen73, Gen74, Gen75);
- the scope row measured the harness, because three of four adapters were never
  given a scope to honour (Gen76), and a fair binding changed the answer
  completely (Gen78);
- configuration isolation was never asked at all until Gen80, and its one real
  engine difference was localised and closed in Gen81 and Gen82.

This module rebuilds the table from the corrected evidence only. **No number is
carried forward because it was previously printed.** Every cell states its own
status and names the generation it comes from; a cell with no provenance is a
construction error and `assert_complete` fails on it.

**Two tables, never one.** They answer different questions and must not share a
ranking column:

- **`frozen_configuration`** — *what did the tested configuration do?* This is the
  Round-2 record: real behaviour of a real setup, including its handicaps.
- **`native_capability`** — *what can this pinned engine and interface do when
  correctly bound?* This is the ablation series, where a handicap was removed and
  exactly one variable moved.

An engine that collapses scopes in the first table and isolates them perfectly in
the second is not a contradiction. It is the difference between a configuration
and a capability, and merging the two columns would erase the only thing eleven
generations established.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from memory_bakeoff.layer_boundary import (ANSWERABLE_AT, READER_LAYER_KINDS,
                                           RETRIEVAL_ONLY, assert_no_layer_mixing)

CONTRACT_VERSION = "round2-reconciliation-gen88-v1"

MEASURED = "MEASURED"
NOT_DEMONSTRABLE = "NOT_DEMONSTRABLE"
NOT_APPLICABLE = "NOT_APPLICABLE"
STATUSES = (MEASURED, NOT_DEMONSTRABLE, NOT_APPLICABLE)

ENGINES = ("perseus", "mem0", "hindsight", "agentmemory")
RETRIEVAL_KINDS = tuple(k for k, v in ANSWERABLE_AT.items() if v == RETRIEVAL_ONLY)


def cell(status: str, finding: str, provenance: str, *, value: Any = None) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}")
    if not provenance:
        raise ValueError("every cell must name where it comes from")
    return {"status": status, "finding": finding, "provenance": provenance,
            "value": value}


# --- Table A: what the tested configuration actually did ------------------
def frozen_configuration() -> dict[str, dict[str, Any]]:
    """The Round-2 record, corrected. Handicaps included, because they were real."""
    table: dict[str, dict[str, Any]] = {k: {} for k in RETRIEVAL_KINDS}

    for engine in ENGINES:
        table["current_truth"][engine] = cell(
            MEASURED, "current-state retrieval was exercised on every engine",
            "Gen68 per-kind counts, retrieval layer, never retracted")

    table["scope_truth"]["perseus"] = cell(
        MEASURED, "the only adapter that passed a scope filter on both paths",
        "Gen76 scope audit: workspace_hash derived from the case scope")
    for engine in ("mem0", "hindsight", "agentmemory"):
        table["scope_truth"][engine] = cell(
            NOT_DEMONSTRABLE,
            "the configuration collapses scopes, which is true of the "
            "configuration; the engine was never asked to isolate",
            "Gen76: no scope filter on write or query in the frozen adapter")

    table["historical_belief"]["perseus"] = cell(
        MEASURED, "preserves what was believed at a past moment",
        "Gen68 6/6 clean; as_of cases, a transaction-time question correctly "
        "mapped; survives Gen75")
    for engine in ("mem0", "hindsight", "agentmemory"):
        table["historical_belief"][engine] = cell(
            MEASURED, "answers with present truth instead of past belief",
            "Gen68 belief_truth_confusion; survives Gen75")

    for kind in ("as_of_event_truth", "corrected_historical_truth"):
        table[kind]["perseus"] = cell(
            NOT_DEMONSTRABLE,
            "the adapter fed valid_at a transaction-time instant, so "
            "effective-time behaviour was never exercised",
            "Gen73 coordinate error; Gen74 measured that the store has no "
            "caller-settable validity coordinate; Gen75 retraction")
        for engine in ("mem0", "agentmemory"):
            table[kind][engine] = cell(
                NOT_APPLICABLE, "no temporal query surface exists to exercise",
                "Gen71: every case routed to current-state search")
        table[kind]["hindsight"] = cell(
            MEASURED, "query_timestamp is accepted and ignored",
            "Gen70: 15 of 15 leaked on its own parameter and its own path")

    table["late_arriving_history"]["perseus"] = cell(
        NOT_DEMONSTRABLE,
        "the recorded failure was the harness asking an effective-time question "
        "through a knowledge-time coordinate",
        "Gen68 line REATTRIBUTED by Gen75; not a perseus capability result")
    for engine in ("mem0", "hindsight", "agentmemory"):
        table["late_arriving_history"][engine] = cell(
            MEASURED, "late-arriving history retrieved cleanly",
            "Gen68 3/3; retrieval layer, never retracted")
    return table


# --- Table B: what the pinned engine can do when correctly bound ----------
def native_capability() -> dict[str, dict[str, Any]]:
    """The ablation series. One variable moved each time, handicap removed."""
    table: dict[str, dict[str, Any]] = {
        "scope_isolation": {}, "configuration_isolation": {},
        "effective_time_recording": {}}

    table["scope_isolation"]["perseus"] = cell(
        MEASURED, "isolates scopes", "Gen76: already exercised in Round 2",
        value="6/9 clean in the frozen configuration")
    for engine in ("mem0", "hindsight", "agentmemory"):
        table["scope_isolation"][engine] = cell(
            MEASURED, "isolates scopes perfectly once given its own scope key",
            "Gen78 ablation, frozen Gen77 binding, three repetitions",
            value="0 scope_collapse in 6 case runs")

    for engine in ("perseus", "mem0", "hindsight"):
        table["configuration_isolation"][engine] = cell(
            MEASURED, "separates two configurations inside one scope",
            "Gen80 ablation on LQ03: 3/3 collapse became 0/3, 3/3 clean retrieval",
            value="0/3 collapse")
    table["configuration_isolation"]["agentmemory"] = cell(
        MEASURED,
        "does not separate configurations; search ignores the project field, and "
        "no second identity is accepted on both write and search",
        "Gen80 3/3 collapse; Gen81 localised it to search-time ignoring; Gen82 "
        "NO_USABLE_SECOND_SURFACE",
        value="3/3 collapse")

    table["effective_time_recording"]["perseus"] = cell(
        NOT_DEMONSTRABLE,
        "valid_from_unix_ms is set from the write instant and no write flag "
        "exposes validity, so a repaired query has nothing to match against",
        "Gen74 measured on the pinned build")
    for engine in ("mem0", "hindsight", "agentmemory"):
        table["effective_time_recording"][engine] = cell(
            NOT_APPLICABLE, "no effective-time surface exists on this interface",
            "Gen71 capability survey")
    return table


def assert_complete(table: Mapping[str, Mapping[str, Any]], *, engines=ENGINES) -> None:
    """Every cell present, statused and sourced. A gap is a construction error."""
    for row, cells in table.items():
        missing = sorted(set(engines) - set(cells))
        if missing:
            raise ValueError(f"row {row!r} has no cell for {missing}")
        for engine, entry in cells.items():
            if entry["status"] not in STATUSES:
                raise ValueError(f"{row}/{engine}: bad status {entry['status']!r}")
            if not entry["provenance"]:
                raise ValueError(f"{row}/{engine}: no provenance")


def reconciliation() -> dict[str, Any]:
    frozen, native = frozen_configuration(), native_capability()
    assert_no_layer_mixing(frozen, layer=RETRIEVAL_ONLY)
    assert_complete(frozen)
    assert_complete(native)
    return {
        "contract_version": CONTRACT_VERSION,
        "retrieval_layer_kinds": list(RETRIEVAL_KINDS),
        "excluded_reader_kinds": sorted(READER_LAYER_KINDS),
        "exclusion_reason": "no retriever can answer them; enforced by the Gen87 "
                            "layer boundary, not by hand",
        "frozen_configuration": frozen,
        "native_capability": native,
        "two_tables_rule": "frozen_configuration answers 'what did this "
                           "configuration do?'; native_capability answers 'what can "
                           "this pinned engine do when correctly bound?'. They must "
                           "never share a ranking column - an engine that collapses "
                           "scopes in the first and isolates them in the second is "
                           "the difference between a configuration and a capability",
        "no_single_score": "the temporal axes vary independently and are not "
                           "collapsed; no engine is given a total",
        "superseded_numbers_not_carried": "no Gen68 cell is reprinted because it was "
                                          "printed before; each is restated from the "
                                          "generation that last examined it",
        "no_engine_runs": True,
    }


def counts() -> dict[str, dict[str, int]]:
    """How much of the corrected table is actually evidence about an engine."""
    out = {}
    for name, table in (("frozen_configuration", frozen_configuration()),
                        ("native_capability", native_capability())):
        tally = {status: 0 for status in STATUSES}
        for cells in table.values():
            for entry in cells.values():
                tally[entry["status"]] += 1
        out[name] = tally
    return out
