from pydantic import BaseModel, Field
from typing import List

from .youtube import VideoTranscript
from .news import NewsArticle


class RunnerConfig(BaseModel):
    time_window_hours: int = Field(
        default=24, description="The time window scrapers run for"
    )
    youtube_channels: List[str] = Field(
        default=None, description="The list of channel ID's to scrape"
    )


class RunnerResult(BaseModel):
    youtube_videos: List[VideoTranscript] = Field(
        default=None, description="List of youtube video transcripts"
    )
    openai_articles: List[NewsArticle] = Field(
        default=None, description="List of OpenAI news articles"
    )
    anthropic_articles: List[NewsArticle] = Field(
        default=None, description="List of Anthropic news articles"
    )
