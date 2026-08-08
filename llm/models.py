from dataclasses import dataclass


@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    reasoning_tokens: int | None = None
    cost: float | None = None


@dataclass(frozen=True)
class LLMResponse:
    content: str
    finish_reason: str | None
    usage: LLMUsage | None = None


__all__ = ["LLMResponse", "LLMUsage"]
