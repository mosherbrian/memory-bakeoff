"""P3-r3: authoritative-claims evidence.

- Both director-postrepair-check.json probes reproduce false-valid outcomes
  on pinned r2 (fresh-interpreter subprocess) and validate INVALID on r3.
- Table-driven mutation matrix over flight variants (dispatched
  worker/verifier, bounded handoff, pending director decision,
  no-current-action) and authority-bearing fields (receipt, action, owner,
  deadline, phase), including missing facts — on store-derived, reopened
  and focused-dict snapshots.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PKG, "fixtures")
R2 = "/home/bmosher/memory-bake-off/campaign4/packages/P3-r2-ledger-authority" \
     "/src/validator.py"

sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "tests"))
from src.validator import validate  # r3 under test
from test_validator import build_store, snap_of


def run_r2(cases):
    lines = [
        "import importlib.util, json, sys",
        "spec = importlib.util.spec_from_file_location('r2v', sys.argv[1])",
        "mod = importlib.util.module_from_spec(spec)",
        "spec.loader.exec_module(mod)",
        "cases = json.load(open(sys.argv[2]))",
        "out = []",
        "for c in cases:",
        "    try:",
        "        v = mod.validate(c['snapshot'], c['ledger'], c['now'])",
        "        out.append({'name': c['name'], 'verdict': v.get('verdict'),"
        " 'code': v.get('code', '')})",
        "    except Exception as e:",
        "        out.append({'name': c['name'], 'verdict': 'EXCEPTION',"
        " 'code': type(e).__name__})",
        "print(json.dumps(out))"]
    probe = os.path.join(FIX, "director-postrepair-check.json")
    p = subprocess.run([sys.executable, "-c", "\n".join(lines), R2, probe],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {r["name"]: r for r in json.loads(p.stdout)}


def _ledger(db):
    sys.path.insert(0, PKG)
    from src.store import Store
    from src.cli import ledger_packages
    store = Store(db)
    try:
        return {"revision": store.ledger_revision(),
                "packages": ledger_packages(store)}
    finally:
        store.close()


class TestR3Probes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["name"]: c for c in json.load(
            open(os.path.join(FIX, "director-postrepair-check.json")))}

    def test_probes_false_valid_on_r2(self):
        got = run_r2(None)
        self.assertEqual(got["invented_decision_reference"]["verdict"], "REST")
        self.assertEqual(got["forged_handoff_ack_satisfies_successor"]
                         ["verdict"], "ACTIVE")

    def test_probes_invalid_on_r3(self):
        for name in ("invented_decision_reference",
                     "forged_handoff_ack_satisfies_successor"):
            c = self.cases[name]
            v = validate(c["snapshot"], c["ledger"], c["now"])
            self.assertEqual(v["verdict"], "INVALID", (name, v))
            self.assertEqual(v["code"], "E_MISMATCH", (name, v))


class TestMutationMatrix(unittest.TestCase):
    """Variant x field matrix. Each row: (base, mutate, expected_code).

    Bases are store-derived (flight-rotate, handoff) or focused dicts
    (decision-task, no-action). Missing facts are mutated as well as
    changed facts. Positive controls assert the unmutated bases first.
    """

    def _bases(self):
        d1, db1 = build_store("flight-rotate.jsonl")
        s1 = json.load(open(snap_of(db1, d1)))
        d2, db2 = build_store("handoff.jsonl")
        s2 = json.load(open(snap_of(db2, d2)))
        return {
            "dispatched": (s1, _ledger(db1), "2026-09-21T17:15:00Z",
                           "ACTIVE"),
            "handoff": (s2, _ledger(db2), "2026-09-21T17:15:00Z", "ACTIVE"),
            "decision": ({
                "schema_version": 1, "ledger_revision": 1,
                "in_flight": [{"package_id": "p", "phase": "DECISION",
                               "action_id": "t", "owner": "tern",
                               "deadline": "2026-09-21T20:00:00Z",
                               "dispatch_receipt": "acknowledged"}],
                "terminal": {"p": {"state": "COMPLETE", "held": True}}},
                {"revision": 1, "packages": {
                    "p": {"phase": "COMPLETE", "disposition": None,
                          "decision_task": {"task_id": "t",
                                            "deadline":
                                            "2026-09-21T20:00:00Z"}}}},
                "2026-09-21T19:00:00Z", "ACTIVE"),
            "noaction": ({
                "schema_version": 1, "ledger_revision": 1,
                "in_flight": [{"package_id": "p", "phase": "REGISTERED",
                               "action_id": None, "owner": None,
                               "deadline": None, "dispatch_receipt": None}],
                "terminal": {}},
                {"revision": 1, "packages": {
                    "p": {"phase": "REGISTERED"}}},
                "2026-09-21T19:00:00Z", "ACTIVE"),
        }

    def test_positive_controls(self):
        for name, (snap, ledger, now, verdict) in self._bases().items():
            v = validate(snap, ledger, now)
            self.assertEqual(v["verdict"], verdict, (name, v))

    def test_matrix(self):
        # Explicit (variant, field, forged value, expected code). Every
        # row is INVALID; codes are deterministic per variant semantics.
        rows = [
            ("dispatched", "dispatch_receipt", "acknowledged", "E_MISMATCH"),
            ("dispatched", "action_id", "forged-9", "E_MISMATCH"),
            ("dispatched", "owner", "mallory", "E_MISMATCH"),
            ("dispatched", "deadline", "2026-09-22T20:00:00Z", "E_MISMATCH"),
            ("dispatched", "phase", "RUNNING", "E_MISMATCH"),
            ("dispatched", "dispatch_receipt", None, "E_MISMATCH"),
            ("dispatched", "deadline", None, "E_MALFORMED"),
            ("handoff", "dispatch_receipt", "acknowledged", "E_MISMATCH"),
            ("handoff", "action_id", "forged-9", "E_MISMATCH"),
            ("handoff", "owner", "mallory", "E_MISMATCH"),
            ("handoff", "deadline", "2026-09-22T20:00:00Z", "E_MISMATCH"),
            ("handoff", "phase", "RUNNING", "E_MISMATCH"),
            ("handoff", "owner", None, "E_MISMATCH"),
            ("decision", "dispatch_receipt", "intended",
             "E_LEDGER_INCOMPLETE"),
            ("decision", "action_id", "other-task", "E_LEDGER_INCOMPLETE"),
            ("decision", "owner", "mallory", "E_LEDGER_INCOMPLETE"),
            ("decision", "deadline", "2026-09-22T20:00:00Z",
             "E_LEDGER_INCOMPLETE"),
            ("decision", "phase", "RUNNING", "E_MISSING_DISPOSITION"),
            ("noaction", "action_id", "forged-9", "E_FABRICATED"),
            ("noaction", "owner", "kiln", "E_MISMATCH"),
            ("noaction", "deadline", "2026-09-21T20:00:00Z", "E_MISMATCH"),
            ("noaction", "dispatch_receipt", "acknowledged", "E_MISMATCH"),
            ("noaction", "phase", "RUNNING", "E_MISMATCH"),
        ]
        for variant, field, bad, code in rows:
            snap, ledger, now, _ = self._bases()[variant]
            snap = copy.deepcopy(snap)
            if snap["in_flight"][0][field] == bad:
                continue  # no mutation: positive control covers it
            snap["in_flight"][0][field] = bad
            v = validate(snap, ledger, now)
            self.assertEqual(v["verdict"], "INVALID",
                             (variant, field, bad, v))
            self.assertEqual(v["code"], code, (variant, field, bad, v))

    def test_reopened_store_matrix(self):
        sys.path.insert(0, PKG)
        from src.store import Store
        d, db = build_store("flight-rotate.jsonl")
        Store(db).close()
        snap = json.load(open(snap_of(db, d)))
        ledger = _ledger(db)
        v = validate(snap, ledger, "2026-09-21T17:15:00Z")
        self.assertEqual(v["verdict"], "ACTIVE", v)
        snap["in_flight"][0]["owner"] = "mallory"
        v = validate(snap, ledger, "2026-09-21T17:15:00Z")
        self.assertEqual((v["verdict"], v["code"]),
                         ("INVALID", "E_MISMATCH"), v)


if __name__ == "__main__":
    unittest.main()
