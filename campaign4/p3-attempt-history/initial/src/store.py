"""Durable authoritative SQLite event store + atomic derived snapshot.

One SQLite file is the authority. Terminal status and disposition commit in
the same transaction. The derived snapshot is published atomically (temp
file, flush, os.replace) only after commit. Restart reconstructs state from
the ledger; mismatched/missing snapshots never hide ledger packages and
never authorize execution.
"""
from __future__ import annotations

import json
import os
import sqlite3

from .lifecycle import apply, new_revision, TransitionError

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  question_id TEXT NOT NULL,
  revision INTEGER NOT NULL,
  type TEXT NOT NULL,
  actor_seat TEXT, actor_role TEXT,
  at TEXT NOT NULL,
  body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


class Store:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        # in-memory projection; rebuilt from ledger on open (restart-safe)
        self.revisions = {}  # (question_id, revision) -> lifecycle record
        self.seen_events = set()
        self.acks = {}       # action_id -> "acknowledged" | "intended"
        self._replay()

    def _replay(self):
        cur = self.conn.execute("SELECT value FROM meta WHERE key='acks'")
        row = cur.fetchone()
        if row:
            self.acks.update(json.loads(row[0]))
        cur = self.conn.execute(
            "SELECT event_id, question_id, revision, type, actor_seat,"
            " actor_role, at, body FROM events ORDER BY rowid")
        for eid, q, rev, typ, seat, role, at, body in cur.fetchall():
            self.seen_events.add(eid)
            payload = json.loads(body)
            event = {"event_id": eid, "type": typ,
                     "actor": {"seat": seat, "role": role}, "at": at}
            event.update(payload)
            key = (q, rev)
            if key not in self.revisions:
                rec = new_revision(q)
                rec["revision"] = rev
                self.revisions[key] = rec
            # replay must succeed; a stored event was valid at append time
            new_rec, _ = apply(self.revisions[key], event, at,
                               payload.get("_budget", _default_budget()))
            self.revisions[key] = new_rec
            aid = payload.get("action_id")
            if aid and payload.get("acknowledged"):
                self.acks[aid] = "acknowledged"
            elif aid:
                self.acks.setdefault(aid, "intended")

    def append(self, event, budget=None):
        """Validate + durably store one event. Idempotent on event_id.

        Returns (outcome, duplicate:bool). Duplicate delivery returns the
        original outcome without re-applying.
        """
        budget = budget or _default_budget()
        eid = event["event_id"]
        if eid in self.seen_events:
            return "duplicate-ignored", True
        q, rev = event["question_id"], event.get("revision", 1)
        key = (q, rev)
        base = self.revisions.get(key)
        if base is None:
            base = new_revision(q)
            base["revision"] = rev
        new_rec, outcome = apply(base, event, event["at"], budget)
        body = {k: v for k, v in event.items()
                if k not in ("event_id", "question_id", "revision", "type",
                             "actor", "at")}
        body["_budget"] = budget
        with self.conn:  # single transaction: event (+ terminal) atomic
            self.conn.execute(
                "INSERT INTO events (event_id, question_id, revision, type,"
                " actor_seat, actor_role, at, body) VALUES (?,?,?,?,?,?,?,?)",
                (eid, q, rev, event["type"],
                 event.get("actor", {}).get("seat"),
                 event.get("actor", {}).get("role"),
                 event["at"], json.dumps(body, sort_keys=True)))
        self.seen_events.add(eid)
        self.revisions[key] = new_rec
        aid = body.get("action_id")
        if aid:
            self.set_ack(aid, "acknowledged" if body.get("acknowledged")
                         else "intended")
        return outcome, False

    def record_terminal(self, verdict_event, decide_event, budget=None):
        """Commit terminal verdict + director disposition atomically.

        Both events validate first; both rows insert in ONE transaction.
        Either failure rolls back both (fail closed).
        """
        budget = budget or _default_budget()
        q, rev = verdict_event["question_id"], verdict_event.get("revision", 1)
        key = (q, rev)
        base = self.revisions.get(key)
        if base is None:
            base = new_revision(q)
            base["revision"] = rev
        rec1, out1 = apply(base, verdict_event, verdict_event["at"], budget)
        rec2, out2 = apply(rec1, decide_event, decide_event["at"], budget)
        with self.conn:
            for ev in (verdict_event, decide_event):
                if ev["event_id"] in self.seen_events:
                    raise TransitionError("E_DUP_EVENT", ev["event_id"])
                body = {k: v for k, v in ev.items()
                        if k not in ("event_id", "question_id", "revision",
                                     "type", "actor", "at")}
                body["_budget"] = budget
                self.conn.execute(
                    "INSERT INTO events (event_id, question_id, revision,"
                    " type, actor_seat, actor_role, at, body)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (ev["event_id"], q, rev, ev["type"],
                     ev.get("actor", {}).get("seat"),
                     ev.get("actor", {}).get("role"),
                     ev["at"], json.dumps(body, sort_keys=True)))
                self.seen_events.add(ev["event_id"])
        self.revisions[key] = rec2
        return out1, out2

    def set_ack(self, action_id, status):
        """Persist delivery state (acknowledged vs intended). Same transaction."""
        self.acks[action_id] = status
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('acks', ?)",
                (json.dumps(self.acks, sort_keys=True),))

    def ledger_view(self):
        """Authoritative inventory for the validator."""
        out = {}
        for (q, rev), rec in self.revisions.items():
            out.setdefault(q, {})[rev] = {
                "phase": rec["phase"],
                "attempt": rec["attempt"],
                "verdict": rec.get("verdict"),
                "disposition": rec.get("disposition"),
                "decision_task": rec.get("decision_task"),
                "blocked": rec.get("blocked"),
            }
        return out

    def ledger_revision(self):
        row = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0]

    def publish_snapshot(self, path, extra=None):
        """Atomic derived snapshot, only after commit. Returns snapshot dict."""
        snap = {"schema_version": 1,
                "ledger_revision": self.ledger_revision(),
                "terminal": {}, "in_flight": []}
        for q, revs in self.ledger_view().items():
            for rev, r in revs.items():
                pid = "%s-r%d" % (q, rev)
                if r["phase"] in ("COMPLETE", "EXHAUSTED", "TERMINATED",
                                  "SUPERSEDED"):
                    entry = {"state": r["phase"]}
                    if r["disposition"] is not None:
                        d = r["disposition"]
                        entry["disposition"] = d
                        entry["decided_by"] = "tern"
                        entry["decision_ref"] = d.get("decision_ref", "")
                        entry["reason"] = d.get("reason", "")
                    snap["terminal"][pid] = entry
                else:
                    snap["in_flight"].append({"package_id": pid,
                                             "phase": r["phase"]})
        if extra:
            snap.update(extra)
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(snap, fh, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        return snap

    def close(self):
        self.conn.close()


def _default_budget():
    return {"attempts": 1, "repairs": 1, "verifier_s": 1800}
