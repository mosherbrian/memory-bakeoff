"""Regression tests for the four pre-exposure findings (Alice, 2026-09-13)."""
from memory_bakeoff.longcontext_null import LongContextNull
from memory_bakeoff.stale_use_penalty import StaleDisposition, aggregate, score_stale_use


def test_null_limit_zero_offers_nothing():
    arm = LongContextNull([{"id": "a", "text": "x"}], limit=0)
    items, _ = arm.search("q")
    assert items == []
    assert arm.inventory()["observations_offered"] == 0
    assert arm.inventory()["approx_tokens_offered"] == 0


def test_null_token_accounting_respects_limit():
    obs = [{"id": str(i), "text": "w " * 10} for i in range(5)]
    arm = LongContextNull(obs, limit=2)
    assert arm.inventory()["observations_offered"] == 2
    assert arm.inventory()["approx_tokens_offered"] == 20


def test_neither_with_stale_present_is_not_tolerated():
    r = score_stale_use(answer_id="rec-other", current_id="rec-cur",
                        stale_ids={"rec-stale"}, returned_ids={"rec-cur", "rec-stale"})
    assert r.disposition is StaleDisposition.NEITHER
    assert r.tolerated is False


def test_stale_use_rate_excludes_without_retrieval():
    a = aggregate([score_stale_use(answer_id="rec-stale", current_id="rec-cur",
                                   stale_ids={"rec-stale"}, returned_ids={"rec-cur"})])
    assert a["stale_use_rate"] == 0.0
    assert a["stale_use_without_retrieval_rate"] == 1.0
