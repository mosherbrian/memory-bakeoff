"""`interference-v3`: the same experiment, with the world's chronology the right way round.

Gen100 found that `interference-v2` writes the **current** record first and the
**superseded** record second. That is backwards from the world it models: a fact
is stated, and later a newer fact replaces it. The ordering was invisible until
agentmemory's write-time rule met it — its rule retires the older near-duplicate,
so on our order it retired the record we meant to keep, and Gen99 read that as
"agentmemory never finds the current fact in kestrel".

The rule was right. The fixture was wrong.

**This is a new version, not an edit.** `interference_v2` is untouched and its
frozen hashes stay valid for every committed Gen99 result. Nothing about Gen95 or
Gen98 is rewritten; the defect stays on the record, and the repair carries its own
version.

**Exactly one thing changes: the ingest order.** Same four semantic cores, same
load levels, same scope and configuration bindings, same foreign record on both
axes, same query, same scorer. Only the sequence in which the two versions of the
fact are written.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from memory_bakeoff.interference import Case, Fixture, LOAD_LEVELS
from memory_bakeoff.interference_v2 import (CORES, REPLICATION_QUESTIONS,
                                            build_fixture as build_v2,
                                            cases_for_core, replication_verdict)

FIXTURE_VERSION = "interference-v3"
SCORER_VERSION = "interference-scorer-v1"      # unchanged
SUPERSEDES = "interference-v2"

# World chronology: the superseded fact is stated first; the current one replaces
# it. Everything after is unchanged.
INGEST_ROLE_ORDER = ("superseded", "current", "foreign", "distractor")


def build_fixture(cores: Sequence[Mapping[str, Any]] = CORES,
                  levels: Sequence[int] = LOAD_LEVELS) -> Fixture:
    """Identical to v2 in every respect except the order records are written."""
    return build_v2(cores, levels)


def visible_ids(fixture: Fixture, case: Case) -> tuple[str, ...]:
    """This core's records only, in WORLD CHRONOLOGY order.

    v2's helper returned them in construction order, which put the current record
    first. The set is identical; the sequence is the repair.
    """
    mine = [o for o in fixture.observations if o.core == case.core]
    ordered: list[str] = []
    for role in INGEST_ROLE_ORDER:
        group = [o.id for o in mine if o.role == role]
        ordered.extend(group[:case.load] if role == "distractor" else group)
    return tuple(ordered)


def order_changed(fixture: Fixture, case: Case, v2_order: Sequence[str]) -> dict[str, Any]:
    """Show the repair, rather than asserting it."""
    v3 = list(visible_ids(fixture, case))
    return {
        "case": case.id,
        "v2_order": list(v2_order[:3]),
        "v3_order": v3[:3],
        "same_records": sorted(v2_order) == sorted(v3),
        "superseded_now_first": v3[0].endswith("-SUP"),
        "current_now_second": v3[1].endswith("-CUR"),
    }


def contract() -> dict[str, Any]:
    return {
        "fixture_version": FIXTURE_VERSION,
        "supersedes": SUPERSEDES,
        "scorer_version": SCORER_VERSION,
        "single_change": "the ingest order: the superseded record is written FIRST "
                         "and the current record SECOND",
        "why": "v2's order was backwards from the world it models, and agentmemory's "
               "write-time rule - which retires the older near-duplicate - therefore "
               "retired the record we meant to keep (Gen100)",
        "unchanged": ["semantic cores", "load levels", "scope and configuration "
                      "bindings", "the foreign record on both axes", "the query",
                      "the scorer"],
        "v2_not_rewritten": "interference_v2 is untouched; its hashes stay valid for "
                            "every committed Gen99 result, and the defect stays on "
                            "the record",
        "replication_questions_carried_forward": sorted(REPLICATION_QUESTIONS),
        "frozen_before_any_engine_run": True,
    }


def contract_sha256() -> str:
    return hashlib.sha256(
        json.dumps(contract(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
