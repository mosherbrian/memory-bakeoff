"""Read-only pi-lcm store-reader adapter (portfolio rows 1-2, locked baseline arm).

Ports ``extensions/pi-project-recall``'s store queries exactly — the FTS5
sanitize rule, FTS5 MATCH with the LIKE fallback, recency ordering
(``timestamp DESC, seq DESC``), no relevance scores — minus the
current-conversation filter that confines pi-lcm's own search to the live
conversation. Two modes:

- **corpus mode** (default, ``pi_lcm_store_reader``): ``ingest`` materializes
  the prepared conflict corpus into a fresh temporary store in the exact
  pi-lcm schema (per ``extensions/pi-project-recall/test/pilot_store.ts``,
  which mirrors pi-lcm ``src/db/schema.ts``) and the ported reader queries run
  over it. Experiment class: ``controlled_core``.
- **attach mode** (``pi_lcm_store_reader_attach``): ``ingest`` is a no-op
  attach of an EXISTING store, opened strictly read-only at the driver level.
  Retrieved content is real session text, so canonical record IDs are
  unmappable and items carry ``record_id=None``. Experiment class:
  ``raw_product``.

The tool-level query relaxation in ``runRecall`` is deliberately NOT ported:
it lives above the store queries, and this adapter is the raw store-reader
path (charter row 2's A/B is exactly tool-level vs raw store). Canonical
record identity in corpus mode flows through adapter bookkeeping keyed by
message rowid — the retrieval decision itself is made only by the ported
queries over ``content_text``.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

from memory_bakeoff.models import (
    MemoryRecord,
    ProviderCapabilities,
    ProviderProbe,
    QueryCase,
    RetrievalItem,
    RetrievalResult,
)
from memory_bakeoff.providers.base import MemoryProvider, ProviderUnavailable

# DDL mirrors pi-lcm src/db/schema.ts via pilot_store.ts (base tables first;
# the FTS5 table and its sync triggers are created separately so a host
# without FTS5 still materializes a valid store and queries take the same
# LIKE fallback path the extension takes on FTS5 errors).
BASE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
  id            TEXT PRIMARY KEY,
  session_id    TEXT NOT NULL UNIQUE,
  session_file  TEXT,
  cwd           TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
  id             TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  entry_id       TEXT,
  role           TEXT NOT NULL,
  content_text   TEXT NOT NULL,
  content_json   TEXT NOT NULL,
  tool_name      TEXT,
  token_estimate INTEGER NOT NULL,
  timestamp      INTEGER NOT NULL,
  seq            INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS summaries (
  id              TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  depth           INTEGER NOT NULL,
  text            TEXT NOT NULL,
  token_estimate  INTEGER NOT NULL,
  metadata_json   TEXT,
  created_at      TEXT NOT NULL
);
"""

FTS_SCHEMA_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
  content_text,
  content='messages',
  content_rowid='rowid'
);
CREATE TRIGGER IF NOT EXISTS messages_fts_ai AFTER INSERT ON messages BEGIN
  INSERT INTO messages_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
END;
CREATE TRIGGER IF NOT EXISTS messages_fts_ad AFTER DELETE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, content_text)
    VALUES ('delete', old.rowid, old.content_text);
END;
CREATE TRIGGER IF NOT EXISTS messages_fts_au AFTER UPDATE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, content_text)
    VALUES ('delete', old.rowid, old.content_text);
  INSERT INTO messages_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
END;
"""

# Same driver probe the extension does, expressed for the sqlite3 module.
def fts5_supported() -> bool:
    try:
        con = sqlite3.connect(":memory:")
        try:
            con.execute("CREATE VIRTUAL TABLE fts5_probe USING fts5(x)")
            return True
        finally:
            con.close()
    except sqlite3.Error:
        return False


def sanitize_fts_query(query: str) -> str:
    """Verbatim behaviour of pi-lcm's sanitizeFtsQuery (via the extension)."""
    return " ".join(
        f'"{token.replace(chr(34), chr(34) * 2)}"'
        for token in re.split(r"\s+", query)
        if token
    )


def hash_cwd(cwd: str) -> str:
    """sha256(cwd) truncated to 16 hex chars - pi-lcm's per-project DB filename."""
    return hashlib.sha256(cwd.encode("utf-8")).hexdigest()[:16]


def resolve_db_dir() -> Path:
    """Same precedence pi-lcm uses: LCM_DB_DIR, else lcm.dbDir in the agent
    settings.json, else <agentDir>/lcm where agentDir is PI_CODING_AGENT_DIR
    else ~/.pi/agent. Rejects '..' in an explicit dbDir (extension fix-14)."""
    import os

    agent_dir = Path(os.environ.get("PI_CODING_AGENT_DIR") or Path.home() / ".pi" / "agent")
    dir_raw = os.environ.get("LCM_DB_DIR")
    if not dir_raw:
        try:
            settings = json.loads((agent_dir / "settings.json").read_text(encoding="utf-8"))
            candidate = settings.get("lcm", {}).get("dbDir")
            if isinstance(candidate, str) and candidate:
                dir_raw = candidate
        except (OSError, json.JSONDecodeError):
            pass
    if not dir_raw:
        dir_raw = str(agent_dir / "lcm")
    resolved = Path(dir_raw).resolve()
    if ".." in resolved.parts:
        raise ProviderUnavailable(f"pi-lcm store reader: dbDir must not contain '..': {dir_raw}")
    return resolved


def store_path_for_cwd(cwd: str) -> Path:
    return resolve_db_dir() / f"{hash_cwd(cwd)}.db"


def epoch_ms(ts: datetime) -> int:
    return int(round(ts.timestamp() * 1000))


def iso(ts: Any) -> str:
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).isoformat()
    return str(ts)


def snippet_for(text: str, query: str, max_len: int = 280) -> str:
    """Truncate around the first query term occurrence, else the head."""
    if not text:
        return ""
    tokens = [t for t in re.split(r"\s+", query) if t]
    first_term = tokens[0] if tokens else ""
    at = text.lower().find(first_term.lower()) if first_term else -1
    start = at - 40 if at > 40 else 0
    cut = re.sub(r"\s+", " ", text[start:start + max_len]).strip()
    return ("…" if start > 0 else "") + cut + ("…" if start + max_len < len(text) else "")


def _ts_filter(after_ms: int | None, before_ms: int | None) -> tuple[str, list[int]]:
    params: list[int] = []
    clause = ""
    if after_ms is not None:
        clause += " AND m.timestamp >= ?"
        params.append(after_ms)
    if before_ms is not None:
        clause += " AND m.timestamp <= ?"
        params.append(before_ms)
    return clause, params


def _connect_read_only(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path))}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def query_messages(
    db: sqlite3.Connection,
    query: str,
    limit: int,
    after_ms: int | None = None,
    before_ms: int | None = None,
) -> list[dict[str, Any]]:
    sanitized = sanitize_fts_query(query)
    if not sanitized:
        return []
    clause, params = _ts_filter(after_ms, before_ms)

    # NOTE: no conversation_id filter - the entire point of the adapter.
    # m.rowid is selected for adapter bookkeeping only (canonical mapping);
    # it does not participate in matching or ordering.
    match_sql = (
        "SELECT m.rowid AS message_rowid, m.role, m.content_text, m.timestamp,"
        " c.id AS conversation_id, c.session_id, c.created_at AS session_start"
        " FROM messages m"
        " JOIN messages_fts fts ON m.rowid = fts.rowid"
        " JOIN conversations c ON c.id = m.conversation_id"
        f" WHERE fts.messages_fts MATCH ?{clause}"
        " ORDER BY m.timestamp DESC, m.seq DESC LIMIT ?"
    )
    try:
        rows = db.execute(match_sql, (sanitized, *params, limit)).fetchall()
    except sqlite3.OperationalError:
        # FTS5 unavailable or errored: fall back to LIKE, as the extension does.
        escaped = (
            query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        like_sql = (
            "SELECT m.rowid AS message_rowid, m.role, m.content_text, m.timestamp,"
            " c.id AS conversation_id, c.session_id, c.created_at AS session_start"
            " FROM messages m"
            " JOIN conversations c ON c.id = m.conversation_id"
            " WHERE m.content_text LIKE ? ESCAPE '\\'"
            f"{clause}"
            " ORDER BY m.timestamp DESC, m.seq DESC LIMIT ?"
        )
        rows = db.execute(like_sql, (f"%{escaped}%", *params, limit)).fetchall()
    return [
        {
            "source": "messages",
            "message_rowid": r[0],
            "conversation_id": r[4],
            "session_id": r[5],
            "session_start": iso(r[6]),
            "timestamp": iso(r[3]),
            "role": r[1],
            "snippet": snippet_for(r[2] or "", query),
        }
        for r in rows
    ]


def query_summaries(db: sqlite3.Connection, query: str, limit: int) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []
    escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    sql = (
        "SELECT s.text, s.created_at, c.id AS conversation_id,"
        " c.session_id, c.created_at AS session_start"
        " FROM summaries s"
        " JOIN conversations c ON c.id = s.conversation_id"
        " WHERE s.text LIKE ? ESCAPE '\\'"
        " ORDER BY s.created_at DESC LIMIT ?"
    )
    rows = db.execute(sql, (f"%{escaped}%", limit)).fetchall()
    return [
        {
            "source": "summaries",
            "conversation_id": r[2],
            "session_id": r[3],
            "session_start": iso(r[4]),
            "timestamp": iso(r[1]),
            "role": "summary",
            "snippet": snippet_for(r[0] or "", query),
        }
        for r in rows
    ]


class PiLcmStoreReaderProvider(MemoryProvider):
    """Corpus mode: materialize the corpus into a fresh pi-lcm-schema store
    and run the ported reader queries over it (no conversation filter)."""

    name = "pi_lcm_store_reader"
    raw_experiment_class = "controlled_core"
    product_experiment_class = "controlled_core"
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        supports_as_of=True,
        service_required=False,
        notes=(
            "pi-lcm store-reader port of extensions/pi-project-recall (FTS5 + "
            "LIKE fallback, recency order, no scores) minus the conversation "
            "filter; corpus materialized into a fresh temporary store in the "
            "exact pi-lcm schema. Tool-level relaxation is not ported."
        ),
    )

    def __init__(self, store_path: str | Path | None = None, allow_fts: bool = True) -> None:
        super().__init__()
        self.attach = store_path is not None
        if self.attach:
            self.name = "pi_lcm_store_reader_attach"
            self.raw_experiment_class = "raw_product"
            self.product_experiment_class = "raw_product"
        self.store_path = Path(store_path) if store_path is not None else None
        self.allow_fts = allow_fts
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self._db: sqlite3.Connection | None = None
        self._fts_active = False
        self._rowid_to_record: dict[int, str] = {}
        self._ignored_records = 0
        self._store_used: Path | None = None

    # ── lifecycle ──────────────────────────────────────────────────────────

    def probe(self) -> ProviderProbe:
        if self.attach:
            if self.store_path is None or not self.store_path.is_file():
                return ProviderProbe(
                    self.name, False,
                    f"no pi-lcm store at {self.store_path}; set PI_LCM_STORE_PATH or check the project dbDir",
                    self.capabilities,
                )
            return ProviderProbe(self.name, True, f"read-only attach of {self.store_path}", self.capabilities)
        mode = "FTS5 native" if (self.allow_fts and fts5_supported()) else "LIKE fallback (FTS5 unavailable or disabled)"
        return ProviderProbe(self.name, True, f"sqlite {sqlite3.sqlite_version}, corpus materialization, {mode}", self.capabilities)

    def reset(self) -> None:
        self.close()
        self._records.clear()
        self._rowid_to_record.clear()
        self._ignored_records = 0
        self._fts_active = False
        self._store_used = None

    def close(self) -> None:
        if self._db is not None:
            try:
                self._db.close()
            except sqlite3.Error:
                pass
            self._db = None
        if self._temp is not None:
            self._temp.cleanup()
            self._temp = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    # ── ingest ─────────────────────────────────────────────────────────────

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        if mode != "raw":
            raise ProviderUnavailable("pi-lcm store reader evaluates only the raw read path")
        if self.attach:
            self._ingest_attach(records)
        else:
            self._ingest_corpus(records)

    def _ingest_attach(self, records: Sequence[MemoryRecord]) -> None:
        self.close()
        if self.store_path is None or not self.store_path.is_file():
            raise ProviderUnavailable(f"attach mode: no pi-lcm store at {self.store_path}")
        db = _connect_read_only(self.store_path)
        try:
            names = {
                row[0]
                for row in db.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
            }
        except sqlite3.Error as exc:
            db.close()
            raise ProviderUnavailable(
                f"attach mode: {self.store_path} is not a valid sqlite/pi-lcm store ({exc})"
            ) from exc
        missing = {"conversations", "messages"} - names
        if missing:
            db.close()
            raise ProviderUnavailable(
                f"attach mode: {self.store_path} is not a pi-lcm store (missing {sorted(missing)})"
            )
        self._db = db
        self._fts_active = "messages_fts" in names
        self._store_used = self.store_path
        # Corpus records are intentionally NOT ingested: this arm reads the
        # existing store exactly as the product left it.
        self._ignored_records = len(records)

    def _ingest_corpus(self, records: Sequence[MemoryRecord]) -> None:
        self.close()
        self._rowid_to_record.clear()
        self._temp = tempfile.TemporaryDirectory(prefix="memory-bakeoff-pilcm-")
        path = Path(self._temp.name) / "lcm.db"
        con = sqlite3.connect(path)
        con.executescript(BASE_SCHEMA_SQL)
        if self.allow_fts and fts5_supported():
            con.executescript(FTS_SCHEMA_SQL)
            self._fts_active = True
        else:
            self._fts_active = False

        sessions: dict[str, list[MemoryRecord]] = {}
        for record in records:
            sessions.setdefault(record.session_id, []).append(record)

        cwd = "memory-bakeoff-materialized"
        for session_id, recs in sessions.items():
            recs_sorted = sorted(recs, key=lambda r: (r.timestamp, r.id))
            conv_id = "conv-" + hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:16]
            stamps = [epoch_ms(r.timestamp) for r in recs_sorted]
            con.execute(
                "INSERT INTO conversations (id, session_id, session_file, cwd, created_at, updated_at)"
                " VALUES (?, ?, NULL, ?, ?, ?)",
                (conv_id, session_id, cwd, iso(min(stamps)), iso(max(stamps))),
            )
            for seq, record in enumerate(recs_sorted):
                role = str(record.metadata.get("role", "user"))
                cur = con.execute(
                    "INSERT INTO messages (id, conversation_id, entry_id, role, content_text,"
                    " content_json, tool_name, token_estimate, timestamp, seq)"
                    " VALUES (?, ?, NULL, ?, ?, ?, NULL, ?, ?, ?)",
                    (
                        f"{conv_id}-m{seq}",
                        conv_id,
                        role,
                        record.text,
                        json.dumps({"role": role, "content": record.text}),
                        math.ceil(len(record.text) / 3.5),
                        epoch_ms(record.timestamp),
                        seq,
                    ),
                )
                self._rowid_to_record[cur.lastrowid] = record.id
        con.commit()
        con.close()
        # Reopen strictly read-only so the retrieval path matches the
        # extension's driver-level readOnly guarantee.
        self._db = _connect_read_only(path)
        self._store_used = path
        self.remember_records(records)

    # ── retrieve ───────────────────────────────────────────────────────────

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        if self._db is None:
            raise ProviderUnavailable("pi-lcm store reader has no store attached; call ingest first")
        start = time.perf_counter()
        before_ms = epoch_ms(case.as_of) if case.as_of is not None else None
        m_hits = query_messages(self._db, case.query, top_k, None, before_ms)
        s_hits = query_summaries(self._db, case.query, top_k)
        hits = (m_hits + s_hits)[:top_k]
        items: list[RetrievalItem] = []
        for hit in hits:
            record_id: str | None = None
            if not self.attach:
                record_id = self._rowid_to_record.get(hit.get("message_rowid", -1))
                if record_id is not None:
                    self._record_provenance("native")
            else:
                self._record_provenance("unmapped")
            items.append(
                RetrievalItem(
                    record_id=record_id,
                    text=hit["snippet"],
                    score=None,  # reader orders by recency; no scores exist to report
                    metadata={
                        "source": hit["source"],
                        "conversation_id": hit["conversation_id"],
                        "session_id": hit["session_id"],
                        "session_start": hit["session_start"],
                        "timestamp": hit["timestamp"],
                        "role": hit["role"],
                    },
                )
            )
        raw = {
            "reader": "extensions/pi-project-recall port (no conversation filter, no tool-level relaxation)",
            "mode": "attach_existing_store" if self.attach else "corpus_materialized",
            "store_path": str(self._store_used) if self._store_used else None,
            "fts_active": self._fts_active,
            "message_hits": len(m_hits),
            "summary_hits": len(s_hits),
            "corpus_records_ignored": self._ignored_records if self.attach else 0,
        }
        return RetrievalResult(items, (time.perf_counter() - start) * 1000.0, raw)

    # ── honesty surfaces ───────────────────────────────────────────────────

    def configuration(self) -> dict[str, Any]:
        if self.attach:
            if self._db is None:
                fts_label = "unknown - store not attached yet"
            else:
                fts_label = "native" if self._fts_active else "LIKE fallback (FTS5 table absent in attached store)"
        else:
            fts_label = (
                "native" if (self.allow_fts and fts5_supported())
                else "LIKE fallback (FTS5 unavailable or disabled)"
            )
        return {
            "reader_port": "extensions/pi-project-recall queryMessages/querySummaries minus the current-conversation filter",
            "schema_lineage": "extensions/pi-project-recall/test/pilot_store.ts (mirrors pi-lcm src/db/schema.ts)",
            "mode": "attach_existing_store" if self.attach else "corpus_materialized",
            "store_path": str(self.store_path) if self.store_path else None,
            "fts5": fts_label,
            "scores": "none - the reader orders by m.timestamp DESC, m.seq DESC (recency); FTS5 rank is not consulted",
            "relaxation": "not ported - tool-level runRecall behavior above the raw store queries (charter row 2 A/B)",
            "conversation_mapping": "one conversation per distinct record.session_id; canonical identity kept in adapter bookkeeping keyed by message rowid",
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "fts_active": self._fts_active,
            "store_path": str(self._store_used) if self._store_used else None,
            "corpus_records_ignored": self._ignored_records,
            "canonical_map_size": len(self._rowid_to_record),
        }


class PiLcmStoreReaderAttachProvider(PiLcmStoreReaderProvider):
    """Attach-mode convenience for the harness registry: resolves the store
    from PI_LCM_STORE_PATH, else from the pi-lcm path rules for the current
    working directory. Fails closed when no store exists."""

    def __init__(self) -> None:
        import os

        env = os.environ.get("PI_LCM_STORE_PATH")
        path = Path(env).expanduser() if env else store_path_for_cwd(os.getcwd())
        super().__init__(store_path=path)
