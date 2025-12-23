"""Pydantic models for the AI news aggregator."""

from .news import NewsItem
from .config import RunnerConfig, RunnerResult
from .llm_response import DigestLLMResponse, EmailItem, EmailLLMResponse

__all__ = [
    "NewsItem",
    "RunnerConfig",
    "RunnerResult",
    "DigestLLMResponse",
    "EmailLLMResponse",
    "EmailItem",
]
