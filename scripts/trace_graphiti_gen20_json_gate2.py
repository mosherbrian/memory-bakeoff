#!/usr/bin/env python3
"""Run Generation 20's fixed second native structured-episode gate; no score."""
import asyncio
import json
import tempfile
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


OUT = Path(__file__).resolve().parents[1] / "results" / "graphiti_gen20_json_gate2"
MODEL = "qwen3.6-35b-vulkan-nothink"
BASE_URL = "http://strix-halo.local:8080/v1"
RECORD_IDS = ("M011", "M012", "M013", "M014", "M035", "M036", "M023", "M024")


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
    by_id = {record.id: record for record in records}
    selected = [by_id[record_id] for record_id in RECORD_IDS]
    if len({record.scope for record in selected}) != 1:
        raise SystemExit("second gate requires one mechanically copied canonical scope")
    OUT.mkdir(parents=True)
    cfg = LLMConfig(api_key="local", model=MODEL, small_model=MODEL, base_url=BASE_URL, temperature=0)
    llm = RecordingClient(
        config=cfg,
        client=AsyncOpenAI(api_key="local", base_url=BASE_URL, timeout=120),
        structured_output_mode="json_schema",
    )
    with tempfile.TemporaryDirectory(prefix="memory-bakeoff-graphiti-gen20-") as temp_dir:
        db = AsyncFalkorDB(dbfilename=str(Path(temp_dir) / "graphiti.falkordb"))
        graphiti = Graphiti(
            graph_driver=FalkorDriver(falkor_db=db, database=graphiti_group_id(selected[0].scope)),
            llm_client=llm,
            embedder=OpenAIEmbedder(config=OpenAIEmbedderConfig(
                api_key="ollama", embedding_model="nomic-embed-text", embedding_dim=768,
                base_url="http://127.0.0.1:11434/v1",
            )),
            cross_encoder=OpenAIRerankerClient(client=llm, config=cfg),
        )
        try:
            episodes = []
            for record in selected:
                call_start = len(llm.calls)
                result = await graphiti.add_episode(
                    name=record.id,
                    episode_body=serialize_episode_envelope(record),
                    source_description="canonical benchmark memory record; mechanically copied fields",
                    reference_time=record.timestamp,
                    source=EpisodeType.json,
                    group_id=graphiti_group_id(record.scope),
                    entity_types=ENTITY_TYPES,
                    edge_types=EDGE_TYPES,
                    edge_type_map=EDGE_TYPE_MAP,
                    custom_extraction_instructions=EXTRACTION_INSTRUCTIONS,
                )
                episodes.append({
                    "canonical_record_id": record.id,
                    "json_body": json.loads(serialize_episode_envelope(record)),
                    "episode_uuid": result.episode.uuid,
                    "episode": native_object(result.episode),
                    "episodic_edges": [native_object(edge) for edge in result.episodic_edges],
                    "nodes": [native_object(node) for node in result.nodes],
                    "edges": [native_object(edge) for edge in result.edges],
                    "llm_calls": llm.calls[call_start:],
                })
            trace = {
                "generation": 20,
                "experiment_class": "product",
                "status": "second_structured_gate",
                "record_ids": list(RECORD_IDS),
                "group_id": graphiti_group_id(selected[0].scope),
                "envelope_config": envelope_config(),
                "runtime": {
                    "graphiti": "0.29.3",
                    "llm_model": MODEL,
                    "llm_base_url": BASE_URL,
                    "embedder": "nomic-embed-text",
                    "embedding_dim": 768,
                    "backend": "embedded FalkorDB Lite",
                },
                "episodes": episodes,
            }
            (OUT / "trace.json").write_text(json.dumps(trace, indent=2) + "\n")
        finally:
            await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
