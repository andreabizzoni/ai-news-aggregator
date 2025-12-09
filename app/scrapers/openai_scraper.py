"""OpenAI news scraper using RSS feed."""

from datetime import datetime, timedelta, timezone
import feedparser
from pydantic import BaseModel


class NewsArticle(BaseModel):
    """Represents an OpenAI news article."""

    title: str
    description: str
    url: str
    published_at: datetime
    guid: str


class OpenAIScraper:
    """Scrapes OpenAI RSS feed for recent news articles."""

    RSS_FEED_URL = "https://openai.com/news/rss.xml"

    def scrape_news(self, time_window_hours: int = 24) -> list[NewsArticle]:
        """
        Scrape OpenAI news feed for articles published within a time window.

        Args:
            time_window_hours: Number of hours to look back (default: 24)

        Returns:
            List of NewsArticle objects published within the time window
        """
        feed = feedparser.parse(self.RSS_FEED_URL)

        if not feed.entries:
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        articles = []

        for entry in feed.entries:
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published_at >= cutoff_time:
                article = NewsArticle(
                    title=entry.title,
                    description=entry.description,
                    url=entry.link,
                    published_at=published_at,
                    guid=entry.guid,
                )
                articles.append(article)

        return articles


if __name__ == "__main__":
    scraper = OpenAIScraper()
    articles = scraper.scrape_news(time_window_hours=24)
