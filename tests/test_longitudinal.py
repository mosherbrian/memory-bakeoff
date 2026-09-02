from memory_bakeoff.longitudinal import (
    TargetKind,
    build_longitudinal_fixture,
    oracle_expected_ids,
    score_longitudinal_case,
    aggregate_failure_classes,
)


def case(fixture, ident):
    return next(c for c in fixture.cases if c.id == ident)


def test_fixture_keeps_configuration_scopes_and_corrected_truth_distinct():
    fixture = build_longitudinal_fixture()
    assert oracle_expected_ids(fixture, case(fixture, "LQ01")) == ("L001",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ02")) == ("L002",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ03")) == ("L001",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ04")) == ("L001",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ05")) == ("L003",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ06")) == ("L002",)


def test_checkpoint_prefix_prevents_future_leakage_and_late_history_corruption():
    fixture = build_longitudinal_fixture()
    cp2 = fixture.prefix("CP2")
    assert {o.id for o in cp2} == {"L001", "L002"}
    assert oracle_expected_ids(fixture, case(fixture, "LQ08")) == ("L008",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ09")) == ("L009",)
    score = score_longitudinal_case(fixture, case(fixture, "LQ01"), ("L003",))
    assert "future_leakage" in score.failure_classes
    current = score_longitudinal_case(fixture, case(fixture, "LQ08"), ("L009",))
    assert "future_leakage" in current.failure_classes


def test_oracle_handles_procedure_and_unknown_and_scores_named_failures():
    fixture = build_longitudinal_fixture()
    assert oracle_expected_ids(fixture, case(fixture, "LQ07")) == ("L006",)
    assert oracle_expected_ids(fixture, case(fixture, "LQ10")) == ()
    scope = score_longitudinal_case(fixture, case(fixture, "LQ06"), ("L004",))
    assert "scope_collapse" in scope.failure_classes
    procedure = score_longitudinal_case(fixture, case(fixture, "LQ07"), ("L005",))
    assert "failed_procedure_adoption" in procedure.failure_classes
    unknown = score_longitudinal_case(fixture, case(fixture, "LQ10"), ("L001",))
    assert "unknown_hallucination" in unknown.failure_classes
    corrected = score_longitudinal_case(fixture, case(fixture, "LQ05"), ("L001",))
    assert {"correction_failure", "false_persistence"}.issubset(corrected.failure_classes)
    counts = aggregate_failure_classes((scope, procedure, unknown, corrected))
    assert counts["scope_collapse"] == 1
    assert counts["false_persistence"] == 1
