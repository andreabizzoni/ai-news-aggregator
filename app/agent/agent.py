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


class Agent:
    def __init__(self):
        self.model = "gemini-2.5-flash"
        self.client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.langfuse = get_client()

    @observe(capture_input=False, capture_output=False, as_type="generation")
    async def add_digest(self, items: List[NewsItem]) -> List[NewsItem]:
        prompt = self.langfuse.get_prompt("digest-prompt")
        formatted_prompt = prompt.compile(
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
        prompt = self.langfuse.get_prompt("email-prompt")
        formatted_prompt = prompt.compile(
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
