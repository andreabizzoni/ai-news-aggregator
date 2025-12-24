from .models import RunnerConfig
from .models.news import NewsItem
from .scrapers import AnthropicAIScraper, YouTubeScraper, OpenAIScraper, ModularScraper
from .db import Repository
from .agent import Agent
from .services import EmailService
import asyncio
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, config: RunnerConfig, repository: Repository):
        self.time_window_hours = config.time_window_hours
        self.youtube_channels = config.youtube_channels
        self.repository = repository
        self.agent = Agent()
        self.email_service = EmailService()

    async def _run_digest_async(
        self, articles: List[NewsItem], videos: List[NewsItem]
    ) -> Tuple[List[NewsItem], List[NewsItem]]:
        articles_task = self.agent.add_digest(articles)
        videos_task = self.agent.add_digest(videos)
        return await asyncio.gather(articles_task, videos_task)

    async def _scrape_all_async(
        self,
    ) -> Tuple[List[NewsItem], List[NewsItem], List[NewsItem], List[NewsItem]]:
        youtube_scraper = YouTubeScraper()
        openai_scraper = OpenAIScraper()
        anthropic_scraper = AnthropicAIScraper()
        modular_scraper = ModularScraper()

        tasks = []

        for channel in self.youtube_channels:
            task = asyncio.to_thread(
                youtube_scraper.scrape_youtube_channel, channel, self.time_window_hours
            )
            tasks.append(task)

        openai_task = asyncio.to_thread(
            openai_scraper.scrape_news, self.time_window_hours
        )
        tasks.append(openai_task)

        anthropic_task = asyncio.to_thread(
            anthropic_scraper.scrape_news, self.time_window_hours
        )
        tasks.append(anthropic_task)

        modular_task = asyncio.to_thread(
            modular_scraper.scrape_news, self.time_window_hours
        )
        tasks.append(modular_task)

        results = await asyncio.gather(*tasks)

        youtube_videos = []
        for result in results[:-3]:
            youtube_videos.extend(result)

        openai_articles = results[-3]
        anthropic_articles = results[-2]
        modular_articles = results[-1]

        return youtube_videos, openai_articles, anthropic_articles, modular_articles

    def run(self):
        youtube_videos, openai_articles, anthropic_articles, modular_articles = (
            asyncio.run(self._scrape_all_async())
        )

        all_articles = openai_articles + anthropic_articles + modular_articles

        digested_articles, digested_youtube_videos = asyncio.run(
            self._run_digest_async(all_articles, youtube_videos)
        )

        videos_saved = self.repository.save_news_items(digested_youtube_videos)
        articles_saved = self.repository.save_news_items(digested_articles)
        logger.info(
            f"Saved {videos_saved} videos and {articles_saved} articles to database"
        )

        all_digested_items = digested_articles + digested_youtube_videos
        email_content = self.agent.create_email_content(all_digested_items)
        email_sent = self.email_service.send_email(email_content)

        if not email_sent:
            logger.error("Failed to send email. Check logs for details")
