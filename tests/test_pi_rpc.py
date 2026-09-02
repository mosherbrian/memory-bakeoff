import json
import pytest

from memory_bakeoff.pi_rpc import PiRpc, RpcProtocolError, RpcTrace, require_quiescence


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
