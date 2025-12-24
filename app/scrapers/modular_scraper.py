from datetime import datetime, timedelta, timezone
import feedparser
import logging

from ..models.news import NewsItem

logger = logging.getLogger(__name__)


class ModularScraper:
    """Scrapes Modular RSS feed for recent news articles."""

    RSS_FEED_URL = "https://www.modular.com/blog/rss.xml"

    def scrape_news(self, time_window_hours: int = 24) -> list[NewsItem]:
        feed = feedparser.parse(self.RSS_FEED_URL)

        if not feed.entries:
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        articles = []

        for entry in feed.entries:
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published_at >= cutoff_time:
                article = NewsItem(
                    source="Modular",
                    title=entry.title,
                    description=entry.description,
                    url=entry.link,
                    published_at=published_at,
                    guid=entry.guid,
                    author="Modular",
                )
                articles.append(article)

        logger.info("Modular articles scraped successfully")
        return articles
