#!/usr/bin/env python3
"""Run the one frozen Graphiti Gen20 ``EpisodeType.json`` M035 gate.

The embedded graph store is deliberately outside the repository.  The committed
trace contains only the source-safe native objects and recorded LLM responses.
"""
import asyncio
import json
import tempfile
from datetime import timezone
from pathlib import Path

from graphiti_core import Graphiti
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.nodes import EpisodeType
from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.graphiti_gen19_schema import (
    EDGE_TYPE_MAP,
    EDGE_TYPES,
    ENTITY_TYPES,
    EXTRACTION_INSTRUCTIONS,
)
from memory_bakeoff.graphiti_gen20_envelope import envelope_config, graphiti_group_id, serialize_episode_envelope
from openai import AsyncOpenAI
from redislite.async_falkordb_client import AsyncFalkorDB


OUT = Path(__file__).resolve().parents[1] / "results" / "graphiti_gen20_json_m035_gate"
MODEL = "qwen3.6-35b-vulkan-nothink"
BASE_URL = "http://strix-halo.local:8080/v1"


class RecordingClient(OpenAIGenericClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls = []

    async def generate_response(self, messages, response_model=None, **kwargs):
        result = await super().generate_response(messages, response_model, **kwargs)
        self.calls.append({"prompt_name": kwargs.get("prompt_name"), "response": result})
        return result


def native_object(value):
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


async def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    records, _ = build_corpus()
    record = next(record for record in records if record.id == "M035")
    body = serialize_episode_envelope(record)
    OUT.mkdir(parents=True)
    cfg = LLMConfig(
        api_key="local",
        model=MODEL,
        small_model=MODEL,
        base_url=BASE_URL,
        temperature=0,
    )
    llm = RecordingClient(
        config=cfg,
        client=AsyncOpenAI(api_key="local", base_url=BASE_URL, timeout=120),
        structured_output_mode="json_schema",
    )
    with tempfile.TemporaryDirectory(prefix="memory-bakeoff-graphiti-gen20-") as temp_dir:
        db = AsyncFalkorDB(dbfilename=str(Path(temp_dir) / "graphiti.falkordb"))
        graphiti = Graphiti(
            graph_driver=FalkorDriver(falkor_db=db, database="graphiti_gen20_m035"),
            llm_client=llm,
            embedder=OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    api_key="ollama",
                    embedding_model="nomic-embed-text",
                    embedding_dim=768,
                    base_url="http://127.0.0.1:11434/v1",
                )
            ),
            cross_encoder=OpenAIRerankerClient(client=llm, config=cfg),
        )
        try:
            result = await graphiti.add_episode(
                name=record.id,
                episode_body=body,
                source_description="canonical benchmark memory record; mechanically copied fields",
                reference_time=record.timestamp.astimezone(timezone.utc),
                source=EpisodeType.json,
                group_id=graphiti_group_id(record.scope),
                entity_types=ENTITY_TYPES,
                edge_types=EDGE_TYPES,
                edge_type_map=EDGE_TYPE_MAP,
                custom_extraction_instructions=EXTRACTION_INSTRUCTIONS,
            )
            trace = {
                "generation": 20,
                "experiment_class": "product",
                "status": "m035_json_gate",
                "canonical_record_id": record.id,
                "json_body": json.loads(body),
                "serialized_json_body": body,
                "envelope_config": envelope_config(),
                "runtime": {
                    "graphiti": "0.29.3",
                    "llm_model": MODEL,
                    "llm_base_url": BASE_URL,
                    "embedder": "nomic-embed-text",
                    "embedding_dim": 768,
                    "backend": "embedded FalkorDB Lite",
                },
                "episode_uuid": result.episode.uuid,
                "group_id": graphiti_group_id(record.scope),
                "episode": native_object(result.episode),
                "episodic_edges": [native_object(edge) for edge in result.episodic_edges],
                "nodes": [native_object(node) for node in result.nodes],
                "edges": [native_object(edge) for edge in result.edges],
                "llm_calls": llm.calls,
            }
            (OUT / "trace.json").write_text(json.dumps(trace, indent=2) + "\n")
        finally:
            await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
