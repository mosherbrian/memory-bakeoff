from __future__ import annotations

import json
from pathlib import Path
import threading
import time

from memory_bakeoff.llm import (
    ChatGPTSidecarLLM,
    DeterministicFakeLLM,
    LLMMessage,
    LLMRequest,
    list_pending,
    write_sidecar_response,
)


def req(text: str, request_id: str | None = None) -> LLMRequest:
    return LLMRequest(messages=(LLMMessage("system", "Be concise."), LLMMessage("user", text)), request_id=request_id)


def test_request_fingerprint_ignores_metadata():
    a = LLMRequest(messages=(LLMMessage("user", "hello"),), metadata={"run": 1})
    b = LLMRequest(messages=(LLMMessage("user", "hello"),), metadata={"run": 2})
    assert a.fingerprint() == b.fingerprint()


def test_fake_is_deterministic():
    llm = DeterministicFakeLLM()
    a = llm.complete(req("hello"))
    b = llm.complete(req("hello"))
    assert a.content == b.content == "[fake] hello"


def test_sidecar_batch_enqueues_before_waiting(tmp_path: Path):
    llm = ChatGPTSidecarLLM(tmp_path, timeout_s=3, poll_interval_s=0.01)
    seen: list[str] = []

    def worker():
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            pending = list_pending(tmp_path)
            if len(pending) == 2:
                seen.extend(x["request_id"] for x in pending)
                for item in pending:
                    prompt = item["openai_request"]["messages"][-1]["content"]
                    write_sidecar_response(tmp_path, item["request_id"], f"answer:{prompt}")
                return
            time.sleep(0.01)
        raise AssertionError("worker never observed complete batch")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    out = llm.complete_batch([req("one", "r1"), req("two", "r2")])
    thread.join(timeout=1)
    assert seen == ["r1", "r2"]
    assert [x.content for x in out] == ["answer:one", "answer:two"]


def test_sidecar_files_are_openai_shaped(tmp_path: Path):
    llm = ChatGPTSidecarLLM(tmp_path, timeout_s=3, poll_interval_s=0.01)

    def worker():
        while True:
            pending = list_pending(tmp_path)
            if pending:
                item = pending[0]
                assert item["openai_request"]["messages"][0] == {"role": "system", "content": "Be concise."}
                write_sidecar_response(tmp_path, item["request_id"], "ok")
                return
            time.sleep(0.01)

    threading.Thread(target=worker, daemon=True).start()
    response = llm.complete(req("test", "known-id"))
    assert response.request_id == "known-id"
    assert response.content == "ok"
    raw = json.loads((tmp_path / "requests" / "known-id.json").read_text())
    assert raw["protocol_version"] == 1


def test_factory_creates_fake():
    from memory_bakeoff.llm import create_llm_backend
    llm = create_llm_backend("fake")
    assert llm.complete(req("x")).content == "[fake] x"


def test_replay_llm_validates_fingerprint(tmp_path):
    import json
    from memory_bakeoff.llm import LLMMessage, LLMRequest
    from memory_bakeoff.llm.replay import ReplayLLM
    from memory_bakeoff.llm.base import LLMBackendError
    import pytest

    trace = tmp_path / "trace"
    (trace / "requests").mkdir(parents=True)
    (trace / "responses").mkdir()
    req = LLMRequest(messages=(LLMMessage("user", "hello"),), request_id="r1")
    (trace / "requests" / "r1.json").write_text(json.dumps({"fingerprint": req.fingerprint()}))
    (trace / "responses" / "r1.json").write_text(json.dumps({"request_id": "r1", "content": "world"}))
    assert ReplayLLM(trace).complete(req).content == "world"

    changed = LLMRequest(messages=(LLMMessage("user", "different"),), request_id="r1")
    with pytest.raises(LLMBackendError, match="fingerprint mismatch"):
        ReplayLLM(trace).complete(changed)


def test_anthropic_proxy_normalizes_messages_and_tools():
    from memory_bakeoff.llm.proxy import _anthropic_request, _anthropic_response, _anthropic_sse_events
    from memory_bakeoff.llm.base import LLMResponse

    payload = {
        "model": "claude-test",
        "system": [{"type": "text", "text": "compress observations"}],
        "messages": [{"role": "user", "content": [{"type": "text", "text": "hello"}]}],
        "max_tokens": 123,
        "tools": [{"name": "store", "description": "store fact", "input_schema": {"type": "object", "properties": {"x": {"type": "string"}}}}],
        "tool_choice": {"type": "tool", "name": "store"},
    }
    req = _anthropic_request(payload)
    assert req.messages[0].role == "system"
    assert req.messages[1].content == "hello"
    assert req.tools[0]["function"]["name"] == "store"
    assert req.tool_choice == {"type": "function", "function": {"name": "store"}}

    out = _anthropic_response(LLMResponse(content="done", model="sidecar"), req)
    assert out["type"] == "message"
    assert out["content"] == [{"type": "text", "text": "done"}]
    events = _anthropic_sse_events(out)
    assert events[0][0] == "message_start"
    assert events[-1][0] == "message_stop"


def test_anthropic_proxy_maps_tool_call_response():
    from memory_bakeoff.llm.proxy import _anthropic_response
    from memory_bakeoff.llm.base import LLMResponse
    request = req("x")
    response = LLMResponse(
        content="",
        tool_calls=[{"id": "call1", "type": "function", "function": {"name": "store", "arguments": '{"x":"y"}'}}],
    )
    out = _anthropic_response(response, request)
    assert out["stop_reason"] == "tool_use"
    assert out["content"][0] == {"type": "tool_use", "id": "call1", "name": "store", "input": {"x": "y"}}
