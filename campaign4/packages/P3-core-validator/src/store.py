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

TERMINAL_MAKERS = ("verify_pass", "verify_fail", "withhold", "terminate",
                   "exhaust", "amend")

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

    def append(self, event, budget=None, atomic=None):
        """Validate + durably store one event. Idempotent on event_id.

        D4 atomic rule: an event that would commit a terminal verdict with
        no disposition is rejected (E_MISSING_DISPOSITION) unless ``atomic``
        closes or holds it in the same transaction:
        ``{"decide": decide_event}`` or ``{"hold": deadline_iso}``.
        Returns (outcome, duplicate:bool).
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
        extra_rows = []
        if new_rec["phase"] in ("COMPLETE", "EXHAUSTED", "TERMINATED",
                                "SUPERSEDED") and \
                event["type"] in TERMINAL_MAKERS and \
                new_rec.get("disposition") is None:
            # Atomic terminal-boundary rule: bare terminal commits are
            # rejected. Close it or hold it in this same transaction.
            if atomic is None:
                raise TransitionError(
                    "E_MISSING_DISPOSITION",
                    "terminal verdict needs a same-transaction disposition "
                    "(use close) or bounded hold (row 17)")
            if "decide" in atomic:
                dec = atomic["decide"]
                new_rec, outcome2 = apply(new_rec, dec, dec["at"], budget)
                outcome = (outcome, outcome2)
                extra_rows.append(dec)
            elif "hold" in atomic:
                hold = {"event_id": eid + "-hold", "type": "decision_task",
                        "actor": {"seat": "cairn", "role": "duty"},
                        "at": event["at"], "deadline": atomic["hold"]}
                new_rec, outcome2 = apply(new_rec, hold, event["at"], budget)
                outcome = (outcome, outcome2)
                extra_rows.append(hold)
            else:
                raise TransitionError("E_MISSING_DISPOSITION",
                                      "atomic must be decide or hold")
        body = {k: v for k, v in event.items()
                if k not in ("event_id", "question_id", "revision", "type",
                             "actor", "at")}
        body["_budget"] = budget
        with self.conn:  # single transaction: event (+ terminal) atomic
            self._insert(eid, q, rev, event, body)
            for extra in extra_rows:
                xbody = {k: v for k, v in extra.items()
                         if k not in ("event_id", "question_id", "revision",
                                      "type", "actor", "at")}
                xbody["_budget"] = budget
                self._insert(extra["event_id"], q, rev, extra, xbody)
                self.seen_events.add(extra["event_id"])
        self.seen_events.add(eid)
        self.revisions[key] = new_rec
        # In-flight identity is set by the pure core (START/PUBLISH); the
        # store only persists acknowledgement state distinctly.
        aid = body.get("action_id")
        if aid:
            self.set_ack(aid, "acknowledged" if body.get("acknowledged")
                         else "intended")
        # Verifier-flight acknowledgement is recorded distinctly from the
        # worker dispatch ack: only an explicit verify_acknowledged flag
        # marks it; otherwise it stays intended (dispatched, not yet acked).
        fl = (new_rec.get("flight") or {})
        if event["type"] == "publish" and fl.get("action_id"):
            self.set_ack(fl["action_id"],
                         "acknowledged"
                         if event.get("verify_acknowledged") else "intended")
        return outcome, False

    def _insert(self, eid, q, rev, event, body):
        self.conn.execute(
            "INSERT INTO events (event_id, question_id, revision, type,"
            " actor_seat, actor_role, at, body) VALUES (?,?,?,?,?,?,?,?)",
            (eid, q, rev, event["type"],
             event.get("actor", {}).get("seat"),
             event.get("actor", {}).get("role"),
             event["at"], json.dumps(body, sort_keys=True)))

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
        if rec2.get("disposition") is None:
            raise TransitionError("E_MISSING_DISPOSITION",
                                  "record_terminal needs a decide event")
        with self.conn:
            for ev in (verdict_event, decide_event):
                if ev["event_id"] in self.seen_events:
                    raise TransitionError("E_DUP_EVENT", ev["event_id"])
                body = {k: v for k, v in ev.items()
                        if k not in ("event_id", "question_id", "revision",
                                     "type", "actor", "at")}
                body["_budget"] = budget
                self._insert(ev["event_id"], q, rev, ev, body)
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
                "flight": rec.get("flight"),
                "handoff": rec.get("handoff"),
            }
        return out

    def ledger_revision(self):
        row = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()
        return row[0]

    def publish_snapshot(self, path, extra=None):
        """Atomic derived snapshot, only after commit. Returns snapshot dict.

        D2: in-flight entries carry the full action identity
        (action_id, owner, deadline, dispatch_receipt) required by
        boundary-schema.md, so overdue in-flight work is detectable.
        Row-17 held terminals (verdict without disposition but with an open
        bounded director-decision task) are marked "held" and the task is
        carried as a DECISION in-flight entry.
        """
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
                    else:
                        task = r.get("decision_task")
                        if task is not None:
                            entry["held"] = True
                            snap["in_flight"].append({
                                "package_id": pid, "phase": "DECISION",
                                "action_id": task["task_id"], "owner": "tern",
                                "deadline": task["deadline"],
                                "dispatch_receipt": "acknowledged"})
                    snap["terminal"][pid] = entry
                else:
                    fl = r.get("flight") or {}
                    ho = r.get("handoff") or {}
                    aid = fl.get("action_id")
                    if aid:
                        entry = {
                            "package_id": pid, "phase": r["phase"],
                            "action_id": aid,
                            "owner": fl.get("owner"),
                            "deadline": fl.get("deadline"),
                            "dispatch_receipt": self.acks.get(aid, "none")}
                    elif ho:
                        # Bounded handoff: explicitly owned, explicitly
                        # bounded — never an unbounded-silence ACTIVE.
                        entry = {
                            "package_id": pid, "phase": r["phase"],
                            "action_id": None,
                            "owner": ho.get("owner"),
                            "deadline": ho.get("deadline"),
                            "dispatch_receipt": None}
                    else:
                        entry = {
                            "package_id": pid, "phase": r["phase"],
                            "action_id": None, "owner": None,
                            "deadline": None, "dispatch_receipt": None}
                    snap["in_flight"].append(entry)
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
    return {"attempts": 1, "repairs": 1, "verifier_s": 1800,
            "passes": {"verify": {"max_s": 1800},
                       "controller_recovery": {"max_s": 600}}}
