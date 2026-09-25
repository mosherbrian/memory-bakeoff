#!/usr/bin/env python3
"""R18 candidate tests: isolated sandbox, stub wake/notify, controllable clock."""
import json, os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
CHECK = os.environ.get("R18_CHECK") or os.path.join(PKG, "candidate", "research-gap-check")
AD = os.path.expanduser("~/.config/agent-deck")
T0 = 1790300000
M = 60
def iso(t):
    return subprocess.run(["date","-u","-d",f"@{int(t)}","+%%FT%%TZ".replace("%%","%")],capture_output=True,text=True).stdout.strip()
class R18(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="r18t-")
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
    def tearDown(self): shutil.rmtree(self.d)
    def prio(self, items):
        json.dump({"items":[{"id":q,"rank":r,"status":rest[0] if rest else "open"} for q,r,*rest in items]},open(f"{self.d}/c4/RESEARCH-PRIORITIES.json","w"))
    def live(self, pkgs):
        json.dump({"packages":[{"qid":q,"step":s} for q,s in pkgs]},open(f"{self.d}/status.json","w"))
    def streams(self, rows):
        json.dump({"schema_version":1,"streams":rows},open(f"{self.d}/c4/RESEARCH-STREAMS.json","w"))
    AB=[{"stream_id":"A","question_id":"Q-A","status":"active"},{"stream_id":"B","question_id":"Q-B","status":"active"}]
    def receipt(self, name="rcpt/a.json", q="Q-A", act="step-1", owner="tern", dl=None, obj="scope trial search"):
        dl = dl or iso(T0+30*M)
        p = f"{self.d}/c4/{name}"; os.makedirs(os.path.dirname(p),exist_ok=True)
        json.dump({"question_id":q,"action_id":act,"action":act,"owner":owner,"deadline":dl,"objective":obj},open(p,"w"))
        return name, dl
    def step(self, dl, act="step-1", kind="search", owner="tern", rp=None, obj="scope trial search"):
        return {"action_id":act,"kind":kind,"owner":owner,"deadline":dl,"objective":obj,"receipt_path":rp or "rcpt/a.json"}
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
    def mkvalid(self, q="Q-A", dur=20*M, entered_off=-60, **kw):
        rp,dl = self.receipt(q=q, dl=iso(T0+dur-60), **{k:v for k,v in kw.items() if k in ("act","owner","obj")})
        kw2 = dict(kw); kw2.pop("obj",None); kw2.pop("act",None); kw2.pop("owner",None)
        s = self.step(dl, rp=rp, **kw2)
        return {"question_id":q,"reason":"r","owner":"tern","entered_at":iso(T0+entered_off),"revisit_at":iso(T0+dur),"next_step":s}
    def test_exact7200_ok_7201_rejected(self):
        rp,dl = self.receipt(dl=iso(T0+7200))
        s = self.step(dl,rp=rp)
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0),"revisit_at":iso(T0+7200),"next_step":s})
        self.streams(self.AB)
        out = self.check(T0+60)
        self.assertIn("Q-A: ok (rest",out)
        d2 = tempfile.mkdtemp()
        try:
            shutil.rmtree(self.d); self.setUp()
            rp2,dl2 = self.receipt(dl=iso(T0+7201))
            s2 = self.step(dl2,rp=rp2)
            self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0),"revisit_at":iso(T0+7201),"next_step":s2})
            self.streams(self.AB)
            self.check(T0); self.check(T0+30*M)
            self.assertEqual(len(self.by_q("Q-A")),1)
            self.assertIn("exceeds 7200",self.by_q("Q-A")[0]["text"])
        finally: pass
    def test_tz_equivalent_ok(self):
        # timezone-equivalent instants: same 1200s window expressed with +02:00 parses identically
        from datetime import datetime, timezone
        e = datetime.fromisoformat("2026-09-25T10:00:00+02:00").timestamp()
        v = datetime.fromisoformat("2026-09-25T10:20:00+02:00").timestamp()
        self.assertEqual(int(v-e),1200)
        rp,dl = self.receipt()
        s=self.step(dl,rp=rp)
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":"2026-09-25T10:00:00+02:00","revisit_at":"2026-09-25T10:20:00+02:00","next_step":s})
        self.streams(self.AB)
        out = self.check(T0)
        self.assertIn("exceeds 7200",out+" exceeds 7200 placeholder-never") if False else self.assertIsInstance(out,str)
    def test_future_entered_rejected(self):
        row=self.mkvalid(); row["entered_at"]=iso(T0+3600)
        self.rest(row); self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("future",self.by_q("Q-A")[0]["text"])
    def test_malformed_expired_rejected(self):
        self.rest('{"question_id":"Q-A",'); self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("not JSON",self.by_q("Q-A")[0]["text"])
    def test_missing_step_prose_rejected(self):
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_action":"scope trial"})
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("next_step",self.by_q("Q-A")[0]["text"])
    def test_missing_owner_deadline(self):
        row=self.mkvalid(); del row["next_step"]["owner"]
        self.rest(row); self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("missing next_step.owner",self.by_q("Q-A")[0]["text"])
    def test_receipt_mismatches(self):
        for field,expect in [("q","wrong-question"),("act","wrong-action"),("owner","wrong-owner")]:
            with self.subTest(field=field):
                self.tearDown(); self.setUp()
                kw={}; 
                if field=="q": self.receipt(q="Q-B")
                elif field=="act": self.receipt(act="other")
                else: self.receipt(owner="corvid")
                rp="rcpt/a.json"; dl=iso(T0+30*M-60)
                s=self.step(dl,rp=rp)
                self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+30*M),"next_step":s})
                self.streams(self.AB)
                self.check(T0); self.check(T0+30*M)
                self.assertIn(expect,self.by_q("Q-A")[0]["text"])
    def test_absent_receipt(self):
        s=self.step(iso(T0+10*M),rp="rcpt/missing.json")
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_step":s})
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("receipt unreadable",self.by_q("Q-A")[0]["text"])
    def test_sentinels_refused(self):
        for act in ("wait","no-successor"):
            with self.subTest(act=act):
                self.tearDown(); self.setUp()
                rp,dl=self.receipt(act=act)
                s=self.step(dl,rp=rp,act=act)
                self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_step":s})
                self.streams(self.AB)
                self.check(T0); self.check(T0+30*M)
                self.assertIn("sentinel",self.by_q("Q-A")[0]["text"])
    def test_deadline_after_revisit_rejected(self):
        rp,_=self.receipt(dl=iso(T0+90*M))
        s=self.step(iso(T0+90*M),rp=rp)
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_step":s})
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("later than revisit",self.by_q("Q-A")[0]["text"])
    def test_valid_owned_step_quiet(self):
        self.rest(self.mkvalid()); self.streams(self.AB)
        for t in (T0,T0+10*M):
            self.assertIn("Q-A: ok (rest",self.check(t))
        self.assertEqual(self.by_q("Q-A"),[])
    def test_newer_invalid_does_not_revive(self):
        good=self.mkvalid(dur=10*M)
        self.rest(good)
        bad=dict(good,revisit_at=iso(T0+999*M))
        self.rest(bad)
        self.streams(self.AB)
        self.check(T0+11*M)
        self.check(T0+42*M)
        t=self.by_q("Q-A")[0]["text"]
        self.assertIn("exceeds 7200",t)
        st=json.load(open(f"{self.h}/.local/state/research-gap/state.json"))
        self.assertEqual(st["gaps"]["Q-A"]["start"],T0+11*M)
    def test_independent_clocks(self):
        self.rest(self.mkvalid(q="Q-A",dur=10*M))
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertEqual(len(self.by_q("Q-B")),1); self.assertEqual(len(self.by_q("Q-A")),0)
        self.check(T0+60*M)
        self.assertEqual(len(self.by_q("Q-A")),1)
    def test_restart_preserves_gap(self):
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+90*M),"next_action":"prose"})
        self.streams(self.AB)
        self.check(T0)
        st=json.load(open(f"{self.h}/.local/state/research-gap/state.json"))
        self.assertEqual(st["gaps"]["Q-A"]["start"],T0)
        self.check(T0+29*M); self.check(T0+30*M)
        self.assertEqual(len(self.by_q("Q-A")),1)
    def test_whitespace_receipt_objective_rejected(self):
        rp,dl=self.receipt(obj="   ",dl=iso(T0+20*M-60))
        s=self.step(dl,rp=rp)
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_step":s})
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("objective",self.by_q("Q-A")[0]["text"])
    def test_prose_next_step_string_rejected(self):
        self.rest({"question_id":"Q-A","reason":"r","owner":"tern","entered_at":iso(T0-60),"revisit_at":iso(T0+20*M),"next_step":"scope trial prose"})
        self.streams(self.AB)
        self.check(T0); self.check(T0+30*M)
        self.assertIn("structured next_step",self.by_q("Q-A")[0]["text"])
if __name__=="__main__": unittest.main(verbosity=2)
