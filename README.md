# AI News Aggregator

> Stay up-to-date with AI news, delivered to your inbox with smart summaries!

This project scrapes the latest AI news from YouTube channels, OpenAI, Anthropic and other sources, uses AI to generate smart summaries, stores everything in PostgreSQL, and emails you a digest daily.

## Quick Start

**Prerequisites**: Python 3.12+, PostgreSQL, Gmail account, and a [Google Gemini API key](https://ai.google.dev/)

1. **Install dependencies**
   ```bash
   uv sync  # or: pip install -e .
   ```

2. **Start PostgreSQL** (with Docker)
   ```bash
   docker-compose up -d
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
   
   You'll need:
   - `DATABASE_URL` - PostgreSQL connection string
   - `EMAIL_FROM`, `EMAIL_TO`, `EMAIL_PASSWORD` - Gmail credentials ([use App Password](https://support.google.com/accounts/answer/185833))
   - `GEMINI_API_KEY` - Your Gemini API key

4. **Run it**
   ```bash
   python main.py
   ```

That's it! Check your email for the digest.
