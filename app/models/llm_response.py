from pydantic import BaseModel, Field
from typing import List


class DigestItem(BaseModel):
    """Represents a news item digest"""

    guid: str = Field(..., description="The globally unique identifier for the item")
    digest: str = Field(..., description="The digest for the item")


class DigestLLMResponse(BaseModel):
    """Represents a structured LLM response"""

    digests: List[DigestItem] = Field(..., description="A list of digests")


class EmailItem(BaseModel):
    """Represents a single news item in the email digest."""

    title: str = Field(..., description="The headline for this digest item")
    summary: str = Field(..., description="The digest summary (2-3 sentences)")
    url: str = Field(..., description="The URL to the original content")
    source: str = Field(
        ...,
        description="Source attribution (e.g., 'OpenAI', 'Anthropic', 'Modular', 'YouTube - Channel Name')",
    )


class EmailLLMResponse(BaseModel):
    """Represents the structured content of an email digest."""

    introduction: str = Field(..., description="Brief 1-2 sentence introduction")
    digest_items: List[EmailItem] = Field(..., description="List of news digest items")
