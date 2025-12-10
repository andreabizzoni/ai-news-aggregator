"""Pydantic models for the AI news aggregator."""

from .news import NewsArticle
from .youtube import YouTubeVideo, VideoTranscript
from .config import RunnerConfig, RunnerResult

__all__ = [
    "NewsArticle",
    "YouTubeVideo",
    "VideoTranscript",
    "RunnerConfig",
    "RunnerResult",
]
