"""P6-r18 launch closure: fixture-only lane wrappers resolve the local
runtime, preserve lane settings, and cannot fall back to shared runtime.

Verification uses an injected final executor (argument capture) on the
same shipped branch — no models, no credentials, no launches. Injected
effects only.
"""
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
RUNTIME = os.path.join(PKG, "runtime")
GO = os.path.join(RUNTIME, "launch-acp-go")
DEEPSEEK = os.path.join(RUNTIME, "launch-acp-go-deepseek")
LOCAL_RT = os.path.join(RUNTIME, "acp-worker")
INPUTS = ("/home/bmosher/memory-bake-off/campaign4/packages/"
          "P6-r18-runtime-source-time/inputs")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _capture(argv, env_extra=None):
    tmp = tempfile.mkdtemp(prefix="p6r18-launch-")
    cap = os.path.join(tmp, "exec")
    out = os.path.join(tmp, "captured.json")
    with open(cap, "w") as fh:
        fh.write("#!/usr/bin/env bash\n"
                 "python3 - \"$@\" <<'PYEOF'\n"
                 "import json,os,sys\n"
                 "json.dump({\"argv\": sys.argv[1:],\n"
                 "  \"env\": {k: os.environ.get(k) for k in\n"
                 "   [\"ACP_MODEL\",\"ACP_GO_MODEL\",\"ACP_AUTO_APPROVE\",\n"
                 "    \"ACP_STALL_SECS\",\"ACP_PROMISE_CHECK\",\n"
                 "    \"P6_SOURCE_MODE\",\"OPENCODE_API_KEY\"]}},\n"
                 "  open(os.environ[\"CAPTURE_OUT\"],\"w\"), sort_keys=True)\n"
                 "PYEOF\n")
    os.chmod(cap, 0o755)
    env = dict(os.environ)
    env.pop("ACP_SOURCE_TEST_NOW", None)
    env["FIXTURE_LAUNCH_EXEC"] = cap
    env["CAPTURE_OUT"] = out
    env.update(env_extra or {})
    r = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                       env=env)
    assert r.returncode == 0, r.stderr[-1000:]
    return json.load(open(out))


HOSTILE = {"ACP_GO_MODEL": "hostile-inherited-model",
           "ACP_MODEL": "hostile-inherited-model"}


def _plan_argv(lane):
    plan = json.load(open(os.path.join(PKG, "fixture-launch-plan.json")))
    return plan["launch_closure"]["exact_argv"][lane]


def test_both_lanes_resolve_local_runtime_and_settings():
    # EXACT plan argv, hostile inherited model values: backend appears
    # exactly once, no extra args, worker Muse / verifier DeepSeek.
    got = _capture(_plan_argv("go"), env_extra=dict(HOSTILE))
    assert got["argv"] == [os.path.realpath(LOCAL_RT), "muse-engine",
                           "acp"], got["argv"]
    assert got["argv"].count("muse-engine") == 1
    assert got["argv"].count("acp") == 1
    assert got["env"]["ACP_MODEL"] == \
        "opencode-go/muse-spark-1.3-contributor", got["env"]
    assert got["env"]["ACP_AUTO_APPROVE"] == "1"
    assert got["env"]["ACP_STALL_SECS"] == "1800"
    assert got["env"]["ACP_PROMISE_CHECK"] == "1"
    assert got["env"]["P6_SOURCE_MODE"] == "runtime"
    assert got["env"]["OPENCODE_API_KEY"] is None
    assert ".config/agent-deck" not in " ".join(got["argv"])
    got = _capture(_plan_argv("deepseek"), env_extra=dict(HOSTILE))
    assert got["argv"] == [os.path.realpath(LOCAL_RT), "muse-engine",
                           "acp"], got["argv"]
    assert got["argv"].count("muse-engine") == 1
    assert got["argv"].count("acp") == 1
    assert got["env"]["ACP_MODEL"] == "opencode-go/deepseek-v4.1-flash", \
        got["env"]
    assert got["env"]["ACP_GO_MODEL"] == "opencode-go/deepseek-v4.1-flash"
    assert got["env"]["P6_SOURCE_MODE"] == "runtime"
    assert ".config/agent-deck" not in " ".join(got["argv"])


def test_no_shared_fallback_or_leak():
    for path in (GO, DEEPSEEK):
        raw = open(path).read()
        assert ".config/agent-deck" not in raw, path
        # The only $HOME reference is the lane credential-existence gate;
        # no shared runtime path is ever executed or fallen back to.
        assert "$HOME/.config/agent-deck/acp-worker" not in raw, path
        assert raw.count("$HOME") <= 1, path
    # Missing local runtime is a hard failure, never substitution: run a
    # copy of the wrapper in an empty dir (same shipped branch).
    tmp = tempfile.mkdtemp(prefix="p6r18-nolocal-")
    lonely = os.path.join(tmp, "launch-acp-go")
    with open(lonely, "w") as fh:
        fh.write(open(GO).read())
    os.chmod(lonely, 0o755)
    r = subprocess.run([lonely, "muse-engine", "acp"],
                       capture_output=True, text=True, timeout=30,
                       env={k: v for k, v in os.environ.items()
                            if k != "FIXTURE_LAUNCH_EXEC"})
    assert r.returncode == 1, (r.returncode, r.stdout)
    assert "missing" in r.stderr and "fallback" not in r.stderr.lower() \
        or "missing" in r.stderr, r.stderr


def test_live_rejects_test_clock_and_syntax_checks():
    for path in (GO, DEEPSEEK):
        r = subprocess.run(["bash", "-n", path], capture_output=True,
                           text=True, timeout=30)
        assert r.returncode == 0, (path, r.stderr)
        assert os.stat(path).st_mode & stat.S_IXUSR, path
    env = dict(os.environ, ACP_SOURCE_TEST_NOW="2026-09-23T00:00:00Z")
    for lane in (GO, DEEPSEEK):
        r = subprocess.run([lane, "muse-engine", "acp"],
                           capture_output=True, text=True, timeout=30,
                           env=env)
        assert r.returncode == 1, (lane, r.returncode)
        assert "ACP_SOURCE_TEST_NOW" in r.stderr, r.stderr


def test_plan_binds_wrappers_and_inputs_untouched():
    plan = json.load(open(os.path.join(PKG, "fixture-launch-plan.json")))
    for lane, path in (("go", GO), ("deepseek", DEEPSEEK)):
        entry = plan["launch_closure"]["wrappers"][lane]
        assert entry["path"].endswith(os.path.basename(path))
        assert entry["sha256"] == sha(path), lane
    assert plan["launch_closure"]["exact_argv"]["go"][0].endswith(
        "launch-acp-go")
    assert "ACP_SOURCE_TEST_NOW" in json.dumps(
        plan["launch_closure"]["exact_environment"])
    assert sha(os.path.join(INPUTS, "acp-worker")).startswith("6871ceb1")
    assert sha(os.path.join(INPUTS, "acp-go")).startswith("72b50d8a")
    assert sha(os.path.join(INPUTS, "acp-go-deepseek")).startswith(
        "0d009f0d")
