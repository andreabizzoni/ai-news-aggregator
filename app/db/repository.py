import os
from typing import List
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from .models import Base, NewsItemDB
from models.news import NewsItem

load_dotenv()


class Repository:
    """Repository for database operations."""

    def __init__(self, database_url: str | None = None):
        """Initialize the repository with a database connection.

        Args:
            database_url: Database connection URL. If not provided, reads from DATABASE_URL env var.
        """
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def save_news_items(self, items: List[NewsItem]) -> int:
        """Save news items to the database using upsert.

        Args:
            items: List of news items to save.

        Returns:
            Number of items saved.
        """
        if not items:
            return 0

        with self.SessionLocal() as session:
            for item in items:
                stmt = insert(NewsItemDB).values(
                    source=item.source,
                    title=item.title,
                    description=item.description,
                    url=item.url,
                    published_at=item.published_at,
                    guid=item.guid,
                    digest=item.digest,
                    author=item.author,
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=["guid"])
                session.execute(stmt)

            session.commit()
            return len(items)

    def get_all_youtube_videos(self) -> List[NewsItemDB]:
        """Retrieve all YouTube videos from the database."""
        with self.SessionLocal() as session:
            return session.query(NewsItemDB).all()

    def get_all_news_articles(self) -> List[NewsItemDB]:
        """Retrieve all news articles from the database."""
        with self.SessionLocal() as session:
            return session.query(NewsItemDB).all()
