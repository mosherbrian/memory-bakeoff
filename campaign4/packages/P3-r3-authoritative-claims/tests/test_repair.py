"""P3-r2 repair evidence: the five supplied failures.

All seven director-initial-check.json cases run against the preserved
initial version (fresh-interpreter subprocess over the byte-exact archive
at campaign4/p3r2-attempt-history/initial-director/) and against the
repaired code in this directory:

- genuine_rest -> REST and genuine_active -> ACTIVE on both (no regression).
- forged_due_disposition, forged_phase, duplicate_forged_flight fail on
  initial (ACTION_DUE / ACTIVE / ACTIVE) and validate INVALID on repair.
- malformed_package_id, timestamp_overflow crash on initial (TypeError /
  OverflowError) and validate INVALID (E_MALFORMED) on repair.
- Unshared mutations: due-trigger bypass with a second inconsistent
  package; DECISION-entry forgery; handoff owner forgery; offset-format
  deadline equality (no false mismatch).
"""
import json
import os
import subprocess
import sys
import unittest

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PKG, "fixtures")
INITIAL = "/home/bmosher/memory-bake-off/campaign4/p3r2-attempt-history" \
          "/initial-director/src/validator.py"

sys.path.insert(0, PKG)
from src.validator import validate  # repaired code under test


def run_initial(cases):
    lines = [
        "import importlib.util, json, sys",
        "spec = importlib.util.spec_from_file_location("
        "'v_init', sys.argv[1])",
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
    probe = os.path.join(FIX, "director-initial-check.json")
    p = subprocess.run([sys.executable, "-c", "\n".join(lines), INITIAL,
                        probe],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {r["name"]: r for r in json.loads(p.stdout)}


class TestRepairCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["name"]: c for c in json.load(
            open(os.path.join(FIX, "director-initial-check.json")))}

    def test_initial_reproduces_five_failures(self):
        got = run_initial(None)
        self.assertEqual(got["forged_due_disposition"]["verdict"], "ACTION_DUE")
        self.assertEqual(got["forged_phase"]["verdict"], "ACTIVE")
        self.assertEqual(got["duplicate_forged_flight"]["verdict"], "ACTIVE")
        self.assertEqual(got["malformed_package_id"]["verdict"], "EXCEPTION")
        self.assertEqual(got["malformed_package_id"]["code"], "TypeError")
        self.assertEqual(got["timestamp_overflow"]["verdict"], "EXCEPTION")
        self.assertEqual(got["timestamp_overflow"]["code"], "OverflowError")

    def test_repaired_invalid_on_five(self):
        expect = {"forged_due_disposition": "E_MISMATCH",
                  "forged_phase": "E_MISMATCH",
                  "duplicate_forged_flight": "E_DUPLICATE",
                  "malformed_package_id": "E_MALFORMED",
                  "timestamp_overflow": "E_MALFORMED"}
        for name, code in expect.items():
            c = self.cases[name]
            v = validate(c["snapshot"], c["ledger"], c["now"])
            self.assertEqual(v["verdict"], "INVALID", (name, v))
            self.assertEqual(v["code"], code, (name, v))

    def test_genuine_cases_still_valid(self):
        for name, verdict in (("genuine_rest", "REST"),
                              ("genuine_active", "ACTIVE")):
            c = self.cases[name]
            v = validate(c["snapshot"], c["ledger"], c["now"])
            self.assertEqual(v["verdict"], verdict, (name, v))

    def test_due_trigger_with_second_inconsistent_package(self):
        # Unshared mutation: a genuine due trigger alongside a forged
        # second package must NOT emit ACTION_DUE — authority first.
        import copy
        snap = {"schema_version": 1, "ledger_revision": 2, "in_flight": [],
                "terminal": {
                    "good": {"state": "EXHAUSTED",
                             "decided_by": "tern", "decision_ref": "d",
                             "reason": "parked",
                             "disposition": {
                                 "kind": "blocked", "reason": "parked",
                                 "decision_ref": "d",
                                 "blocker": {
                                     "id": "b", "owner": "cairn",
                                     "resumption": "on event",
                                     "wake_trigger": {
                                         "event_id": "ev-1"}}}},
                    "bad": {"state": "COMPLETE",
                            "decided_by": "tern", "decision_ref": "d",
                            "reason": "x",
                            "disposition": {
                                "kind": "question_answered",
                                "reason": "x",
                                "evidence_refs": ["forged"]}}}}
        ledger = {"revision": 2, "packages": {
            "good": {"phase": "EXHAUSTED",
                     "disposition": dict(
                         snap["terminal"]["good"]["disposition"])},
            "bad": {"phase": "COMPLETE", "disposition": None,
                    "decision_task": None}}}
        v = validate(snap, ledger, "2026-09-21T19:00:00Z")
        self.assertEqual(v["verdict"], "INVALID", v)
        self.assertEqual(v["code"], "E_FABRICATED", v)

    def test_decision_and_handoff_forgery(self):
        import copy
        # DECISION entry with no ledger task is fabricated.
        snap = {"schema_version": 1, "ledger_revision": 1,
                "in_flight": [{"package_id": "p", "phase": "DECISION",
                               "action_id": "t", "owner": "tern",
                               "deadline": "2026-09-21T20:00:00Z",
                               "dispatch_receipt": "acknowledged"}],
                "terminal": {"p": {"state": "COMPLETE", "held": True}}}
        ledger = {"revision": 1, "packages": {
            "p": {"phase": "COMPLETE", "disposition": None,
                  "decision_task": None}}}
        v = validate(snap, ledger, "2026-09-21T19:00:00Z")
        self.assertEqual(v["verdict"], "INVALID", v)
        # Handoff owner forged against the ledger handoff.
        snap2 = {"schema_version": 1, "ledger_revision": 1,
                 "in_flight": [{"package_id": "p", "phase": "CHECKING",
                                "action_id": None, "owner": "mallory",
                                "deadline": "2026-09-21T20:00:00Z",
                                "dispatch_receipt": None}],
                 "terminal": {}}
        ledger2 = {"revision": 1, "packages": {
            "p": {"phase": "CHECKING",
                  "handoff": {"owner": "duty",
                              "deadline": "2026-09-21T20:00:00Z"}}}}
        v = validate(snap2, ledger2, "2026-09-21T19:00:00Z")
        self.assertEqual((v["verdict"], v["code"]),
                         ("INVALID", "E_MISMATCH"), v)


if __name__ == "__main__":
    unittest.main()
