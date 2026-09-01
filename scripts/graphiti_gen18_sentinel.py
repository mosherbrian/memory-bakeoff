#!/usr/bin/env python3
"""Generation 18 Graphiti OSS provenance/temporal sentinel; not a score run."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from graphiti_core import Graphiti
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.nodes import EpisodeType
from redislite.async_falkordb_client import AsyncFalkorDB


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "graphiti_gen18_sentinel"
DB = OUT / "graphiti.falkordb"
EPISODES = [
    ("M011", "The build coordinator is strix03.", "2026-02-01T09:00:00", "alpha"),
    ("M012", "The build coordinator moved from strix03 to strix07; strix07 is now authoritative.", "2026-03-15T09:00:00", "alpha"),
    ("M013", "Production deploys use 'deployctl push --region west'.", "2026-02-02T10:00:00", "alpha"),
    ("M014", "After the deploy service migration, production deploys use 'shipit release --cluster pdx'; deployctl is obsolete.", "2026-04-10T10:00:00", "alpha"),
    ("M035", "The alpha release branch is release/alpha.", "2026-02-04T10:00:00", "alpha"),
    ("M036", "The beta release branch is release/beta.", "2026-02-04T10:00:00", "beta"),
]


async def main() -> None:
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    llm_config = LLMConfig(api_key="ollama", model="qwen2.5:3b", small_model="qwen2.5:3b", base_url="http://127.0.0.1:11434/v1", temperature=0)
    db = AsyncFalkorDB(dbfilename=str(DB))
    driver = FalkorDriver(falkor_db=db, database="graphiti_gen18")
    llm = OpenAIGenericClient(config=llm_config, structured_output_mode="json_schema")
    graphiti = Graphiti(
        graph_driver=driver,
        llm_client=llm,
        embedder=OpenAIEmbedder(config=OpenAIEmbedderConfig(api_key="ollama", embedding_model="nomic-embed-text", embedding_dim=768, base_url="http://127.0.0.1:11434/v1")),
        cross_encoder=OpenAIRerankerClient(client=llm, config=llm_config),
    )
    written = []
    try:
        for record_id, text, timestamp, group_id in EPISODES:
            result = await graphiti.add_episode(name=record_id, episode_body=text, source_description=f"canonical benchmark record {record_id}", reference_time=datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc), source=EpisodeType.text, group_id=group_id)
            written.append({"record_id": record_id, "group_id": group_id, "episode_uuid": result.episode.uuid, "native_edge_uuids": [edge.uuid for edge in result.edges]})
        queries = {}
        for query, groups in (("What machine is the current build coordinator?", ["alpha"]), ("What is the alpha release branch?", ["alpha"]), ("What is the beta release branch?", ["beta"])):
            edges = await graphiti.search(query, group_ids=groups, num_results=5)
            queries[query] = [{"edge_uuid": edge.uuid, "fact": edge.fact, "episode_uuids": edge.episodes, "valid_at": edge.valid_at.isoformat() if edge.valid_at else None, "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None} for edge in edges]
        (OUT / "evidence.json").write_text(json.dumps({"mode": "product_diagnostic", "graphiti": {"version": "0.29.3", "commit": "021d3a57d511f21b10adaf7fa923bd5c1fce5e9d"}, "runtime": {"backend": "FalkorDB Lite 4.18.3", "llm": "Ollama qwen2.5:3b", "embedder": "Ollama nomic-embed-text (768)", "reranker": "OpenAIRerankerClient via qwen2.5:3b"}, "written": written, "queries": queries}, indent=2) + "\n")
    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())
