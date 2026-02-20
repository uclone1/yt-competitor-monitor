"""
Telegram Bot notifier.
Sends outperforming video alerts to a Telegram chat/group.
"""

import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _format_views(views):
    """Format view count with shorthand."""
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def _format_ratio(ratio):
    """Format performance ratio as percentage above average."""
    percentage = (ratio - 1) * 100
    return f"+{percentage:.0f}%"


def _build_telegram_message(analysis_results):
    """
    Build a Telegram-friendly message (supports HTML formatting).
    """
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")

    total_channels = len(analysis_results)
    total_outperforming = sum(
        len(r["outperforming_videos"]) for r in analysis_results
    )

    lines = []
    lines.append(f"🎯 <b>YouTube Competitor Report</b>")
    lines.append(f"📅 {today}")
    lines.append(f"📊 {total_outperforming} outperforming videos across {total_channels} channels")
    lines.append("")

    if not analysis_results:
        lines.append("✅ No outperforming videos found today. All competitors at baseline.")
        return "\n".join(lines)

    for result in analysis_results:
        channel = result["channel_name"]
        handle = result["handle"]
        avg = int(result["avg_views"])
        outperforming = result["outperforming_videos"]

        lines.append(f"━━━━━━━━━━━━━━━━━━")
        lines.append(f"📺 <b>{channel}</b> ({handle})")
        lines.append(f"   Avg: {_format_views(avg)} views | {len(outperforming)} hits")
        lines.append("")

        # Show top 5 videos per channel
        for video in outperforming[:5]:
            title = video["title"][:60]
            views = _format_views(video["views"])
            ratio = _format_ratio(video["performance_ratio"])
            link = video["link"]
            recent = " 🆕" if video.get("is_recent") else ""

            lines.append(f"  🔥 <a href=\"{link}\">{title}</a>{recent}")
            lines.append(f"     👁 {views} views | {ratio} above avg")
            lines.append("")

        remaining = len(outperforming) - 5
        if remaining > 0:
            lines.append(f"   ... and {remaining} more")
            lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 <i>UAbility YouTube Monitor</i>")

    return "\n".join(lines)


def send_telegram_alert(analysis_results):
    """
    Send the analysis results as a Telegram message.

    Args:
        analysis_results: list of analysis dicts from analyzer

    Returns:
        True if sent successfully, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured. Skipping Telegram alert.")
        return False

    message = _build_telegram_message(analysis_results)

    # Telegram has a 4096 character limit per message
    # If the message is too long, split it
    messages = []
    if len(message) > 4000:
        # Split by channel sections
        parts = message.split("━━━━━━━━━━━━━━━━━━")
        current = parts[0]
        for part in parts[1:]:
            if len(current) + len(part) + 20 > 4000:
                messages.append(current)
                current = "━━━━━━━━━━━━━━━━━━" + part
            else:
                current += "━━━━━━━━━━━━━━━━━━" + part
        if current:
            messages.append(current)
    else:
        messages = [message]

    url = TELEGRAM_API.format(token=TELEGRAM_BOT_TOKEN)
    success = True

    for i, msg in enumerate(messages):
        try:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Telegram message {i + 1}/{len(messages)} sent successfully!")
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text[:200]}")
                success = False

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            success = False

    if success:
        logger.info("[OK] Telegram alerts sent!")
    return success
