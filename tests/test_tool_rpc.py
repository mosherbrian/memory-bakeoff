from __future__ import annotations

import json
from pathlib import Path
import threading
import time

import pytest

from memory_bakeoff.tool_rpc import (
    ToolLoopRPCClient,
    ToolRPCError,
    ToolRPCRequest,
    list_pending_rpc,
    write_rpc_error,
    write_rpc_response,
)


def test_rpc_fingerprint_ignores_metadata():
    a = ToolRPCRequest("github.fetch_file", {"repo": "o/r", "path": "a.py"}, {"run": 1})
    b = ToolRPCRequest("github.fetch_file", {"repo": "o/r", "path": "a.py"}, {"run": 2})
    assert a.fingerprint() == b.fingerprint()


def test_rpc_batch_is_fully_enqueued_before_waiting(tmp_path: Path):
    client = ToolLoopRPCClient(tmp_path, timeout_s=3, poll_interval_s=0.01)
    observed: list[str] = []

    def worker():
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            pending = list_pending_rpc(tmp_path)
            if len(pending) == 2:
                observed.extend(x["request_id"] for x in pending)
                for item in pending:
                    write_rpc_response(
                        tmp_path,
                        item["request_id"],
                        result={"echo": item["params"]["value"]},
                    )
                return
            time.sleep(0.01)
        raise AssertionError("worker never observed complete batch")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    out = client.call_batch(
        [
            ToolRPCRequest("test.echo", {"value": 1}, request_id="rpc1"),
            ToolRPCRequest("test.echo", {"value": 2}, request_id="rpc2"),
        ]
    )
    thread.join(timeout=1)
    assert observed == ["rpc1", "rpc2"]
    assert [r.result for r in out] == [{"echo": 1}, {"echo": 2}]
    assert all(r.ok for r in out)


def test_rpc_failure_is_data_not_transport_failure(tmp_path: Path):
    client = ToolLoopRPCClient(tmp_path, timeout_s=3, poll_interval_s=0.01)

    def worker():
        while not list_pending_rpc(tmp_path):
            time.sleep(0.01)
        write_rpc_error(tmp_path, "bad", "not allowlisted", error_type="PolicyDenied")

    threading.Thread(target=worker, daemon=True).start()
    out = client.call(ToolRPCRequest("web.fetch", {"url": "x"}, request_id="bad"))
    assert out.ok is False
    assert out.error == {"type": "PolicyDenied", "message": "not allowlisted"}


def test_rpc_response_validation_rejects_malformed_response(tmp_path: Path):
    client = ToolLoopRPCClient(tmp_path, timeout_s=1, poll_interval_s=0.01)

    def worker():
        while not list_pending_rpc(tmp_path):
            time.sleep(0.01)
        response = tmp_path / "responses" / "x.json"
        response.parent.mkdir(parents=True, exist_ok=True)
        response.write_text(json.dumps({"protocol_version": 1, "request_id": "x", "ok": "yes"}))

    threading.Thread(target=worker, daemon=True).start()
    with pytest.raises(ToolRPCError, match="boolean"):
        client.call(ToolRPCRequest("test", request_id="x"))
