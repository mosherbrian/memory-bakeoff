"""SMOKE ONLY — portfolio locked pi-lcm arms against the REAL MemConflict dataset.

The P2 composition (`memory_bakeoff.portfolio`) was locked on the synthetic
stream; this suite locks the bridge to the real thing now that the dataset
is materialized and triple-pin-verified (receipt:
docs/PORTFOLIO-P1-discovery/MEMCONFLICT-MATERIALIZATION.md). It proves the
store-reader and history-null arms ingest the real corpus shape end-to-end
and answer real released question text through the shared provider
interface.

NOT a benchmark claim: no gold is loaded (Gold is scorer-only), nothing is
scored, no Hit@k is asserted. Descriptive composition receipt.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff.memconflict import (  # noqa: E402
    ingestion_units,
    load_personas,
    questions,
)
from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers.pi_lcm_store_reader import (  # noqa: E402
    PiLcmHistoryNullProvider,
    PiLcmStoreReaderProvider,
)


def _records_for(persona: dict) -> list[MemoryRecord]:
    units = ingestion_units(persona)
    records = []
    for u in units:
        stamp = datetime.fromisoformat(u.date).replace(tzinfo=timezone.utc)
        records.append(
            MemoryRecord(
                id=u.provenance_id,
                text=u.text,
                timestamp=stamp,
                session_id=f"{u.persona_id}|S{u.session_id}",
                scope=u.persona_id,
                metadata={"role": u.role},
            )
        )
    return records


@pytest.fixture(scope="module")
def persona():
    return load_personas()[0]


def test_arms_ingest_and_answer_real_persona_data(persona):
    records = _records_for(persona)
    assert records, "persona yielded no ingestible units"
    known_ids = {r.id for r in records}

    reader = PiLcmStoreReaderProvider()
    reader.ingest(records)
    qs = questions(persona)
    assert qs, "persona yielded no questions"
    for q in (qs[0], qs[len(qs) // 2], qs[-1]):  # first, middle, last
        result = reader.retrieve(QueryCase(id=q.key, category="real", query=q.text, relevant_ids=()))
        assert result.latency_ms >= 0.0
        assert all(i.score is None for i in result.items)  # reader never imputes scores
        for item in result.items:  # every hit maps to a real ingested unit
            assert item.record_id in known_ids
    reader.close()


def test_history_null_serves_the_full_real_history(persona):
    records = _records_for(persona)
    null = PiLcmHistoryNullProvider()
    null.ingest(records)
    qs = questions(persona)
    a = null.retrieve(QueryCase(id="q1", category="real", query=qs[0].text, relevant_ids=()))
    b = null.retrieve(QueryCase(id="q2", category="real", query=qs[-1].text, relevant_ids=()))
    # unranked passthrough: the full history, identical for any question
    assert len(a.items) == len(b.items) == len(records)
    assert [i.record_id for i in a.items] == [i.record_id for i in b.items]
    assert [i.metadata["rank"] for i in a.items] == list(range(1, len(records) + 1))
    assert null.diagnostics()["null_inventory"]["retrieval_performed"] is False
    null.close()


def test_both_arms_hold_the_same_real_store(persona):
    records = _records_for(persona)
    reader, null = PiLcmStoreReaderProvider(), PiLcmHistoryNullProvider()
    reader.ingest(records)
    null.ingest(records)
    assert reader.diagnostics()["canonical_map_size"] == len(records)
    assert null.diagnostics()["null_inventory"]["observations_held"] == len(records)
    reader.close()
    null.close()
