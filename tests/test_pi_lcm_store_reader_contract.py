"""P1 per-adapter unit receipt: pi-lcm store-reader contract conformance.

The portfolio charter (rows 1-2, LOCKED BASELINE ARM per Patch 3) requires
the pi-lcm store reader to enter the run through the shared provider
interface. This test locks the contract the harness relies on: the ported
reader semantics (recency order, no imputed scores, FTS5 MATCH with the LIKE
fallback), corpus materialization with canonical-ID bookkeeping, strictly
read-only store attach, fail-closed lifecycle, and configuration honesty.
"""

import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from memory_bakeoff.models import MemoryRecord, QueryCase  # noqa: E402
from memory_bakeoff.providers import PROVIDERS  # noqa: E402
from memory_bakeoff.providers.base import ProviderUnavailable  # noqa: E402
from memory_bakeoff.providers.pi_lcm_store_reader import (  # noqa: E402
    PiLcmHistoryNullProvider,
    PiLcmStoreReaderAttachProvider,
    PiLcmStoreReaderProvider,
    sanitize_fts_query,
)

T0 = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)


def _rec(rid: str, text: str, hours: float, session: str = "sess-a") -> MemoryRecord:
    return MemoryRecord(
        id=rid, text=text, timestamp=T0 + timedelta(hours=hours), session_id=session
    )


def _records():
    return [
        _rec("obs-1", "staging deploys via helm on the kite cluster", 1, "sess-a"),
        _rec("obs-2", "development still uses docker compose", 2, "sess-b"),
        _rec("obs-3", "the ledger convention lives in trial-ledger.py", 3, "sess-c"),
    ]


def _case(query: str, **kw) -> QueryCase:
    return QueryCase(id="q", category="c", query=query, relevant_ids=(), **kw)


def test_corpus_mode_maps_hits_to_canonical_ids():
    p = PiLcmStoreReaderProvider()
    p.ingest(_records())
    res = p.retrieve(_case("ledger convention"))
    assert res.items, "expected at least one hit"
    assert res.items[0].record_id == "obs-3"
    assert "ledger" in res.items[0].text
    assert res.items[0].score is None
    assert res.items[0].metadata["session_id"] == "sess-c"
    assert res.items[0].metadata["conversation_id"].startswith("conv-")
    assert p.provenance_report()["status"] == "verified"
    p.close()


def test_reader_orders_by_recency_not_relevance():
    p = PiLcmStoreReaderProvider()
    p.ingest([
        _rec("old", "deploy the widget", 1, "s1"),
        _rec("new", "deploy the gadget", 5, "s2"),
        _rec("mid", "deploy the gizmo", 3, "s3"),
    ])
    res = p.retrieve(_case("deploy"))
    # The ported query orders by m.timestamp DESC, m.seq DESC - recency,
    # not lexical relevance. All three match equally.
    assert [i.record_id for i in res.items] == ["new", "mid", "old"]
    p.close()


def test_no_score_is_ever_imputed():
    p = PiLcmStoreReaderProvider()
    p.ingest(_records())
    res = p.retrieve(_case("deploy helm docker ledger"))
    assert all(i.score is None for i in res.items)
    p.close()


def test_as_of_limits_visibility():
    p = PiLcmStoreReaderProvider()
    p.ingest(_records())  # obs-1 @+1h, obs-2 @+2h, obs-3 @+3h
    future = p.retrieve(_case("docker compose"))
    assert [i.record_id for i in future.items] == ["obs-2"]
    past = p.retrieve(_case("docker compose", as_of=T0 + timedelta(hours=1, minutes=30)))
    assert past.items == []  # obs-2 did not exist yet at the as_of boundary
    p.close()


def test_like_fallback_returns_the_same_hits():
    fts = PiLcmStoreReaderProvider()
    fts.ingest(_records())
    like = PiLcmStoreReaderProvider(allow_fts=False)
    like.ingest(_records())
    # Adjacent terms: both paths agree (LIKE is a literal substring match).
    a, b = fts.retrieve(_case("docker compose")), like.retrieve(_case("docker compose"))
    assert [i.record_id for i in a.items] == [i.record_id for i in b.items] == ["obs-2"]
    # Non-adjacent terms: FTS5 ANDs them, the LIKE fallback is substring-only -
    # exactly pi-lcm's own searchFts5 fallback semantics, ported faithfully.
    assert [i.record_id for i in fts.retrieve(_case("helm kite")).items] == ["obs-1"]
    assert like.retrieve(_case("helm kite")).items == []
    assert a.raw["fts_active"] is True
    assert b.raw["fts_active"] is False
    # LIKE metacharacters must not error the fallback path
    assert like.retrieve(_case("100%_done")).items == []
    fts.close()
    like.close()


def test_attach_mode_is_read_only_and_leaves_the_store_unchanged(tmp_path):
    builder = PiLcmStoreReaderProvider()
    builder.ingest(_records())
    # The corpus store is temporary; copy it out before close() cleans it up.
    store_path = tmp_path / "lcm.db"
    store_path.write_bytes(Path(builder._store_used).read_bytes())
    builder.close()
    digest_before = hashlib.sha256(store_path.read_bytes()).hexdigest()

    att = PiLcmStoreReaderProvider(store_path=store_path)
    assert att.experiment_class("raw") == "raw_product"
    att.ingest(_records())  # intentionally ignored: read-only attach
    res = att.retrieve(_case("docker compose"))
    assert res.items and res.items[0].record_id is None  # real session text: unmappable
    assert "docker" in res.items[0].text
    assert att.diagnostics()["corpus_records_ignored"] == 3
    assert att.provenance_report()["status"] == "exploratory_only"
    assert hashlib.sha256(store_path.read_bytes()).hexdigest() == digest_before
    att.close()


def test_attach_fails_closed_on_missing_or_non_pi_lcm_store(tmp_path):
    missing = PiLcmStoreReaderProvider(store_path=tmp_path / "absent.db")
    with pytest.raises(ProviderUnavailable):
        missing.ingest([])
    empty = PiLcmStoreReaderProvider(store_path=tmp_path / "notstore.db")
    empty.store_path.write_bytes(b"this is not a database")
    with pytest.raises(ProviderUnavailable):
        empty.ingest([])


def test_lifecycle_fails_closed_after_close():
    p = PiLcmStoreReaderProvider()
    with pytest.raises(ProviderUnavailable):
        p.retrieve(_case("deploy"))  # no store yet
    p.ingest(_records())
    assert p.retrieve(_case("deploys")).items
    p.close()
    with pytest.raises(ProviderUnavailable):
        p.retrieve(_case("deploys"))
    p.reset()  # reset after close stays safe
    with pytest.raises(ProviderUnavailable):
        p.retrieve(_case("deploy"))


def test_top_k_is_a_ceiling():
    p = PiLcmStoreReaderProvider()
    p.ingest([_rec(f"r{n}", f"deploy variant {n}", n, f"s{n}") for n in range(1, 6)])
    assert len(p.retrieve(_case("deploy"), top_k=2).items) == 2
    assert len(p.retrieve(_case("deploy"), top_k=50).items) == 5
    p.close()


def test_configuration_declares_reader_lineage_and_honesty():
    corpus_cfg = PiLcmStoreReaderProvider().configuration()
    assert "pi-project-recall" in corpus_cfg["reader_port"]
    assert corpus_cfg["mode"] == "corpus_materialized"
    assert corpus_cfg["relaxation"].startswith("not ported")
    assert corpus_cfg["scores"].startswith("none")
    assert corpus_cfg["fts5"] == "native"  # this host has FTS5 (sqlite 3.50.2)
    attach_cfg = PiLcmStoreReaderProvider(store_path="x.db").configuration()
    assert attach_cfg["mode"] == "attach_existing_store"


def test_sanitize_fts_query_matches_the_extension_verbatim():
    assert sanitize_fts_query('hello "world"  x') == '"hello" """world""" "x"'
    assert sanitize_fts_query("   ") == ""


def test_registry_names_resolve():
    assert PROVIDERS["pi_lcm_store_reader"] is PiLcmStoreReaderProvider
    assert PROVIDERS["pi_lcm_store_reader_attach"] is PiLcmStoreReaderAttachProvider
    # attach construction is lazy: resolving a nonexistent default store must
    # not raise until probe/ingest
    PiLcmStoreReaderAttachProvider()


def test_append_grows_the_store_incrementally():
    """Chronology protocol (memconflict contract): sessions append; each
    question may see sessions 0..i inclusive. The store is the SAME store,
    grown — and appended units are retrievable with canonical mapping."""
    p = PiLcmStoreReaderProvider()
    p.ingest([_rec("obs-1", "staging deploys via helm on the kite cluster", 1, "sess-a")])
    assert p.retrieve(_case("ledger convention")).items == []  # not ingested yet
    p.append([_rec("obs-3", "the ledger convention lives in trial-ledger.py", 3, "sess-c")])
    grown = p.retrieve(_case("ledger convention"))
    assert [i.record_id for i in grown.items] == ["obs-3"]  # canonical mapping survives append
    assert grown.raw["message_hits"] == 1
    p.append([_rec("obs-2", "development still uses docker compose", 2, "sess-b")])
    assert [i.record_id for i in p.retrieve(_case("docker compose")).items] == ["obs-2"]
    p.close()
    with pytest.raises(ProviderUnavailable):
        p.retrieve(_case("docker"))  # closed is closed, appended or not


def test_append_is_corpus_mode_only():
    att = PiLcmStoreReaderProvider(store_path="x.db")
    with pytest.raises(ProviderUnavailable, match="read-only"):
        att.append([])


def test_history_null_append_grows_the_passthrough():
    null = PiLcmHistoryNullProvider()
    null.ingest([_rec("old", "deploy the widget", 1, "s1")])
    null.append([_rec("new", "deploy the gadget", 5, "s2")])
    res = null.retrieve(_case("anything"), top_k=1)
    assert [i.record_id for i in res.items] == ["old", "new"]  # chronological full history
    assert res.raw["observations_offered"] == 2
    null.close()
