"""P6-r3 sole-repair tests: D1 bound setup/task text, D2 notification +
host timer proof, D3 honest latency gates, D4 reconciling rollback."""
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import harness as harness_mod
from host_adapter import HostAdapter, OwnedFault
from driver import Driver, FakeClock, FakeExternalWorld


def mktree():
    tmp = tempfile.mkdtemp(prefix="p6q-")
    for sub in ("stream", "claims", "art"):
        os.makedirs(os.path.join(tmp, sub))
    return tmp


def mk(tmp):
    w = FakeExternalWorld(os.path.join(tmp, "world.json"))
    d = Driver(os.path.join(tmp, "ledger.db"), FakeClock(), w)
    return d, HostAdapter(d)


def plan_doc(tmp, **kw):
    plan = {"fixture_id": "p6-fixture-handoff-1", "package_id": "P6H",
            "worker_action": "p6h-w1", "verify_action": "p6h-v1",
            "seats": {"fixture_seats": ["p6-fixture-worker",
                                        "p6-fixture-verifier"]},
            "allowlist": {"seats": ["p6-fixture-worker",
                                    "p6-fixture-verifier"],
                          "timer_units": ["p6-fixture-handoff-1.timer"],
                          "wake_path": os.path.join(tmp, "bin", "wake")},
            "bounds": {"duration_s": 900, "verify_window_s": 600,
                       "wait_s": 5, "poll_interval_s": 0.05,
                       "escalation_window_s": 120,
                       "stream_dir": os.path.join(tmp, "stream"),
                       "artifact_base_dir": os.path.join(tmp, "art"),
                       "latency_path": os.path.join(tmp, "latency.jsonl")},
            "task_texts": {"worker": "TASK-W run {action} claim {claims}",
                           "verifier": "TASK-V run {action}"},
            "authorized_dispositions": [],
            "routes": {}}
    plan.update(kw)
    path = os.path.join(tmp, "plan.json")
    json.dump(plan, open(path, "w"), sort_keys=True)
    return path


# --- D1 --------------------------------------------------------------------------
def test_d1_setup_creates_stream_surface_rejects_reuse():
    # L2: explicit per-seat bindings only; suffix inference is forbidden
    # and setup never creates or truncates producer files.
    tmp = mktree()
    pp = plan_doc(tmp)
    out = os.path.join(tmp, "m.json")
    before = '{"t":"d","item":"i Old"}\n'
    for key in ("wsk-ev", "vsk-ev"):
        with open(os.path.join(tmp, "stream", key + ".jsonl"),
                  "w") as fh:
            fh.write(before)
    m = harness_mod.setup_manifest(pp, out, "sess-ev", "sk-ev",
                                   "wsk-ev", "vsk-ev")
    assert m["worker_stream_key"] == "wsk-ev"
    assert m["verifier_stream_key"] == "vsk-ev"
    for key in ("wsk-ev", "vsk-ev"):
        assert open(os.path.join(tmp, "stream",
                                 key + ".jsonl")).read() == before
    try:
        harness_mod.setup_manifest(pp, out, "sess-ev", "sk-ev")
        assert False, "expected E_UNBOUND"
    except OwnedFault as e:
        assert e.code == "E_UNBOUND", e


def test_d1_wake_text_carries_task_instructions():
    tmp = mktree()
    d, ha = mk(tmp)
    calls = []
    ha.transport.send = lambda seat, text, **kw: (
        calls.append((seat, text)), "mid-1")[1]
    text = "TASK-W run {action} claim {claims}".format(
        action="a-w1", execution="ex-1", claims="/tmp/p6h/claims")
    ha.transport.send("p6-fixture-worker", text, action="a-w1",
                      execution="ex-1")
    assert calls[0][1].startswith("TASK-W run a-w1")  # pinned instructions
    assert "dispatch:a-w1" not in calls[0][1]  # not a bare id ping
    d.close()


# --- D2 --------------------------------------------------------------------------
def test_d2_host_timer_invoked_from_fixture_path():
    from host_adapter import HostTimerService
    tmp = mktree()
    d, ha = mk(tmp)
    seen = []

    class Rec:
        def __call__(self, cmd, **kw):
            seen.append(cmd)
            class O:
                returncode = 0
                stdout = ""
                stderr = ""
            return O()
    ts = HostTimerService(kv_get=d.kv.get, kv_put=d._kv_put, enabled=True,
                          allowlist=("t-h1",), runner=Rec(),
                          callback_argv=["python3", "harness.py"])
    out, dup = ts.create_host("t-h1", "2026-09-22T01:00:00Z", 60,
                              ["python3", "harness.py", "timer-callback"])
    assert (out, dup) == ("armed-host", False)
    assert seen[0][:4] == ["systemd-run", "--user", "--unit=t-h1",
                           "--on-active=60s"]  # real configured invocation
    assert "harness.py" in seen[0]  # candidate callback, never true
    d.close()


# --- D3 --------------------------------------------------------------------------
def test_d3_vacuous_latency_cannot_pass():
    tmp = mktree()
    lat = os.path.join(tmp, "latency.jsonl")
    with open(lat, "w") as fh:
        fh.write(json.dumps({"action": "a", "dispatch_at":
                             "2026-09-22T00:00:00Z", "detected_at": None,
                             "committed_at": None,
                             "outcome": "no-end-failure"}) + "\n")
    try:
        harness_mod.check_latency(lat)
        assert False, "expected failure"
    except OwnedFault as e:
        assert e.code in ("E_NO_SUCCESS", "E_BAD_SAMPLE"), e
    with open(lat, "w") as fh:
        fh.write(json.dumps({"action": "a",
                             "dispatch_at": "2026-09-22T00:00:00Z",
                             "detected_at": "2026-09-22T00:00:10Z",
                             "committed_at": "2026-09-22T00:00:40Z",
                             "outcome": "transition-committed"}) + "\n")
        fh.write(json.dumps({"action": "b",
                             "dispatch_at": "2026-09-22T00:00:00Z",
                             "detected_at": None, "committed_at": None,
                             "outcome": "no-end-failure"}) + "\n")
    verdict = harness_mod.check_latency(lat)  # positive + retained failure
    assert verdict["verdict"] == "gates-hold"
    assert verdict["success"] == 1 and verdict["failures"] == 1


def test_d3_unacked_escalation_not_recovery():
    tmp = mktree()
    lat = os.path.join(tmp, "latency.jsonl")
    with open(lat, "w") as fh:
        fh.write(json.dumps({"action": "a",
                             "dispatch_at": "2026-09-22T00:00:00Z",
                             "detected_at": "2026-09-22T00:00:10Z",
                             "committed_at": "2026-09-22T00:00:40Z",
                             "outcome": "owned-recovery:pending"}) + "\n")
    try:
        harness_mod.check_latency(lat)
        assert False, "expected E_NO_SUCCESS"
    except OwnedFault as e:
        assert e.code == "E_NO_SUCCESS", e


# --- D4 --------------------------------------------------------------------------
def test_d4_rollback_blocked_on_intent_derived_on_clean():
    tmp = mktree()
    d, ha = mk(tmp)
    d._kv_put("outbox-pending:ob-1", '{"target":"a-v1"}')
    try:
        harness_mod.rollback_verify(
            os.path.join(tmp, "ledger.db"),
            _manifest(tmp), os.path.join(tmp, "arc"))
        assert False, "expected E_ROLLBACK_BLOCKED"
    except OwnedFault as e:
        assert e.code == "E_ROLLBACK_BLOCKED", e
    assert not os.path.exists(os.path.join(tmp, "arc",
                                           "rollback-report.json"))
    d._kv_put("outbox-pending:ob-1", "")
    d._kv_put("outbox-acked:ob-1", "mid-1")
    report = harness_mod.rollback_verify(
        os.path.join(tmp, "ledger.db"), _manifest(tmp),
        os.path.join(tmp, "arc"))
    assert report["timers"] == "none-armed-verified"
    assert report["intents"] == "none-outstanding-verified"
    assert os.path.exists(os.path.join(tmp, "arc", "fixture.db"))
    d.close()


def _manifest(tmp):
    path = os.path.join(tmp, "m.json")
    json.dump({"allowlist_units": []}, open(path, "w"))
    return path
