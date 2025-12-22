from models import RunnerConfig, RunnerResult
from scrapers import AnthropicAIScraper, YouTubeScraper, OpenAIScraper


class Runner:
    def __init__(self, config: RunnerConfig):
        self.time_window_hours = config.time_window_hours
        self.youtube_channels = config.youtube_channels

    def run(self):
        youtube_scraper = YouTubeScraper()
        openai_scraper = OpenAIScraper()
        anthropic_scraper = AnthropicAIScraper()

        youtube_videos = []
        for channel in self.youtube_channels:
            for video in youtube_scraper.scrape_youtube_channel(
                channel, self.time_window_hours
            ):
                youtube_videos.append(video)

        openai_articles = openai_scraper.scrape_news(self.time_window_hours)
        anthropic_articles = anthropic_scraper.scrape_news(self.time_window_hours)

        return RunnerResult(
            youtube_videos=youtube_videos,
            openai_articles=openai_articles,
            anthropic_articles=anthropic_articles,
        )


if __name__ == "__main__":
    config = RunnerConfig(
        time_window_hours=24,
        youtube_channels=["UCLKPca3kwwd-B59HNr-_lvA", "UCn8ujwUInbJkBhffxqAPBVQ"],
    )
    runner = Runner(config)
    result = runner.run()
    print(result)
