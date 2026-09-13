"""Portfolio P2 composition receipt: locked baseline arms (charter Patch 3).

Locks the composition the P2 run matrix must see: the composition
declaration matches the live registry and classes, both pi-lcm arms run
end-to-end through the shared harness (``runner.run_provider``), the
history null is a true unranked passthrough over the SAME store the
reader arm queries, and the engine-shape null seam is intact.
"""

import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.portfolio import (  # noqa: E402
    ENGINE_ARMS,
    LOCKED_BASELINE_ARMS,
    validate_composition,
)
from memory_bakeoff.providers import PROVIDERS  # noqa: E402
from memory_bakeoff.providers.pi_lcm_store_reader import (  # noqa: E402
    PiLcmHistoryNullProvider,
    PiLcmStoreReaderProvider,
)
from memory_bakeoff.runner import run_provider  # noqa: E402

T0 = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)


def _records():
    return [
        MemoryRecord(id="obs-1", text="staging deploys via helm on the kite cluster",
                     timestamp=T0 + timedelta(hours=1), session_id="sess-a"),
        MemoryRecord(id="obs-2", text="development still uses docker compose",
                     timestamp=T0 + timedelta(hours=2), session_id="sess-b"),
        MemoryRecord(id="obs-3", text="the ledger convention lives in trial-ledger.py",
                     timestamp=T0 + timedelta(hours=3), session_id="sess-c"),
    ]


def _case(query: str) -> QueryCase:
    return QueryCase(id="q", category="c", query=query, relevant_ids=())


def test_composition_declaration_matches_the_live_registry():
    state = validate_composition()  # raises on any drift
    assert state["locked_baseline_arms"] == list(LOCKED_BASELINE_ARMS)
    assert state["engine_arms"]["longcontext_null"] == "longcontext-null-v1"
    for name in state["provider_arms"]:
        assert name in PROVIDERS


def test_store_reader_runs_end_to_end_through_the_shared_harness():
    row = run_provider("pi_lcm_store_reader")
    assert row["status"] == "ok", row["reason"]
    assert row["experiment_class"] == "controlled_core"
    assert row["publishability"]["publishable"] is True
    assert "hit@5" in row["summary"]
    assert row["provider_diagnostics"]["canonical_map_size"] > 0


def test_history_null_runs_end_to_end_through_the_shared_harness():
    row = run_provider("pi_lcm_history_null")
    assert row["status"] == "ok", row["reason"]
    assert row["experiment_class"] == "baseline"
    assert row["publishability"]["publishable"] is True
    inventory = row["provider_diagnostics"]["null_inventory"]
    assert inventory["retrieval_performed"] is False
    assert inventory["approx_tokens_offered"] > 0


def test_history_null_never_consults_the_question():
    p = PiLcmHistoryNullProvider()
    p.ingest(_records())
    a = p.retrieve(_case("ledger convention trial-ledger"))
    b = p.retrieve(_case("completely unrelated kite staging wording"))
    assert [i.record_id for i in a.items] == [i.record_id for i in b.items]
    assert [(i.text, i.metadata["rank"]) for i in a.items] == [(i.text, i.metadata["rank"]) for i in b.items]
    assert all(i.score is None for i in a.items)
    assert a.raw["question_consulted"] is False
    p.close()


def test_history_null_returns_the_full_history_in_chronological_order():
    p = PiLcmHistoryNullProvider()
    p.ingest([
        MemoryRecord(id=f"r{n}", text=f"note {n} word", timestamp=T0 + timedelta(hours=n),
                     session_id=f"s{n}")
        for n in range(1, 6)
    ])
    res = p.retrieve(_case("anything"), top_k=2)
    # The full history IS the arm: no top_k truncation here - the scorer
    # takes the first k of the passthrough (runner score_case does ids[:k]).
    assert [i.record_id for i in res.items] == ["r1", "r2", "r3", "r4", "r5"]
    assert [i.metadata["rank"] for i in res.items] == [1, 2, 3, 4, 5]
    inv = res.raw
    assert inv["observations_offered"] == 5
    assert inv["approx_tokens_offered"] == 15  # 3 words per record
    p.close()


def test_both_pi_lcm_arms_materialize_the_same_store():
    reader = PiLcmStoreReaderProvider()
    null = PiLcmHistoryNullProvider()
    reader.ingest(_records())
    null.ingest(_records())

    def shape(path: Path) -> tuple[set[str], int, int]:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        messages = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        conversations = con.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        con.close()
        return tables, messages, conversations

    reader_shape = shape(Path(reader.configuration()["store_path"]) if reader.configuration()["store_path"] else Path(reader.diagnostics()["store_path"]))
    # the reader keeps its store path in diagnostics while attached
    null_shape = shape(Path(null.diagnostics()["store_path"]))
    assert reader_shape[1] == null_shape[1] == 3  # same message count
    assert reader_shape[2] == null_shape[2] == 3  # same conversation count (per session)
    # FTS is reader-only machinery: the null builds no index it never queries
    assert "messages_fts" not in null_shape[0]
    reader.close()
    null.close()
