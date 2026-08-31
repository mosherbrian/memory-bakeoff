from memory_bakeoff.providers.bm25 import BM25Provider
from memory_bakeoff.providers.dense import DenseLSAProvider
from memory_bakeoff.providers.tfidf import TfidfCosineProvider
from memory_bakeoff.providers.hybrid import HybridRRFProvider
from memory_bakeoff.providers.toy_adaptive import ToyAdaptiveProvider
from memory_bakeoff.providers.agentmemory_core import AgentMemoryCoreProvider, AgentMemoryRememberCoreProvider
from memory_bakeoff.providers.mem0_core import Mem0CoreLSAProvider
from memory_bakeoff.providers.claude_mem_core import (ClaudeMemFTS5CoreProvider, ClaudeMemChromaLSAProvider, ClaudeMemChromaLSANoRecencyProvider)
from memory_bakeoff.providers.external import Mem0Provider, HabitusProvider, MemBukkitControlledCoreProvider, MemBukkitProvider, AgentMemoryProvider, ClaudeMemProvider, HindsightProvider

PROVIDERS = {
    "bm25": BM25Provider,
    "dense_lsa": DenseLSAProvider,
    "tfidf_cosine": TfidfCosineProvider,
    "hybrid_rrf": HybridRRFProvider,
    "toy_adaptive_diagnostic": ToyAdaptiveProvider,
    "mem0": Mem0Provider,
    "mem0_core_lsa": Mem0CoreLSAProvider,
    "habitus": HabitusProvider,
    "membukkit": MemBukkitProvider,
    "membukkit_core_lsa": MemBukkitControlledCoreProvider,
    "agentmemory": AgentMemoryProvider,
    "agentmemory_core_lsa": AgentMemoryCoreProvider,
    "agentmemory_remember_lsa": AgentMemoryRememberCoreProvider,
    "claude_mem": ClaudeMemProvider,
    "claude_mem_fts5_core": ClaudeMemFTS5CoreProvider,
    "claude_mem_chroma_lsa": ClaudeMemChromaLSAProvider,
    "claude_mem_chroma_lsa_no_recency": ClaudeMemChromaLSANoRecencyProvider,
    "hindsight": HindsightProvider,
}
