from __future__ import annotations

from pathlib import Path
from typing import Any

from memory_bakeoff.llm.anthropic import AnthropicLLM
from memory_bakeoff.llm.base import LLMClient
from memory_bakeoff.llm.fake import DeterministicFakeLLM
from memory_bakeoff.llm.openai_compat import OpenAICompatibleLLM
from memory_bakeoff.llm.replay import ReplayLLM
from memory_bakeoff.llm.sidecar import ChatGPTSidecarLLM


def create_llm_backend(name: str, **kwargs: Any) -> LLMClient:
    name = name.strip().lower().replace("-", "_")
    if name == "fake":
        return DeterministicFakeLLM(fixture_path=kwargs.get("fixture_path"))
    if name in {"chatgpt", "chatgpt_sidecar", "sidecar"}:
        return ChatGPTSidecarLLM(
            queue_dir=kwargs.get("queue_dir"),
            timeout_s=float(kwargs.get("timeout_s", 900.0)),
            model_label=kwargs.get("model") or "chatgpt-sidecar",
        )
    if name == "replay":
        return ReplayLLM(trace_dir=kwargs.get("trace_dir") or kwargs.get("queue_dir") or "results/sidecar_reader_trace")
    if name in {"openai", "openai_compat", "openai_compatible"}:
        return OpenAICompatibleLLM(
            base_url=kwargs.get("base_url"),
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
            timeout_s=float(kwargs.get("timeout_s", 120.0)),
        )
    if name == "anthropic":
        return AnthropicLLM(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
            timeout_s=float(kwargs.get("timeout_s", 120.0)),
        )
    raise ValueError(f"Unknown LLM backend: {name}")


LLM_BACKENDS = ("fake", "chatgpt_sidecar", "replay", "openai_compat", "anthropic")
