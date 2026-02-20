"""
YouTube Competitor Monitoring Automation - Main Entry Point.

Orchestrates the full pipeline:
    1. Load config & competitor list
    2. Scrape all competitor channels via ScrapingDog
    3. Analyze videos to find outperformers (above channel average)
    4. Send a styled HTML email report

Run manually:  python main.py
Schedule:      cron job at 1 PM IST daily
"""

import sys
import io
import logging
from datetime import datetime

# Fix Windows console encoding for emoji/unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Logging Setup
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("automation.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


def main():
    """Run the full YouTube competitor monitoring pipeline."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("[START] YouTube Competitor Monitor - Starting")
    logger.info(f"   Run time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Step 1: Load Config
    from config import COMPETITOR_CHANNELS, SCRAPINGDOG_API_KEY, GMAIL_ADDRESS

    if not SCRAPINGDOG_API_KEY:
        logger.error("[ERROR] SCRAPINGDOG_API_KEY not set in .env file. Aborting.")
        sys.exit(1)

    if not GMAIL_ADDRESS:
        logger.warning("[WARN] Gmail credentials not configured. Email will not be sent.")

    logger.info(f"[CONFIG] Tracking {len(COMPETITOR_CHANNELS)} competitor channels")

    # Step 2: Scrape Channels
    logger.info("-" * 40)
    logger.info("[STEP 1] Fetching competitor channel data...")
    logger.info("-" * 40)

    from scraper import fetch_all_channels
    channels_data = fetch_all_channels(COMPETITOR_CHANNELS)

    if not channels_data:
        logger.error("[ERROR] No channel data retrieved. Check API key and network. Aborting.")
        sys.exit(1)

    total_videos = sum(len(ch["videos"]) for ch in channels_data)
    logger.info(f"[OK] Fetched {len(channels_data)} channels with {total_videos} total videos")

    # Step 3: Analyze for Outperformers
    logger.info("-" * 40)
    logger.info("[STEP 2] Analyzing for outperforming videos...")
    logger.info("-" * 40)

    from analyzer import analyze_all_channels
    analysis_results = analyze_all_channels(channels_data)

    total_outperforming = sum(
        len(r["outperforming_videos"]) for r in analysis_results
    )
    logger.info(f"[OK] Found {total_outperforming} outperforming videos across {len(analysis_results)} channels")

    # Print summary to console
    for result in analysis_results:
        channel = result["channel_name"]
        count = len(result["outperforming_videos"])
        avg = int(result["avg_views"])
        logger.info(f"   [CHANNEL] {channel}: {count} outperforming (avg: {avg} views)")
        for video in result["outperforming_videos"][:3]:
            title = video['title'][:50]
            logger.info(
                f"      [HIT] {title}... "
                f"({video['views']:,} views, {video['performance_ratio']}x avg)"
            )

    # Step 4: Send Email Report
    logger.info("-" * 40)
    logger.info("[STEP 3] Sending email report...")
    logger.info("-" * 40)

    from emailer import send_email_report
    email_sent = send_email_report(analysis_results)

    # Done
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    if email_sent:
        logger.info(f"[DONE] Report emailed successfully! ({elapsed:.1f}s)")
    else:
        logger.warning(f"[DONE] Completed but email failed to send. ({elapsed:.1f}s)")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
