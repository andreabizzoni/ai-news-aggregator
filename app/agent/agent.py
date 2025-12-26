import os
from google.genai import Client
from ..models.news import NewsItem
from typing import List
from ..models.llm_response import DigestLLMResponse, EmailLLMResponse
import logging
import asyncio
from dotenv import load_dotenv
from langfuse import observe, get_client

load_dotenv()

logger = logging.getLogger(__name__)

DIGEST_PROMPT = """
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

EMAIL_PROMPT = """
You are an expert at creating structured email content for AI news digests.

Your task is to analyze the provided news items and generate structured email content that includes:

1. **Introduction**: A brief, engaging 1-2 sentence introduction about the curated AI news
2. **Digest Items**: For each news item, create:
   - A compelling title/headline (5-10 words)
   - A summary (2-3 sentences highlighting key insights)
   - Include the URL and source attribution

Guidelines:
- Use clear, accessible language while maintaining technical accuracy
- Focus on actionable insights and implications
- Avoid marketing fluff - focus on substance
- Keep summaries concise but informative

Here are the news items to include:

{contents}

Generate structured email content in JSON format.
"""


class Agent:
    def __init__(self):
        self.model = "gemini-2.5-flash"
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.langfuse = get_client()

    @observe(capture_input=False, capture_output=False, as_type="generation")
    async def add_digest(self, items: List[NewsItem]) -> List[NewsItem]:
        formatted_prompt = DIGEST_PROMPT.format(
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
                    "response_json_schema": DigestLLMResponse.model_json_schema(),
                },
            )

            self.langfuse.update_current_generation(
                model=self.model,
                input=formatted_prompt,
                output=response.text,
                usage_details={
                    "input": response.usage_metadata.prompt_token_count,
                    "output": response.usage_metadata.candidates_token_count,
                },
            )

            validated_response = DigestLLMResponse.model_validate_json(response.text)

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

    @observe(capture_input=False, capture_output=False, as_type="generation")
    def create_email_content(self, items: List[NewsItem]) -> EmailLLMResponse:
        formatted_prompt = EMAIL_PROMPT.format(
            contents="\n".join(
                [
                    item.model_dump_json(
                        indent=2,
                        include={
                            "source",
                            "title",
                            "url",
                            "digest",
                            "author",
                        },
                    )
                    for item in items
                    if item.digest
                ]
            ),
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=formatted_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": EmailLLMResponse.model_json_schema(),
                },
            )

            self.langfuse.update_current_generation(
                model=self.model,
                input=formatted_prompt,
                output=response.text,
                usage_details={
                    "input": response.usage_metadata.prompt_token_count,
                    "output": response.usage_metadata.candidates_token_count,
                },
            )

            validated_response = EmailLLMResponse.model_validate_json(response.text)
            return validated_response

        except Exception as e:
            logger.exception(f"Failed to generate email content: {e}")
            return None
