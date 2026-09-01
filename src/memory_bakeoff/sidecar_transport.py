"""Fail-closed transport for frozen ChatGPT-sidecar request batches."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Sequence


CONDITIONS = ("core", "stress")


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def _load_pending(package_root: str | Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = Path(package_root).resolve()
    exported: list[dict[str, Any]] = []
    source: dict[str, Any] = {"package_root": str(root), "conditions": {}}
    seen: set[str] = set()
    for condition in CONDITIONS:
        base = root / condition
        manifest = _read_json(base / "manifest.json")
        batches = sorted((base / "batches").glob("*.json"))
        if len(batches) != 1:
            raise ValueError(f"expected exactly one batch for {condition}: {base / 'batches'}")
        batch = _read_json(batches[0])
        request_ids = batch.get("request_ids")
        if not isinstance(request_ids, list) or request_ids != manifest.get("request_ids"):
            raise ValueError(f"request order mismatch for {condition}")
        source["conditions"][condition] = {
            "manifest_path": str((base / "manifest.json").relative_to(root)),
            "manifest_sha256": hashlib.sha256((base / "manifest.json").read_bytes()).hexdigest(),
            "batch_path": str(batches[0].relative_to(root)),
            "batch_id": batch.get("batch_id"),
        }
        for request_id in request_ids:
            if not isinstance(request_id, str) or request_id in seen:
                raise ValueError(f"duplicate or invalid request ID: {request_id!r}")
            path = base / "requests" / f"{request_id}.json"
            payload = _read_json(path)
            if payload.get("protocol_version") != 1 or payload.get("request_id") != request_id:
                raise ValueError(f"invalid sidecar request envelope: {path}")
            fingerprint = payload.get("fingerprint")
            openai = payload.get("openai_request")
            if not isinstance(fingerprint, str) or not isinstance(openai, dict):
                raise ValueError(f"missing request fingerprint or OpenAI payload: {path}")
            metadata = payload.get("metadata") or {}
            case_id = metadata.get("case_id")
            if not isinstance(case_id, str):
                raise ValueError(f"missing case ID metadata: {path}")
            exported.append(
                {
                    "condition": condition,
                    "case_id": case_id,
                    "request_id": request_id,
                    "fingerprint": fingerprint,
                    "messages": openai.get("messages"),
                    "model": openai.get("model"),
                    "temperature": openai.get("temperature"),
                    "source_request_path": str(path.relative_to(root)),
                }
            )
            seen.add(request_id)
    return exported, source


def export_pending_sidecar_requests(package_root: str | Path, out_path: str | Path) -> dict[str, Any]:
    """Export all frozen pending requests in manifest order without modifying them."""
    out = Path(out_path)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite transport export: {out}")
    requests, source = _load_pending(package_root)
    request_set = [{key: row[key] for key in ("condition", "case_id", "request_id", "fingerprint")} for row in requests]
    payload = {
        "schema_version": 1,
        "kind": "memory-bakeoff-sidecar-request-export",
        "request_set_sha256": _canonical_sha256(request_set),
        "source": source,
        "requests": requests,
        "response_bundle_schema": {
            "schema_version": 1,
            "kind": "memory-bakeoff-sidecar-response-bundle",
            "request_set_sha256": "copy from this export",
            "responses": [
                {
                    "request_id": "string",
                    "fingerprint": "matching exported fingerprint",
                    "content": "ChatGPT answer text",
                    "model": "chatgpt-sidecar",
                    "finish_reason": "stop",
                    "usage": {},
                    "tool_calls": [],
                }
            ],
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(out, payload)
    return payload


def import_sidecar_response_bundle(package_root: str | Path, bundle_path: str | Path) -> dict[str, Any]:
    """Validate one complete response bundle and write normal sidecar responses.

    No response file is written until every request ID and fingerprint validates.
    """
    root = Path(package_root).resolve()
    requests, _source = _load_pending(root)
    expected = {row["request_id"]: row for row in requests}
    expected_set = [{key: row[key] for key in ("condition", "case_id", "request_id", "fingerprint")} for row in requests]
    bundle = _read_json(Path(bundle_path))
    if bundle.get("schema_version") != 1 or bundle.get("kind") != "memory-bakeoff-sidecar-response-bundle":
        raise ValueError("unsupported response bundle schema")
    if bundle.get("request_set_sha256") != _canonical_sha256(expected_set):
        raise ValueError("response bundle request set does not match frozen export")
    responses = bundle.get("responses")
    if not isinstance(responses, list):
        raise ValueError("response bundle has no responses array")
    supplied: dict[str, dict[str, Any]] = {}
    for response in responses:
        if not isinstance(response, dict):
            raise ValueError("response bundle contains a non-object response")
        request_id = response.get("request_id")
        if not isinstance(request_id, str) or request_id in supplied:
            raise ValueError(f"duplicate or invalid response request ID: {request_id!r}")
        expected_row = expected.get(request_id)
        if expected_row is None:
            raise ValueError(f"unexpected response request ID: {request_id}")
        if response.get("fingerprint") != expected_row["fingerprint"]:
            raise ValueError(f"fingerprint mismatch for {request_id}")
        if not isinstance(response.get("content"), str):
            raise ValueError(f"response content must be a string for {request_id}")
        if response.get("model") != "chatgpt-sidecar" or response.get("finish_reason") != "stop":
            raise ValueError(f"response envelope mismatch for {request_id}")
        if response.get("usage") != {} or response.get("tool_calls") != []:
            raise ValueError(f"response envelope usage/tool_calls mismatch for {request_id}")
        supplied[request_id] = response
    if set(supplied) != set(expected):
        missing = sorted(set(expected) - set(supplied))
        unexpected = sorted(set(supplied) - set(expected))
        raise ValueError(f"response bundle must be complete; missing={missing}, unexpected={unexpected}")

    destinations: list[tuple[Path, dict[str, Any]]] = []
    for row in requests:
        response = supplied[row["request_id"]]
        destination = root / row["condition"] / "responses" / f"{row['request_id']}.json"
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite sidecar response: {destination}")
        destinations.append(
            (
                destination,
                {
                    "protocol_version": 1,
                    "request_id": row["request_id"],
                    "content": response["content"],
                    "model": "chatgpt-sidecar",
                    "finish_reason": "stop",
                    "usage": {},
                    "tool_calls": [],
                    "created_at": time.time(),
                },
            )
        )
    for destination, response in destinations:
        _atomic_write(destination, response)
    return {"status": "imported", "response_count": len(destinations), "request_set_sha256": _canonical_sha256(expected_set)}
