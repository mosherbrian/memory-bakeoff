from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.providers.dense import DenseLSAProvider
from memory_bakeoff.providers.hybrid import HybridRRFProvider


def test_baselines_return_known_ids():
    records,cases=build_corpus()
    for cls in (BM25Provider,DenseLSAProvider,HybridRRFProvider):
        p=cls(); p.ingest(records)
        r=p.retrieve(cases[0],5)
        assert r.items
        assert all(i.record_id for i in r.items)


def test_scope_is_not_hidden_prefiltered():
    """Scope questions should be solved from query text, not oracle metadata filtering."""
    records,cases=build_corpus(); case=next(x for x in cases if x.id=="Q019")
    p=BM25Provider(); p.ingest(records)
    # Both Atlas and Beacon branch records remain candidates in the index.
    assert {"M029","M030"}.issubset({r.id for r in p.docs})
    result=p.retrieve(case,5)
    assert result.ids[0] == "M029"


def test_tfidf_baseline_retrieves_exact_identifier():
    from memory_bakeoff.providers.tfidf import TfidfCosineProvider
    from memory_bakeoff.corpus import build_corpus
    records, cases = build_corpus()
    p = TfidfCosineProvider(); p.ingest(records)
    case = next(c for c in cases if c.id == "Q001")
    assert p.retrieve(case, 3).ids[0] == "M001"
