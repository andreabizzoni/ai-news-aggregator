from google.genai import Client
from models.news import NewsItem
from typing import List
from models.llm_response import LLMResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

PROMPT = """
You are an expert AI news analyst specializing in summarizing technical articles, research papers, and video content about artificial intelligence.

Your role is to create concise, informative digests that help readers quickly understand the key points and significance of AI-related content.

Guidelines:
- Create a compelling title (5-10 words) that captures the essence of the content
- Write a 2-3 sentence summary that highlights the main points and why they matter
- Focus on actionable insights and implications
- Use clear, accessible language while maintaining technical accuracy
- Avoid marketing fluff - focus on substance

These are the contents to create digests for:

{contents}
"""


class Agent:
    def __init__(self):
        self.model = "gemini-2.5-flash"
        self.client = Client()
        self.prompt = PROMPT

    async def add_digest(self, items: List[NewsItem]) -> List[NewsItem]:
        formatted_prompt = self.prompt.format(
            contents="\n".join(
                [
                    item.model_dump_json(
                        indent=2, include={"guid", "source", "title", "description"}
                    )
                    for item in items
                ]
            )
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=formatted_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": LLMResponse.model_json_schema(),
                },
            )
            validated_response = LLMResponse.model_validate_json(response.text)

            digest_map = {
                digest.guid: digest.digest for digest in validated_response.digests
            }

            for item in items:
                if item.guid in digest_map:
                    item.digest = digest_map[item.guid]
            return items

        except Exception as e:
            logger.exception(f"Failed to generate digests for news articles: {e}")
            return items
