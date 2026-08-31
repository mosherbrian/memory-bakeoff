from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Sequence

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, ProviderProbe, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider, ProviderUnavailable
from memory_bakeoff.providers.membukkit_test_doubles import SharedLSAEncoder


class AgentMemoryCoreProvider(MemoryProvider):
    """Pinned agentmemory BM25+vector core, graph/reranker disabled.

    Runs upstream SearchIndex + VectorIndex code in Node and ports the two-stream
    RRF/session-diversification block from upstream HybridSearch. Write-time
    /remember shaping and Jaccard supersession are reproduced. This is a controlled
    core ablation, not the full iii-engine product.
    """
    name = "agentmemory_core_lsa"
    raw_experiment_class = "controlled_core"
    product_experiment_class = "controlled_core"
    apply_supersession = False
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        service_required=False,
        notes="Pinned rohitg00/agentmemory BM25+vector retrieval core; shared LSA embeddings; graph/reranker disabled.",
    )

    def __init__(self):
        super().__init__()
        self.proc = None
        self.encoder = None
        self.init_meta = None

    @property
    def vendor(self) -> Path:
        return Path(__file__).resolve().parents[3] / "vendor" / "agentmemory"

    def probe(self):
        worker = self.vendor / "core_worker.mjs"
        compiled = self.vendor / "dist" / "state" / "search-index.js"
        ok = worker.exists() and compiled.exists()
        return ProviderProbe(self.name, ok, f"agentmemory core {'ready' if ok else 'missing'} at {self.vendor}", self.capabilities)

    def reset(self):
        self._records.clear()
        if self.proc is not None:
            try:
                self._rpc({"op":"close"})
            except Exception:
                pass
            try:
                self.proc.kill()
            except Exception:
                pass
        self.proc = None
        self.encoder = None
        self.init_meta = None

    def _start(self):
        self.proc = subprocess.Popen(
            ["node", str(self.vendor / "core_worker.mjs")],
            cwd=str(self.vendor), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )

    def _rpc(self, payload):
        if not self.proc or self.proc.poll() is not None:
            err = self.proc.stderr.read() if self.proc and self.proc.stderr else ""
            raise ProviderUnavailable(f"agentmemory core worker not running: {err[:500]}")
        self.proc.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            err = self.proc.stderr.read() if self.proc.stderr else ""
            raise ProviderUnavailable(f"agentmemory core worker exited: {err[:500]}")
        out = json.loads(line)
        if not out.get("ok"):
            raise ProviderUnavailable(f"agentmemory core error: {out.get('error')}")
        return out

    def ingest(self, records: Sequence[MemoryRecord], mode="raw"):
        if mode != "raw":
            raise ProviderUnavailable("agentmemory_core_lsa is raw/core-only")
        self.reset(); self.remember_records(records)
        self.encoder = SharedLSAEncoder([r.text for r in records])
        self._start()
        payload=[]
        for r in sorted(records, key=lambda x:(x.timestamp,x.id)):
            title=r.text[:80]
            # Upstream vectorIndexAddGuarded embeds memory.title + ' ' + memory.content.
            vec=self.encoder.encode(title + " " + r.text, normalize=True).tolist()
            payload.append({"record_id":r.id,"internal_id":f"mem_{r.id}","text":r.text,"timestamp":str(r.timestamp),"embedding":vec})
        self.init_meta=self._rpc({"op":"init","records":payload,"supersession":self.apply_supersession})

    def retrieve(self, case: QueryCase, top_k=5):
        t=time.perf_counter()
        qvec=self.encoder.encode(case.query, normalize=True).tolist()
        raw=self._rpc({"op":"search","query":case.query,"embedding":qvec,"limit":top_k})
        items=[]
        for x in raw.get("items",[])[:top_k]:
            rid=x.get("record_id")
            text=self._records[rid].text if rid in self._records else ""
            items.append(RetrievalItem(rid,text,x.get("combinedScore"),x))
        # Use worker-measured retrieval latency; Python IPC time stays in raw metadata.
        raw["ipc_wall_ms"]=(time.perf_counter()-t)*1000
        return RetrievalResult(items,float(raw.get("latency_ms",0.0)),raw)

    def __del__(self):
        try: self.reset()
        except Exception: pass


class AgentMemoryRememberCoreProvider(AgentMemoryCoreProvider):
    """Same core with upstream /remember write-time supersession enabled."""
    name = "agentmemory_remember_lsa"
    apply_supersession = True
    capabilities = ProviderCapabilities(
        raw_ingest=True, product_ingest=False, service_required=False,
        notes="Pinned agentmemory BM25+vector core with /remember >0.7 Jaccard supersession; graph/reranker disabled.",
    )
