from models import RunnerConfig, RunnerResult
from models.news import NewsItem
from scrapers import AnthropicAIScraper, YouTubeScraper, OpenAIScraper
from db import Repository
from agent import Agent
import asyncio
from typing import List, Tuple


class Runner:
    def __init__(self, config: RunnerConfig, repository: Repository):
        self.time_window_hours = config.time_window_hours
        self.youtube_channels = config.youtube_channels
        self.repository = repository
        self.agent = Agent()

    async def _run_digest_async(
        self, articles: List[NewsItem], videos: List[NewsItem]
    ) -> Tuple[List[NewsItem], List[NewsItem]]:
        """Run digest operations concurrently"""
        articles_task = self.agent.add_digest(articles)
        videos_task = self.agent.add_digest(videos)
        return await asyncio.gather(articles_task, videos_task)

    async def _scrape_all_async(
        self,
    ) -> Tuple[List[NewsItem], List[NewsItem], List[NewsItem]]:
        """Run all scraping operations concurrently"""
        youtube_scraper = YouTubeScraper()
        openai_scraper = OpenAIScraper()
        anthropic_scraper = AnthropicAIScraper()

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

        results = await asyncio.gather(*tasks)

        youtube_videos = []
        for result in results[:-2]:  # All but last 2 are YouTube results
            youtube_videos.extend(result)

        openai_articles = results[-2]  # Second to last
        anthropic_articles = results[-1]  # Last

        return youtube_videos, openai_articles, anthropic_articles

    def run(self) -> RunnerResult:
        youtube_videos, openai_articles, anthropic_articles = asyncio.run(
            self._scrape_all_async()
        )

        all_articles = openai_articles + anthropic_articles

        digested_articles, digested_youtube_videos = asyncio.run(
            self._run_digest_async(all_articles, youtube_videos)
        )

        videos_saved = self.repository.save_news_items(digested_youtube_videos)
        articles_saved = self.repository.save_news_items(digested_articles)

        return RunnerResult(
            youtube_videos=digested_youtube_videos,
            videos_saved=videos_saved,
            articles=digested_articles,
            articles_saved=articles_saved,
        )


if __name__ == "__main__":
    repository = Repository()
    repository.create_tables()

    config = RunnerConfig(
        time_window_hours=100,
        youtube_channels=["UCLKPca3kwwd-B59HNr-_lvA", "UCn8ujwUInbJkBhffxqAPBVQ"],
    )
    runner = Runner(config, repository)
    result = runner.run()
    print("\nScraping completed successfully!")
    print(f"YouTube videos: {result.videos_saved}")
    print(f"Articles: {result.articles_saved}")
