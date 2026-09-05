"""Gen100: was any engine ever told that one record supersedes another?"""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference_v2 as v2
from memory_bakeoff import supersession_surface as ss

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "supersession_gen100" / "audit.json"


@pytest.fixture(scope="module")
def audit():
    return json.loads(AUDIT.read_text())


def test_no_engine_lacks_a_supersession_surface(audit):
    assert audit["verdict"]["no_engine_lacks_a_surface"] is True
    assert ss.NO_SURFACE not in audit["verdict"]["statuses"].values()


def test_three_surfaces_exist_and_were_not_called(audit):
    statuses = audit["verdict"]["statuses"]
    unused = sorted(e for e, s in statuses.items() if s == ss.PRESENT_BUT_UNUSED)
    assert unused == ["hindsight", "mem0", "perseus"]
    for engine in unused:
        assert "frozen" in ss.SURFACES[engine]["evidence"]


def test_only_perseus_names_an_explicit_lineage():
    explicit = [e for e, s in ss.SURFACES.items() if s["explicit_lineage"]]
    assert explicit == ["perseus"]
    assert "supersedes" in ss.SURFACES["perseus"]["description"]
    assert "to_key" in ss.SURFACES["perseus"]["parameters"]


def test_agentmemory_already_exercises_its_own(audit):
    assert audit["verdict"]["statuses"]["agentmemory"] == ss.ALREADY_EXERCISED
    assert ss.SURFACES["agentmemory"]["rule"]["threshold"] == 0.7
    assert "harness never selects" in ss.SURFACES["agentmemory"]["evidence"]


def test_supersession_is_never_manufactured_by_deletion(audit):
    """No engine client is imported, so nothing can be deleted or retired here.

    A substring ban on 'delete' would flag the audit's own DESCRIPTIONS of the
    surfaces it catalogues - the same over-broad shape as the Gen99 pooling
    guard. The invariant is that nothing is CALLED, and an AST walk states it.
    """
    import ast
    assert "never simulated by deleting" in audit["verdict"]["never_manufacture"]
    clients = {"mem0", "hindsight_client", "requests", "subprocess", "httpx"}
    for path in (ROOT / "src" / "memory_bakeoff" / "supersession_surface.py",
                 ROOT / "scripts" / "run_gen100_supersession_audit.py"):
        tree = ast.parse(path.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert not (imported & clients), (path.name, sorted(imported & clients))


# --- the rule, reimplemented and applied ---------------------------------
def test_the_jaccard_rule_matches_the_frozen_definition():
    assert ss.jaccard("a bb ccc ddd", "a bb ccc ddd") == 1.0
    # tokens of two characters or fewer are ignored
    assert ss.jaccard("aa bbb", "xx bbb") == 1.0
    assert ss.jaccard("alpha beta", "gamma delta") == 0.0


def test_the_rule_can_fire_in_exactly_one_core(audit):
    fired = audit["cores_where_the_rule_can_fire"]
    assert fired == ["oncall:kestrel"]
    per_core = audit["agentmemory_rule_per_core"]
    assert per_core["oncall:kestrel"]["jaccard"] > 0.7
    for core in ("throughput:atlas", "branch:vega", "budget:solstice"):
        assert per_core[core]["jaccard"] < 0.7, core


def test_the_rule_explains_the_gen99_kestrel_absence(audit):
    entry = audit["agentmemory_rule_per_core"]["oncall:kestrel"]
    assert entry["rule_can_fire"] is True
    assert entry["current_written_first"] is True
    assert entry["explains_absence"] is True
    assert audit["gen99_kestrel_explained"] is True
    assert entry["harness_or_product"].startswith("BOTH")


def test_the_ingest_order_is_named_as_a_harness_choice(audit):
    entry = audit["agentmemory_rule_per_core"]["oncall:kestrel"]
    assert "the harness chose" in entry["why"]
    assert "backwards from the world it models" in entry["harness_or_product"]


def test_the_verdict_withholds_the_defect_reading_for_three_engines(audit):
    reading = audit["verdict"]["reading"]
    assert "NOT yet a ranking defect" in reading
    assert "never asked" in reading
    assert "real product observation" in audit["verdict"]["agentmemory_exception"]


def test_no_engine_runs(audit):
    assert audit["verdict"]["no_engine_runs"] is True
