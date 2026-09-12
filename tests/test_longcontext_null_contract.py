"""P1 per-adapter unit receipt: LongContextNull engine-contract conformance.

The portfolio charter (row 18 / DECISION_MEMO row 4) requires the
BUILT-never-run long-context null to enter the run as an engine arm. This
test locks the contract the harness relies on: unranked ingestion-order
passthrough, no imputed scores, snapshot no-ops, inventory honesty, and the
token-cost accounting that makes the null comparable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff.longcontext_null import ARM_VERSION, LongContextNull  # noqa: E402


def _obs():
    return [
        {"id": "obs-1", "text": "staging deploys via helm on the kite cluster"},
        {"id": "obs-2", "text": "development still uses docker compose"},
        {"id": "obs-3", "text": "the ledger convention lives in trial-ledger.py"},
    ]


def test_search_returns_every_observation_in_ingestion_order():
    arm = LongContextNull(_obs())
    items, latency = arm.search("how do we deploy to production?")
    assert [i["native_id"] for i in items] == ["obs-1", "obs-2", "obs-3"]
    assert [i["rank"] for i in items] == [1, 2, 3]
    assert latency >= 0.0


def test_the_question_is_never_consulted():
    arm = LongContextNull(_obs())
    a, _ = arm.search("deployments")
    b, _ = arm.search("completely unrelated ledger plumbing")
    assert a == b  # unranked passthrough: identical output for any question


def test_no_score_is_ever_imputed():
    arm = LongContextNull(_obs())
    items, _ = arm.search("anything")
    assert all(i["score"] is None for i in items)


def test_limit_models_a_context_ceiling_once_not_per_question():
    arm = LongContextNull(_obs(), limit=2)
    items, _ = arm.search("earliest observations please")
    assert [i["native_id"] for i in items] == ["obs-2", "obs-3"]  # trailing window
    assert arm.inventory()["observations_offered"] == 2


def test_snapshot_noops_present_for_harness_parity():
    arm = LongContextNull(_obs())
    assert arm.open_read_snapshot() is None
    assert arm.close_read_snapshot() is None


def test_inventory_declares_the_arm_is_not_a_memory_system():
    inv = LongContextNull(_obs()).inventory()
    assert inv["arm"] == ARM_VERSION == "longcontext-null-v1"
    assert inv["retrieval_performed"] is False
    for flag in ("supersession_expressible", "scope_expressible", "provenance_expressible"):
        assert inv[flag] is False
    assert inv["approx_tokens_offered"] == sum(
        len(str(o["text"]).split()) for o in _obs())


def test_token_accounting_scales_with_history():
    big = LongContextNull([{"id": str(n), "text": "word " * 10} for n in range(40)])
    assert big.tokens_offered == 400
    assert big.inventory()["observations_held"] == 40
