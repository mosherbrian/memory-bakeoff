"""Gen37 engine harnesses: Perseus and Mem0 against the frozen MemConflict contract.

Mechanics only. Neither engine ever receives a scorer-only field, and neither is
asked anything the frozen contract does not define. Every returned item must map
through the write ledger; nothing is ever recovered from text.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PERSEUS_BIN = Path.home() / ".local/perseus-2.23.2/perseus-vault"
MEM0_CHECKOUT = ROOT / "external/mem0"


def sha256_dir(path: Path) -> str:
    """Digest of a store directory: names plus contents, order-independent."""
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(file.relative_to(path)).encode())
        digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()


def dir_size(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


@dataclass
class Timings:
    values: list[float] = field(default_factory=list)

    def add(self, ms: float) -> None:
        self.values.append(ms)

    def summary(self) -> dict[str, Any]:
        if not self.values:
            return {"count": 0}
        ordered = sorted(self.values)

        def percentile(p: float) -> float:
            index = min(len(ordered) - 1, int(round(p * (len(ordered) - 1))))
            return round(ordered[index], 3)

        total = sum(ordered)
        return {"count": len(ordered), "total_ms": round(total, 1),
                "p50_ms": percentile(0.50), "p90_ms": percentile(0.90),
                "p95_ms": percentile(0.95), "p99_ms": percentile(0.99),
                "max_ms": round(ordered[-1], 3),
                "per_second": round(len(ordered) / (total / 1000.0), 2) if total else None}


class PerseusEngine:
    """Ordinary CLI writes; queries run against a byte-for-byte vault snapshot."""

    name = "perseus"

    def __init__(self, persona_id: str, root: Path):
        from memory_bakeoff.providers import perseus_memconflict as A

        self.A = A
        self.persona_id = persona_id
        self.home = root / f"perseus-{persona_id}"
        self.home.mkdir(parents=True)
        self.db = self.home / "vault.sqlite"
        self.key = self.home / "vault.key"
        self.snapshot_root = root / f"perseus-snap-{persona_id}"
        self._sh([PERSEUS_BIN, "keygen", "--key-file", self.key])
        self.server = None
        self.ordinal = 0

    def _sh(self, args, timeout=180) -> str:
        done = subprocess.run([str(a) for a in args], text=True, capture_output=True, timeout=timeout)
        if done.returncode != 0:
            raise RuntimeError(f"perseus command failed ({done.returncode}): {args}\n{done.stderr[:400]}")
        return done.stdout

    def write(self, text: str) -> tuple[str, float]:
        self.ordinal += 1
        arguments = self.A.write_arguments(text, self.ordinal, self.persona_id)
        started = time.perf_counter()
        receipt = json.loads(self._sh([
            PERSEUS_BIN, "write", "--db", self.db, "--encryption-key", self.key,
            "--category", arguments["category"], "--key", arguments["key"],
            "--body", json.dumps(arguments["body"], sort_keys=True, separators=(",", ":")),
            "--workspace-hash", arguments["workspace_hash"]]))
        latency = (time.perf_counter() - started) * 1000
        native_id = receipt.get("id") or receipt.get("entity_id") or receipt.get("uuid")
        if not native_id:
            raise RuntimeError(f"perseus write receipt has no native id: {receipt}")
        return str(native_id), latency, str(receipt.get("action", "unknown"))

    def open_read_snapshot(self) -> None:
        """Fresh snapshot of the write-authoritative vault; reads never touch it."""
        self.close_read_snapshot()
        if self.snapshot_root.exists():
            shutil.rmtree(self.snapshot_root)
        self.snapshot_root.mkdir(parents=True)
        db = self.snapshot_root / "vault.sqlite"
        for suffix in ("", "-wal", "-shm"):
            source = Path(str(self.db) + suffix)
            if source.exists():
                shutil.copy2(source, str(db) + suffix)
        key = self.snapshot_root / "vault.key"
        shutil.copy2(self.key, key)
        self.server = _PerseusServer(db, key)

    def close_read_snapshot(self) -> None:
        if self.server is not None:
            self.server.stop()
            self.server = None

    def search(self, question_text: str) -> tuple[list[dict], float]:
        if self.server is None:
            raise RuntimeError("no read snapshot is open")
        arguments = self.A.recall_arguments(question_text, self.persona_id)
        started = time.perf_counter()
        payload = self.server.recall(arguments)
        latency = (time.perf_counter() - started) * 1000
        items = []
        for rank, hit in enumerate(payload[: self.A.LIMIT], start=1):
            items.append({"rank": rank, "native_id": str(hit.get("id") or hit.get("entity_id") or ""),
                          "score": hit.get("score")})
        return items, latency

    def inventory(self) -> dict[str, Any]:
        """Native stats only. Read-only, and it never touches entity state."""
        stats = json.loads(self._sh([PERSEUS_BIN, "stats", "--db", self.db]))
        keep = ("total_entities", "active_entities", "archived_entities", "by_category", "by_layer",
                "by_type", "by_category_active", "by_layer_active", "total_journal_events",
                "total_history_rows", "db_file_size_bytes")
        return {k: stats[k] for k in keep if k in stats}

    def state_digest(self) -> str:
        """Perseus own cheap digest of the recall-visible entity set."""
        return json.loads(self._sh([PERSEUS_BIN, "state-digest", "--db", self.db]))["digest"]

    def store_bytes(self) -> int:
        return dir_size(self.home)

    def store_digest(self) -> str:
        return sha256_dir(self.home)

    def close(self) -> None:
        self.close_read_snapshot()


class _PerseusServer:
    def __init__(self, db: Path, key: Path):
        self.proc = subprocess.Popen([str(PERSEUS_BIN), "serve", "--db", str(db), "--encryption-key", str(key)],
                                     text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, bufsize=1)
        self._id = 0
        info = self.rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                       "clientInfo": {"name": "memory-bakeoff", "version": "generation-37"}})
        version = (info.get("serverInfo") or {}).get("version")
        if version != "2.23.2":
            raise RuntimeError(f"perseus MCP server version drift: {info.get('serverInfo')}")

    def rpc(self, method: str, params: dict) -> dict:
        self._id += 1
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": self._id,
                                          "method": method, "params": params}) + "\n")
        self.proc.stdin.flush()
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("perseus serve closed the pipe")
            message = json.loads(line)
            if message.get("id") == self._id:
                if "error" in message:
                    raise RuntimeError(f"perseus rpc error: {message['error']}")
                return message.get("result") or {}

    def recall(self, arguments: dict) -> list[dict]:
        result = self.rpc("tools/call", {"name": "perseus_vault_recall", "arguments": arguments})
        payload = result.get("structuredContent")
        if not isinstance(payload, dict):
            content = result.get("content") or []
            if len(content) == 1 and isinstance(content[0].get("text"), str):
                payload = json.loads(content[0]["text"])
            else:
                raise RuntimeError("perseus recall response lacks structured content")
        hits = payload.get("items")
        if hits is None:
            raise RuntimeError(f"perseus recall payload has no items: {sorted(payload)}")
        return hits

    def stop(self) -> None:
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
            self.proc.wait(timeout=10)


class Mem0Engine:
    """Raw infer=False adds; native search. Gen32 measured reads side-effect-free."""

    name = "mem0"

    def __init__(self, persona_id: str, root: Path):
        import sys

        if str(MEM0_CHECKOUT) not in sys.path:
            sys.path.insert(0, str(MEM0_CHECKOUT))
        from mem0 import Memory
        from memory_bakeoff.providers import mem0_memconflict as A

        self.A = A
        self.persona_id = persona_id
        self.home = root / f"mem0-{persona_id}"
        self.home.mkdir(parents=True)
        collection = "mc-" + hashlib.sha256(persona_id.encode()).hexdigest()[:24]
        self.memory = Memory.from_config(
            A.config_for(str(self.home / "qdrant"), collection, str(self.home / "history.db")))

    def write(self, text: str) -> tuple[str, float]:
        arguments = self.A.add_arguments(text, self.persona_id)
        started = time.perf_counter()
        result = self.memory.add(arguments["text"], user_id=arguments["user_id"], infer=arguments["infer"])
        latency = (time.perf_counter() - started) * 1000
        rows = result.get("results") if isinstance(result, dict) else result
        ids = [row.get("id") for row in (rows or []) if isinstance(row, dict) and row.get("id")]
        if len(ids) != 1:
            raise RuntimeError(f"mem0 add returned {len(ids)} ids for one message: {result}")
        event = next((row.get("event") for row in rows if isinstance(row, dict)), "unknown")
        return str(ids[0]), latency, str(event)

    def open_read_snapshot(self) -> None:
        return None

    def close_read_snapshot(self) -> None:
        return None

    def search(self, question_text: str) -> tuple[list[dict], float]:
        arguments = self.A.search_arguments(question_text, self.persona_id)
        started = time.perf_counter()
        raw = self.memory.search(arguments["query"], filters=arguments["filters"],
                                 limit=arguments["limit"], threshold=arguments["threshold"])
        latency = (time.perf_counter() - started) * 1000
        hits = raw.get("results") if isinstance(raw, dict) else raw
        items = []
        for rank, hit in enumerate((hits or [])[: self.A.LIMIT], start=1):
            items.append({"rank": rank, "native_id": str(hit.get("id") or ""), "score": hit.get("score")})
        return items, latency

    def inventory(self) -> dict[str, Any]:
        import sqlite3

        stored = self.memory.get_all(filters={"user_id": self.A.user_id_for_persona(self.persona_id)},
                                     limit=1000000)
        rows = stored.get("results") if isinstance(stored, dict) else stored
        history = {}
        db = self.home / "history.db"
        if db.exists():
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            try:
                tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
                history = {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in tables}
            finally:
                con.close()
        return {"points": len(rows or []), "history": history}

    def store_bytes(self) -> int:
        return dir_size(self.home)

    def store_digest(self) -> str:
        return sha256_dir(self.home)

    def state_digest(self) -> str:
        return sha256_dir(self.home / "qdrant")

    def close(self) -> None:
        """Release the embedded Qdrant handles; one process may hold only one."""
        for attribute in ("vector_store", "_telemetry_vector_store"):
            store = getattr(self.memory, attribute, None)
            client = getattr(store, "client", None)
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass


ENGINES = {"perseus": PerseusEngine, "mem0": Mem0Engine}
