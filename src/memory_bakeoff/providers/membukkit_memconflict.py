"""Frozen MemBukkit adapter for the MemConflict exact-provenance lane.

Adapter identity is hashed before any calibration question is exposed and
re-checked at run time, exactly as the Gen37 Perseus and Mem0 adapters are.

What this adapter does and does not send to the product:

* indexed text is the released message content, verbatim and alone;
* the write receipt is an opaque ordinal (``m000001``) assigned in write order,
  never a persona, session, turn or question identifier, and never indexed;
* the query is the released question text, verbatim and alone;
* nothing from the scorer side — labels, conflict type, answer, support
  sessions, ability target, updated attributes, session type — is written,
  queried or stored.

Native rank, and why it is not read off the public surface: MemBukkit selects
by relevance and then re-presents the selected hits in date order, so the order
of ``MemorySearchResult.hits`` is a presentation property. The native relevance
order is the sequence ``MemorySystem._retrieve`` returns. This adapter observes
that sequence and requires it to hold exactly the same records as the public
surface returned, so rank is native and the equivalence is proven per query
rather than assumed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ADAPTER_VERSION = "membukkit-memconflict-adapter-v1"

# Written to the product, per message. Anything else is a contract violation.
PRODUCT_WRITE_FIELDS = ("text", "fact_id")

# Read back from the product, per returned item.
PRODUCT_READ_FIELDS = ("native_id", "rank", "score")

RECEIPT_PREFIX = "m"


def receipt_for(ordinal: int) -> str:
    """Opaque, order-only write receipt seed."""
    return f"{RECEIPT_PREFIX}{ordinal:06d}"


def write_payload(text: str, ordinal: int) -> dict:
    """The exact payload handed to ``MemorySystem.ingest_facts``."""
    return {"text": text, "fact_id": receipt_for(ordinal)}


def assert_write_payload(payload: dict) -> None:
    if set(payload) != set(PRODUCT_WRITE_FIELDS):
        raise ValueError(f"write payload carries fields outside the contract: {sorted(payload)}")
    if not isinstance(payload["text"], str) or not payload["text"]:
        raise ValueError("indexed text must be the released message content")
    seed = payload["fact_id"]
    if not seed.startswith(RECEIPT_PREFIX) or not seed[len(RECEIPT_PREFIX):].isdigit():
        raise ValueError(f"receipt {seed!r} is not an opaque ordinal")


def adapter_contract_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
