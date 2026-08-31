from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.providers.agentmemory_core import AgentMemoryCoreProvider
from memory_bakeoff.runner import run_provider
import subprocess, sys


def test_agentmemory_vendor_hashes():
    subprocess.run([sys.executable, 'scripts/verify_agentmemory_vendor.py'], check=True)


def test_agentmemory_core_runs_real_indexes():
    p=AgentMemoryCoreProvider()
    records,cases=build_corpus()
    assert all(ord(ch)<128 for r in records for ch in r.text)
    p.ingest(records,'raw')
    assert p.init_meta['count'] <= p.init_meta['input_count'] == len(records)
    result=p.retrieve(cases[0],5)
    assert result.items
    assert result.raw['graph_enabled'] is False
    p.reset()


def test_agentmemory_core_baseline_is_nontrivial():
    r=run_provider('agentmemory_core_lsa',distractors=0,top_k=5)
    assert r['status']=='ok'
    assert r['summary']['hit@5'] >= 0.90
