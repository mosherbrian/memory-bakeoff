#!/usr/bin/env python3
"""Focused fixtures for measure_v2 (synthetic snapshots; no live sources)."""
import json, os, tempfile, unittest, importlib.util
spec = importlib.util.spec_from_file_location("m", os.path.join(os.path.dirname(os.path.abspath(__file__)), "measure_v2.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S, E = m.ts("2026-01-01T00:00:00Z"), m.ts("2026-01-01T10:00:00Z")
Z = lambda h, mi=0: f"2026-01-01T{h:02d}:{mi:02d}:00Z"

def snap(events, rest=(), esc=(), reg=(), binds=None):
    d = tempfile.mkdtemp()
    json.dump(events, open(f"{d}/events.json", "w"))
    open(f"{d}/rest.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rest))
    json.dump(list(esc), open(f"{d}/escalations.json", "w")); json.dump(list(reg), open(f"{d}/registry.json", "w"))
    json.dump([], open(f"{d}/tickets.json", "w"))
    json.dump(binds or [{"package": q, "question_id": "Q-WORK-BENEFIT"} for q in {e["qid"] for e in events}], open(f"{d}/bindings.json", "w"))
    return d

ev = lambda q, t, at: {"qid": q, "type": t, "seat": "x", "role": "x", "at": at}

class T(unittest.TestCase):
    def test_event_after_end_ignored_and_pending_censored(self):
        d = snap([ev("P1", "start", Z(9, 58)), ev("P1", "interrupt", Z(10, 1))])
        b = m.measure(S, E, d)["b_dropped"]
        self.assertEqual(b["timeout_only"], []); self.assertEqual(b["right_censored_open_at_end"], ["P1"])
    def test_in_window_timeout_counted(self):
        b = m.measure(S, E, snap([ev("P1", "start", Z(1)), ev("P1", "interrupt", Z(1, 5))]))["b_dropped"]
        self.assertEqual(b["timeout_only"], ["P1"]); self.assertEqual(b["timeout_only_per_10"], 10.0)
    def test_ended_without_claim_stays_unknown(self):
        b = m.measure(S, E, snap([ev("P1", "start", Z(1))]))["b_dropped"]
        self.assertTrue(b["ended_without_claim"].startswith("UNKNOWN"))
    def test_overlapping_rest_reported_and_stall_unknown(self):
        rest = [{"question_id": "Q-WORK-BENEFIT", "entered_at": Z(1), "revisit_at": Z(5)}, {"question_id": "Q-WORK-BENEFIT", "entered_at": Z(2), "revisit_at": Z(3)}]
        a = m.measure(S, E, snap([ev("P1", "start", Z(6))], rest=rest))["a_stall"]
        self.assertEqual(a["primary_stall_minutes"], "UNKNOWN"); self.assertEqual(a["diagnostic_union"]["A"]["overlapping_rest_row_pairs"], 1)
    def test_escalation_delivery_unknown_not_zero(self):
        d = m.measure(S, E, snap([ev("P1", "start", Z(1))], esc=[{"id": "E-1", "kind": "research-gap", "t": S + 60}]))["d_escalations"]
        self.assertEqual(d["ledger_notices_in_window"], 1); self.assertTrue(d["confirmed_delivery"].startswith("UNKNOWN"))
    def test_decision_next_dispatch_and_censoring(self):
        c = m.measure(S, E, snap([ev("P1", "start", Z(1)), ev("P1", "decide", Z(2)), ev("P2", "start", Z(2, 30)), ev("P2", "decide", Z(9))]))["c_decision_to_next_dispatch"]
        self.assertEqual([(x["decided"], x["minutes"], x["censored_at_end"]) for x in c], [("P1", 30.0, False), ("P2", None, True)])
    def test_offline_only(self):
        src = open(spec.origin).read()
        for live in ("/.local/", "agent-loop status", "escalations.jsonl", "subprocess", "REST.jsonl\""):
            self.assertNotIn(live, src)

if __name__ == "__main__":
    unittest.main(verbosity=1)
