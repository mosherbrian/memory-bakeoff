"""P6-r11 amendment-2 new-pass/negative tests (candidate bytes).

Positive: genuine failed verifier claim with declared==committed worker hash
and differing bytes -> verified-rejection (durable, idempotent).
Negatives: invented expected hash, completed-claim mismatch, failed-worker
code path (non-verify step) -> None (never verified rejection).
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src",
                                "r3harness"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import turn_handoff as th


class KV(dict):
    def keys(self):
        return super().keys()


class Driver:
    def __init__(self):
        self.kv = KV()

    def _kv_put_many(self, pairs):
        for k, v in pairs:
            self.kv[k] = v


class Adapter:
    def __init__(self):
        self.driver = Driver()


def _env():
    tmp = tempfile.mkdtemp(prefix="p6r11-rej-")
    os.makedirs(os.path.join(tmp, "art"), exist_ok=True)
    with open(os.path.join(tmp, "art", "out.bin"), "wb") as fh:
        fh.write(b"tampered-bytes")
    wh = {"out.bin": "aa" * 32}
    a = Adapter()
    a.driver.kv["handoff-intent:wact:wexe"] = json.dumps(
        {"verify_action": "vact", "verify_execution": "vexe",
         "hashes": wh}, sort_keys=True)
    launch = {"package": "p", "attempt": "a", "action": "vact",
              "execution": "vexe", "contract_step": "verify-run",
              "artifact_base_dir": tmp}
    return a, launch


def _claim(outcome, sha):
    return {"package": "p", "attempt": "a", "action": "vact",
            "execution": "vexe", "contract_step": "verify-run",
            "outcome": outcome,
            "artifacts": {"out.bin": {"path": "art/out.bin",
                                      "sha256": sha}},
            "check_detail": "hash mismatch: out.bin"}


def test_genuine_failed_claim_is_verified_rejection():
    a, launch = _env()
    rec = th._authenticated_rejection(a, launch, _claim("failed", "aa" * 32),
                                      "E_ARTIFACT_MISMATCH")
    assert rec is not None and rec["decision"] == "verified-rejection"
    assert rec["expected"]["out.bin"] == "aa" * 32
    assert rec["observed"]["out.bin"] != "aa" * 32
    again = th._authenticated_rejection(a, launch,
                                        _claim("failed", "aa" * 32),
                                        "E_ARTIFACT_MISMATCH")
    assert again["decision"] == "verified-rejection"


def test_invented_expected_hash_never_rejection():
    a, launch = _env()
    assert th._authenticated_rejection(a, launch, _claim("failed", "ff" * 32),
                                       "E_ARTIFACT_MISMATCH") is None


def test_completed_claim_mismatch_never_rejection():
    a, launch = _env()
    assert th._authenticated_rejection(a, launch,
                                       _claim("completed", "aa" * 32),
                                       "E_ARTIFACT_MISMATCH") is None


def test_worker_step_mismatch_never_rejection():
    a, launch = _env()
    launch = dict(launch, contract_step="worker-run")
    assert th._authenticated_rejection(a, launch, _claim("failed", "aa" * 32),
                                       "E_ARTIFACT_MISMATCH") is None
