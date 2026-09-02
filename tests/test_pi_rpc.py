import json
import pytest

from memory_bakeoff.pi_rpc import PiRpc, RpcProtocolError, RpcTrace, observation_barrier, require_quiescence, run_terminal


def test_trace_is_jsonl_auditable(tmp_path):
    trace = RpcTrace(pid=42)
    trace.stdin.append({"at": "t", "data": {"id": "gen25_1", "type": "get_state"}})
    trace.stdout.append({"at": "t", "data": {"id": "gen25_1", "type": "response", "success": True}})
    target = tmp_path / "trace.json"
    trace.save(target)
    saved = json.loads(target.read_text())
    assert saved["pid"] == 42
    assert saved["stdin"][0]["data"]["id"] == saved["stdout"][0]["data"]["id"]


class FakeRpc:
    def __init__(self, leaves=("leaf", "leaf"), changing_session=False):
        self.session_ids = []
        self._leaves = iter(leaves)
        self.changing_session = changing_session

    def state(self):
        ident = "second" if self.changing_session and self.session_ids else "first"
        self.session_ids.append(ident)
        return {"sessionId": ident, "isStreaming": False, "isCompacting": False}

    def entries(self, since=None):
        leaf = next(self._leaves)
        return {"leafId": leaf, "entries": []}


def test_quiescence_requires_terminal_and_stable_ledger(monkeypatch):
    monkeypatch.setattr("memory_bakeoff.pi_rpc.time.sleep", lambda _: None)
    outcome = require_quiescence(FakeRpc(), debug_events=[{"event": "observer.records"}])
    assert outcome["session_id"] == "first"
    with pytest.raises(RpcProtocolError, match="terminal"):
        require_quiescence(FakeRpc(), debug_events=[])
    with pytest.raises(RpcProtocolError, match="changed"):
        require_quiescence(FakeRpc(("a", "b")), debug_events=[{"event": "observer.records"}])


def test_quiescence_rejects_context_error(monkeypatch):
    monkeypatch.setattr("memory_bakeoff.pi_rpc.time.sleep", lambda _: None)
    with pytest.raises(RpcProtocolError, match="OM debug error"):
        require_quiescence(FakeRpc(), debug_events=[{"event": "observer.error", "error": "stale"}])


class BarrierClock:
    now = 0.0
    def __call__(self): return self.now
    def sleep(self, seconds): self.now += seconds


class BarrierRpc:
    def __init__(self, *, session="s", changed_leaf=False):
        self.session, self.changed_leaf = session, changed_leaf
        self.calls = 0
    def state(self): return {"sessionId": self.session, "isStreaming": False, "isCompacting": False}
    def entries(self, since=None):
        self.calls += 1
        return {"leafId": "changed" if since and self.changed_leaf else "leaf", "entries": ["new"] if since and self.changed_leaf else []}


def test_run_terminal_requires_current_run_complete():
    events = [{"runId": "old", "event": "dropper.append"}, {"runId": "new", "event": "observer.start"}, {"runId": "new", "event": "observer.records"}]
    assert run_terminal(events, "new") is not None
    events += [{"runId": "new", "event": "reflector.agent_start"}]
    assert run_terminal(events, "new") is None
    events += [{"runId": "new", "event": "reflector.result"}, {"runId": "new", "event": "dropper.not_ready"}]
    assert run_terminal(events, "new")["event"] == "dropper.not_ready"


def test_run_terminal_handles_reflector_only_run():
    events = [{"runId": "reflect", "event": "reflector.agent_start"}, {"runId": "reflect", "event": "reflector.result"}, {"runId": "reflect", "event": "dropper.waiting_for_reflection"}]
    assert run_terminal(events, "reflect")["event"] == "dropper.waiting_for_reflection"


def test_barrier_no_stage_due_and_current_run_only():
    clock = BarrierClock(); rpc = BarrierRpc()
    old = [{"runId": "old", "event": "observer.start"}, {"runId": "old", "event": "observer.records"}]
    outcome = observation_barrier(rpc, read_debug=lambda: old, baseline_debug_count=len(old), launch_guard_seconds=.1, stability_seconds=0, clock=clock, sleeper=clock.sleep)
    assert outcome["outcome"] == "no_consolidation_due"
    current = old + [{"runId": "new", "event": "observer.start"}, {"runId": "new", "event": "observer.records"}]
    second_clock = BarrierClock()
    outcome = observation_barrier(BarrierRpc(), read_debug=lambda: current, baseline_debug_count=len(old), stability_seconds=0, clock=second_clock, sleeper=second_clock.sleep)
    assert outcome["run_id"] == "new"


def test_barrier_rejects_error_or_ledger_change():
    error = [{"runId": "new", "event": "observer.start"}, {"runId": "new", "event": "observer.error"}]
    error_clock = BarrierClock()
    with pytest.raises(RpcProtocolError, match="terminal error"):
        observation_barrier(BarrierRpc(), read_debug=lambda: error, baseline_debug_count=0, stability_seconds=0, clock=error_clock, sleeper=error_clock.sleep)
    complete = [{"runId": "new", "event": "observer.start"}, {"runId": "new", "event": "observer.records"}]
    change_clock = BarrierClock()
    with pytest.raises(RpcProtocolError, match="ledger changed"):
        observation_barrier(BarrierRpc(changed_leaf=True), read_debug=lambda: complete, baseline_debug_count=0, stability_seconds=0, clock=change_clock, sleeper=change_clock.sleep)
