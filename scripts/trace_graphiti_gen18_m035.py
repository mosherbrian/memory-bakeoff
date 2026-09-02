#!/usr/bin/env python3
"""Capture Graphiti's native node/edge extraction for one diagnostic episode."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from openai import AsyncOpenAI
from graphiti_core import Graphiti
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.nodes import EpisodeType
from memory_bakeoff.graphiti_gen19_schema import EDGE_TYPE_MAP, EDGE_TYPES, ENTITY_TYPES, EXTRACTION_INSTRUCTIONS
from redislite.async_falkordb_client import AsyncFalkorDB

OUT = Path(__file__).resolve().parents[1] / "results" / "graphiti_gen19_schema_trace"

class RecordingClient(OpenAIGenericClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls = []
    async def generate_response(self, messages, response_model=None, **kwargs):
        result = await super().generate_response(messages, response_model, **kwargs)
        self.calls.append({"prompt_name": kwargs.get("prompt_name"), "response": result})
        return result

async def main():
    if OUT.exists(): raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    cfg = LLMConfig(api_key="local", model="qwen3.6-35b-vulkan-nothink", small_model="qwen3.6-35b-vulkan-nothink", base_url="http://strix-halo.local:8080/v1", temperature=0)
    llm = RecordingClient(config=cfg, client=AsyncOpenAI(api_key="local", base_url=cfg.base_url, timeout=120), structured_output_mode="json_schema")
    db = AsyncFalkorDB(dbfilename=str(OUT / "graphiti.falkordb"))
    graphiti = Graphiti(graph_driver=FalkorDriver(falkor_db=db, database="graphiti_gen18_m035_trace"), llm_client=llm, embedder=OpenAIEmbedder(config=OpenAIEmbedderConfig(api_key="ollama", embedding_model="nomic-embed-text", embedding_dim=768, base_url="http://127.0.0.1:11434/v1")), cross_encoder=OpenAIRerankerClient(client=llm, config=cfg))
    try:
        result = await graphiti.add_episode(name="T_BRANCH", episode_body="The alpha release branch is release/alpha.", source_description="publication-safe coding configuration sentinel", reference_time=datetime(2026, 2, 4, 10, tzinfo=timezone.utc), source=EpisodeType.text, group_id="alpha", entity_types=ENTITY_TYPES, edge_types=EDGE_TYPES, edge_type_map=EDGE_TYPE_MAP, custom_extraction_instructions=EXTRACTION_INSTRUCTIONS)
        data = {"nodes": [{"uuid": n.uuid, "name": n.name, "labels": n.labels} for n in result.nodes], "edges": [{"uuid": e.uuid, "fact": e.fact} for e in result.edges], "llm_calls": llm.calls}
        (OUT / "trace.json").write_text(json.dumps(data, indent=2) + "\n")
    finally:
        await graphiti.close()

asyncio.run(main())
