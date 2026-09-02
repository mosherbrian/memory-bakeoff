"""Frozen Generation 20 structured-episode envelope for Graphiti.

This is a representation-preserving transport profile, not a conversion to
facts or triples.  Every field is copied mechanically from ``MemoryRecord``
or is a profile-wide constant.  It deliberately contains no inferred subject,
object, relation, truth status, correction link, or query term.
"""
from __future__ import annotations

import hashlib
import json
from base64 import urlsafe_b64encode
from typing import Any

from memory_bakeoff.models import MemoryRecord


PROFILE_NAME = "graphiti_gen20_structured_episode_v1"
SOURCE_KIND = "benchmark_memory_record"
FIELD_NAMES = (
    "assertion_text",
    "canonical_record_id",
    "reference_time",
    "scope",
    "source_kind",
)


def build_episode_envelope(record: MemoryRecord) -> dict[str, str]:
    """Return the frozen, mechanically copied JSON representation of a record."""
    return {
        "assertion_text": record.text,
        "canonical_record_id": record.id,
        "reference_time": record.timestamp.isoformat(),
        "scope": record.scope,
        "source_kind": SOURCE_KIND,
    }


def serialize_episode_envelope(record: MemoryRecord) -> str:
    """Produce a deterministic compact JSON body for Graphiti ``EpisodeType.json``."""
    return json.dumps(build_episode_envelope(record), sort_keys=True, separators=(",", ":"))


def graphiti_group_id(scope: str) -> str:
    """Encode a canonical scope for Graphiti's restricted native group-id grammar."""
    encoded = urlsafe_b64encode(scope.encode("utf-8")).decode("ascii").rstrip("=")
    return f"scope_{encoded}"


def envelope_config() -> dict[str, Any]:
    """Return the profile configuration and its stable hash for trace publication."""
    config = {
        "profile": PROFILE_NAME,
        "fields": list(FIELD_NAMES),
        "mechanical_rule": (
            "copy MemoryRecord.id, text, timestamp.isoformat(), and scope; "
            "set source_kind to the profile-wide constant benchmark_memory_record"
        ),
        "group_id_rule": "scope_ + unpadded URL-safe base64 of MemoryRecord.scope",
        "forbidden_semantic_fields": [
            "subject_label",
            "object_label",
            "entity_type",
            "relation",
            "truth_status",
            "supersedes",
            "corrects",
            "expected_query_terms",
            "fact_triple",
        ],
    }
    encoded = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return {**config, "sha256": hashlib.sha256(encoded.encode()).hexdigest()}
