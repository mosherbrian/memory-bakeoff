"""The null arm must be a null, and must be unable to pretend otherwise."""
from memory_bakeoff.longcontext_null import ARM_VERSION, LongContextNull

OBS = [{"id": f"o{i}", "text": f"observation number {i} about a budget"} for i in range(1, 6)]


def test_it_returns_everything_in_ingestion_order():
    arm = LongContextNull(OBS)
    items, _ = arm.search("what is the budget?")
    assert [i["native_id"] for i in items] == ["o1", "o2", "o3", "o4", "o5"]


def test_the_question_does_not_change_the_answer():
    """If asking a different question changed the output, this would be a
    retrieval system with a bad ranker - the one thing it must not become."""
    arm = LongContextNull(OBS)
    a, _ = arm.search("what is the budget?")
    b, _ = arm.search("who is on call?")
    assert a == b


def test_it_never_imputes_a_relevance_score():
    """A None score is the honest value. A 1.0 would let a downstream scorer
    treat unranked output as confidently ranked."""
    items, _ = LongContextNull(OBS).search("anything")
    assert all(i["score"] is None for i in items)


def test_a_limit_takes_the_MOST_RECENT_window_not_the_first():
    """A real context ceiling drops the oldest turns. Dropping the newest would
    invert the recency the whole experiment is about."""
    items, _ = LongContextNull(OBS, limit=2).search("anything")
    assert [i["native_id"] for i in items] == ["o4", "o5"]


def test_inventory_declares_what_it_cannot_express():
    inv = LongContextNull(OBS).inventory()
    assert inv["arm"] == ARM_VERSION
    assert inv["retrieval_performed"] is False
    for prop in ("supersession_expressible", "scope_expressible", "provenance_expressible"):
        assert inv[prop] is False, f"{prop} must be declared false; this arm cannot express it"


def test_it_reports_the_context_it_spends():
    """An arm that wins on accuracy while spending 40x the context has not won
    for free, and the cost must be in the record."""
    inv = LongContextNull(OBS).inventory()
    assert inv["approx_tokens_offered"] > 0
    assert inv["observations_offered"] == 5
    assert LongContextNull(OBS, limit=2).inventory()["observations_offered"] == 2


def test_empty_history_is_not_a_crash():
    items, _ = LongContextNull([]).search("anything")
    assert items == []
