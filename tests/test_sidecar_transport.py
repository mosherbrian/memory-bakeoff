import json
from pathlib import Path

import pytest

from memory_bakeoff.sidecar_transport import _read_json, export_pending_sidecar_requests, import_sidecar_response_bundle


def _package(root: Path) -> Path:
    for condition in ("core", "stress"):
        base = root / condition
        for name in ("requests", "responses", "batches"):
            (base / name).mkdir(parents=True, exist_ok=True)
        request_id = f"reader_{condition}_Q007"
        request = {
            "protocol_version": 1,
            "request_id": request_id,
            "fingerprint": f"fp-{condition}",
            "openai_request": {"model": "chatgpt-sidecar", "messages": [{"role": "user", "content": condition}], "temperature": 0.0},
            "metadata": {"case_id": "Q007"},
        }
        (base / "requests" / f"{request_id}.json").write_text(json.dumps(request))
        (base / "batches" / f"{condition}.json").write_text(json.dumps({"batch_id": condition, "request_ids": [request_id]}))
        (base / "manifest.json").write_text(json.dumps({"request_ids": [request_id]}))
    return root


def test_transport_exports_in_manifest_order_and_imports_complete_bundle(tmp_path):
    package = _package(tmp_path / "package")
    export = export_pending_sidecar_requests(package, tmp_path / "export.json")
    assert [row["condition"] for row in export["requests"]] == ["core", "stress"]
    bundle = {
        "schema_version": 1,
        "kind": "memory-bakeoff-sidecar-response-bundle",
        "request_set_sha256": export["request_set_sha256"],
        "responses": [
            {"request_id": row["request_id"], "fingerprint": row["fingerprint"], "content": "answer", "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}
            for row in export["requests"]
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle))
    imported = import_sidecar_response_bundle(package, bundle_path)
    assert imported["response_count"] == 2
    assert len(list((package / "core" / "responses").glob("*.json"))) == 1


def test_transport_rejects_partial_or_fingerprint_mismatched_bundle(tmp_path):
    package = _package(tmp_path / "package")
    export = export_pending_sidecar_requests(package, tmp_path / "export.json")
    bad = {
        "schema_version": 1,
        "kind": "memory-bakeoff-sidecar-response-bundle",
        "request_set_sha256": export["request_set_sha256"],
        "responses": [{"request_id": "reader_core_Q007", "fingerprint": "wrong", "content": "answer", "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        import_sidecar_response_bundle(package, path)
    assert not list((package / "core" / "responses").glob("*.json"))
    missing = {**bad, "responses": [{"request_id": "reader_core_Q007", "fingerprint": "fp-core", "content": "answer", "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}]}
    path.write_text(json.dumps(missing))
    with pytest.raises(ValueError, match="must be complete"):
        import_sidecar_response_bundle(package, path)
    unexpected = {**missing, "responses": missing["responses"] + [{"request_id": "unknown", "fingerprint": "x", "content": "answer", "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}]}
    path.write_text(json.dumps(unexpected))
    with pytest.raises(ValueError, match="unexpected response"):
        import_sidecar_response_bundle(package, path)
    duplicate = {**missing, "responses": missing["responses"] + missing["responses"]}
    path.write_text(json.dumps(duplicate))
    with pytest.raises(ValueError, match="duplicate"):
        import_sidecar_response_bundle(package, path)


def test_transport_accepts_only_a_leading_utf8_bom_without_changing_bundle_content(tmp_path):
    payload = {
        "schema_version": 1,
        "kind": "memory-bakeoff-sidecar-response-bundle",
        "request_set_sha256": "set",
        "responses": [
            {"request_id": f"r{index}", "fingerprint": f"f{index}", "content": f"exact answer {index}", "model": "chatgpt-sidecar", "finish_reason": "stop", "usage": {}, "tool_calls": []}
            for index in range(28)
        ],
    }
    plain = tmp_path / "plain.json"
    bom = tmp_path / "bom.json"
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    plain.write_bytes(raw)
    bom.write_bytes(b"\xef\xbb\xbf" + raw)
    assert _read_json(plain) == _read_json(bom) == payload
    assert _read_json(plain)["responses"] == _read_json(bom)["responses"]
    assert len(_read_json(bom)["responses"]) == 28
    assert all(set(response) == {"request_id", "fingerprint", "content", "model", "finish_reason", "usage", "tool_calls"} for response in _read_json(bom)["responses"])


def test_transport_rejects_malformed_prefix_bytes(tmp_path):
    malformed = tmp_path / "malformed.json"
    malformed.write_bytes(b"\xef\xbb\xbe{\"schema_version\": 1}")
    with pytest.raises(ValueError, match="invalid JSON"):
        _read_json(malformed)
