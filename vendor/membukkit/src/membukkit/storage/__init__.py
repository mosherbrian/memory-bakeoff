"""Raw-benchmark storage shim: upstream in-memory backend only."""
from membukkit.config import RetrievalConfig, StorageConfig
from membukkit.storage.base import Candidate, CandidatePool, FactRecord, MemoryBackend, content_id
from membukkit.storage.memory import InMemoryBackend

def make_backend(retrieval: RetrievalConfig, encoder, storage: StorageConfig | None = None):
    storage = storage or StorageConfig()
    kind = (storage.backend or "memory").lower()
    if kind in ("memory", "local", "inmemory", "in_memory"):
        return InMemoryBackend(retrieval, encoder)
    raise ValueError(f"vendored raw benchmark only supports in-memory backend, got {storage.backend!r}")

__all__ = ["MemoryBackend", "FactRecord", "Candidate", "CandidatePool", "InMemoryBackend", "content_id", "make_backend"]
