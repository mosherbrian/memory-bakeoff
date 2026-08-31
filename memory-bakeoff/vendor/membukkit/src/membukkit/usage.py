"""No-cost usage shim for vendored MemBukkit raw retrieval."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    source: str = "none"
    calls: int = 0
    @property
    def total_tokens(self):
        return self.prompt_tokens + self.completion_tokens
    def to_dict(self):
        return {"prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens, "source": self.source, "calls": self.calls}

class _Meter:
    def take(self):
        return TokenUsage()

_METER = _Meter()

def get_meter():
    return _METER

def estimate_tokens(*texts):
    return max(0, sum(len(text or "") for text in texts) // 4)

def estimate_cost_usd(*args, **kwargs):
    return None

def llm_model_spec(*args, **kwargs):
    return ""
def window_fraction(*args, **kwargs):
    return 0.0
