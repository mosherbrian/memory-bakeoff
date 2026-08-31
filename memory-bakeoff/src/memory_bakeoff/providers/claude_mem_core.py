from __future__ import annotations

import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Sequence

import numpy as np

from memory_bakeoff.models import (
    MemoryRecord,
    ProviderCapabilities,
    ProviderProbe,
    QueryCase,
    RetrievalItem,
    RetrievalResult,
)
from memory_bakeoff.providers.base import MemoryProvider, ProviderUnavailable
from memory_bakeoff.providers.membukkit_test_doubles import SharedLSAEncoder


# Current Claude-Mem source constant at pinned commit fa6a1e9e... .
# Keep the clock explicit so the 90-day policy is reproducible instead of
# silently drifting every time this benchmark is rerun months later.
DEFAULT_EVAL_NOW = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)
RECENCY_WINDOW_DAYS = 90
CHROMA_BATCH_SIZE = 100


def _eval_now() -> datetime:
    raw = os.getenv("CLAUDE_MEM_EVAL_NOW")
    if not raw:
        return DEFAULT_EVAL_NOW
    text = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class ClaudeMemFTS5CoreProvider(MemoryProvider):
    """Controlled Claude-Mem SQLite FTS5 search arm.

    This executes the key current SessionSearch semantics using Python's SQLite
    FTS5 engine: observations_fts MATCH an escaped *quoted phrase*, relevance by
    FTS5 rank, optional end-date cutoff for harness as-of cases.

    Raw benchmark records are injected into the observation `text` field. This
    is NOT Claude-Mem's product compression pipeline and is intentionally named
    as a core/search ablation.
    """

    name = "claude_mem_fts5_core"
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        supports_as_of=True,
        service_required=False,
        notes=(
            "Pinned Claude-Mem SessionSearch FTS5 query semantics over synthetic "
            "raw observation text; quoted-phrase MATCH; product compression not run."
        ),
    )

    def __init__(self):
        super().__init__()
        self.db: sqlite3.Connection | None = None

    def probe(self) -> ProviderProbe:
        try:
            db = sqlite3.connect(":memory:")
            db.execute("CREATE VIRTUAL TABLE _probe USING fts5(x)")
            db.close()
            return ProviderProbe(self.name, True, "Python SQLite FTS5 available", self.capabilities)
        except Exception as e:
            return ProviderProbe(self.name, False, f"SQLite FTS5 unavailable: {e}", self.capabilities)

    def reset(self) -> None:
        self._records.clear()
        if self.db is not None:
            try:
                self.db.close()
            except Exception:
                pass
        self.db = None

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        if mode != "raw":
            raise ProviderUnavailable("claude_mem_fts5_core is controlled raw/core-only")
        self.reset()
        self.remember_records(records)
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.executescript(
            """
            CREATE TABLE observations(
              rowid INTEGER PRIMARY KEY,
              record_id TEXT UNIQUE NOT NULL,
              title TEXT,
              subtitle TEXT,
              narrative TEXT,
              text TEXT,
              facts TEXT,
              concepts TEXT,
              created_at_epoch INTEGER NOT NULL
            );
            CREATE VIRTUAL TABLE observations_fts USING fts5(
              title, subtitle, narrative, text, facts, concepts,
              content='observations', content_rowid='rowid'
            );
            CREATE TRIGGER observations_ai AFTER INSERT ON observations BEGIN
              INSERT INTO observations_fts(rowid,title,subtitle,narrative,text,facts,concepts)
              VALUES(new.rowid,new.title,new.subtitle,new.narrative,new.text,new.facts,new.concepts);
            END;
            """
        )
        for i, r in enumerate(records, start=1):
            db.execute(
                "INSERT INTO observations(rowid,record_id,title,subtitle,narrative,text,facts,concepts,created_at_epoch) VALUES(?,?,?,?,?,?,?,?,?)",
                (i, r.id, "", "", "", r.text, "", "", int(r.timestamp.timestamp() * 1000)),
            )
        db.commit()
        self.db = db

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        if self.db is None:
            raise ProviderUnavailable("claude_mem_fts5_core not ingested")
        t0 = time.perf_counter()
        # Mirrors SessionSearch: '"' + query.replace(/"/g, '""') + '"'
        escaped = '"' + case.query.replace('"', '""') + '"'
        sql = """
          SELECT o.record_id,o.text,observations_fts.rank AS rank,o.created_at_epoch
          FROM observations o
          JOIN observations_fts ON observations_fts.rowid=o.rowid
          WHERE observations_fts MATCH ?
        """
        params: list[object] = [escaped]
        if case.as_of is not None:
            sql += " AND o.created_at_epoch <= ?"
            params.append(int(case.as_of.timestamp() * 1000))
        sql += " ORDER BY observations_fts.rank ASC LIMIT ?"
        params.append(top_k)
        try:
            rows = self.db.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            raise ProviderUnavailable(f"Claude-Mem FTS5 query failed: {e}") from e
        items = [
            RetrievalItem(
                row["record_id"],
                row["text"],
                -float(row["rank"]),  # higher-is-better convention for harness metadata
                {"fts_rank": float(row["rank"]), "quoted_phrase": True},
            )
            for row in rows
        ]
        return RetrievalResult(
            items,
            (time.perf_counter() - t0) * 1000,
            {"strategy": "sqlite_fts5", "quoted_phrase": True, "as_of_mapped_to_date_end": case.as_of is not None},
        )


class ClaudeMemChromaLSAProvider(MemoryProvider):
    """Controlled current Claude-Mem Chroma search policy with shared LSA vectors.

    The external semantic model/database is held constant using the benchmark's
    LSA representation; Claude-Mem policy is preserved: top-100 semantic
    candidates, default 90-day recency filter unless an explicit date range is
    supplied, and observation hydration in semantic relevance order.
    """

    name = "claude_mem_chroma_lsa"
    apply_default_recency = True
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        supports_as_of=True,
        service_required=False,
        notes=(
            "Pinned Claude-Mem Chroma search policy with shared LSA semantic ranking; "
            "top-100 then default 90-day recency filter; product compression/Chroma model not run."
        ),
    )

    def __init__(self):
        super().__init__()
        self.encoder: SharedLSAEncoder | None = None
        self.docs: list[MemoryRecord] = []
        self.matrix: np.ndarray | None = None
        self.eval_now = _eval_now()

    def probe(self) -> ProviderProbe:
        return ProviderProbe(self.name, True, "controlled Claude-Mem semantic policy ready", self.capabilities)

    def reset(self) -> None:
        self._records.clear()
        self.encoder = None
        self.docs = []
        self.matrix = None
        self.eval_now = _eval_now()

    def ingest(self, records: Sequence[MemoryRecord], mode: str = "raw") -> None:
        if mode != "raw":
            raise ProviderUnavailable(f"{self.name} is controlled raw/core-only")
        self.reset()
        self.remember_records(records)
        self.docs = list(records)
        self.encoder = SharedLSAEncoder([r.text for r in self.docs])
        self.matrix = self.encoder.encode([r.text for r in self.docs], normalize=True)

    def retrieve(self, case: QueryCase, top_k: int = 5) -> RetrievalResult:
        if self.encoder is None or self.matrix is None:
            raise ProviderUnavailable(f"{self.name} not ingested")
        t0 = time.perf_counter()
        q = self.encoder.encode(case.query, normalize=True)
        scores = np.asarray(self.matrix @ q, dtype=float)
        # Chroma query is capped at SEARCH_CONSTANTS.CHROMA_BATCH_SIZE = 100.
        semantic_order = list(np.argsort(scores)[::-1][: min(CHROMA_BATCH_SIZE, len(self.docs))])

        if case.as_of is not None:
            # Harness as-of is mapped to the API's explicit dateRange.end. In
            # current Claude-Mem, presence of any dateRange suppresses the
            # implicit 90-day start cutoff.
            start = None
            end = case.as_of
            policy = "explicit_date_end"
        elif self.apply_default_recency:
            start = self.eval_now - timedelta(days=RECENCY_WINDOW_DAYS)
            end = None
            policy = "default_90d"
        else:
            start = None
            end = None
            policy = "recency_disabled_ablation"

        kept: list[int] = []
        for idx in semantic_order:
            r = self.docs[idx]
            if start is not None and r.timestamp < start:
                continue
            if end is not None and r.timestamp > end:
                continue
            kept.append(idx)
            if len(kept) >= top_k:
                break

        items = [
            RetrievalItem(
                self.docs[i].id,
                self.docs[i].text,
                float(scores[i]),
                {
                    "timestamp": self.docs[i].timestamp.isoformat(),
                    "semantic_rank": semantic_order.index(i) + 1,
                    "recency_policy": policy,
                },
            )
            for i in kept
        ]
        cutoff = start.isoformat() if start is not None else None
        return RetrievalResult(
            items,
            (time.perf_counter() - t0) * 1000,
            {
                "strategy": "chroma_policy_shared_lsa",
                "semantic_batch_size": min(CHROMA_BATCH_SIZE, len(self.docs)),
                "recency_policy": policy,
                "eval_now": self.eval_now.isoformat(),
                "cutoff": cutoff,
                "semantic_candidates_before_recency": len(semantic_order),
                "returned_after_recency": len(items),
            },
        )


class ClaudeMemChromaLSANoRecencyProvider(ClaudeMemChromaLSAProvider):
    name = "claude_mem_chroma_lsa_no_recency"
    apply_default_recency = False
    capabilities = ProviderCapabilities(
        raw_ingest=True,
        product_ingest=False,
        supports_as_of=True,
        service_required=False,
        notes=(
            "Ablation: same pinned Claude-Mem Chroma top-100/relevance policy and shared LSA "
            "ranking, but implicit 90-day recency filter disabled."
        ),
    )
