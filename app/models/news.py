from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional


class NewsItem(BaseModel):
    """Represents a news item, whether an article or a video"""

    guid: str = Field(..., description="The unique item ID")
    source: Literal["OpenAI", "Anthropic", "YouTube"] = Field(
        description="The source of the news item"
    )
    title: str = Field(..., description="The title of the news item")
    description: Optional[str] = Field(
        default=None, description="The description or summary of the news item"
    )
    url: str = Field(..., description="The URL to the item")
    published_at: datetime = Field(..., description="The publication date and time")
    author: str = Field(..., description="The author's name")
    digest: str = Field(
        default=None, description="A digest summary of the news article"
    )
