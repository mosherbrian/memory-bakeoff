"""Fail-closed adapter for the pinned Perseus Vault operator-seed profile."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any, Sequence

from memory_bakeoff.models import MemoryRecord, ProviderCapabilities, ProviderProbe, QueryCase, RetrievalItem, RetrievalResult
from memory_bakeoff.providers.base import MemoryProvider, ProviderUnavailable


PINNED_VERSION = "2.23.2"
PINNED_COMMIT = "9c829207a4b44a8e679ba912b4c1c5608c8f1e36"
DEFAULT_BINARY = "/private/tmp/perseus-vault-v2.23.2/perseus-vault"
CATEGORY = "benchmark_record"
BODY_FIELDS = ("assertion_text", "canonical_record_id", "reference_time", "scope", "source_kind")


def workspace_for_scope(scope: str) -> str:
    """Map a canonical scope to the product's opaque workspace identifier."""
    return hashlib.sha256(scope.encode("utf-8")).hexdigest()


def key_for_record(record_id: str) -> str:
    """Use a reversible non-semantic key; never reuse supersession truth."""
    return f"record-{record_id}"


def body_for_record(record: MemoryRecord) -> dict[str, str]:
    """The frozen, representation-preserving raw-write envelope."""
    return {
        "assertion_text": record.text,
        "canonical_record_id": record.id,
        "reference_time": record.timestamp.isoformat(),
        "scope": record.scope,
        "source_kind": "memory_bakeoff_round1_record",
    }


class PerseusVaultProvider(MemoryProvider):
    """Official binary: operator CLI seed writes + native MCP hybrid recall.

    The public MCP ``remember`` tool deliberately creates non-serveable
    proposals without an admission envelope.  The documented ``write`` command
    is the product's explicit operator seeding/scripting operation and lands
    active verified records.  This adapter labels that composite raw-product
    mode exactly and does not claim automatic capture or correction behavior.
    """

    name = "perseus_vault"
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        supports_as_of=True,
        notes=(
            "Pinned official binary profile: operator CLI write (active verified seed) "
            "+ MCP hybrid recall. MCP remember without admission is deliberately "
            "non-serveable and is not substituted. Explicit correction/supersede and "
            "maintenance are excluded from this raw retrieval lane."
        ),
    )

    def __init__(self) -> None:
        super().__init__()
        self.binary = Path(os.getenv("PERSEUS_VAULT_BIN", DEFAULT_BINARY)).expanduser()
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self._db: Path | None = None
        self._key: Path | None = None
        self._server: subprocess.Popen[str] | None = None
        self._next_id = 1
        self._native_ids: dict[str, str] = {}
        self._operations: list[dict[str, Any]] = []
        self._server_stderr: Path | None = None
        self._lifecycle_audit: dict[str, Any] | None = None

    def probe(self) -> ProviderProbe:
        if not self.binary.is_file() or not os.access(self.binary, os.X_OK):
            return ProviderProbe(
                self.name,
                False,
                "official Perseus Vault binary unavailable; set PERSEUS_VAULT_BIN to the verified v2.23.2 aarch64 binary",
                self.capabilities,
            )
        version = subprocess.run([str(self.binary), "--version"], text=True, capture_output=True, timeout=20)
        expected = f"perseus-vault {PINNED_VERSION} ({PINNED_COMMIT[:7]})"
        if version.returncode != 0 or version.stdout.strip() != expected:
            return ProviderProbe(self.name, False, f"binary version mismatch: expected {expected!r}, got {version.stdout.strip()!r}", self.capabilities)
        return ProviderProbe(self.name, True, f"verified official Perseus Vault {version.stdout.strip()} at {self.binary}", self.capabilities)

    def configuration(self) -> dict[str, Any]:
        return {
            "source_repo": "Perseus-Computing-LLC/perseus-vault",
            "release_tag": f"v{PINNED_VERSION}",
            "source_commit": PINNED_COMMIT,
            "binary": str(self.binary),
            "native_write_mode": "perseus-vault write (documented operator-seed/scripting path)",
            "native_recall_mode": "perseus_vault_recall mode=hybrid",
            "embedding": "bundled quantized all-MiniLM-L6-v2, 384 dimensions",
            "retrieval": "FTS5 + dense cosine reciprocal-rank fusion; native default hybrid explicitly selected",
            "storage": "fresh encrypted SQLite database and fresh temporary AES-256-GCM key per run",
            "category": CATEGORY,
            "key_rule": "record- + canonical record ID",
            "workspace_rule": "SHA-256 hex of canonical record/query scope",
            "body_fields": list(BODY_FIELDS),
            "automatic_lifecycle": "native write-time dedup remains product-default; no correction/supersede/forget/maintenance call is issued",
        }

    def reset(self) -> None:
        self.close()
        self._records.clear()
        self._native_ids.clear()
        self._operations.clear()
        self._lifecycle_audit = None

    def _run_cli(self, args: list[str]) -> dict[str, Any]:
        completed = subprocess.run(args, text=True, capture_output=True, timeout=90)
        operation = {"kind": "cli_write", "argv": args[1:], "stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode}
        self._operations.append(operation)
        if completed.returncode != 0:
            raise ProviderUnavailable(f"Perseus native write failed: {completed.stderr[-500:]}")
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ProviderUnavailable(f"Perseus write did not return JSON receipt: {exc}") from exc

    def _start_server(self) -> None:
        assert self._db and self._key and self._temp
        self._server_stderr = Path(self._temp.name) / "server.stderr.log"
        stderr = self._server_stderr.open("w", encoding="utf-8")
        self._server = subprocess.Popen(
            [str(self.binary), "serve", "--db", str(self._db), "--encryption-key", str(self._key)],
            text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, bufsize=1,
        )
        response = self._mcp("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "memory-bakeoff", "version": "generation-21"},
        })
        info = response.get("serverInfo", {})
        if info.get("version") != PINNED_VERSION:
            raise ProviderUnavailable(f"MCP server version mismatch: {info}")

    def _mcp(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._server or not self._server.stdin or not self._server.stdout:
            raise ProviderUnavailable("Perseus MCP server is not running")
        request_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self._server.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
        self._server.stdin.flush()
        line = self._server.stdout.readline()
        if not line:
            raise ProviderUnavailable("Perseus MCP server closed without a response")
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProviderUnavailable(f"Perseus MCP emitted non-JSON response: {line[:300]!r}") from exc
        self._operations.append({"kind": "mcp", "request": request, "response": response})
        if response.get("id") != request_id or "error" in response:
            raise ProviderUnavailable(f"Perseus MCP failure: {response}")
        return response["result"]

    @staticmethod
    def _structured(result: dict[str, Any]) -> dict[str, Any]:
        payload = result.get("structuredContent")
        if isinstance(payload, dict):
            return payload
        content = result.get("content", [])
        if len(content) == 1 and isinstance(content[0], dict) and isinstance(content[0].get("text"), str):
            return json.loads(content[0]["text"])
        raise ProviderUnavailable("Perseus MCP tool response lacks structuredContent")

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        if mode != "raw":
            raise ProviderUnavailable("Perseus Gen21 evaluates only the documented raw operator-seed write mode")
        probe = self.probe()
        if not probe.available:
            raise ProviderUnavailable(probe.reason)
        self.reset()
        self.remember_records(records)
        self._temp = tempfile.TemporaryDirectory(prefix="memory-bakeoff-perseus-", dir="/private/tmp")
        root = Path(self._temp.name)
        self._db, self._key = root / "vault.sqlite", root / "vault.key"
        keygen = subprocess.run([str(self.binary), "keygen", "--key-file", str(self._key)], text=True, capture_output=True, timeout=30)
        if keygen.returncode != 0:
            raise ProviderUnavailable(f"Perseus temporary keygen failed: {keygen.stderr[-500:]}")
        self._operations.append({"kind": "keygen", "stdout": keygen.stdout, "stderr": keygen.stderr, "returncode": keygen.returncode})
        for record in records:
            receipt = self._run_cli([
                str(self.binary), "write", "--db", str(self._db), "--encryption-key", str(self._key),
                "--category", CATEGORY, "--key", key_for_record(record.id),
                "--body", json.dumps(body_for_record(record), sort_keys=True, separators=(",", ":")),
                "--workspace-hash", workspace_for_scope(record.scope),
            ])
            native_id = receipt.get("id")
            if not receipt.get("ok") or not isinstance(native_id, str):
                raise ProviderUnavailable(f"Perseus write receipt lacks native ID for {record.id}: {receipt}")
            self._native_ids[native_id] = record.id
        self._start_server()

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        start = time.perf_counter()
        result = self._mcp("tools/call", {"name": "perseus_vault_recall", "arguments": {
            "query": case.query, "workspace_hash": workspace_for_scope(case.scope),
            "limit": top_k, "mode": "hybrid", "include_outcome": True,
        }})
        payload = self._structured(result)
        items: list[RetrievalItem] = []
        for hit in payload.get("items", [])[:top_k]:
            native_id, record_id = hit.get("id"), hit.get("canonical_record_id")
            if not isinstance(native_id, str) or self._native_ids.get(native_id) != record_id or record_id not in self._records:
                raise ProviderUnavailable("Perseus recall returned an item without an exact native ID → canonical record mapping")
            body = hit.get("body_json")
            try:
                body_id = json.loads(body).get("canonical_record_id")
            except (TypeError, json.JSONDecodeError):
                body_id = None
            if body_id != record_id:
                raise ProviderUnavailable("Perseus returned canonical marker does not match native body provenance")
            self._record_provenance("native")
            items.append(RetrievalItem(record_id, hit.get("assertion_text", self._records[record_id].text), None, {"perseus_entity_id": native_id, "key": hit.get("key"), "workspace_hash": hit.get("workspace_hash"), "outcome": payload.get("outcome")}))
        return RetrievalResult(items, (time.perf_counter() - start) * 1000, payload)

    def diagnostics(self) -> dict[str, Any]:
        if self._server and self._lifecycle_audit is None:
            stats = self._structured(self._mcp("tools/call", {"name": "perseus_vault_stats", "arguments": {}}))
            workspaces: dict[str, list[dict[str, Any]]] = {}
            for scope in sorted({record.scope for record in self._records.values()}):
                workspace = workspace_for_scope(scope)
                scan = self._structured(self._mcp("tools/call", {"name": "perseus_vault_scan", "arguments": {
                    "workspace_hash": workspace, "include_archived": True, "limit": 1000,
                }}))
                rows = scan.get("items", [])
                for row in rows:
                    native_id, record_id = row.get("id"), row.get("canonical_record_id")
                    if self._native_ids.get(native_id) != record_id:
                        raise ProviderUnavailable("Perseus lifecycle scan lacks an exact native ID → canonical record mapping")
                workspaces[scope] = rows
            states: dict[str, int] = {}
            for rows in workspaces.values():
                for row in rows:
                    state = str(row.get("status", "unknown"))
                    states[state] = states.get(state, 0) + 1
            self._lifecycle_audit = {"native_stats": stats, "scanned_workspaces": workspaces, "state_counts": states}
        return {"native_operation_count": len(self._operations), "native_operations": self._operations, "native_id_to_canonical_id": self._native_ids, "lifecycle_audit": self._lifecycle_audit}

    def close(self) -> None:
        if self._server:
            if self._server.stdin:
                self._server.stdin.close()
            try:
                self._server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._server.terminate()
                self._server.wait(timeout=10)
            self._server = None
        if self._temp:
            self._temp.cleanup()
            self._temp = None
        self._db = self._key = None
