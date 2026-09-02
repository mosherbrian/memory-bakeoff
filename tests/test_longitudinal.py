from memory_bakeoff.longitudinal import *

def c(f,id): return next(x for x in f.cases if x.id==id)

def test_bitemporal_before_after_and_belief_are_distinct():
    f=build_longitudinal_fixture()
    assert oracle_expected_ids(f,c(f,"LQ04")) == ("L001",)
    assert oracle_expected_ids(f,c(f,"LQ05")) == ("L005",)
    assert oracle_expected_ids(f,c(f,"LQ06")) == ("L001",)
    assert oracle_expected_ids(f,c(f,"LQ07")) == ("L005",)
    assert "belief_truth_confusion" in score_longitudinal_case(f,c(f,"LQ06"),("L005",)).failure_classes

def test_scope_config_late_and_procedure_diagnostics():
    f=build_longitudinal_fixture()
    assert "scope_collapse" in score_longitudinal_case(f,c(f,"LQ08"),("L006",)).failure_classes
    assert "configuration_collapse" in score_longitudinal_case(f,c(f,"LQ03"),("L003",)).failure_classes
    assert "late_history_corruption" in score_longitudinal_case(f,c(f,"LQ12"),("L011",)).failure_classes
    assert "procedure_recommendation_missing" in score_longitudinal_case(f,c(f,"LQ10"),()).failure_classes
    assert "failed_procedure_adoption" in score_longitudinal_case(f,c(f,"LQ10"),("L007",)).failure_classes
    assert not score_longitudinal_case(f,c(f,"LQ10"),("L008",)).failure_classes

def test_provenance_negative_and_lifecycle_are_separate():
    f=build_longitudinal_fixture()
    future=score_longitudinal_case(f,c(f,"LQ17"),("L005",))
    assert "future_leakage" in future.failure_classes
    unmapped=score_longitudinal_case(f,c(f,"LQ17"),("outside",))
    assert "unmapped_provenance" in unmapped.failure_classes and "future_leakage" not in unmapped.failure_classes
    assert "unsupported_evidence" in score_longitudinal_case(f,c(f,"LQ16"),("L001",)).failure_classes
    assert score_answer_claim(c(f,"LQ16"),assertion_supported=False)==("unknown_hallucination",)
    state=score_lifecycle_state(f,"CP06",(LifecycleEvidence("L003",False,True),))
    assert "false_supersession" in state.failure_classes

def test_all_taxonomy_reachable_and_invariants_hold():
    f=build_longitudinal_fixture(); ids={o.id:o for o in f.observations}
    assert {x.target_kind for x in f.cases}==set(TargetKind)
    for q in f.cases:
      assert not set(q.expected_ids)&set(q.prohibited_ids)
      assert oracle_expected_ids(f,q)==q.expected_ids
      assert all(ids[x].scope==q.scope and ids[x].configuration==q.configuration for x in q.expected_ids)
      assert all(ids[x].ingestion_order<=f.checkpoint(q.checkpoint_id).ingestion_order for x in q.expected_ids+q.prohibited_ids)
    for o in f.observations:
      assert sum(x is not None for x in (o.corrects_id,o.supersedes_id,o.retracts_id,o.invalidates_id))<=1
      if o.corrects_id: assert o.transition is Transition.CORRECTION
      if o.supersedes_id: assert o.transition is Transition.SUPERSEDE_CURRENT
      if o.retracts_id: assert o.transition is Transition.RETRACTION
      if o.invalidates_id: assert o.transition is Transition.INVALIDATION
    m=ruler_manifest(f)
    assert m["fixture_version"]=="longitudinal-v1" and len(m["fixture_sha256"])==64 and len(m["scorer_contract_sha256"])==64
    assert fixture_sha256(f)==fixture_sha256(build_longitudinal_fixture())

def test_every_declared_failure_has_a_synthetic_adversary():
    f=build_longitudinal_fixture()
    scores=(
      score_longitudinal_case(f,c(f,"LQ17"),("L005",)), score_longitudinal_case(f,c(f,"LQ11"),("L009",)), score_longitudinal_case(f,c(f,"LQ07"),("L001",)), score_longitudinal_case(f,c(f,"LQ06"),()), score_longitudinal_case(f,c(f,"LQ08"),("L006",)), score_longitudinal_case(f,c(f,"LQ03"),("L003",)), score_lifecycle_state(f,"CP06",(LifecycleEvidence("L003",False,True),)), score_longitudinal_case(f,c(f,"LQ06"),("L005",)), score_longitudinal_case(f,c(f,"LQ10"),("L007",)), score_longitudinal_case(f,c(f,"LQ10"),()), score_longitudinal_case(f,c(f,"LQ12"),("L011",)), score_longitudinal_case(f,c(f,"LQ16"),("L001",)), score_longitudinal_case(f,c(f,"LQ16"),("outside",)), score_longitudinal_case(f,c(f,"LQ01"),()),
    )
    seen={name for name,count in aggregate_failure_classes(scores).items() if count}
    seen.add("unknown_hallucination")
    assert seen=={str(x) for x in FailureClass}

def test_naive_policy_adversaries_are_test_infrastructure_only():
    f=build_longitudinal_fixture()
    # latest-ingested ignores world validity: L011 incorrectly replaces current L010.
    latest=max((o for o in f.prefix("CP11") if o.truth_key=="branch:aurora"),key=lambda o:o.ingestion_order)
    assert "late_history_corruption" in score_longitudinal_case(f,c(f,"LQ12"),(latest.id,)).failure_classes
    # current-only lifecycle drops an earlier belief after its correction.
    current_only=(LifecycleEvidence("L001",active_current=False,historically_recoverable=False),)
    assert "history_erasure" in score_lifecycle_state(f,"CP05",current_only).failure_classes
