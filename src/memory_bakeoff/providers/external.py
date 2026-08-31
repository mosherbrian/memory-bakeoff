from __future__ import annotations

import importlib.util
import os
import json
import sys
from pathlib import Path
import time
import uuid
from typing import Sequence
import requests

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, ProviderProbe, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider, ProviderUnavailable


class Mem0Provider(MemoryProvider):
    name="mem0"
    capabilities=ProviderCapabilities(raw_ingest=True,product_ingest=True,requires_llm_for_product_ingest=True,notes="Raw mode uses add(..., infer=False); Python SDK/vector backend still required.")
    def __init__(self): super().__init__(); self.mem=None; self.user_id="memory-bakeoff"
    def probe(self):
        ok=importlib.util.find_spec("mem0") is not None
        return ProviderProbe(self.name,ok,"mem0 Python package found" if ok else "mem0 Python package not installed",self.capabilities)
    def reset(self): self._records.clear(); self.mem=None
    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if not self.probe().available: raise ProviderUnavailable(self.probe().reason)
        from mem0 import Memory
        self.reset(); self.remember_records(records); self.mem=Memory()
        for r in records:
            kwargs={"user_id":self.user_id,"metadata":{"record_id":r.id,"scope":r.scope,"timestamp":r.timestamp.isoformat()}}
            if mode=="raw": kwargs["infer"]=False
            self.mem.add(r.text,**kwargs)
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter(); raw=self.mem.search(case.query,user_id=self.user_id,limit=top_k)
        rows=raw.get("results",raw) if isinstance(raw,dict) else raw; items=[]
        for x in rows[:top_k]:
            text=x.get("memory") or x.get("text") or str(x); md=x.get("metadata") or {}; rid=md.get("record_id") or self.resolve_record_id(text)
            items.append(RetrievalItem(rid,text,x.get("score"),md))
        return RetrievalResult(items,(time.perf_counter()-t)*1000,raw)


class HabitusProvider(MemoryProvider):
    name="habitus"
    capabilities=ProviderCapabilities(raw_ingest=True,product_ingest=True,supports_as_of=False,supports_feedback=False,notes="Stock Habitus recall; stock record_outcome credits output-decision paths, not retrieval paths.")
    def __init__(self): super().__init__(); self.mind=None
    @staticmethod
    def _ensure_vendor_path():
        vendor=Path(__file__).resolve().parents[3]/"vendor"/"habitus"/"src"
        if vendor.exists() and str(vendor) not in sys.path:
            sys.path.insert(0,str(vendor))
        return vendor
    def probe(self):
        vendor=self._ensure_vendor_path()
        ok=importlib.util.find_spec("habitus_ai") is not None
        if ok and vendor.exists(): reason=f"vendored Habitus core found at {vendor}"
        else: reason="habitus_ai package found" if ok else "habitus-ai package not installed"
        return ProviderProbe(self.name,ok,reason,self.capabilities)
    def reset(self): self._records.clear(); self.mind=None
    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if not self.probe().available: raise ProviderUnavailable(self.probe().reason)
        import tempfile, os
        from habitus_ai import HabitusAI
        self.reset(); self.remember_records(records); path=os.path.join(tempfile.mkdtemp(prefix="habitus-bakeoff-"),"memory.sqlite"); self.mind=HabitusAI(path)
        for r in records:
            self.mind.remember(
                r.text,
                record_id=r.id,
                source_id=r.session_id,
                timestamp=r.timestamp.isoformat(),
                metadata={**r.metadata,"scope":r.scope,"outcome":r.outcome},
                supersedes_id=r.supersedes_id,
            )
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter(); rr=self.mind.recall(case.query,include_current_input=False); items=[]
        for hit in rr.hits[:top_k]:
            rec=hit.record
            score=max(float(getattr(hit,"dense_score",0.0)),float(getattr(hit,"lexical_score",0.0)),float(getattr(hit,"path_score",0.0)))
            items.append(RetrievalItem(getattr(rec,"record_id",None),rec.text,score,{"lane":getattr(hit,"lane",None)}))
        return RetrievalResult(items,(time.perf_counter()-t)*1000,rr)


class MemBukkitProvider(MemoryProvider):
    name="membukkit"
    capabilities=ProviderCapabilities(
        raw_ingest=True,
        product_ingest=True,
        requires_llm_for_product_ingest=True,
        supports_as_of=True,
        notes=(
            "Vendored raw mode runs the pinned upstream MemorySystem + InMemoryBackend with "
            "the same corpus-fit 32-D LSA representation as the benchmark dense baseline. "
            "Default raw select=none isolates MemBukkit bucket routing at ~30% scan; set "
            "MEMBUKKIT_SELECT=hybrid for the upstream CI lexical-reranker diagnostic. Product weights are separate."
        ),
    )

    def __init__(self):
        super().__init__()
        self.mem=None

    @staticmethod
    def _ensure_vendor_path():
        vendor=Path(__file__).resolve().parents[3]/"vendor"/"membukkit"/"src"
        if vendor.exists() and str(vendor) not in sys.path:
            sys.path.insert(0,str(vendor))
        return vendor

    def probe(self):
        vendor=self._ensure_vendor_path()
        ok=importlib.util.find_spec("membukkit.pipeline") is not None
        reason=(f"vendored MemBukkit core found at {vendor}" if ok and vendor.exists()
                else "membukkit package found" if ok else "membukkit package not installed")
        return ProviderProbe(self.name,ok,reason,self.capabilities)

    def reset(self):
        self._records.clear()
        self.mem=None

    def _raw_system(self, records):
        self._ensure_vendor_path()
        from membukkit.config import PromptConfig, RetrievalConfig
        from membukkit.pipeline import MemorySystem
        from memory_bakeoff.providers.membukkit_test_doubles import SharedLSAEncoder, FakeReranker

        # One atomic lane = one benchmark memory record. We deliberately do not
        # duplicate raw input into both verbatim + atomic lanes in this retrieval-only
        # round. Product mode later exercises normal distillation/union behavior.
        retrieval=RetrievalConfig(
            union=True,
            union_lanes=("atomic",),
            bucket_mode="topic",
            scan_budget=float(os.getenv("MEMBUKKIT_SCAN_BUDGET","0.3")),
            scan_budget_temporal=None,
            num_buckets=24,
            k_proto=0,
            select=os.getenv("MEMBUKKIT_SELECT","none"),
            rerank_cap=50,
            top_k=10,
            reasoning_top_k=30,
            k_rrf=60,
            lexical_lane=False,
        )
        return MemorySystem(
            encoder=SharedLSAEncoder([r.text for r in records]),
            reranker=FakeReranker(),
            llm_fn=lambda _prompt: "N/I",
            retrieval=retrieval,
            prompts=PromptConfig.default(),
            distiller=None,
        )

    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if not self.probe().available:
            raise ProviderUnavailable(self.probe().reason)
        self.reset()
        self.remember_records(records)

        if mode != "raw":
            # Product mode intentionally requires a full installed MemBukkit package
            # and model/LLM configuration; the vendored offline core is not presented
            # as a substitute for its pretrained product path.
            from membukkit.pipeline import MemorySystem
            self.mem=MemorySystem.from_pretrained(llm=os.getenv("MEMBUKKIT_LLM","openai:gpt-4o-mini"))
            sessions=[[{"role":"user","content":r.text}] for r in records]
            dates=[r.timestamp for r in records]
            self.mem.ingest(sessions=sessions,dates=dates,subject="memory-bakeoff")
            return

        self.mem=self._raw_system(records)
        # ingest_facts() is MemBukkit's documented no-distiller structured input
        # path. It intentionally does not infer supersession; raw mode preserves that
        # behavior rather than injecting benchmark ground truth or running a model-
        # dependent update heuristic with the shared LSA representation.
        for r in sorted(records,key=lambda x:(x.timestamp,x.id)):
            self.mem.ingest_facts([
                {
                    "text":r.text,
                    "timestamp":r.timestamp,
                    "source":r.session_id,
                    "fact_id":r.id,
                    "source_ref":r.id,
                    "doc_id":r.scope,
                }
            ],subject="memory-bakeoff")

    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter()
        raw=self.mem.search(
            case.query,
            top_k=top_k,
            question_date=case.as_of,
            include_history=False,
        )
        items=[]
        for hit in raw.hits[:top_k]:
            text=getattr(hit,"text","") or getattr(hit,"fact","")
            rid=getattr(hit,"source_ref","") or self.resolve_record_id(text)
            if rid not in self._records:
                rid=self.resolve_record_id(text)
            items.append(
                RetrievalItem(
                    rid,
                    text,
                    None,
                    {
                        "ref":getattr(hit,"ref",None),
                        "status":getattr(hit,"status",None),
                        "timestamp":getattr(hit,"timestamp",None),
                        "scan_fraction":getattr(raw.trace,"scan_fraction",None),
                    },
                )
            )
        return RetrievalResult(items,(time.perf_counter()-t)*1000,raw)


class AgentMemoryProvider(MemoryProvider):
    name="agentmemory"
    capabilities=ProviderCapabilities(raw_ingest=True,product_ingest=True,service_required=True,notes="Targets rohitg00/agentmemory REST API; its coding-agent-life eval uses /remember + /smart-search without an LLM in the retrieval loop.")
    def __init__(self,base_url=None):
        super().__init__(); self.base=(base_url or os.getenv("AGENTMEMORY_URL","http://127.0.0.1:3111")).rstrip("/"); self.project=os.getenv("AGENTMEMORY_PROJECT") or f"memory-bakeoff-{uuid.uuid4().hex[:8]}"
    def _headers(self):
        secret=os.getenv("AGENTMEMORY_SECRET")
        return {"Authorization":f"Bearer {secret}"} if secret else {}
    def probe(self):
        try:
            r=requests.get(self.base+"/agentmemory/health",headers=self._headers(),timeout=.5); ok=r.ok; reason=f"HTTP {r.status_code}" if not ok else "service healthy"
        except Exception as e: ok=False; reason=f"service unavailable at {self.base}: {type(e).__name__}"
        return ProviderProbe(self.name,ok,reason,self.capabilities)
    def reset(self): self._records.clear()
    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if not self.probe().available: raise ProviderUnavailable(self.probe().reason)
        self.remember_records(records)
        for r in records:
            # Current agentmemory does not accept arbitrary metadata on /remember.
            # Carry the benchmark ID in the returned `type` field instead. The query
            # never contains this marker, so it is provenance transport rather than
            # an oracle retrieval feature.
            payload={
                "project":self.project,
                "content":r.text,
                "type":f"memory-bakeoff:{r.id}",
            }
            resp=requests.post(self.base+"/agentmemory/remember",json=payload,headers=self._headers(),timeout=10)
            if not resp.ok: raise ProviderUnavailable(f"agentmemory remember failed: HTTP {resp.status_code}: {resp.text[:200]}")
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter()
        payload={"project":self.project,"query":case.query,"limit":top_k,"format":"compact"}
        r=requests.post(self.base+"/agentmemory/smart-search",json=payload,headers=self._headers(),timeout=10)
        if not r.ok: raise ProviderUnavailable(f"agentmemory search failed: HTTP {r.status_code}")
        raw=r.json(); rows=raw.get("results",raw if isinstance(raw,list) else []) if isinstance(raw,dict) else raw; items=[]
        for x in rows[:top_k]:
            marker=x.get("type") if isinstance(x,dict) else None
            rid=marker.split(":",1)[1] if isinstance(marker,str) and marker.startswith("memory-bakeoff:") else None
            if rid not in self._records:
                rid=None
            surfaced=(x.get("content") or x.get("text") or x.get("memory") or "") if isinstance(x,dict) else str(x)
            if not rid:
                rid=self.resolve_record_id(surfaced)
            # smart-search may return compact rows without content. Once the engine
            # has selected a stable benchmark ID, reconstruct the canonical source
            # text for downstream reader tests; this does not alter the ranking.
            text=self._records[rid].text if rid in self._records else surfaced or str(x)
            score=x.get("score") if isinstance(x,dict) else None
            md=dict(x) if isinstance(x,dict) else {}
            items.append(RetrievalItem(rid,text,score,md))
        return RetrievalResult(items,(time.perf_counter()-t)*1000,raw)


def _claude_mem_default_url() -> str:
    explicit = os.getenv("CLAUDE_MEM_URL")
    if explicit:
        return explicit.rstrip("/")
    port = os.getenv("CLAUDE_MEM_WORKER_PORT")
    if not port:
        settings = Path.home() / ".claude-mem" / "settings.json"
        try:
            data = json.loads(settings.read_text())
            port = str(data.get("CLAUDE_MEM_WORKER_PORT") or data.get("workerPort") or "") or None
        except (OSError, ValueError, TypeError):
            port = None
    if not port:
        try:
            port = str(37700 + (os.getuid() % 100))
        except (AttributeError, OSError):
            port = "37700"
    return f"http://127.0.0.1:{port}"


class ClaudeMemProvider(MemoryProvider):
    name="claude_mem"
    capabilities=ProviderCapabilities(raw_ingest=False,product_ingest=True,requires_llm_for_product_ingest=True,service_required=True,notes="Targets thedotmack/claude-mem worker. Normal observation ingestion is processed by Claude Agent SDK; no supported raw/no-LLM ingest path is assumed.")
    def __init__(self,base_url=None): super().__init__(); self.base=(base_url or _claude_mem_default_url()).rstrip("/"); self.project=os.getenv("CLAUDE_MEM_PROJECT") or f"memory-bakeoff-{uuid.uuid4().hex[:8]}"
    def probe(self):
        try:
            r=requests.get(self.base+"/api/health",timeout=.5); ok=r.ok; reason="service healthy" if ok else f"HTTP {r.status_code}"
        except Exception as e: ok=False; reason=f"service unavailable at {self.base}: {type(e).__name__}"
        return ProviderProbe(self.name,ok,reason,self.capabilities)
    def reset(self): self._records.clear()
    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if mode=="raw": raise ProviderUnavailable("Claude-Mem has no assumed supported no-LLM raw ingestion path; run in product mode.")
        if not self.probe().available: raise ProviderUnavailable(self.probe().reason)
        self.remember_records(records)
        # Use the documented platform-integration endpoint. Processing is asynchronous
        # and invokes Claude-Mem's configured compression model.
        for r in records:
            payload={
                "claudeSessionId": f"memory-bakeoff-{r.session_id}",
                "tool_name": "memory_bakeoff",
                "tool_input": {"record_id": r.id, "timestamp": r.timestamp.isoformat(), "scope": r.scope},
                "tool_response": r.text,
                "cwd": f"/{self.project}",
            }
            resp=requests.post(self.base+"/api/sessions/observations",json=payload,timeout=10)
            if not resp.ok: raise ProviderUnavailable(f"Claude-Mem observation ingest failed: HTTP {resp.status_code}: {resp.text[:200]}")
        # Observation compression is asynchronous. Wait for the documented queue to drain,
        # with a hard bound so a broken worker cannot hang the benchmark.
        deadline=time.monotonic()+120
        while time.monotonic() < deadline:
            try:
                status=requests.get(self.base+"/api/processing-status",timeout=2).json()
                if not status.get("isProcessing") and int(status.get("queueDepth",0)) == 0:
                    break
            except Exception:
                pass
            time.sleep(0.25)
        else:
            raise ProviderUnavailable("Claude-Mem processing queue did not drain within 120 seconds")
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter(); r=requests.get(self.base+"/api/search",params={"query":case.query,"limit":top_k,"project":self.project,"type":"observations","format":"full"},timeout=15)
        if not r.ok: raise ProviderUnavailable(f"Claude-Mem search failed: HTTP {r.status_code}")
        raw=r.json(); rows=raw.get("observations",raw.get("results",raw if isinstance(raw,list) else [])) if isinstance(raw,dict) else raw; items=[]
        for x in rows[:top_k]:
            text=x.get("narrative") or x.get("content") or x.get("observation") or x.get("preview") or x.get("text") or str(x); items.append(RetrievalItem(self.resolve_record_id(text),text,x.get("score"),x))
        return RetrievalResult(items,(time.perf_counter()-t)*1000,raw)


class HindsightProvider(MemoryProvider):
    name="hindsight"
    capabilities=ProviderCapabilities(raw_ingest=True,product_ingest=True,requires_llm_for_product_ingest=True,service_required=True,supports_as_of=True,notes="Raw mode is supported when the Hindsight server is explicitly launched with HINDSIGHT_API_LLM_PROVIDER=none (chunk storage, no fact extraction). Product mode uses normal LLM-powered retain().")
    def __init__(self,base_url=None): super().__init__(); self.base=(base_url or os.getenv("HINDSIGHT_URL","http://127.0.0.1:8888")).rstrip("/"); self.bank=os.getenv("HINDSIGHT_BANK") or f"memory-bakeoff-{uuid.uuid4().hex[:8]}"
    def probe(self):
        try:
            r=requests.get(self.base+"/health",timeout=.5); ok=r.ok; reason="service healthy" if ok else f"HTTP {r.status_code}"
        except Exception as e: ok=False; reason=f"service unavailable at {self.base}: {type(e).__name__}"
        return ProviderProbe(self.name,ok,reason,self.capabilities)
    def reset(self): self._records.clear()
    def ingest(self,records:Sequence[MemoryRecord],mode="raw"):
        if mode == "raw":
            declared = os.getenv("HINDSIGHT_RAW_LLM_PROVIDER", "").strip().lower()
            if declared != "none":
                raise ProviderUnavailable(
                    "Raw Hindsight runs require an explicit HINDSIGHT_RAW_LLM_PROVIDER=none declaration after launching the server with HINDSIGHT_API_LLM_PROVIDER=none; the harness will not assume the server's LLM mode."
                )
        if importlib.util.find_spec("hindsight_client") is None: raise ProviderUnavailable("hindsight-client Python package not installed")
        from hindsight_client import Hindsight
        self.remember_records(records); client=Hindsight(base_url=self.base); self.client=client
        for r in records:
            client.retain(
                bank_id=self.bank,
                content=r.text,
                context=f"memory-bakeoff; scope={r.scope}",
                timestamp=r.timestamp,
                document_id=r.id,
                metadata={"record_id":r.id,"session_id":r.session_id,"scope":r.scope,"outcome":r.outcome or ""},
            )
    def retrieve(self,case:QueryCase,top_k=5):
        t=time.perf_counter()
        kwargs={"bank_id":self.bank,"query":case.query,"max_tokens":4096}
        if case.as_of is not None:
            kwargs["query_timestamp"]=case.as_of.isoformat()
        raw=self.client.recall(**kwargs)
        # Client result shapes may contain memories/facts in multiple releases.
        rows=getattr(raw,"results",None) or getattr(raw,"memories",None) or (raw.get("results") or raw.get("memories",[]) if isinstance(raw,dict) else [])
        items=[]
        for x in list(rows)[:top_k]:
            if isinstance(x,str): text=x; score=None; md={}
            elif isinstance(x,dict): text=x.get("content") or x.get("text") or x.get("fact") or str(x); score=x.get("score"); md=x
            else: text=getattr(x,"content",None) or getattr(x,"text",None) or str(x); score=getattr(x,"score",None); md={}
            explicit=None
            if isinstance(md,dict):
                explicit=md.get("document_id") or md.get("source_document_id") or (md.get("metadata") or {}).get("record_id")
            else:
                explicit=getattr(x,"document_id",None) or getattr(x,"source_document_id",None)
                nested=getattr(x,"metadata",None)
                if not explicit and isinstance(nested,dict): explicit=nested.get("record_id")
            items.append(RetrievalItem(self.resolve_record_id(text,explicit),text,score,md if isinstance(md,dict) else {}))
        return RetrievalResult(items,(time.perf_counter()-t)*1000,raw)
