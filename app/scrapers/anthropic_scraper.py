from datetime import datetime, timedelta, timezone
import feedparser
from docling.document_converter import DocumentConverter
import logging

from models.news import NewsItem

logger = logging.getLogger(__name__)


class AnthropicAIScraper:
    """Scrapes Anthropic RSS feeds for recent news articles."""

    RSS_FEED_URLS = [
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
    ]

    def __init__(self):
        """Initialize the scraper with a DocumentConverter instance."""
        self.converter = DocumentConverter()

    def scrape_news(self, time_window_hours: int = 24) -> list[NewsItem]:
        """
        Scrape Anthropic news feeds for articles published within a time window.

        Args:
            time_window_hours: Number of hours to look back (default: 24)

        Returns:
            List of NewsArticle objects published within the time window
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        articles = []

        for feed_url in self.RSS_FEED_URLS:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                continue

            for entry in feed.entries:
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(
                        *entry.published_parsed[:6], tzinfo=timezone.utc
                    )
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published_at = datetime(
                        *entry.updated_parsed[:6], tzinfo=timezone.utc
                    )
                else:
                    continue

                if published_at >= cutoff_time:
                    article = NewsItem(
                        source="Anthropic",
                        title=entry.title,
                        description=entry.description,
                        url=entry.link,
                        published_at=published_at,
                        guid=entry.guid,
                        author="Anthropic",
                    )
                    articles.append(article)

        articles.sort(key=lambda x: x.published_at, reverse=True)
        logger.info("Anthropic articles scraped successfully")
        return articles

    def convert_article_to_markdown(self, url: str) -> str:
        """
        Convert an article from URL to markdown format.

        Args:
            url: The URL of the article to convert

        Returns:
            The article content in markdown format
        """
        result = self.converter.convert(url)
        return result.document.export_to_markdown()


if __name__ == "__main__":
    scraper = AnthropicAIScraper()
    articles = scraper.scrape_news(time_window_hours=200)
    results = [scraper.convert_article_to_markdown(article.url) for article in articles]
