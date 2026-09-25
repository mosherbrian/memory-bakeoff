#!/usr/bin/env python3
"""Adapted copies of the 7 retained R11 rest fixtures that fail against the
candidate with prose/next_action rows, migrated to the R18 structured
next_step + receipt schema. inputs/ untouched. CHECK defaults to candidate.
One INTENTIONAL behavior change is labeled: latest-invalid-overrides-old-valid
(R18 latest-row-governs; R11 kept the older valid row)."""
import json, os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CHECK = os.environ.get("R18_CHECK") or os.path.join(PKG, "candidate", "research-gap-check")
AD = os.path.expanduser("~/.config/agent-deck")
T0 = 1790300000
M = 60
def iso(t):
    return subprocess.run(["date","-u","-d",f"@{int(t)}","+%FT%TZ"],capture_output=True,text=True).stdout.strip()
class R11Adapted(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="r11a-")
        h = self.h = f"{self.d}/home"
        os.makedirs(f"{h}/.config/agent-deck"); os.makedirs(f"{h}/.local/share/agent-deck")
        for f in ("escalations","escalation-resolve","escalation-watch"):
            shutil.copy2(f"{AD}/{f}", f"{h}/.config/agent-deck/{f}")
        self.log = f"{self.d}/calls.log"
        def stub(name, body):
            open(f"{self.d}/{name}","w").write("#!/bin/sh\n"+body)
            os.chmod(f"{self.d}/{name}",0o755)
        stub("wake", f'echo "wake $1 :: $2" >> {self.log}\nexit ${{WAKE_RC:-0}}\n')
        stub("notify", f'b=$(cat); echo "notify $1 :: $b" >> {self.log}\nprintf %s "$b" | {h}/.config/agent-deck/escalations --add "$1" --source notify-claude >/dev/null\n')
        stub("status", f'[ -f {self.d}/status.fail ] && {{ echo boom >&2; exit 2; }}; cat {self.d}/status.json\n')
        os.makedirs(f"{self.d}/c4/packages")
        self.prio([("Q-A",1),("Q-B",2)]); self.live([])
        self._n = 0
    def tearDown(self): shutil.rmtree(self.d)
    def prio(self, items):
        json.dump({"items":[{"id":q,"rank":r,"status":rest[0] if rest else "open"} for q,r,*rest in items]},open(f"{self.d}/c4/RESEARCH-PRIORITIES.json","w"))
    def live(self, pkgs):
        json.dump({"packages":[{"qid":q,"step":s} for q,s in pkgs]},open(f"{self.d}/status.json","w"))
    def streams(self, rows):
        json.dump({"schema_version":1,"streams":rows},open(f"{self.d}/c4/RESEARCH-STREAMS.json","w"))
    AB=[{"stream_id":"A","question_id":"Q-A","status":"active"},{"stream_id":"B","question_id":"Q-B","status":"active"}]
    def mkrow(self, q="Q-A", entered=-60, dur=20*M, act=None, kind="search", owner="tern", obj="scope trial search"):
        self._n += 1
        act = act or f"step-{self._n}"
        dl = iso(T0+dur-60 if dur>0 else T0-120)
        rp = f"rcpt/{act}.json"
        p = f"{self.d}/c4/{rp}"; os.makedirs(os.path.dirname(p),exist_ok=True)
        json.dump({"question_id":q,"action_id":act,"owner":owner,"deadline":dl,"objective":obj},open(p,"w"))
        return {"question_id":q,"reason":"r","owner":"tern","entered_at":iso(T0+entered),"revisit_at":iso(T0+dur),
                "next_step":{"action_id":act,"kind":kind,"owner":owner,"deadline":dl,"objective":obj,"receipt_path":rp}}
    def rest(self, *rows):
        open(f"{self.d}/c4/REST.jsonl","a").write("".join((r if isinstance(r,str) else json.dumps(r))+"\n" for r in rows))
    def check(self, t, **env):
        e = dict(os.environ,HOME=self.h,GAP_NOW=str(t),GAP_CAMPAIGN=f"{self.d}/c4",GAP_STATUS_CMD=f"{self.d}/status",GAP_WAKE=f"{self.d}/wake",GAP_NOTIFY=f"{self.d}/notify",**env)
        r = subprocess.run([sys.executable,CHECK],env=e,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr); return r.stdout
    def ledger(self):
        p=f"{self.h}/.local/share/agent-deck/escalations.jsonl"
        return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
    def raised(self): return [r for r in self.ledger() if "id" in r]
    def by_q(self,q): return [r for r in self.raised() if f"question {q} " in r["text"] or f"GAP-{q}-" in r["text"]]
    # 1. expired rest -> ladder, reason cites expiry
    def test_expired_rest(self):
        row = self.mkrow(entered=-3600, dur=0)
        row["revisit_at"] = iso(T0); row["next_step"]["deadline"] = iso(T0-120)
        rp = row["next_step"]["receipt_path"]
        rec = json.load(open(f"{self.d}/c4/{rp}")); rec["deadline"] = iso(T0-120); json.dump(rec, open(f"{self.d}/c4/{rp}","w"))
        self.rest(row)
        out = self.check(T0)
        self.assertIn("gap 0m", out)
        self.check(T0+30*M)
        self.assertEqual(len(self.raised()),1)
        self.assertIn("rest expired", self.raised()[0]["text"])
    # 2. CHANGED BEHAVIOR (R18 latest-row-governs): newer invalid row overrides older valid
    def test_latest_invalid_overrides_old_valid_changed(self):
        good = self.mkrow(dur=10*M)
        bad = dict(good); bad = json.loads(json.dumps(good))
        bad["revisit_at"] = ""
        self.rest(good, bad, "{not json")
        out = self.check(T0)
        self.assertIn("gap 0m", out, "latest row is invalid -> no rest even though an older valid row exists (R18 change)")
        self.check(T0+30*M)
        t = self.raised()[0]["text"]
        self.assertIn("not JSON", t)
    # 3. independent rest and expiry per stream
    def test_r11_independent_rest_and_expiry(self):
        self.streams(self.AB)
        self.rest(self.mkrow(q="Q-B", dur=20*M))
        self.check(T0); self.check(T0+20*M); self.check(T0+30*M)
        self.assertEqual(len(self.by_q("Q-A")), 1)
        self.assertEqual(len(self.by_q("Q-B")), 0)
        self.check(T0+49*M)
        self.assertEqual(len(self.by_q("Q-B")), 0)
        self.check(T0+50*M)
        self.assertEqual(len(self.by_q("Q-B")), 1)
    def _quiet_B_then(self, rows_after):
        self.streams(self.AB)
        self.rest(self.mkrow(q="Q-B", dur=20*M))
        self.assertIn("Q-B: ok (rest", self.check(T0))
        self.streams(rows_after)
        out = self.check(T0 + 10 * M)
        self.assertIn("Q-B: ok (rest", out)
        self.check(T0 + 20 * M)
        self.check(T0 + 49 * M)
        self.assertEqual(len(self.by_q("Q-B")), 0)
        self.check(T0 + 50 * M)
        return self.by_q("Q-B")
    def test_r11_quiet_stream_removed_still_watched(self):
        got = self._quiet_B_then([self.AB[0]])
        self.assertEqual(len(got), 1)
        self.assertIn("not an active registered stream", got[0]["text"])
    def test_r11_quiet_stream_set_inactive_still_watched(self):
        self.assertEqual(len(self._quiet_B_then([self.AB[0], dict(self.AB[1], status="inactive")])), 1)
    def test_r11_quiet_stream_retired_stops_watch(self):
        self.streams(self.AB)
        self.rest(self.mkrow(q="Q-B", dur=20*M))
        self.assertIn("Q-B: ok (rest", self.check(T0))
        self.streams([self.AB[0], dict(self.AB[1], status="retired", retired_at=iso(T0 + 5 * M), by="tern", reason="done")])
        for t in (T0 + 10 * M, T0 + 20 * M, T0 + 50 * M, T0 + 90 * M):
            self.assertNotIn("Q-B", self.check(t))
        self.assertEqual(self.by_q("Q-B"), [])
    # 7. valid rest quiet (window within 7200s)
    def test_valid_rest_is_quiet(self):
        self.rest(self.mkrow(dur=100*M))
        for t in (T0, T0 + 60 * M, T0 + 99 * M):
            self.assertIn("ok (rest", self.check(t))
        self.assertEqual(self.raised(), [])
if __name__=="__main__": unittest.main(verbosity=2)
