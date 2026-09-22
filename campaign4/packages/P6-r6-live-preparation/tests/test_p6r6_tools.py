"""P6-r6 candidate tool tests: injected OS boundaries + private tmp only.
No real seats/services; live launcher never touched (AGENTDECK_PROFILE
unset here; all launcher reads use --inject-list)."""
import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
WL = "/home/bmosher/.config/agent-deck/acp-go"
VL = "/home/bmosher/.config/agent-deck/acp-go-deepseek"


def mkfixture(sock_real=True, title_ok=True, with_stream=True,
              src="dry-run-injected"):
    tmp = tempfile.mkdtemp(prefix="p6r6-")
    sockd = os.path.join(tmp, "sock")
    streamd = os.path.join(tmp, "stream")
    os.makedirs(sockd)
    os.makedirs(streamd)
    names = ["p6-fixture-worker", "p6-fixture-verifier"]
    lst = []
    for n in names:
        lst.append({"id": n, "title": n if title_ok else "other-" + n,
                    "path": "/tmp/x", "tool": "shell", "profile": "campaign4",
                    "command": WL if "worker" in n and "verifier" not in n
                    else VL, "status": "idle"})
    lst[0]["command"] = WL
    lst[1]["command"] = VL
    lf = os.path.join(tmp, "list.json")
    json.dump(lst, open(lf, "w"))
    socks = []
    for n in names:
        p = os.path.join(sockd, n + ".sock")
        if sock_real:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.bind(p)
            socks.append(s)
        else:
            open(p, "w").write("fake")
        if with_stream:
            open(os.path.join(streamd, n + ".jsonl"), "w").write("")
    return tmp, lf, sockd, streamd, socks


def run(*args):
    return subprocess.run([sys.executable] + list(args), capture_output=True,
                          text=True, timeout=120)


# --- prepare_live dry-run ----------------------------------------------------
def test_dry_run_manifest_labels_injected_never_live():
    tmp, lf, sockd, streamd, socks = mkfixture()
    out = os.path.join(tmp, "m.json")
    r = run(os.path.join(SRC, "prepare_live.py"), "--dry-run",
            "--inject-list", lf, "--inject-sock-dir", sockd,
            "--inject-stream-root", streamd, "--manifest-out", out)
    assert r.returncode == 0, r.stdout + r.stderr
    man = json.load(open(out))
    assert man["launcher_source"] == "dry-run-injected"
    assert man["worker"]["session_id"] == "p6-fixture-worker"
    assert man["worker"]["incarnation"]["ino"] > 0
    for s in socks:
        s.close()


def test_dry_run_rejects_regular_file_fake_socket():
    tmp, lf, sockd, streamd, socks = mkfixture(sock_real=False)
    out = os.path.join(tmp, "m.json")
    r = run(os.path.join(SRC, "prepare_live.py"), "--dry-run",
            "--inject-list", lf, "--inject-sock-dir", sockd,
            "--inject-stream-root", streamd, "--manifest-out", out)
    assert r.returncode == 3, r.stdout
    assert json.loads(r.stdout)["error"] == "E_FAKE_SOCKET"


def test_name_collision_and_main_seat_refuse():
    tmp, lf, sockd, streamd, socks = mkfixture()
    out = os.path.join(tmp, "m.json")
    lst = json.load(open(lf))
    lst.append({"id": "x", "title": "p6-fixture-worker", "profile":
                "campaign4", "command": WL})
    json.dump(lst, open(lf, "w"))
    r = run(os.path.join(SRC, "prepare_live.py"), "--dry-run",
            "--inject-list", lf, "--inject-sock-dir", sockd,
            "--inject-stream-root", streamd, "--manifest-out", out)
    assert r.returncode == 3
    assert json.loads(r.stdout)["error"] == "E_COLLISION"
    r = run(os.path.join(SRC, "prepare_live.py"), "--dry-run",
            "--worker-name", "tern", "--inject-list", lf, "--manifest-out",
            out)
    assert json.loads(r.stdout)["error"] == "E_MAIN_SEAT"
    for s in socks:
        s.close()


# --- prewake gate -------------------------------------------------------------
def _dry_manifest(tmp):
    _, lf, sockd, streamd, socks = mkfixture()
    out = os.path.join(tmp, "m.json")
    r = run(os.path.join(SRC, "prepare_live.py"), "--dry-run",
            "--inject-list", lf, "--inject-sock-dir", sockd,
            "--inject-stream-root", streamd, "--manifest-out", out)
    assert r.returncode == 0, r.stdout
    return out, lf, sockd, socks


def test_gate_rejects_dry_run_manifest_before_wake():
    tmp = tempfile.mkdtemp(prefix="p6r6-g-")
    man, lf, sockd, socks = _dry_manifest(tmp)
    plan = os.path.join(PKG, "live-fixture-plan.json")
    sig = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern", "plan_sha256": "x",
               "manifest_sha256": "y"}, open(sig, "w"))
    r = run(os.path.join(SRC, "prewake_gate.py"), "--manifest", man,
            "--plan", plan, "--signatures", sig, "--inject-list", lf,
            "--inject-sock-dir", sockd)
    assert r.returncode == 3
    assert json.loads(r.stdout)["error"] == "E_NOT_LIVE", r.stdout
    for s in socks:
        s.close()


def test_gate_rejects_missing_and_changed_signature():
    import hashlib
    tmp = tempfile.mkdtemp(prefix="p6r6-g2-")
    man, lf, sockd, socks = _dry_manifest(tmp)
    m = json.load(open(man))
    m["launcher_source"] = "live-agent-deck"  # simulate signed live bytes
    json.dump(m, open(man, "w"), sort_keys=True)
    plan = os.path.join(PKG, "live-fixture-plan.json")
    ph = hashlib.sha256(open(plan, "rb").read()).hexdigest()
    mh = hashlib.sha256(open(man, "rb").read()).hexdigest()
    r = run(os.path.join(SRC, "prewake_gate.py"), "--manifest", man,
            "--plan", plan, "--signatures", os.path.join(tmp, "nosig"),
            "--inject-list", lf, "--inject-sock-dir", sockd)
    assert json.loads(r.stdout)["error"] == "E_NO_SIGNATURE"
    sig = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern", "plan_sha256": "changed",
               "manifest_sha256": mh}, open(sig, "w"))
    r = run(os.path.join(SRC, "prewake_gate.py"), "--manifest", man,
            "--plan", plan, "--signatures", sig, "--inject-list", lf,
            "--inject-sock-dir", sockd)
    assert json.loads(r.stdout)["error"] == "E_PLAN_CHANGED"
    json.dump({"signer": "tern", "plan_sha256": ph,
               "manifest_sha256": mh}, open(sig, "w"))
    r = run(os.path.join(SRC, "prewake_gate.py"), "--manifest", man,
            "--plan", plan, "--signatures", sig, "--inject-list", lf,
            "--inject-sock-dir", sockd)
    assert r.returncode == 0, r.stdout  # exact boundary passes in review
    assert json.loads(r.stdout)["gate"] == "PASS"
    for s in socks:
        s.close()


def test_gate_rejects_stale_incarnation():
    import hashlib
    tmp = tempfile.mkdtemp(prefix="p6r6-g3-")
    man, lf, sockd, socks = _dry_manifest(tmp)
    for s in socks:
        s.close()
    m = json.load(open(man))  # sockets unlinked -> gone
    import glob as _g
    for f in _g.glob(os.path.join(sockd, "*.sock")):
        os.remove(f)
    m["launcher_source"] = "live-agent-deck"
    json.dump(m, open(man, "w"), sort_keys=True)
    plan = os.path.join(PKG, "live-fixture-plan.json")
    sig = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern",
               "plan_sha256": hashlib.sha256(open(plan, "rb").read())
               .hexdigest(),
               "manifest_sha256": hashlib.sha256(open(man, "rb").read())
               .hexdigest()}, open(sig, "w"))
    r = run(os.path.join(SRC, "prewake_gate.py"), "--manifest", man,
            "--plan", plan, "--signatures", sig, "--inject-list", lf,
            "--inject-sock-dir", sockd)
    assert json.loads(r.stdout)["error"] == "E_NO_SOCKET", r.stdout


# --- cleanup -------------------------------------------------------------------
def test_cleanup_dry_run_plans_owned_ids_only_and_archive_first():
    tmp = tempfile.mkdtemp(prefix="p6r6-c-")
    man, lf, sockd, socks = _dry_manifest(tmp)
    m = json.load(open(man))
    m["launcher_source"] = "live-agent-deck"
    json.dump(m, open(man, "w"), sort_keys=True)
    r = run(os.path.join(SRC, "cleanup_live.py"), "--manifest", man,
            "--archive-dir", os.path.join(tmp, "arc"), "--dry-run",
            "--inject-list", lf)
    assert r.returncode == 0, r.stdout
    out = json.loads(r.stdout)
    assert out["executed"] is False
    assert sorted(out["owned"]) == ["p6-fixture-verifier",
                                    "p6-fixture-worker"]
    assert all("p6-fixture" in c[-1] for _, c in out["steps"]
               if isinstance(c, list))
    m["worker"]["session_id"] = "tern"  # main seat must refuse
    json.dump(m, open(man, "w"), sort_keys=True)
    r = run(os.path.join(SRC, "cleanup_live.py"), "--manifest", man,
            "--archive-dir", os.path.join(tmp, "arc"), "--dry-run",
            "--inject-list", lf)
    assert json.loads(r.stdout)["error"] == "E_MAIN_SEAT", r.stdout
    for s in socks:
        s.close()


# --- witness --------------------------------------------------------------------
def test_witness_observe_check_and_incomplete():
    import witness_timing as _w  # noqa: direct import, no live effect
    tmp = tempfile.mkdtemp(prefix="p6r6-w-")
    stream = os.path.join(tmp, "s.jsonl")
    open(stream, "w").write('{"t":"start","item":"i1"}\n')
    onset = {"onset_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                       time.gmtime()),
             "provenance": "operator-fault-marker", "uncertainty_s": 1}
    onsetf = os.path.join(tmp, "onset.json")
    json.dump(onset, open(onsetf, "w"))

    def _append():
        time.sleep(0.6)
        open(stream, "a").write('{"t":"end","item":"i1"}\n')
    import threading
    threading.Thread(target=_append).start()
    out = os.path.join(tmp, "rows.jsonl")
    r = run(os.path.join(SRC, "witness_timing.py"), "observe", "--stream",
            stream, "--item", "i1", "--onset-file", onsetf, "--action",
            "p6h-w1", "--execution", "ex-1", "--dispatch-at",
            "2026-09-22T03:00:00Z", "--timeout-s", "10", "--out", out)
    assert r.returncode == 0, r.stdout + r.stderr
    row = json.loads(r.stdout)
    assert row["onset_known"] is True and row["detection_latency_s"] >= 0
    r = run(os.path.join(SRC, "witness_timing.py"), "check", "--rows", out)
    assert r.returncode == 0 and "within-bounds" in r.stdout, r.stdout
    out2 = os.path.join(tmp, "rows2.jsonl")  # invented onset rejected path
    r = run(os.path.join(SRC, "witness_timing.py"), "observe", "--stream",
            stream, "--item", "i1", "--action", "p6h-w1", "--execution",
            "ex-1", "--timeout-s", "10", "--out", out2)
    assert r.returncode == 0
    r = run(os.path.join(SRC, "witness_timing.py"), "check", "--rows", out2)
    assert r.returncode == 3 and "incomplete" in r.stdout, r.stdout
