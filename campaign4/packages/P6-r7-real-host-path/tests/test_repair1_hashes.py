"""P6-r7 H2 repair tests: required signature hashes fail closed (missing/
null/empty/wrong reject before effect); exact subprocess CLI per hash field
plus bound positive; omission-PASS reproduced on pinned original bytes.
Injected effects only; no real seats."""
import copy
import json
import os
import subprocess
import sys

import pytest

PKG = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(PKG, "src")
SCRIPT = os.path.join(SRC, "stagec_host.py")
ORIG_SCRIPT = "/tmp/p6r7-orig-stagec_host.py"

sys.path.insert(0, SRC)
from tests.test_stagec_host import _make_env  # noqa: E402


def cli_run(script, *args):
    return subprocess.run([sys.executable, script] + list(args),
                          capture_output=True, text=True, timeout=120,
                          cwd=PKG)


@pytest.fixture()
def env():
    e = _make_env()
    yield e
    for s in e["socks"]:
        s.close()


def _snapshot(tmp):
    out = []
    for root, _, files in os.walk(tmp):
        for f in files:
            out.append(os.path.join(root, f))
    return sorted(out)


REQUIRED_HASHES = ["plan_sha256", "config_sha256", "stagec_entry_sha256",
                   "candidate_harness_sha256"]


def test_omission_pass_on_pinned_original_bytes(env):
    if not os.path.exists(ORIG_SCRIPT):
        r = subprocess.run(
            ["git", "-C", "/home/bmosher/memory-bake-off", "show",
             "5643f2ddbaf40200a3fcf9dc087b479ca5e82a8a:"
             "campaign4/packages/P6-r7-real-host-path/src/stagec_host.py"],
            capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        assert ",\n                   want) != want:" in r.stdout \
            or "want) != want:" in r.stdout  # fail-open default present
        open(ORIG_SCRIPT, "w").write(r.stdout)
    sig = json.load(open(env["sig"]))
    del sig["candidate_harness_sha256"]  # omitted required hash
    with open(ORIG_SCRIPT, "rb") as fh:  # test sig binds ORIGINAL bytes
        import hashlib as _hl
        sig["stagec_entry_sha256"] = _hl.sha256(fh.read()).hexdigest()
    sp = os.path.join(env["tmp"], "omit-sig.json")
    json.dump(sig, open(sp, "w"))
    r = cli_run(ORIG_SCRIPT, "gate", "--config", env["cfg"], "--plan",
                env["plan"], "--signatures", sp, "--registry-file",
                env["reg"])
    assert r.returncode == 0 and '"gate": "PASS"' in r.stdout, \
        (r.returncode, r.stdout)  # original fail-open omission PASS


def test_each_omitted_hash_rejects_before_effect(env):
    base = json.load(open(env["sig"]))
    for field in REQUIRED_HASHES:
        sig = {k: v for k, v in base.items() if k != field}
        sp = os.path.join(env["tmp"], "omit-%s.json" % field)
        json.dump(sig, open(sp, "w"))
        before = _snapshot(env["tmp"])
        r = cli_run(SCRIPT, "gate", "--config", env["cfg"], "--plan",
                    env["plan"], "--signatures", sp, "--registry-file",
                    env["reg"])
        assert r.returncode == 3, (field, r.stdout)
        assert _snapshot(env["tmp"]) == before  # zero effect
    # null / empty / wrong candidate hash also reject
    for bad in (None, "", "deadbeef"):
        sig = dict(base, candidate_harness_sha256=bad)
        sp = os.path.join(env["tmp"], "bad-sig.json")
        json.dump(sig, open(sp, "w"))
        r = cli_run(SCRIPT, "gate", "--config", env["cfg"], "--plan",
                    env["plan"], "--signatures", sp, "--registry-file",
                    env["reg"])
        assert r.returncode == 3 and "E_TOOL_CHANGED" in r.stdout, \
            (bad, r.stdout)


def test_fully_bound_positive_passes(env):
    before = _snapshot(env["tmp"])
    r = cli_run(SCRIPT, "gate", "--config", env["cfg"], "--plan",
                env["plan"], "--signatures", env["sig"], "--registry-file",
                env["reg"])
    assert r.returncode == 0 and '"gate": "PASS"' in r.stdout, r.stdout
    assert _snapshot(env["tmp"]) == before
