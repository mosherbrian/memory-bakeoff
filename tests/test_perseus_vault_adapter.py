from datetime import datetime, timezone

from memory_bakeoff.models import MemoryRecord
from memory_bakeoff.providers.perseus_vault import body_for_record, key_for_record, workspace_for_scope


def test_perseus_mapping_is_deterministic_and_nonsemantic():
    record = MemoryRecord("M012", "The build coordinator moved from strix03 to strix07.", datetime(2026, 3, 15, tzinfo=timezone.utc), "s06", "repo:demo", supersedes_id="M011")
    assert key_for_record(record.id) == "record-M012"
    assert workspace_for_scope(record.scope) == workspace_for_scope("repo:demo")
    assert workspace_for_scope(record.scope) != workspace_for_scope("repo:atlas")
    body = body_for_record(record)
    assert body["canonical_record_id"] == "M012"
    assert body["assertion_text"] == record.text
    assert "supersedes_id" not in body
    assert set(body) == {"assertion_text", "canonical_record_id", "reference_time", "scope", "source_kind"}
