#!/usr/bin/env python3
"""R5 planted-fault tests. Sandbox HOME with byte copies of the installed
escalations/escalation-resolve/escalation-watch; wake and the notify channel
are stubs, so nothing reaches a seat, a chat session or Signal. GAP_NOW is the
controllable clock; each check() is a fresh process, so every step is also a
restart."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.environ.get("R5_CHECK") or os.path.join(HERE, "research-gap-check")
AD = os.path.expanduser("~/.config/agent-deck")
T0 = 1790300000  # fixed epoch for the controllable clock
M = 60


def iso(t):
    return subprocess.run(["date", "-u", "-d", f"@{int(t)}", "+%FT%TZ"], capture_output=True, text=True).stdout.strip()


class Gap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="r5t-")
        h = self.h = f"{self.d}/home"
        os.makedirs(f"{h}/.config/agent-deck"); os.makedirs(f"{h}/.local/share/agent-deck")
        for f in ("escalations", "escalation-resolve", "escalation-watch"):
            shutil.copy2(f"{AD}/{f}", f"{h}/.config/agent-deck/{f}")
        self.log = f"{self.d}/calls.log"
        def stub(name, body):
            with open(f"{self.d}/{name}", "w") as f:
                f.write("#!/bin/sh\n" + body)
            os.chmod(f"{self.d}/{name}", 0o755)
        stub("wake", f'echo "wake $1 :: $2" >> {self.log}\nexit ${{WAKE_RC:-0}}\n')
        stub("notify", f'b=$(cat); echo "notify $1 :: $b" >> {self.log}\nprintf %s "$b" | {h}/.config/agent-deck/escalations --add "$1" --source notify-claude >/dev/null\n')
        stub("status", f'[ -f {self.d}/status.fail ] && {{ echo boom >&2; exit 2; }}; cat {self.d}/status.json\n')
        os.makedirs(f"{self.d}/c4/packages")
        self.prio([("Q-A", 1), ("Q-B", 2)])
        self.live([])

    def tearDown(self):
        shutil.rmtree(self.d)

    def prio(self, items):
        json.dump({"items": [{"id": q, "rank": r, "status": s} for q, r, *rest in items for s in [rest[0] if rest else "open"]]},
                  open(f"{self.d}/c4/RESEARCH-PRIORITIES.json", "w"))

    def live(self, pkgs):
        json.dump({"packages": [{"qid": q, "step": s} for q, s in pkgs]}, open(f"{self.d}/status.json", "w"))

    def bind(self, pkg, q, name="dispatch-receipt.json", stream=None):
        os.makedirs(f"{self.d}/c4/packages/{pkg}", exist_ok=True)
        rec = {"package_id": pkg, "question_id": q} | ({"stream_id": stream} if stream else {})
        json.dump(rec, open(f"{self.d}/c4/packages/{pkg}/{name}", "w"))

    def streams(self, rows=None, raw=None):
        with open(f"{self.d}/c4/RESEARCH-STREAMS.json", "w") as f:
            f.write(raw if raw is not None else json.dumps({"schema_version": 1, "streams": rows}))

    AB = [{"stream_id": "A", "question_id": "Q-A", "status": "active"},
          {"stream_id": "B", "question_id": "Q-B", "status": "active"}]

    def by_q(self, q):
        return [r for r in self.raised() if f"question {q} " in r["text"] or f"GAP-{q}-" in r["text"]]

    def rest(self, *rows):
        with open(f"{self.d}/c4/REST.jsonl", "a") as f:
            for r in rows:
                f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")

    def check(self, t, **env):
        e = dict(os.environ, HOME=self.h, GAP_NOW=str(t), GAP_CAMPAIGN=f"{self.d}/c4", GAP_STATUS_CMD=f"{self.d}/status",
                 GAP_WAKE=f"{self.d}/wake", GAP_NOTIFY=f"{self.d}/notify", **env)
        r = subprocess.run([sys.executable, CHECK], env=e, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def ledger(self):
        p = f"{self.h}/.local/share/agent-deck/escalations.jsonl"
        return [json.loads(l) for l in open(p)] if os.path.exists(p) else []

    def raised(self):
        return [r for r in self.ledger() if "id" in r]

    def calls(self):
        return open(self.log).read().splitlines() if os.path.exists(self.log) else []

    def ladder(self):
        """Walk the exact thresholds; return nothing, assert everything."""
        self.check(T0)
        self.check(T0 + 30 * M - 1)
        self.assertEqual(self.raised(), [], "no notice before 30 min")
        self.check(T0 + 30 * M)
        self.assertEqual(len(self.raised()), 1)
        self.assertIn("owner tern", self.raised()[0]["text"])
        self.assertTrue(any(c.startswith("wake tern") for c in self.calls()))
        self.check(T0 + 45 * M - 1)
        self.assertEqual(len(self.raised()), 1, "no escalation before 15 more min")
        self.check(T0 + 45 * M)
        self.assertEqual(len(self.raised()), 2)
        self.assertIn("ESCALATED", self.raised()[1]["text"])

    # -- faults that must open the gap ---------------------------------------
    def test_no_package_thresholds_30_then_15(self):
        self.ladder()
        self.check(T0 + 90 * M)
        self.assertEqual(len(self.raised()), 2, "restarts never duplicate the incident or escalation")
        self.assertEqual(sum(c.startswith("wake") for c in self.calls()), 1)

    def test_missing_rest_file_is_no_rest(self):
        self.assertFalse(os.path.exists(f"{self.d}/c4/REST.jsonl"))
        self.ladder()

    def test_expired_rest(self):
        self.rest({"question_id": "Q-A", "reason": "r", "owner": "tern", "entered_at": iso(T0 - 3600),
                   "revisit_at": iso(T0), "next_action": "n"})
        out = self.check(T0)
        self.assertIn("gap 0m", out)
        self.ladder()
        self.assertIn("rest expired", self.raised()[0]["text"])

    def test_missing_required_field_and_newer_bad_row_does_not_extend(self):
        good = {"question_id": "Q-A", "reason": "r", "owner": "tern", "entered_at": iso(T0 - 60), "revisit_at": iso(T0 + 10 * M), "next_action": "n"}
        self.rest(good, {k: v for k, v in good.items() if k != "revisit_at"} | {"revisit_at": ""},
                  dict(good, revisit_at=iso(T0 + 999 * M), owner=""), "{not json")
        self.assertIn("ok (rest", self.check(T0))
        self.check(T0 + 10 * M)  # older valid rest expires; the bad newer rows did not extend it
        self.check(T0 + 40 * M)
        t = self.raised()[0]["text"]
        self.assertIn("missing revisit_at", t); self.assertIn("missing owner", t); self.assertIn("not JSON", t)

    def test_status_failure_is_unknown_not_rest(self):
        self.bind("P1", "Q-A"); self.live([("P1", "worker")])
        open(f"{self.d}/status.fail", "w").close()
        self.ladder()
        self.assertIn("agent-loop status failed", self.raised()[0]["text"])

    def test_unknown_binding_and_name_is_not_binding(self):
        self.live([("Q-A-lookalike", "worker"), ("P2", "worker")])  # no records bind either
        self.ladder()

    def test_contradictory_binding_is_unknown(self):
        self.bind("P1", "Q-A"); self.bind("P1", "Q-B", "other-receipt.json"); self.live([("P1", "worker")])
        self.ladder()
        self.assertIn("contradictory", self.raised()[0]["text"])

    def test_irrelevant_work_does_not_reset(self):
        self.bind("PB", "Q-B")
        self.check(T0)
        self.live([("PB", "worker")]); self.check(T0 + 20 * M)
        self.live([]); self.check(T0 + 30 * M)
        self.assertEqual(len(self.raised()), 1)

    def test_ack_is_not_closure(self):
        self.check(T0); self.check(T0 + 30 * M)
        subprocess.run([f"{self.h}/.config/agent-deck/escalations", "--ack", self.raised()[0]["id"], "--note", "seen"],
                       env=dict(os.environ, HOME=self.h), capture_output=True)
        self.check(T0 + 45 * M)
        self.assertEqual(len(self.raised()), 2)

    def test_restart_keeps_original_clock(self):
        self.check(T0)
        st = json.load(open(f"{self.h}/.local/state/research-gap/state.json"))
        self.assertEqual(st["gaps"]["Q-A"]["start"], T0)
        self.check(T0 + 29 * M); self.check(T0 + 30 * M)
        self.assertEqual(len(self.raised()), 1)

    def test_corrupt_state_is_reported_and_kept(self):
        os.makedirs(f"{self.h}/.local/state/research-gap")
        open(f"{self.h}/.local/state/research-gap/state.json", "w").write("{broken")
        self.check(T0)
        self.assertIn("UNKNOWN: gap state unreadable", self.raised()[0]["text"])
        self.assertTrue([f for f in os.listdir(f"{self.h}/.local/state/research-gap") if ".corrupt-" in f])

    def test_failed_wake_is_retried_next_tick(self):
        self.check(T0); self.check(T0 + 30 * M, WAKE_RC="1")
        self.check(T0 + 35 * M)
        self.assertEqual(sum(c.startswith("wake") for c in self.calls()), 2)
        self.assertEqual(len(self.raised()), 1)

    def test_top_switch_keeps_incident(self):
        self.check(T0); self.check(T0 + 30 * M)
        self.prio([("Q-A", 2), ("Q-B", 1)])
        out = self.check(T0 + 45 * M)
        self.assertIn("Q-A: escalated", out)

    # -- must stay quiet and close ---------------------------------------------
    def test_bound_executing_package_is_quiet(self):
        for step in ("worker", "verify"):
            self.bind("P1", "Q-A"); self.live([("P1", step)])
            for t in (T0, T0 + 30 * M, T0 + 60 * M):
                self.assertIn("ok (package P1)", self.check(t))
            self.assertEqual(self.raised(), [])

    # -- R5-repair-1 D2: only declared executing steps suppress the gap ----------
    def test_non_executing_steps_open_the_gap(self):
        for step in ("held", "blocked", "unknown", "decision", "handoff", ""):
            with self.subTest(step=step):
                self.tearDown(); self.setUp()
                self.bind("P1", "Q-A"); self.live([("P1", step)])
                self.ladder()

    # -- R5-repair-1 D1: open and active are unresolved; only answered/dropped close
    def test_active_top_question_is_tracked(self):
        self.prio([("Q-A", 1, "active"), ("Q-B", 2)])
        self.ladder()
        self.assertIn("Q-A", self.raised()[0]["text"])

    def test_open_to_active_keeps_incident(self):
        self.check(T0); self.check(T0 + 30 * M)
        self.prio([("Q-A", 1, "active"), ("Q-B", 2)])
        self.assertIn("Q-A: escalated", self.check(T0 + 45 * M))
        self.assertEqual([r for r in self.ledger() if "resolve" in r], [])

    def test_unknown_or_absent_status_does_not_close(self):
        self.check(T0); self.check(T0 + 30 * M)
        self.prio([("Q-A", 1, "weird"), ("Q-B", 2)])
        self.check(T0 + 35 * M)
        self.prio([("Q-B", 2)])  # Q-A vanished from the file
        out = self.check(T0 + 45 * M)
        self.assertIn("Q-A: escalated", out)
        self.assertEqual([r for r in self.ledger() if "resolve" in r], [])

    def test_dropped_closes(self):
        self.check(T0); self.check(T0 + 30 * M)
        self.prio([("Q-A", 1, "dropped"), ("Q-B", 2)])
        self.check(T0 + 35 * M)
        self.assertEqual(len([r for r in self.ledger() if "resolve" in r]), 1)

    def test_unreadable_priorities_gap_carries_to_top(self):
        open(f"{self.d}/c4/RESEARCH-PRIORITIES.json", "w").write("{")
        self.check(T0); self.check(T0 + 30 * M)
        self.assertIn("priorities unreadable", self.raised()[0]["text"])
        self.prio([("Q-A", 1), ("Q-B", 2)])
        self.assertIn("Q-A: escalated", self.check(T0 + 45 * M))
        self.assertEqual(len(self.raised()), 2)

    def test_bound_but_closed_or_timed_out_is_not_active(self):
        self.bind("P1", "Q-A"); self.bind("P2", "Q-A"); self.live([("P1", "closed"), ("P2", "timed-out")])
        self.ladder()

    def test_valid_rest_is_quiet(self):
        self.rest({"question_id": "Q-A", "reason": "waiting for R5", "owner": "tern", "entered_at": iso(T0 - 60),
                   "revisit_at": iso(T0 + 120 * M), "next_action": "scope trial"})
        for t in (T0, T0 + 60 * M, T0 + 119 * M):
            self.assertIn("ok (rest", self.check(t))
        self.assertEqual(self.raised(), [])

    def test_package_closes_incident_and_watch_stays_quiet(self):
        self.ladder()
        self.bind("P1", "Q-A"); self.live([("P1", "worker")])
        self.assertIn("ok (package P1)", self.check(T0 + 50 * M))
        res = [r for r in self.ledger() if "resolve" in r]
        self.assertEqual({r["resolve"] for r in res}, {r["key"] for r in self.raised()})
        w = subprocess.run([sys.executable, f"{self.h}/.config/agent-deck/escalation-watch"],
                           env=dict(os.environ, HOME=self.h, ESCALATION_GRACE_MIN="0"), capture_output=True, text=True)
        self.assertIn("0 unacked", w.stdout + w.stderr)
        self.live([]); self.check(T0 + 55 * M)  # a new gap starts fresh, as a new incident
        self.assertIn("gap 0m", self.check(T0 + 55 * M))

    def test_question_answered_closes(self):
        self.ladder()
        self.prio([("Q-A", 1, "answered"), ("Q-B", 2)])
        self.check(T0 + 50 * M)
        self.assertEqual(len([r for r in self.ledger() if "resolve" in r]), 2)

    # -- R11: explicit streams ----------------------------------------------------
    def test_r11_one_active_one_stalled(self):
        self.streams(self.AB); self.bind("PA", "Q-A", stream="A"); self.live([("PA", "worker")])
        for t in (T0, T0 + 30 * M, T0 + 45 * M):
            out = self.check(t)
        self.assertIn("Q-A: ok (package PA)", out)
        self.assertEqual(len(self.by_q("Q-A")), 0)
        self.assertEqual(len(self.by_q("Q-B")), 2, "stalled lower-ranked stream B gets notice and escalation")
        self.assertIn("stream B question Q-B", self.by_q("Q-B")[0]["text"])

    def test_r11_inactive_stream_not_tracked(self):
        self.streams([self.AB[0], dict(self.AB[1], status="inactive")])
        self.check(T0); self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-B")), 0)
        self.assertEqual(len(self.by_q("Q-A")), 1)

    def test_r11_independent_rest_and_expiry(self):
        self.streams(self.AB)
        self.rest({"question_id": "Q-B", "reason": "r", "owner": "tern", "entered_at": iso(T0 - 60), "revisit_at": iso(T0 + 20 * M), "next_action": "n"})
        self.check(T0); self.check(T0 + 20 * M); self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-A")), 1)
        self.assertEqual(len(self.by_q("Q-B")), 0, "B rested until +20m; its own clock starts at that tick")
        self.check(T0 + 49 * M)
        self.assertEqual(len(self.by_q("Q-B")), 0)
        self.check(T0 + 50 * M)
        self.assertEqual(len(self.by_q("Q-B")), 1)

    def test_r11_cross_binding_is_unknown(self):
        self.streams(self.AB); self.bind("PX", "Q-B", stream="A"); self.live([("PX", "worker")])
        self.check(T0); self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-B")), 1)
        self.assertIn("contradictory", self.by_q("Q-B")[0]["text"])

    def test_r11_package_for_A_does_not_quiet_B(self):
        self.streams(self.AB); self.bind("PA", "Q-A"); self.live([("PA", "verify")])
        self.check(T0); self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-B")), 1)
        self.assertEqual(len(self.by_q("Q-A")), 0)

    def test_r11_removed_stream_keeps_incident(self):
        self.streams(self.AB)
        self.check(T0); self.check(T0 + 30 * M)
        self.streams([self.AB[0]])  # B dropped with no retirement record
        self.bind("PA", "Q-A"); self.live([("PA", "worker")])
        out = self.check(T0 + 45 * M)
        self.assertIn("Q-B: escalated", out)
        self.assertNotIn("Q-B", " ".join(r["resolve"] for r in self.ledger() if "resolve" in r))

    def test_r11_retirement_resolves_only_that_stream(self):
        self.streams(self.AB)
        self.check(T0); self.check(T0 + 30 * M)
        self.streams([self.AB[0], dict(self.AB[1], status="retired", retired_at=iso(T0 + 31 * M), by="tern", reason="dropped")])
        out = self.check(T0 + 35 * M)
        self.assertNotIn("Q-B:", out)
        self.assertIn("Q-A: tern notified", out)
        res = {r["resolve"] for r in self.ledger() if "resolve" in r}
        self.assertEqual(res, {r["key"] for r in self.by_q("Q-B")})

    def test_r11_retirement_without_fields_is_bad_registry(self):
        self.streams(self.AB)
        self.check(T0); self.check(T0 + 30 * M)
        self.streams([self.AB[0], dict(self.AB[1], status="retired")])
        out = self.check(T0 + 45 * M)
        self.assertIn("Q-B: escalated", out)
        self.assertIn("unusable", self.raised()[-1]["text"])

    def test_r11_two_clocks_through_restart(self):
        self.streams(self.AB); self.bind("PA", "Q-A"); self.live([("PA", "worker")])
        self.check(T0)
        self.live([]); self.check(T0 + 10 * M)  # A's clock starts 10 min after B's
        self.check(T0 + 30 * M)
        self.assertEqual((len(self.by_q("Q-A")), len(self.by_q("Q-B"))), (0, 1))
        self.check(T0 + 40 * M)
        self.assertEqual((len(self.by_q("Q-A")), len(self.by_q("Q-B"))), (1, 1))
        self.check(T0 + 90 * M)
        self.assertEqual((len(self.by_q("Q-A")), len(self.by_q("Q-B"))), (2, 2), "no duplicates after many restarts")

    def test_r11_bad_registry_keeps_legacy_and_existing(self):
        self.streams(raw="{not json")
        self.bind("PA", "Q-A"); self.live([("PA", "worker")])
        self.check(T0); self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-A")), 1, "an unusable registry is owned, not quiet")
        self.assertIn("unusable", self.by_q("Q-A")[0]["text"])

    def test_r11_unknown_status_and_duplicates_are_bad(self):
        for rows in ([dict(self.AB[0], status="paused")], [self.AB[0], dict(self.AB[1], question_id="Q-A")]):
            with self.subTest(rows=rows):
                self.tearDown(); self.setUp()
                self.streams(rows); self.check(T0); self.check(T0 + 30 * M)
                self.assertIn("unusable", self.raised()[0]["text"])

    def test_r11_migration_keeps_legacy_clock(self):
        self.check(T0)  # R5 legacy: Q-A gap starts at T0
        self.streams([dict(self.AB[0]), dict(self.AB[1], status="inactive")])
        self.check(T0 + 29 * M)
        self.assertEqual(self.raised(), [])
        self.check(T0 + 30 * M)
        self.assertEqual(len(self.by_q("Q-A")), 1, "clock from T0 survives adopting the registry")

    def test_r11_no_package_either_stream(self):
        self.streams(self.AB)
        for t in (T0, T0 + 30 * M, T0 + 45 * M):
            self.check(t)
        self.assertEqual((len(self.by_q("Q-A")), len(self.by_q("Q-B"))), (2, 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
