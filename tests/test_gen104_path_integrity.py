"""Gen104: the two invariants that would have caught the Gen102 defect."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from memory_bakeoff import interference as ITF
from memory_bakeoff import interference_v2 as V2
from memory_bakeoff import interference_v3 as V3

ROOT = Path(__file__).resolve().parents[1]


# --- the defect itself ------------------------------------------------------
def test_the_defect_only_ever_bit_v3():
    """v1 and v2 resolver order matched construction order; v3's did not.

    This is the blast radius. Gen97 (v1) and Gen99 (v2) are untouched by the
    ordering defect; every one of Gen102's v3 cases ran the wrong order.
    """
    changed = {}
    for name, module in (("v1", ITF), ("v2", V2), ("v3", V3)):
        fixture = module.build_fixture()
        changed[name] = sum(
            1 for case in fixture.cases
            if list(module.visible_ids(fixture, case))
            != [o.id for o in fixture.observations
                if o.id in set(module.visible_ids(fixture, case))])
    assert changed == {"v1": 0, "v2": 0, "v3": 16}


def test_v3_writes_superseded_before_current():
    """The whole point of the v3 repair, now actually reaching the write."""
    fixture = V3.build_fixture()
    for case in fixture.cases:
        by_id = {o.id: o for o in fixture.observations}
        roles = [by_id[i].role for i in V3.visible_ids(fixture, case)]
        assert roles.index("superseded") < roles.index("current"), case.id


def test_observations_for_preserves_resolver_order():
    """The runner must consume the resolver's sequence, not the fixture's."""
    source = (ROOT / "scripts" / "run_gen97_interference.py").read_text()
    func = next(n for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.FunctionDef) and n.name == "observations_for")
    # An AST walk, not a substring check: the docstring that DESCRIBES the
    # defect contains the word, which is the Gen100 mistake exactly.
    calls = [n.func.id for n in ast.walk(func)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "set" not in calls, \
        "taking a set of the resolver's output discards its order"
    returned = next(n for n in ast.walk(func) if isinstance(n, ast.Return))
    names = {n.id for n in ast.walk(returned) if isinstance(n, ast.Name)}
    assert "VISIBLE_IDS" in names, "the return must be driven by the resolver"


# --- invariant 1: ingest order ---------------------------------------------
def test_ingest_order_invariant_accepts_the_right_order():
    ITF.assert_ingest_order_preserved(["A", "B", "C"], ["A", "B", "C"])


def test_ingest_order_invariant_rejects_the_gen102_defect():
    with pytest.raises(ValueError, match="ingest order was not preserved"):
        ITF.assert_ingest_order_preserved(["SUP", "CUR"], ["CUR", "SUP"])


# --- invariant 2: hits map to a live identity -------------------------------
def test_hits_invariant_accepts_a_live_mapped_hit():
    ITF.assert_hits_map_to_live_identity(["m1"], ["m1"], {"m1": "C2-CUR"})


def test_hits_invariant_rejects_an_unmapped_hit():
    with pytest.raises(ValueError, match="no stored identity"):
        ITF.assert_hits_map_to_live_identity(["m9"], ["m1"], {"m1": "C2-CUR"})


def test_hits_invariant_rejects_a_retired_hit():
    """Search and the store disagreeing is not a result about the engine."""
    with pytest.raises(ValueError, match="not live in the store"):
        ITF.assert_hits_map_to_live_identity(
            ["m1"], ["m2"], {"m1": "C2-SUP", "m2": "C2-CUR"})


# --- the corrected measurement ----------------------------------------------
def _rows():
    path = (ROOT / "results" / "supersession_ablation_gen102"
            / "agentmemory-on.json")
    if not path.exists():
        pytest.skip("engine results are produced on the Mac")
    return json.loads(path.read_text())


def test_corrected_arm_never_loses_the_current_record():
    """Gen102 reported the current record absent in kestrel at every load.

    On the corrected order it is present in all 48 cells. That claim was the
    harness's ordering defect and is retracted.
    """
    data = _rows()
    assert data["fixture_version"] == "interference-v3"
    assert all(r["current_retrievable"] for r in data["rows"])


def test_corrected_arm_removes_stale_only_where_the_threshold_fires():
    """agentmemory's automatic supersession is real, and fires in one core.

    Kestrel is the core whose wording clears the 0.7 Jaccard threshold, so the
    stale record is retired there and nowhere else. Not a ranking property.
    """
    data = _rows()
    stale = {}
    for row in data["rows"]:
        stale.setdefault(row["core"], []).append(
            "stale_version_interference" in (row["mechanisms"] or []))
    assert not any(stale["oncall:kestrel"])
    for core, flags in stale.items():
        if core != "oncall:kestrel":
            assert all(flags), core


# --- Gen105: the same defect existed at four sites ---------------------------
def test_no_script_rederives_ingest_order_from_a_set():
    """Four sites had each written `set(visible_ids(...))` plus a fixture loop.

    Harmless while resolver order matched construction order; silently wrong
    the moment v3 reordered ingestion on purpose. One shared helper now, and
    this asserts nobody re-derives it.
    """
    offenders = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == "set"):
                continue
            inner = node.args[0] if node.args else None
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "visible_ids"):
                offenders.append(path.name)
    assert offenders == [], f"ingest order re-derived from a set in {offenders}"


def test_shared_helper_returns_the_resolver_order():
    fixture = V3.build_fixture()
    for case in fixture.cases:
        got = [o.id for o in ITF.ordered_observations(
            fixture, case, V3.visible_ids)]
        assert got == list(V3.visible_ids(fixture, case)), case.id
