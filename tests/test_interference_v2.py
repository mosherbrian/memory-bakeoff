"""Gen98: the replication fixture, and the questions declared before it ran."""
from __future__ import annotations

import json
import pathlib

import pytest

from memory_bakeoff import interference as itf
from memory_bakeoff import interference_v2 as v2

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = ROOT / "results" / "interference_v2_gen98" / "fixture.json"


@pytest.fixture(scope="module")
def fixture():
    return v2.build_fixture()


@pytest.fixture(scope="module")
def frozen():
    return json.loads(FROZEN.read_text())


# --- several independent cores, identical structure ----------------------
def test_there_are_several_independent_cores(fixture):
    cores = {c.core for c in fixture.cases}
    assert len(cores) == len(v2.CORES) >= 3
    assert len({c["subject"] for c in v2.CORES}) == len(v2.CORES)


def test_every_core_carries_the_same_structure(fixture):
    for core in v2.CORES:
        cases = v2.cases_for_core(fixture, core["id"])
        assert sorted(c.load for c in cases) == list(itf.LOAD_LEVELS)
        for case in cases:
            assert len(case.expected) == 1
            assert len(case.prohibited_stale) == 1
            assert len(case.prohibited_foreign) == 1
            assert case.scope == core["scope"]
            assert case.configuration == core["configuration"]


def test_each_core_has_its_own_scope_and_configuration(fixture):
    scopes = {c["scope"] for c in v2.CORES}
    configurations = {c["configuration"] for c in v2.CORES}
    assert len(scopes) == len(v2.CORES)
    assert len(configurations) == len(v2.CORES)


def test_the_foreign_record_differs_on_both_axes_in_every_core(fixture):
    by_id = fixture.by_id()
    for case in fixture.cases:
        foreign = by_id[case.prohibited_foreign[0]]
        assert foreign.scope != case.scope
        assert foreign.configuration != case.configuration


def test_only_subject_and_wording_vary_between_cores(fixture):
    """Load levels and structure are identical; the vocabulary is the variable."""
    sizes = {}
    for case in fixture.cases:
        sizes.setdefault(case.load, set()).add(len(v2.visible_ids(fixture, case)))
    for load, seen in sizes.items():
        assert seen == {load + 3}, load


def test_a_case_never_sees_another_cores_records(fixture):
    """The v1 helper would have ingested other neighbourhoods; v2 must not."""
    by_id = fixture.by_id()
    for case in fixture.cases:
        for record_id in v2.visible_ids(fixture, case):
            assert by_id[record_id].core == case.core, (case.id, record_id)


def test_records_are_namespaced_so_cores_cannot_bleed(fixture):
    by_core = {}
    for observation in fixture.observations:
        by_core.setdefault(observation.core, set()).add(observation.id)
    ids = [i for group in by_core.values() for i in group]
    assert len(ids) == len(set(ids)), "ids must be unique across cores"
    for core, group in by_core.items():
        prefixes = {i.split("-")[0] for i in group}
        assert len(prefixes) == 1, core


# --- every mechanism still fires, in every core --------------------------
def test_all_mechanisms_fire_in_every_core(frozen):
    assert frozen["reachability"]["all_mechanisms_fire_in_every_core"] is True
    for core, controls in frozen["controls_per_core"].items():
        assert controls["clean"] == [], core
        assert itf.TRUE_FORGETTING in controls[itf.TRUE_FORGETTING], core
        assert itf.DISTRACTOR_DISPLACEMENT in controls[itf.DISTRACTOR_DISPLACEMENT], core
        assert itf.STALE_VERSION_INTERFERENCE in \
            controls[itf.STALE_VERSION_INTERFERENCE], core
        assert itf.CROSS_SCOPE_CONTAMINATION in \
            controls[itf.CROSS_SCOPE_CONTAMINATION], core


# --- the questions are declared, and the verdict rule is strict ----------
def test_the_replication_questions_were_declared_before_any_run(frozen):
    contract = frozen["contract"]
    assert contract["questions_declared_before_any_run"] is True
    assert contract["frozen_before_any_engine_run"] is True
    assert set(contract["replication_questions"]) == {
        "Q1_perseus_rank_declines_with_density",
        "Q2_stale_interference_recurs",
        "Q3_other_engines_hold_their_shape"}
    for entry in contract["replication_questions"].values():
        assert entry["replicated_if"] and entry["fixture_specific_if"]
        assert entry["gen97_observation"]


def test_a_pattern_in_one_core_is_fixture_specific():
    assert v2.replication_verdict({"a": True, "b": False, "c": False,
                                   "d": False}) == v2.FIXTURE_SPECIFIC
    assert v2.replication_verdict({"a": True, "b": True, "c": True,
                                   "d": True}) == v2.GENERAL
    assert v2.replication_verdict({"a": True, "b": True, "c": False,
                                   "d": False}) == v2.PARTIAL
    assert v2.replication_verdict({}) == v2.NOT_APPLICABLE


def test_cores_are_never_pooled():
    v2.assert_no_core_pooling("perseus declines in 3 of 4 cores")
    for bad in ("mean across cores was 0.7", "pooled across cores",
                "all cores combined gives 62%", "the core mean is 3.2"):
        with pytest.raises(ValueError, match="replication factor"):
            v2.assert_no_core_pooling(bad)


def test_the_fixture_and_contract_are_hashed(frozen):
    assert len(frozen["fixture_sha256"]) == 64
    assert frozen["contract_sha256"] == v2.contract_sha256()
    assert len(frozen["observations"]) == 268 and len(frozen["cases"]) == 16


def test_the_fixture_rebuilds_identically(fixture, frozen):
    assert [o.id for o in fixture.observations] == \
        [o["id"] for o in frozen["observations"]]
    assert [c.id for c in fixture.cases] == [c["id"] for c in frozen["cases"]]


def test_the_scorer_is_unchanged():
    assert v2.SCORER_VERSION == itf.SCORER_VERSION
