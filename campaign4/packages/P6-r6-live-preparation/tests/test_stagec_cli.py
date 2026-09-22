"""P6-r6 composition CLI repair tests: real subprocess with the exact
script argv documented in stagec-plan.json; injected OS effects + private
tmp only (no wakes/launches/restarts, no live harness). Every acceptance
check asserts artifacts AND stdout/exit, so silent rc0 cannot pass."""
import hashlib
import json
import os
import subprocess
import sys

import pytest

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
SCRIPT = os.path.join(SRC, "stagec_entry.py")
BINDING = os.path.join(PKG, "live-preparation-3",
                        "launch-manifest-reconciled.json")
PLAN = os.path.join(PKG, "stagec-plan.json")

from tests.test_stagec_composition import write_shims  # noqa: E402


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def cli(*args, cwd=None):
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          capture_output=True, text=True, timeout=120,
                          cwd=cwd or PKG)


def test_old_cli_failure_on_pinned_original_bytes(tmp_path):
    orig = os.path.join(str(tmp_path), "orig_stagec_entry.py")
    r = subprocess.run(["git", "-C", "/home/bmosher/memory-bake-off",
                        "show", "dc51558a90b799053a15a5fa4b40a2465945c2fe:"
                        "campaign4/packages/P6-r6-live-preparation/src/"
                        "stagec_entry.py"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    open(orig, "w").write(r.stdout)
    assert "if __name__" not in r.stdout  # no guard on pinned bytes
    r = subprocess.run([sys.executable, orig, "gate", "--help"],
                       capture_output=True, text=True, timeout=60)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "")  # old failure


def test_help_and_aliases_parse(tmp_path):
    r = cli("gate", "--help")
    assert r.returncode == 0 and "gate" in r.stdout  # no longer silent
    for flag in ("--binding", "--config"):
        r = cli("derive-config", "--help")
        assert r.returncode == 0
    # aliases actually bind: derive via --config alias on real paths
    tmp = str(tmp_path)
    cfg = os.path.join(tmp, "c.json")
    sig = os.path.join(tmp, "s.json")
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(BINDING)}, open(sig, "w"))
    r = cli("derive-config", "--plan", PLAN, "--config", BINDING,
            "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    assert os.path.exists(cfg) and "parent_binding_sha256" in r.stdout


def _signed_pair(tmp):
    write_shims(tmp)
    cfg = os.path.join(tmp, "execution-config.json")
    sig = os.path.join(tmp, "sig.json")
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(BINDING)}, open(sig, "w"))
    r = cli("derive-config", "--plan", PLAN, "--binding", BINDING,
            "--signatures", sig, "--out", cfg)
    assert r.returncode == 0, r.stdout + r.stderr
    json.dump({"signer": "tern", "plan_sha256": sha(PLAN),
               "binding_sha256": sha(BINDING),
               "config_sha256": sha(cfg)}, open(sig, "w"))
    return cfg, sig


def test_cli_missing_args_reject_before_any_send(tmp_path):
    tmp = str(tmp_path)
    write_shims(tmp)
    r = cli("run-case", "--config", os.path.join(tmp, "nope.json"),
            "--plan", PLAN)
    assert r.returncode == 2  # argparse usage error, nonzero
    assert "CALL wake" not in open(os.path.join(tmp, "trace.log")).read()


def test_cli_unsigned_and_drifted_reject_before_send(tmp_path):
    tmp = str(tmp_path)
    cfg, sig = _signed_pair(tmp)
    bad_sig = os.path.join(tmp, "bad-sig.json")
    json.dump({"signer": "tern", "plan_sha256": "changed",
               "config_sha256": sha(cfg)}, open(bad_sig, "w"))
    r = cli("gate", "--config", cfg, "--plan", PLAN, "--signatures",
            bad_sig)
    assert r.returncode == 3 and "E_PLAN_CHANGED" in r.stdout, r.stdout
    man = json.load(open(cfg))
    man["worker"]["session_id"] = "forged-id"
    json.dump(man, open(cfg, "w"))
    r = cli("run-case", "--config", cfg, "--plan", PLAN, "--signatures",
            sig, "--case", "positive-handoff", "--overlay-dir", tmp,
            "--out", os.path.join(tmp, "receipt.json"))
    assert r.returncode == 3, r.stdout
    assert "E_CONFIG_CHANGED" in r.stdout or "E_BINDING_CHANGED" in \
        r.stdout
    assert not os.path.exists(os.path.join(tmp, "trace.log")) or \
        "CALL wake" not in open(os.path.join(tmp, "trace.log")).read()


def test_cli_positive_e2e_artifacts_and_stdout(tmp_path):
    tmp = str(tmp_path)
    cfg, sig = _signed_pair(tmp)
    r = cli("gate", "--config", cfg, "--plan", PLAN, "--signatures", sig)
    assert r.returncode == 0 and '"gate": "PASS"' in r.stdout, r.stdout
    receipt = os.path.join(tmp, "receipt-positive.json")
    r = cli("run-case", "--config", cfg, "--plan", PLAN, "--signatures",
            sig, "--case", "positive-handoff", "--overlay-dir", tmp,
            "--out", receipt)
    assert r.returncode == 0, r.stdout
    assert os.path.exists(receipt)
    body = json.loads(r.stdout)
    assert body["sends"] == {"worker": 1, "verifier": 1}, body
    assert body["timecheck"] == "accept", body
    verdict = os.path.join(tmp, "verdict.json")
    lat = os.path.join(tmp, "latency.jsonl")
    wit = os.path.join(tmp, "witness-rows.jsonl")
    r = cli("timecheck", "--config", cfg, "--latency", lat, "--witness",
            wit, "--out", verdict)
    assert r.returncode == 0 and '"verdict": "accept"' in r.stdout, \
        r.stdout
    assert json.load(open(verdict))["verdict"] == "accept"
    arc = os.path.join(tmp, "archive")
    r = cli("rollback", "--config", cfg, "--overlay-dir", tmp,
            "--archive-dir", arc)
    assert r.returncode == 0 and "witness_archived" in r.stdout, r.stdout
    assert os.path.exists(os.path.join(arc, "rollback-report.json"))


def test_cli_timing_negatives_nonzero_never_accept(tmp_path):
    tmp = str(tmp_path)
    cfg, sig = _signed_pair(tmp)
    lat = os.path.join(tmp, "l.jsonl")
    wit = os.path.join(tmp, "w.jsonl")
    lrow = {"action": "p6c-w1", "execution": "ex-1",
            "dispatch_at": "2026-09-22T04:00:00Z",
            "detected_at": "2026-09-22T04:00:05Z",
            "committed_at": "2026-09-22T04:00:20Z",
            "outcome": "transition-committed", "onset_at": None}
    wrow = {"action": "p6c-w1", "execution": "ex-1", "onset_at": None,
            "outcome": "observed-end"}
    open(lat, "w").write(json.dumps(lrow) + "\n")
    open(wit, "w").write(json.dumps(wrow) + "\n")
    r = cli("timecheck", "--config", cfg, "--latency", lat, "--witness",
            wit)
    assert r.returncode == 3, r.stdout
    assert "reject" in r.stdout and "accept" not in r.stdout, r.stdout
