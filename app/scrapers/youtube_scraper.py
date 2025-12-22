from datetime import datetime, timedelta, timezone
from typing import List
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
import logging

from models.news import NewsItem

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Scrapes YouTube channel RSS feeds for recent videos."""

    RSS_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def get_transcript(self, video_id: str) -> str:
        """
        Fetch the transcript for a YouTube video.

        Args:
            video_id: The YouTube video ID

        Returns:
            The full transcript as a string
        """
        ytt_api = YouTubeTranscriptApi()
        try:
            transcript_list = ytt_api.fetch(video_id)
            return " ".join([snippet.text for snippet in transcript_list])
        except Exception:
            return None

    def scrape_youtube_channel(
        self, channel_id: str, time_window_hours: int = 24
    ) -> List[NewsItem]:
        """
        Scrape a YouTube channel for videos published within a time window.

        Args:
            channel_id: The YouTube channel ID
            time_window_hours: Number of hours to look back (default: 24)

        Returns:
            List of YouTubeVideo objects published within the time window
        """
        feed_url = self.RSS_FEED_URL.format(channel_id=channel_id)
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            logger.info("No YouTube videos available to scrape")
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        videos = []

        for entry in feed.entries:
            if "/shorts/" in entry.link:
                continue

            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published_at >= cutoff_time:
                video = NewsItem(
                    guid=entry.yt_videoid,
                    source="YouTube",
                    title=entry.title,
                    url=entry.link,
                    published_at=published_at,
                    author=entry.author,
                    description=self.get_transcript(entry.yt_videoid),
                )
                videos.append(video)
        logger.info("YouTube videos scraped successfully")
        return videos
