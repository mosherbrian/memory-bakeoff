from __future__ import annotations
import sys,time
from pathlib import Path
from typing import Sequence
import numpy as np
from memory_bakeoff.models import MemoryRecord,ProviderCapabilities,ProviderProbe,QueryCase,RetrievalItem,RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider
from memory_bakeoff.providers.membukkit_test_doubles import SharedLSAEncoder

class Mem0CoreLSAProvider(MemoryProvider):
    name='mem0_core_lsa'
    capabilities=ProviderCapabilities(raw_ingest=True,product_ingest=False,service_required=False,notes='Pinned Mem0 semantic-only search policy with shared LSA; BM25/entity inactive.')
    def __init__(self):
        super().__init__(); self.encoder=None; self.ids=[]; self.vecs=None
    @property
    def vendor(self): return Path(__file__).resolve().parents[3]/'vendor'/'mem0'
    def probe(self):
        ok=(self.vendor/'mem0/utils/scoring.py').exists(); return ProviderProbe(self.name,ok,'vendored Mem0 scoring policy ready' if ok else 'vendored Mem0 scoring missing',self.capabilities)
    def reset(self): self._records.clear(); self.encoder=None; self.ids=[]; self.vecs=None
    def ingest(self,records:Sequence[MemoryRecord],mode='raw'):
        if mode!='raw': raise RuntimeError('mem0_core_lsa is raw/core-only')
        self.reset(); self.remember_records(records); self.ids=[r.id for r in records]
        self.encoder=SharedLSAEncoder([r.text for r in records]); self.vecs=self.encoder.encode([r.text for r in records],normalize=True)
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter(); q=self.encoder.encode(case.query,normalize=True)
        scores=np.asarray(self.vecs@q,dtype=float); internal=max(top_k*4,60)
        idx=np.argsort(scores)[::-1][:internal]
        semantic=[{'id':self.ids[i],'score':float(scores[i]),'payload':{'data':self._records[self.ids[i]].text}} for i in idx]
        v=str(self.vendor)
        if v not in sys.path: sys.path.insert(0,v)
        from mem0.utils.scoring import score_and_rank
        ranked=score_and_rank(semantic,{}, {}, threshold=0.1,top_k=top_k,explain=True)
        items=[RetrievalItem(x['id'],self._records[x['id']].text,x['score'],x.get('score_details') or {}) for x in ranked]
        return RetrievalResult(items,(time.perf_counter()-t)*1000,{'internal_limit':internal,'threshold':0.1,'bm25_active':False,'entity_active':False})
