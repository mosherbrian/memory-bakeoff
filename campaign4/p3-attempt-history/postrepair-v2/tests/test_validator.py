"""Group 1 (validator) + group 3 (idempotency/crash/snapshot).

Drives the real CLI against fixture files into fresh temp stores. Fake clock
only (fixed ISO strings). Nothing here wakes/stops/signals anything.
"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PKG, "fixtures")
NOW = "2026-09-21T17:15:00Z"


def cli(*args):
    env = dict(os.environ)
    p = subprocess.run([sys.executable, "-m", "src.cli"] + list(args),
                       cwd=PKG, capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


TERMINAL_VERDICTS = {"verify_pass", "verify_fail", "withhold",
                     "terminate", "exhaust"}


def build_store(events_file, legacy_last=False):
    """Drive fixture events through the real CLI.

    A terminal-verdict event immediately followed by a decide event for the
    same question/revision commits atomically via ``close`` (D4 rule).
    ``legacy_last=True`` inserts the final event as raw pre-core state
    (bypassing the atomic guard) to reproduce historical omission shapes.
    """
    import sqlite3 as _sq
    d = tempfile.mkdtemp()
    db = os.path.join(d, "ledger.db")
    with open(os.path.join(FIX, "events", events_file)) as fh:
        lines = [json.loads(l) for l in fh if l.strip()]
    i = 0
    while i < len(lines):
        e = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if legacy_last and i == len(lines) - 1:
            con = _sq.connect(db)
            body = {k: v for k, v in e.items()
                    if k not in ("event_id", "question_id", "revision",
                                 "type", "actor", "at")}
            body["_budget"] = {"attempts": 1, "repairs": 1,
                               "verifier_s": 1800}
            con.execute(
                "INSERT INTO events (event_id, question_id, revision, type,"
                " actor_seat, actor_role, at, body) VALUES (?,?,?,?,?,?,?,?)",
                (e["event_id"], e["question_id"], e.get("revision", 1),
                 e["type"], e["actor"]["seat"], e["actor"]["role"], e["at"],
                 json.dumps(body, sort_keys=True)))
            con.commit()
            con.close()
            i += 1
            continue
        if e["type"] in TERMINAL_VERDICTS and nxt is not None and \
                nxt["type"] == "decide" and \
                nxt["question_id"] == e["question_id"] and \
                nxt.get("revision", 1) == e.get("revision", 1):
            vf = os.path.join(d, "verdict.json")
            df = os.path.join(d, "decide.json")
            json.dump(e, open(vf, "w"))
            json.dump(nxt, open(df, "w"))
            out = cli("close", "--store", db, "--verdict", vf,
                      "--decide", df)
            assert out["ok"], out
            i += 2
            continue
        ef = os.path.join(d, "e.json")
        json.dump(e, open(ef, "w"))
        out = cli("apply", "--store", db, "--event", ef)
        assert out["ok"], out
        i += 1
    return d, db


def snap_of(db, d, extra=None):
    sp = os.path.join(d, "snap.json")
    args = ["snapshot", "--store", db, "--out", sp]
    if extra:
        ep = os.path.join(d, "extra.json")
        json.dump(extra, open(ep, "w"))
        args += ["--extra", ep]
    cli(*args)
    return sp


def validate(db, snap, now=NOW, fired=None):
    args = ["validate", "--store", db, "--snapshot", snap, "--now", now]
    if fired is not None:
        fp = os.path.join(tempfile.mkdtemp(), "f.json")
        json.dump(list(fired), open(fp, "w"))
        args += ["--triggers-fired", fp]
    return cli(*args)


class TestValidator(unittest.TestCase):
    def test_tern_omission_is_invalid(self):
        # Legacy bare terminal (pre-core state): verdict committed with no
        # disposition and no bounded hold — the omission shape.
        d, db = build_store("omission.jsonl", legacy_last=True)
        v = validate(db, snap_of(db, d))
        self.assertEqual(v["verdict"], "INVALID")
        self.assertEqual(v["code"], "E_MISSING_DISPOSITION")

    def test_bare_terminal_rejected_by_store(self):
        # D4: the core itself refuses to commit a terminal without a
        # same-transaction disposition or bounded hold.
        import sqlite3 as _sq
        d = tempfile.mkdtemp()
        db = os.path.join(d, "b.db")
        with open(os.path.join(FIX, "events", "rest-answered.jsonl")) as fh:
            lines = [json.loads(l) for l in fh if l.strip()]
        for e in lines[:4]:  # admit..publish
            ef = os.path.join(d, "e.json")
            json.dump(e, open(ef, "w"))
            out = cli("apply", "--store", db, "--event", ef)
            assert out["ok"], out
        n0 = _sq.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        vf = os.path.join(d, "v.json")
        json.dump(lines[4], open(vf, "w"))
        out = cli("apply", "--store", db, "--event", vf)
        self.assertFalse(out["ok"], out)
        self.assertEqual(out["code"], "E_MISSING_DISPOSITION")
        n1 = _sq.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        self.assertEqual(n0, n1, "rejected commit stored nothing")

    def test_held_state_is_pending_not_omission(self):
        # D4 row 17: verify_pass + same-transaction bounded hold validates
        # as pending decision work, not E_MISSING_DISPOSITION.
        import sys as _sys
        _sys.path.insert(0, PKG)
        d = tempfile.mkdtemp()
        db = os.path.join(d, "h.db")
        for name in ("rest-answered",):
            pass
        with open(os.path.join(FIX, "events", "rest-answered.jsonl")) as fh:
            lines = [json.loads(l) for l in fh if l.strip()]
        for e in lines[:4]:  # admit..publish
            ef = os.path.join(d, "e.json")
            json.dump(e, open(ef, "w"))
            out = cli("apply", "--store", db, "--event", ef)
            assert out["ok"], out
        vf = os.path.join(d, "v.json")
        json.dump(lines[4], open(vf, "w"))
        out = cli("apply", "--store", db, "--event", vf, "--hold",
                  "2026-09-21T18:00:00Z")
        self.assertTrue(out["ok"], out)
        v = validate(db, snap_of(db, d))
        self.assertNotEqual(v.get("code"), "E_MISSING_DISPOSITION", v)
        self.assertEqual(v["verdict"], "ACTIVE", v)

    def test_overdue_flight_from_ledger(self):
        # D2 (corvid script B): ledger-derived in-flight attempt past its
        # deadline validates E_OVERDUE_ACTION, not ACTIVE.
        d, db = build_store("overdue-flight.jsonl")
        v = validate(db, snap_of(db, d))
        self.assertEqual(v["verdict"], "INVALID", v)
        self.assertEqual(v["code"], "E_OVERDUE_ACTION", v)

    def test_successor_without_receipt_is_invalid(self):
        # D3 (corvid script A): in-flight entry with no acknowledged
        # dispatch or finite deadline cannot satisfy a successor link.
        d, db = build_store("rest-answered.jsonl")
        import sqlite3 as _sq
        rev = _sq.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        snap = json.load(open(os.path.join(FIX, "snapshots",
                                           "no-receipt.json")))
        snap["ledger_revision"] = rev
        real = cli("snapshot", "--store", db, "--out",
                   os.path.join(d, "real.json"))["snapshot"]
        for pid, entry in real["terminal"].items():
            snap["terminal"].setdefault(pid, entry)
        dst = os.path.join(d, "noreceipt.json")
        json.dump(snap, open(dst, "w"))
        v = validate(db, dst)
        self.assertEqual(v["verdict"], "INVALID", v)

    def test_rest_kinds_return_rest_no_alarm(self):
        for name in ("rest-answered", "rest-blocked-parked", "rest-budget"):
            d, db = build_store(name + ".jsonl")
            v = validate(db, snap_of(db, d))
            self.assertEqual(v["verdict"], "REST", (name, v))
            self.assertNotIn("action", v)

    def test_due_trigger_returns_exactly_once(self):
        d, db = build_store("trigger-due.jsonl")
        sp = snap_of(db, d)
        v1 = validate(db, sp)
        self.assertEqual(v1["verdict"], "ACTION_DUE")
        self.assertTrue(v1["action"]["bounded"])
        tid = v1["action"]["trigger_id"]
        v2 = validate(db, sp, fired={tid})
        self.assertEqual(v2["verdict"], "REST", v2)

    def test_chain_live_is_active(self):
        d, db = build_store("chain-live.jsonl")
        v = validate(db, snap_of(db, d))
        self.assertEqual(v["verdict"], "ACTIVE", v)

    def test_two_successors_rest(self):
        d, db = build_store("chain-rest.jsonl")
        v = validate(db, snap_of(db, d))
        self.assertEqual(v["verdict"], "REST", v)

    def test_adversarial_snapshots(self):
        import sqlite3 as _sq
        d, db = build_store("rest-answered.jsonl")
        rev = _sq.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        base = os.path.join(FIX, "snapshots")

        def aligned(name):
            src = os.path.join(base, name + ".json")
            snap = json.load(open(src))
            snap["ledger_revision"] = rev
            # ledger built from rest-answered holds Q-r1 COMPLETE+disposition;
            # adversarial entries reference other ids, so completeness holds
            # only if the snapshot also carries the real terminal entry.
            real = cli("snapshot", "--store", db, "--out",
                       os.path.join(d, "real.json"))["snapshot"]
            for pid, entry in real["terminal"].items():
                snap["terminal"].setdefault(pid, entry)
            dst = os.path.join(d, name + ".json")
            json.dump(snap, open(dst, "w"))
            return dst

        for name, code in (("cycle", "E_CYCLE"),
                           ("dangling", "E_DANGLING_SUCCESSOR"),
                           ("free-kind", "E_MISSING_DISPOSITION"),
                           ("no-director", "E_OWNERSHIP"),
                           ("overdue", "E_OVERDUE_ACTION")):
            v = validate(db, aligned(name))
            self.assertEqual(v.get("code"), code, (name, v))
        for name, code in (("empty-terminal", "E_LEDGER_INCOMPLETE"),
                           ("stale-revision", "E_LEDGER_INCOMPLETE"),
                           ("version99", "E_VERSION")):
            v = validate(db, os.path.join(base, name + ".json"))
            self.assertEqual(v["code"], code, (name, v))
        v = validate(db, os.path.join(base, "malformed.txt"))
        self.assertEqual(v["verdict"], "INVALID")
        v = cli("validate", "--store", db, "--snapshot",
                os.path.join(d, "nope.json"), "--now", NOW)
        self.assertEqual(v["code"], "E_ABSENT_STATE")

    def test_unrelated_busy_does_not_satisfy_successor(self):
        # chain-live: QC-r1 --successor--> QC-r2, QC-r2 RUNNING in flight.
        # Rewrite the projection so the only busy entry is an unrelated
        # package: the named successor then has no acknowledged work.
        d, db = build_store("chain-live.jsonl")
        sp = snap_of(db, d)
        snap = json.load(open(sp))
        snap["in_flight"] = [
            {"package_id": "OTHER-r1", "phase": "RUNNING",
             "action_id": "z", "owner": "kiln",
             "deadline": "2026-09-22T00:00:00Z", "dispatch_receipt": "r"}]
        json.dump(snap, open(sp, "w"))
        v = validate(db, sp)
        self.assertEqual(v["verdict"], "INVALID", v)
        self.assertEqual(v["code"], "E_DANGLING_SUCCESSOR", v)

    def test_snapshot_mismatch_cannot_hide_ledger(self):
        d, db = build_store("omission.jsonl", legacy_last=True)
        v = validate(db, os.path.join(FIX, "snapshots", "empty-terminal.json"))
        self.assertEqual(v["code"], "E_LEDGER_INCOMPLETE")


class TestIdempotency(unittest.TestCase):
    def test_duplicate_event_delivery_ignored(self):
        d, db = build_store("rest-answered.jsonl")
        n0 = sqlite3.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        with open(os.path.join(FIX, "events", "rest-answered.jsonl")) as fh:
            first = fh.readline().strip()
        ef = os.path.join(d, "dup.json")
        open(ef, "w").write(first)
        out = cli("apply", "--store", db, "--event", ef)
        self.assertEqual((out["ok"], out["duplicate"]), (True, True))
        n1 = sqlite3.connect(db).execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        self.assertEqual(n0, n1)

    def test_crash_after_start_reconciles_same_action(self):
        sys.path.insert(0, PKG)
        from src.store import Store
        from src.fake import FakeExecutor, dispatch, reconcile_after_crash
        d = tempfile.mkdtemp()
        db = os.path.join(d, "c.db")
        store = Store(db)
        for typ, actor in (("admit", ("corvid", "reader")),
                           ("authorize", ("tern", "director"))):
            store.append({"event_id": "k-" + typ, "question_id": "QK",
                          "revision": 1, "type": typ,
                          "actor": {"seat": actor[0], "role": actor[1]},
                          "at": NOW})
        action = {"action_id": "act-1", "question_id": "QK", "revision": 1,
                  "deadline": "2026-09-21T18:00:00Z", "at": NOW}
        exe = FakeExecutor()
        out, dup = dispatch(store, action, exe, now=NOW)
        self.assertFalse(dup)
        # Simulate crash: new handle, same ledger; redelivery reconciles.
        store.close()
        store2 = Store(db)
        self.assertEqual(store2.acks.get("act-1"), "acknowledged")
        rec = reconcile_after_crash(store2, action)
        self.assertEqual(rec["attempt_delta"], 0)
        out2, dup2 = dispatch(store2, action, exe, now=NOW)
        self.assertEqual(out2, "redelivered-same-action")
        self.assertTrue(dup2)
        self.assertEqual(exe.runs.count("act-1"), 1,
                         "executor ran exactly once")
        store2.close()

    def test_interrupted_snapshot_rebuilt_from_ledger(self):
        d, db = build_store("rest-answered.jsonl")
        sp = os.path.join(d, "snap.json")
        open(sp, "w").write('{"schema_version":1,"cut')
        v = validate(db, sp)
        self.assertEqual(v["verdict"], "INVALID")
        v2 = validate(db, snap_of(db, d))
        self.assertEqual(v2["verdict"], "REST")

    def test_changed_registration_rejected(self):
        d, db = build_store("rest-answered.jsonl")
        ef = os.path.join(d, "evil.json")
        json.dump({"event_id": "evil", "question_id": "Q", "revision": 1,
                   "type": "publish",
                   "actor": {"seat": "kiln", "role": "worker"}, "at": NOW,
                   "artifact_hashes": ["forged"]}, open(ef, "w"))
        out = cli("apply", "--store", db, "--event", ef)
        self.assertFalse(out["ok"])
        self.assertIn(out["code"], ("E_BAD_TRANSITION", "E_TERMINAL"))

    def test_stale_deadline_event_after_completion(self):
        d, db = build_store("rest-answered.jsonl")
        ef = os.path.join(d, "stale.json")
        json.dump({"event_id": "stale", "question_id": "Q", "revision": 1,
                   "type": "interrupt",
                   "actor": {"seat": "cairn", "role": "duty"}, "at": NOW,
                   "reason": "late"}, open(ef, "w"))
        out = cli("apply", "--store", db, "--event", ef)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
