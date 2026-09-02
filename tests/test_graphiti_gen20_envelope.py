import json

from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.graphiti_gen20_envelope import (
    FIELD_NAMES,
    build_episode_envelope,
    envelope_config,
    graphiti_group_id,
    serialize_episode_envelope,
)


def test_gen20_episode_envelope_is_mechanical_and_deterministic():
    records, _ = build_corpus()
    record = next(record for record in records if record.id == "M035")

    envelope = build_episode_envelope(record)
    assert tuple(sorted(envelope)) == tuple(sorted(FIELD_NAMES))
    assert envelope["canonical_record_id"] == "M035"
    assert envelope["assertion_text"] == record.text
    assert envelope["reference_time"] == record.timestamp.isoformat()
    assert envelope["scope"] == record.scope
    assert json.loads(serialize_episode_envelope(record)) == envelope
    assert serialize_episode_envelope(record) == serialize_episode_envelope(record)
    assert graphiti_group_id(record.scope) == "scope_cmVwbzpkZW1v"


def test_gen20_envelope_config_excludes_harness_semantics():
    config = envelope_config()
    assert len(config["sha256"]) == 64
    assert "relation" in config["forbidden_semantic_fields"]
    assert "fact_triple" in config["forbidden_semantic_fields"]
