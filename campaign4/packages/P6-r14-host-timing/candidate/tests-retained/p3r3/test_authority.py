"""P3-r2: ledger-authority tests.
- Both director-probes.json cases fail (false REST) on preserved v3 and
  validate INVALID on r2.
- Omissions/forgeries for each authority-bearing field: inventory, phase,
  disposition, decision, action, owner, deadline, receipt, successor linkage.
- Reopen + real store-derived snapshots (not only hand dicts).
- Genuine rest/chains/handoff/expiry/flight outcomes preserved (also covered
  by the carried suite).
"""
import copy
import json
import os
import sys
import tempfile
import unittest

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PKG, "fixtures")
V3 = "/home/bmosher/memory-bake-off/campaign4/packages/P3-core-validator" \
     "/src/validator.py"
NOW = "2026-09-21T18:50:00Z"

sys.path.insert(0, "/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/candidate/src/r3harness")  # ADAPTED P6-r13: NEW core first
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "tests"))
from validator import validate  # r2 under test
from test_validator import build_store, snap_of


class TestDirectorProbes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probes = json.load(open(os.path.join(
            FIX, "director-probes.json")))["cases"]

    @staticmethod
    def _run_v3():
        """Execute preserved v3 in a fresh interpreter (its bytes are the
        baseline; no in-process import entanglement). Returns verdicts."""
        code = (
            "import importlib.util, json, sys;"
            "spec = importlib.util.spec_from_file_location("
            "'v3_validator', sys.argv[1]);"
            "mod = importlib.util.module_from_spec(spec);"
            "spec.loader.exec_module(mod);"
            "cases = json.load(open(sys.argv[2]))['cases'];"
            "print(json.dumps([{'name': c['name'], 'verdict': "
            "mod.validate(c['snapshot'], c['ledger'], c['now'])['verdict']} "
            "for c in cases]))")
        import subprocess as _sp
        p = _sp.run(
            [sys.executable, "-c", code, V3,
             os.path.join(FIX, "director-probes.json")],
            capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        return {r["name"]: r["verdict"] for r in json.loads(p.stdout)}

    def test_probes_fail_on_v3(self):
        verdicts = self._run_v3()
        for case in self.probes:
            self.assertEqual(verdicts[case["name"]], "REST",
                             (case["name"], verdicts))

    def test_probes_invalid_on_r2(self):
        for case in self.probes:
            v = validate(case["snapshot"], case["ledger"], case["now"])
            self.assertEqual(v["verdict"], "INVALID", (case["name"], v))
        codes = [validate(c["snapshot"], c["ledger"], c["now"])["code"]
                 for c in self.probes]
        self.assertEqual(codes, ["E_LEDGER_INCOMPLETE", "E_FABRICATED"])


def _store_snapshot(events_file, **kw):
    from test_validator import build_store, snap_of
    d, db = build_store(events_file, **kw)
    return d, db, json.load(open(snap_of(db, d)))


class TestAuthorityFields(unittest.TestCase):
    def test_forged_owner_deadline_receipt(self):
        d, db = build_store("flight-rotate.jsonl")
        base = json.load(open(snap_of(db, d)))
        for mutate, code in (
                (lambda s: s["in_flight"][0].update(owner="mallory"),
                 "E_MISMATCH"),
                (lambda s: s["in_flight"][0].update(
                    deadline="2026-09-22T17:25:00Z"), "E_MISMATCH"),
                (lambda s: s["in_flight"][0].update(
                    dispatch_receipt="acknowledged"), "E_MISMATCH"),
                (lambda s: s["in_flight"][0].update(action_id="forged-9"),
                 "E_MISMATCH")):
            s = copy.deepcopy(base)
            mutate(s)
            v = validate(s, _ledger(db), "2026-09-21T17:15:00Z")
            self.assertEqual(v["verdict"], "INVALID", v)
            self.assertEqual(v["code"], code, v)

    def test_hidden_and_changed_disposition(self):
        d, db = build_store("rest-answered.jsonl")
        base = json.load(open(snap_of(db, d)))
        s = copy.deepcopy(base)
        del s["terminal"]["Q-r1"]["disposition"]
        self.assertEqual(validate(s, _ledger(db), NOW)["code"],
                         "E_MISSING_DISPOSITION")
        s = copy.deepcopy(base)
        s["terminal"]["Q-r1"]["disposition"]["reason"] = "rewritten"
        v = validate(s, _ledger(db), NOW)
        self.assertEqual((v["verdict"], v["code"]), ("INVALID", "E_MISMATCH"))
        s = copy.deepcopy(base)
        s["terminal"]["Q-r1"]["state"] = "TERMINATED"
        v = validate(s, _ledger(db), NOW)
        self.assertEqual((v["verdict"], v["code"]), ("INVALID", "E_MISMATCH"))
        s = copy.deepcopy(base)
        s["terminal"]["Q-r1"]["decision_ref"] = "forged"
        v = validate(s, _ledger(db), NOW)
        self.assertEqual((v["verdict"], v["code"]), ("INVALID", "E_MISMATCH"))

    def test_fabricated_and_missing_packages(self):
        d, db = build_store("rest-answered.jsonl")
        base = json.load(open(snap_of(db, d)))
        s = copy.deepcopy(base)
        s["terminal"]["GHOST-r9"] = copy.deepcopy(s["terminal"]["Q-r1"])
        v = validate(s, _ledger(db), NOW)
        self.assertEqual((v["verdict"], v["code"]), ("INVALID", "E_FABRICATED"))
        s = copy.deepcopy(base)
        del s["terminal"]["Q-r1"]
        v = validate(s, _ledger(db), NOW)
        self.assertEqual(v["code"], "E_LEDGER_INCOMPLETE")
        # Active package dropped from flight: the successor link dangles
        # first (structural), so the deterministic code here is DANGLING;
        # the missing-active rule is pinned by the flight-rotate case below.
        d2, db2 = build_store("chain-live.jsonl")
        s2 = json.load(open(snap_of(db2, d2)))
        s2["in_flight"] = []
        v = validate(s2, _ledger(db2), NOW)
        self.assertEqual((v["verdict"], v["code"]),
                         ("INVALID", "E_DANGLING_SUCCESSOR"))
        d3, db3 = build_store("flight-rotate.jsonl")
        s3 = json.load(open(snap_of(db3, d3)))
        s3["in_flight"] = []
        v = validate(s3, _ledger(db3), "2026-09-21T17:15:00Z")
        self.assertEqual((v["verdict"], v["code"]),
                         ("INVALID", "E_LEDGER_INCOMPLETE"))

    def test_forged_successor_link(self):
        d, db = build_store("chain-rest.jsonl")
        base = json.load(open(snap_of(db, d)))
        s = copy.deepcopy(base)
        self.assertEqual(validate(base, _ledger(db), NOW)["verdict"], "REST")
        # Chain QC-r1 -> QC-r2 is ledger-true; repoint to an unknown id.
        s["terminal"]["QC-r1"]["disposition"]["successor_id"] = "NOPE-r9"
        v = validate(s, _ledger(db), NOW)
        self.assertEqual(v["verdict"], "INVALID", v)

    def test_malformed_timestamps_never_crash(self):
        d, db = build_store("flight-rotate.jsonl")
        base = json.load(open(snap_of(db, d)))
        for bad in ("tomorrow", "2026-13-45T99:99:99Z", 1721600000,
                    "2026-09-21 17:15:00"):
            s = copy.deepcopy(base)
            s["in_flight"][0]["deadline"] = bad
            v = validate(s, _ledger(db), "2026-09-21T17:15:00Z")
            self.assertEqual(v["verdict"], "INVALID", (bad, v))
        v = validate(base, _ledger(db), "not-a-time")
        self.assertEqual(v["code"], "E_MALFORMED")
        # Equivalent formatting compares as the same instant.
        s = copy.deepcopy(base)
        s["in_flight"][0]["deadline"] = "2026-09-21T17:25:00+00:00"
        v = validate(s, _ledger(db), "2026-09-21T17:15:00Z")
        self.assertEqual(v["verdict"], "ACTIVE", v)

    def test_reopen_store_derived_snapshot(self):
        import sys as _sys
        _sys.path.insert(0, "/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/candidate/src/r3harness")  # ADAPTED P6-r13: NEW core first
        sys.path.insert(0, PKG)
        from store import Store
        d, db = build_store("flight-rotate.jsonl")
        Store(db).close()
        v = validate(json.load(open(snap_of(db, d))), _ledger(db),
                     "2026-09-21T17:15:00Z")
        self.assertEqual(v["verdict"], "ACTIVE", v)

    def test_genuine_outcomes_preserved(self):
        for name, now, verdict in (
                ("rest-answered.jsonl", NOW, "REST"),
                ("rest-blocked-parked.jsonl", NOW, "REST"),
                ("rest-budget.jsonl", NOW, "REST"),
                ("chain-rest.jsonl", NOW, "REST"),
                ("chain-live.jsonl", "2026-09-21T17:15:00Z", "ACTIVE"),
                ("handoff.jsonl", "2026-09-21T17:15:00Z", "ACTIVE"),
                ("flight-rotate.jsonl", "2026-09-21T17:15:00Z", "ACTIVE"),
                ("flight-rotate.jsonl", "2026-09-21T17:35:00Z", "INVALID"),
                ("trigger-due.jsonl", NOW, "ACTION_DUE")):
            d, db = build_store(name)
            v = validate(json.load(open(snap_of(db, d))), _ledger(db), now)
            self.assertEqual(v["verdict"], verdict, (name, v))


def _ledger(db):
    import sys as _sys
    _sys.path.insert(0, "/home/bmosher/memory-bake-off/campaign4/packages/P6-r13-core-record-integrity/candidate/src/r3harness")  # ADAPTED P6-r13: NEW core first
    sys.path.insert(0, PKG)
    from store import Store
    from cli import ledger_packages
    store = Store(db)
    try:
        return {"revision": store.ledger_revision(),
                "packages": ledger_packages(store)}
    finally:
        store.close()


if __name__ == "__main__":
    unittest.main()
