import logging
from app.db.repository import Repository
from app.models.config import RunnerConfig
from app.runner import Runner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("ai_news_aggregator.log")],
)

logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("Starting AI News Aggregator...")

        repository = Repository()
        repository.create_tables()
        logger.info("Database initialized successfully")

        config = RunnerConfig(
            time_window_hours=24,
            youtube_channels=[
                "UCLKPca3kwwd-B59HNr-_lvA",
                "UCn8ujwUInbJkBhffxqAPBVQ",
            ],
        )

        runner = Runner(config, repository)
        runner.run()

    except Exception as e:
        logger.error(f"Fatal error in AI News Aggregator: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
