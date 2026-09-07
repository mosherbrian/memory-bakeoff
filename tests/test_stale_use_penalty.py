"""Presence and use must not collapse into each other."""
from memory_bakeoff.stale_use_penalty import (StaleDisposition, aggregate, score_stale_use)

CUR, STALE = "rec-current", frozenset({"rec-stale"})


def s(answer, returned):
    return score_stale_use(answer_id=answer, current_id=CUR, stale_ids=STALE, returned_ids=returned)


def test_stale_present_but_current_answered_is_tolerated_not_penalised():
    """Round 3: every engine returns the stale record. If that alone were the
    failure, all four engines would score identically, which is what happened."""
    r = s(CUR, {"rec-current", "rec-stale"})
    assert r.disposition is StaleDisposition.CURRENT_ANSWERED
    assert r.stale_present_in_context and not r.penalised and r.tolerated


def test_answering_with_the_stale_value_is_the_penalised_case():
    r = s("rec-stale", {"rec-current", "rec-stale"})
    assert r.disposition is StaleDisposition.STALE_USED and r.penalised


def test_stale_used_without_ever_being_retrieved_is_a_different_finding():
    """Sends the investigation to the right layer: if it was never retrieved,
    this is provenance or parametric leakage, not supersession."""
    r = s("rec-stale", {"rec-current"})
    assert r.disposition is StaleDisposition.STALE_USED_WITHOUT_RETRIEVAL
    assert r.penalised and not r.stale_present_in_context


def test_declining_to_answer_is_not_penalised():
    """Refusing is a different behaviour from answering wrongly. Collapsing them
    rewards confident error."""
    r = s(None, {"rec-current", "rec-stale"})
    assert r.disposition is StaleDisposition.NEITHER and not r.penalised


def test_an_unrelated_answer_is_not_scored_as_stale_use():
    assert s("rec-other", {"rec-stale"}).disposition is StaleDisposition.NEITHER


def test_presence_and_use_rates_are_reported_separately():
    """The whole point. An engine at presence 1.0 and use 0.0 is doing its job;
    one number cannot say that."""
    a = aggregate([s(CUR, {"rec-current", "rec-stale"}) for _ in range(4)])
    assert a["stale_presence_rate"] == 1.0
    assert a["stale_use_rate"] == 0.0
    assert a["tolerated"] == 4


def test_the_metric_can_actually_fire():
    a = aggregate([s("rec-stale", {"rec-current", "rec-stale"}),
                   s(CUR, {"rec-current", "rec-stale"})])
    assert a["stale_use_rate"] == 0.5 and a["stale_used"] == 1


def test_empty_is_not_a_zero_rate():
    """No cases means no rate. A 0.0 would read as a perfect score."""
    assert aggregate([]) == {"n": 0}
