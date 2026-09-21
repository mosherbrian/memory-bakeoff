"""Group 1+2: lifecycle semantics + repair/exhaustion/negative/9a cases.

Fake clock = fixed ISO strings passed as ``now``. No sleeps.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.lifecycle import apply, new_revision, TransitionError

T = "2026-09-21T17:00:00Z"
D = "2026-09-21T17:30:00Z"
BUDGET = {"attempts": 1, "repairs": 1, "verifier_s": 1800}
W = {"seat": "kiln", "role": "worker"}
V = {"seat": "corvid", "role": "verifier"}
DR = {"seat": "tern", "role": "director"}
DU = {"seat": "cairn", "role": "duty"}
RD = {"seat": "corvid", "role": "reader"}


def E(eid, typ, actor, at=T, **kw):
    d = {"event_id": eid, "type": typ, "actor": actor, "at": at}
    d.update(kw)
    return d


def drive(events, budget=None):
    st = new_revision("Q")
    outs = []
    for e in events:
        st, out = apply(st, e, e["at"], budget or BUDGET)
        outs.append(out)
    return st, outs


def registered(st):
    for i, (typ, actor) in enumerate(
            [("admit", RD), ("authorize", DR), ("start", DU)]):
        kw = {"deadline": D, "action_id": "a1"} if typ == "start" else {}
        st, _ = apply(st, E("r%d" % i, typ, actor, **kw), T, BUDGET)
    return st


class TestLifecycle(unittest.TestCase):
    def test_happy_path_completes(self):
        st = registered(new_revision("Q"))
        st, o = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        self.assertEqual(o, "checking")
        st, o = apply(st, E("v", "verify_pass", V, finding="positive", elapsed_s=300), T, BUDGET)
        self.assertEqual((st["phase"], o), ("COMPLETE", "complete"))

    def test_valid_negative_completes_not_exhausts(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, o = apply(st, E("v", "verify_pass", V, finding="negative", elapsed_s=300), T, BUDGET)
        self.assertEqual(st["phase"], "COMPLETE")
        self.assertEqual(st["finding"], "negative")

    def test_repair_then_exhausted_no_allocation(self):
        # r1 shape: fail w/ eligible repair -> repair -> fail again -> 9a.
        st = registered(new_revision("Q"))
        st["worker_seat"] = "kiln"
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, o = apply(st, E("v1", "verify_fail", V, eligible_repair=True, elapsed_s=300), T, BUDGET)
        self.assertEqual(o, "repair-allowed")
        st, o = apply(st, E("al", "alloc_repair", DU), T, BUDGET)
        st, o = apply(st, E("s2", "start", DU, deadline=D, action_id="a2"), T,
                      {"attempts": 2, "repairs": 1, "verifier_s": 1800})
        st, _ = apply(st, E("p2", "publish", W, artifact_hashes=["h2"], handoff_deadline="2026-09-21T18:00:00Z"), T,
                      {"attempts": 2, "repairs": 1, "verifier_s": 1800})
        st, o = apply(st, E("v2", "verify_fail", V, eligible_repair=True,
                            reason="still-broken", elapsed_s=300), T,
                      {"attempts": 2, "repairs": 1, "verifier_s": 1800})
        self.assertEqual((st["phase"], o), ("EXHAUSTED", "exhausted"))

    def test_fail_without_repair_budget_exhausts_directly(self):
        st = registered(new_revision("Q"))
        st["worker_seat"] = "kiln"
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, o = apply(st, E("v", "verify_fail", V, eligible_repair=False,
                            reason="acceptance-withheld", elapsed_s=300), T, BUDGET)
        self.assertEqual((st["phase"], st["why_ended"], o),
                         ("EXHAUSTED", "acceptance-withheld", "exhausted"))

    def test_worker_cannot_self_verify(self):
        st = registered(new_revision("Q"))
        st["worker_seat"] = "kiln"
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("v", "verify_pass", {"seat": "kiln", "role": "verifier"}, elapsed_s=300),
                  T, BUDGET)
        self.assertEqual(cm.exception.code, "E_SELF_VERIFY")

    def test_unauthorized_role_fails_closed(self):
        with self.assertRaises(TransitionError) as cm:
            apply(new_revision("Q"), E("x", "admit", W), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_UNAUTHORIZED")

    def test_start_without_deadline_rejected(self):
        st = new_revision("Q")
        st, _ = apply(st, E("a", "admit", RD), T, BUDGET)
        st, _ = apply(st, E("u", "authorize", DR), T, BUDGET)
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("s", "start", DU), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_NO_DEADLINE")

    def test_late_publish_is_leftover(self):
        st = registered(new_revision("Q"))
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"),
                  "2026-09-21T18:00:00Z", BUDGET)
        self.assertEqual(cm.exception.code, "E_DEADLINE_EXPIRED")

    def test_blocked_verification_returns_to_checking_same_attempt(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, o = apply(st, E("i", "interrupt", DU, reason="hash-mismatch",
                            remaining_verifier_s=600), T, BUDGET)
        self.assertEqual(o, "blocked")
        self.assertEqual(st["blocked"]["phase"], "CHECKING")
        before = st["attempt"]
        st, o = apply(st, E("r", "resolve", DU), T, BUDGET)
        self.assertEqual((st["phase"], st["attempt"], o),
                         ("CHECKING", before, "resumed-checking"))

    def test_expired_verification_needs_grant(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, _ = apply(st, E("i", "interrupt", DU, remaining_verifier_s=0),
                      T, BUDGET)
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("r", "resolve", DU), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_NO_ALLOCATION")
        # Free-form grants are rejected: allocation shape required.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("r9", "resolve", DU, new_allocation="10m"), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_BAD_ALLOCATION")
        # Unattributed grants are rejected.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("r8", "resolve", DU,
                        new_allocation={"grant_s": 600}), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_BAD_ALLOCATION")
        st, o = apply(st, E("r2", "resolve", DU, new_allocation={
            "grant_s": 600, "granted_by": "tern"}), T, BUDGET)
        self.assertEqual(o, "resumed-checking")

    def test_verifier_spend_enforced(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        # Missing elapsed_s fails closed.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("v", "verify_pass", V), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_BAD_ALLOCATION")
        # Spend beyond the pass budget is rejected.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("v", "verify_pass", V, elapsed_s=9999,
                        pass_budget_s=1800), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_ALLOC_EXCEEDED")
        # A pass budget above the per-pass ceiling is rejected.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("v", "verify_pass", V, elapsed_s=100,
                        pass_budget_s=99999), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_ALLOC_EXCEEDED")

    def test_controller_recovery_deviation_rejected(self):
        # The P2 r2.1 archive-recheck shape: a recorded 20-minute
        # controller-recovery pass. The 10-minute per-pass ceiling holds
        # regardless of any cumulative campaign ceiling.
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, _ = apply(st, E("i", "interrupt", DU, reason="x"), T, BUDGET)
        big = {"attempts": 5, "repairs": 5, "verifier_s": 99999,
               "passes": {"verify": {"max_s": 99999},
                          "controller_recovery": {"max_s": 99999}}}
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("rc", "recover", DU, elapsed_s=1200,
                        pass_budget_s=1200), T, big)
        self.assertEqual(cm.exception.code, "E_ALLOC_EXCEEDED")
        st, o = apply(st, E("rc", "recover", DU, elapsed_s=480,
                            pass_budget_s=600), T, big)
        self.assertEqual(o, "recovery-recorded")
        # Elapsed beyond even an allowed budget is rejected.
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("rc2", "recover", DU, elapsed_s=601,
                        pass_budget_s=600), T, big)
        self.assertEqual(cm.exception.code, "E_ALLOC_EXCEEDED")

    def test_amend_supersedes_preserves_question(self):
        st = registered(new_revision("Q"))
        st, o = apply(st, E("m", "amend", DR, new_revision=2), T, BUDGET)
        self.assertEqual((st["phase"], st["question_id"], o),
                         ("SUPERSEDED", "Q", "superseded"))

    def test_terminal_has_no_execution_exit(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, _ = apply(st, E("v", "verify_pass", V, elapsed_s=300), T, BUDGET)
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("s", "start", DU, deadline=D), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_TERMINAL")

    def test_flight_rotates_on_publish(self):
        st = registered(new_revision("Q"))
        self.assertEqual(st["flight"]["action_id"], "a1")
        st, o = apply(st, E("p", "publish", W, artifact_hashes=["h"],
                            verify={"action_id": "vv1", "owner": "corvid",
                                    "deadline": "2026-09-21T17:25:00Z"}),
                      T, BUDGET)
        self.assertEqual(o, "checking")
        # Worker flight is gone; the verifier's own bounded action stands.
        self.assertEqual(st["flight"],
                         {"action_id": "vv1", "owner": "corvid",
                          "deadline": "2026-09-21T17:25:00Z"})
        self.assertIsNone(st["handoff"])

    def test_publish_without_verifier_needs_bounded_handoff(self):
        st = registered(new_revision("Q"))
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("p", "publish", W, artifact_hashes=["h"]), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_BAD_ALLOCATION")
        st, o = apply(st, E("p", "publish", W, artifact_hashes=["h"],
                            handoff_deadline="2026-09-21T17:20:00Z"), T, BUDGET)
        self.assertEqual(o, "checking")
        self.assertIsNone(st["flight"])
        self.assertEqual(st["handoff"],
                         {"owner": "duty",
                          "deadline": "2026-09-21T17:20:00Z"})

    def test_blocked_preserves_verifier_flight(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"],
                            verify={"action_id": "vv1", "owner": "corvid",
                                    "deadline": "2026-09-21T17:25:00Z"}),
                      T, BUDGET)
        st, _ = apply(st, E("i", "interrupt", DU, reason="x",
                            remaining_verifier_s=600), T, BUDGET)
        self.assertEqual(st["phase"], "BLOCKED")
        self.assertEqual(st["flight"]["action_id"], "vv1")
        st, o = apply(st, E("r", "resolve", DU), T, BUDGET)
        self.assertEqual((st["phase"], o), ("CHECKING", "resumed-checking"))
        self.assertEqual(st["flight"]["action_id"], "vv1",
                         "same action/allocation after resume")

    def test_decide_needs_enumerable_kind(self):
        st = registered(new_revision("Q"))
        st, _ = apply(st, E("p", "publish", W, artifact_hashes=["h"], handoff_deadline="2026-09-21T18:00:00Z"), T, BUDGET)
        st, _ = apply(st, E("v", "verify_pass", V, elapsed_s=300), T, BUDGET)
        with self.assertRaises(TransitionError) as cm:
            apply(st, E("d", "decide", DR,
                        disposition={"kind": "done-ish"}), T, BUDGET)
        self.assertEqual(cm.exception.code, "E_MISSING_DISPOSITION")
        st, o = apply(st, E("d2", "decide", DR, disposition={
            "kind": "question_answered", "decision_ref": "x",
            "reason": "y", "evidence_refs": ["h"]}), T, BUDGET)
        self.assertEqual(o, "closed-question_answered")


if __name__ == "__main__":
    unittest.main()
