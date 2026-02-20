"""
Configuration for YouTube Competitor Monitoring Automation.
Loads secrets from .env and defines competitor channels + settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── API Keys ───────────────────────────────────────────────
SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY", "")

# ─── Email Settings ─────────────────────────────────────────
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

# ─── ScrapingDog Endpoints ──────────────────────────────────
SCRAPINGDOG_BASE = "https://api.scrapingdog.com/youtube"
CHANNEL_ENDPOINT = f"{SCRAPINGDOG_BASE}/channel/"
SEARCH_ENDPOINT = f"{SCRAPINGDOG_BASE}/search/"
VIDEO_ENDPOINT = f"{SCRAPINGDOG_BASE}/video/"

# ─── Competitor Channels ────────────────────────────────────
# YouTube handles of competitor channels in the AI / no-code / automation niche.
# Add or remove channels here. Use the @handle format.
COMPETITOR_CHANNELS = [
    "@buildwithkaran",
    "@AIJasonZ",
    "@MattVidPro",
    "@WorldofAI",
    "@AllAboutAI",
    "@maboroshitech",
    "@SkillLeapAI",
    "@TheAIGRID",
    "@NoCodeFamily",
    "@MattWolfe",
    "@1littlecoder",
    "@GregIsenberg",
    "@aiaborsh",
    "@income_stream_surfers",
    "@FutureTools",
]

# ─── Analysis Settings ──────────────────────────────────────
# Only consider videos published within this many days as "recent"
RECENT_DAYS = 90

# Minimum performance ratio (views / avg) to flag as outperforming
# 1.0 means above average, 1.5 means 50% above average, etc.
MIN_PERFORMANCE_RATIO = 1.0
