"""P6-r6 Stage C composition tests: exact entrypoint end-to-end with
injected OS effects + fresh producer seeing only dispatched text/named
files; timing boundary regressions. No fixture wakes/launches/restarts,
no live harness, no real seats. The accepted binding manifest is read
ONLY (never modified)."""
import hashlib
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import stagec_entry as se
from stagec_entry import StageCFault

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
BINDING = os.path.join(PKG, "live-preparation-3",
                        "launch-manifest-reconciled.json")
PLAN = os.path.join(PKG, "stagec-plan.json")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write_shims(root):
    binp = os.path.join(root, "bin")
    os.makedirs(binp, exist_ok=True)
    with open(os.path.join(binp, "wake"), "w") as fh:
        fh.write("#!/bin/bash\n"
                 "echo \"CALL wake $1\" >> \"$TRACE\"\n"
                 "n=$(ls \"$MSGDIR\" 2>/dev/null | wc -l)\n"
                 "printf '%s' \"$2\" > \"$MSGDIR/to-$1-$n.txt\"\n"
                 "echo \"wake: $1 -> started\"\n"
                 "exit 0\n")
    with open(os.path.join(binp, "systemd-run"), "w") as fh:
        fh.write("#!/bin/bash\necho \"CALL systemd-run $@\" >> \"$TRACE\"\n"
                 "exit 0\n")
    with open(os.path.join(binp, "systemctl"), "w") as fh:
        fh.write("#!/bin/bash\necho \"CALL systemctl $@\" >> \"$TRACE\"\n"
                 "echo \"ActiveState=inactive\"\necho \"SubState=dead\"\n"
                 "exit 0\n")
    for fn in ("wake", "systemd-run", "systemctl"):
        os.chmod(os.path.join(binp, fn), 0o755)
    for d in ("msgs", "stream", "claims", "art", "onsets"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    open(os.path.join(root, "trace.log"), "w").close()


def derive(tmp, binding=BINDING):
    write_shims(tmp)
    cfg = os.path.join(tmp, "execution-config.json")
    sig = os.path.join(tmp, "sig-bind.json")
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(binding)}, open(sig, "w"))
    se.derive_config(PLAN, binding, sig, cfg)
    sig2 = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(binding),
               "config_sha256": sha(cfg)}, open(sig2, "w"))
    return cfg, sig2


def run_case(tmp, case):
    cfg, sig = derive(tmp)
    return se.run_case(cfg, PLAN, sig, case, se._overlay(tmp),
                       os.path.join(tmp, "receipt-%s.json" % case))


# --- e2e through the same entrypoint ---------------------------------------------
def test_positive_handoff_e2e(tmp_path):
    tmp = str(tmp_path)
    receipt = run_case(tmp, "positive-handoff")
    assert receipt["sends"] == {"worker": 1, "verifier": 1}, receipt["sends"]
    assert receipt["timecheck"]["verdict"] == "accept"
    assert receipt["candidate_gate"] == "pass"
    assert receipt["overlay"] is True
    # fresh producer evidence: claim + onset sidecar exist for observed item
    assert os.path.exists(os.path.join(tmp, "onsets",
                                       receipt["worker_item"] + ".json"))


def test_failed_verification_stays_open(tmp_path):
    receipt = run_case(str(tmp_path), "failed-verification")
    assert receipt["timecheck"]["verdict"] == "accept-open", \
        receipt["timecheck"]
    assert "COMPLETE" not in json.dumps(receipt["outcome"])


def test_restart_quiet_no_fresh_sends(tmp_path):
    receipt = run_case(str(tmp_path), "restart-quiet")
    assert receipt["outcome"]["decision"] == "duplicate-end-ignored"
    assert receipt["sends"] == {"worker": 1, "verifier": 1}
    assert receipt["timecheck"]["verdict"] == "accept"


def test_rollback_archives_before_cleanup(tmp_path):
    tmp = str(tmp_path)
    run_case(tmp, "positive-handoff")
    arc = os.path.join(tmp, "archive")
    report = se.rollback(os.path.join(tmp, "execution-config.json"), tmp,
                         arc)
    assert report["witness_archived"] is True
    assert os.path.exists(os.path.join(arc, "rollback-report.json"))
    assert os.path.exists(os.path.join(arc, "execution-config.json"))


# --- derive/gate negatives ---------------------------------------------------------
def test_derive_rejects_changed_plan_and_synthetic_binding(tmp_path):
    tmp = str(tmp_path)
    cfg = os.path.join(tmp, "c.json")
    sig = os.path.join(tmp, "s.json")
    json.dump({"signer": "tern", "plan_sha256": "changed",
               "binding_sha256": sha(BINDING)}, open(sig, "w"))
    with pytest.raises(StageCFault) as e:
        se.derive_config(PLAN, BINDING, sig, cfg)
    assert e.value.code == "E_PLAN_CHANGED"
    bad = json.load(open(BINDING))
    bad["worker"]["stream_path"] = "/tmp/elsewhere/x.jsonl"
    badp = os.path.join(tmp, "bad-binding.json")
    json.dump(bad, open(badp, "w"))
    sig2 = os.path.join(tmp, "s2.json")
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(badp)}, open(sig2, "w"))
    with pytest.raises(StageCFault) as e:
        se.derive_config(PLAN, badp, sig2, cfg)
    assert e.value.code == "E_MISMATCH"
    assert sha(BINDING) != sha(badp)  # accepted manifest itself untouched
    assert json.load(open(BINDING))["worker"]["stream_path"].endswith(
        "085360c2-1790050499.jsonl")


def test_gate_rejects_changed_binding_and_missing_signature(tmp_path):
    tmp = str(tmp_path)
    cfg, sig = derive(tmp)
    man = json.load(open(cfg))
    man["worker"]["session_id"] = "forged-id"
    json.dump(man, open(cfg, "w"))
    with pytest.raises(StageCFault) as e:
        se.gate(cfg, PLAN, sig)
    assert e.value.code in ("E_CONFIG_CHANGED", "E_BINDING_CHANGED")


# --- timecheck boundaries ------------------------------------------------------------
def _cfg(tmp, cases=("positive-handoff",)):
    p = os.path.join(tmp, "cfg.json")
    json.dump({"timing_bounds": {"detect_s": 30.0, "recover_s": 60.0,
                                 "total_s": 90.0,
                                 "suspicion_detect_s": 180.0,
                                 "suspicion_recover_s": 60.0,
                                 "suspicion_total_s": 240.0},
               "cases": list(cases)}, open(p, "w"))
    return p


def _rows(tmp, lat, wit):
    lp, wp = os.path.join(tmp, "l.jsonl"), os.path.join(tmp, "w.jsonl")
    open(lp, "w").write("\n".join(json.dumps(r) for r in lat) + "\n")
    open(wp, "w").write("\n".join(json.dumps(r) for r in wit) + "\n")
    return lp, wp


def _ok_pair(onset="2026-09-22T04:00:00Z", det="2026-09-22T04:00:05Z",
             com="2026-09-22T04:00:20Z", action="p6c-w1", ex="ex-1"):
    lat = {"action": action, "execution": ex, "dispatch_at":
           "2026-09-22T03:00:00Z", "detected_at": det, "committed_at": com,
           "outcome": "transition-committed", "onset_at": onset,
           "source_time_known": False}
    wit = {"action": action, "execution": ex, "onset_at": onset,
           "onset_provenance": "producer", "onset_uncertainty_s": 1,
           "detected_at": det, "outcome": "observed-end"}
    return lat, wit


def test_timecheck_positive_accepts_worker_duration_separate(tmp_path):
    cfg = _cfg(str(tmp_path))
    lat, wit = _ok_pair()  # dispatch 1h before onset: not stall latency
    lp, wp = _rows(str(tmp_path), [lat], [wit])
    v = se.timecheck(cfg, lp, wp)
    assert v["verdict"] == "accept", v
    assert v["worker_durations_s"][0] > 3000  # reported, never gated


def test_timecheck_negatives(tmp_path):
    tmp = str(tmp_path)
    cfg = _cfg(tmp)
    lat, wit = _ok_pair()
    cases = []
    l2, w2 = _ok_pair()
    l2["onset_at"] = None
    w2["onset_at"] = None
    cases.append(("unknown source", [l2], [w2]))
    l3, w3 = _ok_pair()
    l3["committed_at"] = None
    cases.append(("unknown endpoint", [l3], [w3]))
    l4, w4 = _ok_pair(det="2026-09-22T03:59:00Z")  # detected before onset
    cases.append(("negative interval", [l4], [w4]))
    l5, w5 = _ok_pair(com="2026-09-22T04:05:00Z")  # rec 295s, det fast
    cases.append(("late recovery fast detection", [l5], [w5]))
    l6, w6 = _ok_pair(det="2026-09-22T04:00:25Z", com="2026-09-22T04:01:40Z")
    cases.append(("late total", [l6], [w6]))  # total 100s
    l7, w7 = _ok_pair()
    w7["action"] = "wrong-action"
    cases.append(("wrong action", [l7], [w7]))
    l8, w8 = _ok_pair()
    w8["ack"] = False
    cases.append(("missing ack", [l8], [w8]))
    l9, w9 = _ok_pair()
    w9["outcome"] = "queued-only"
    cases.append(("queued-only", [l9], [w9]))
    l10, w10 = _ok_pair()
    w10["onset_uncertainty_s"] = None
    cases.append(("unknown uncertainty", [l10], [w10]))
    for name, l, w in cases:
        lp, wp = _rows(tmp, l, w)
        v = se.timecheck(cfg, lp, wp)
        assert v["verdict"] == "reject", (name, v)


def test_timecheck_missing_success_all_failure(tmp_path):
    tmp = str(tmp_path)
    cfg = _cfg(tmp)
    lp, wp = _rows(tmp, [], [])
    assert se.timecheck(cfg, lp, wp)["verdict"] == "incomplete"
    lat = {"action": "p6c-w1", "execution": "ex-1", "outcome": "no-end"}
    wit = {"action": "p6c-w1", "execution": "ex-1", "outcome":
           "observed-end", "onset_at": "2026-09-22T04:00:00Z",
           "onset_uncertainty_s": 1}
    lp, wp = _rows(tmp, [lat], [wit])
    v = se.timecheck(cfg, lp, wp)
    assert v["verdict"] == "reject" and "all-failure" in v["reason"], v


def test_timecheck_expect_open(tmp_path):
    tmp = str(tmp_path)
    cfg = _cfg(tmp)
    lat, wit = _ok_pair(action="p6c-w1")
    latv = dict(lat, action="p6c-v1", outcome="transition-committed")
    witv = dict(wit, action="p6c-v1")
    lp, wp = _rows(tmp, [lat, latv], [wit, witv])
    v = se.timecheck(cfg, lp, wp, expect_open="p6c-v1")
    assert v["verdict"] == "reject" and "never close" in v["reason"], v
    lp, wp = _rows(tmp, [lat], [wit])
    v = se.timecheck(cfg, lp, wp, expect_open="p6c-v1")
    assert v["verdict"] == "accept-open", v
