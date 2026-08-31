from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str
    name: str | None = None

    def to_openai(self) -> dict[str, Any]:
        data: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            data["name"] = self.name
        return data


@dataclass(frozen=True)
class LLMRequest:
    """Transport-neutral request intentionally shaped like OpenAI Chat Completions.

    The benchmark uses only this contract. Backends translate it to OpenAI, Anthropic,
    llama.cpp/vLLM OpenAI-compatible HTTP, the ChatGPT file sidecar, or a fake model.
    """

    messages: tuple[LLMMessage, ...]
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int | None = None
    response_format: dict[str, Any] | None = None
    tools: tuple[dict[str, Any], ...] = ()
    tool_choice: str | dict[str, Any] | None = None
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    request_id: str | None = None

    @classmethod
    def from_openai(cls, payload: Mapping[str, Any], *, metadata: dict[str, Any] | None = None) -> "LLMRequest":
        messages = tuple(
            LLMMessage(role=str(m["role"]), content=_content_to_text(m.get("content", "")), name=m.get("name"))
            for m in payload.get("messages", [])
        )
        tools = tuple(payload.get("tools") or ())
        return cls(
            messages=messages,
            model=payload.get("model"),
            temperature=float(payload.get("temperature", 0.0) or 0.0),
            max_tokens=payload.get("max_tokens") or payload.get("max_completion_tokens"),
            response_format=payload.get("response_format"),
            tools=tools,
            tool_choice=payload.get("tool_choice"),
            seed=payload.get("seed"),
            metadata=dict(metadata or {}),
            request_id=payload.get("request_id"),
        )

    def to_openai(self, *, default_model: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self.model or default_model or "default",
            "messages": [m.to_openai() for m in self.messages],
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            body["max_tokens"] = self.max_tokens
        if self.response_format is not None:
            body["response_format"] = self.response_format
        if self.tools:
            body["tools"] = list(self.tools)
        if self.tool_choice is not None:
            body["tool_choice"] = self.tool_choice
        if self.seed is not None:
            body["seed"] = self.seed
        return body

    def canonical_dict(self) -> dict[str, Any]:
        # Metadata is intentionally excluded: it may contain run IDs or bookkeeping that
        # should not change replay/fixture identity for semantically identical requests.
        return {
            "messages": [m.to_openai() for m in self.messages],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
            "tools": list(self.tools),
            "tool_choice": self.tool_choice,
            "seed": self.seed,
        }

    def fingerprint(self) -> str:
        raw = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class LLMResponse:
    content: str
    model: str | None = None
    finish_reason: str | None = "stop"
    usage: LLMUsage = field(default_factory=LLMUsage)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw: Any = None
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "usage": asdict(self.usage),
            "tool_calls": self.tool_calls,
            "request_id": self.request_id,
        }


class LLMBackendError(RuntimeError):
    pass


class LLMClient(ABC):
    name: str

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        ...

    def complete_batch(self, requests: Sequence[LLMRequest]) -> list[LLMResponse]:
        """Default batching preserves order; backends may override for true batching."""
        return [self.complete(request) for request in requests]


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, Mapping):
                if isinstance(part.get("text"), str):
                    parts.append(part["text"])
                elif part.get("type") == "text" and isinstance(part.get("content"), str):
                    parts.append(part["content"])
        return "\n".join(parts)
    return str(content or "")


def simple_token_estimate(text: str) -> int:
    # Used only when a backend does not report usage. Never presented as tokenizer-exact.
    return max(1, (len(text) + 3) // 4) if text else 0


def message_text(messages: Iterable[LLMMessage]) -> str:
    return "\n".join(m.content for m in messages)
