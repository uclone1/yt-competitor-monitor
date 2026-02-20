"""
Outperforming video detection engine.
Analyzes channel data to find videos performing above the channel's average view count.
"""

import logging
from config import RECENT_DAYS, MIN_PERFORMANCE_RATIO

logger = logging.getLogger(__name__)


def analyze_channel(channel_data):
    """
    Analyze a single channel's videos to find outperforming ones.

    A video is "outperforming" if its view count is above the channel's
    average view count across all visible videos.

    Args:
        channel_data: dict from scraper.fetch_channel_data()

    Returns:
        dict with keys:
            - 'channel_name': str
            - 'handle': str
            - 'subscribers': int
            - 'avg_views': float
            - 'total_videos_analyzed': int
            - 'outperforming_videos': list of video dicts with extra 'performance_ratio' key
    """
    channel_name = channel_data["channel_name"]
    videos = channel_data["videos"]

    if not videos:
        logger.warning(f"No videos found for {channel_name}")
        return {
            "channel_name": channel_name,
            "handle": channel_data["handle"],
            "subscribers": channel_data["subscribers"],
            "avg_views": 0,
            "total_videos_analyzed": 0,
            "outperforming_videos": [],
        }

    # Filter to only videos with valid view counts (> 0)
    valid_videos = [v for v in videos if v["views"] > 0]

    if not valid_videos:
        logger.warning(f"No videos with valid view counts for {channel_name}")
        return {
            "channel_name": channel_name,
            "handle": channel_data["handle"],
            "subscribers": channel_data["subscribers"],
            "avg_views": 0,
            "total_videos_analyzed": 0,
            "outperforming_videos": [],
        }

    # Calculate average view count
    total_views = sum(v["views"] for v in valid_videos)
    avg_views = total_views / len(valid_videos)

    # Find outperforming videos (above average)
    outperforming = []
    for video in valid_videos:
        ratio = video["views"] / avg_views if avg_views > 0 else 0
        if ratio >= MIN_PERFORMANCE_RATIO:
            video_copy = video.copy()
            video_copy["performance_ratio"] = round(ratio, 2)
            video_copy["is_recent"] = (
                video["days_ago"] is not None and video["days_ago"] <= RECENT_DAYS
            )
            outperforming.append(video_copy)

    # Sort by performance ratio (highest first)
    outperforming.sort(key=lambda v: v["performance_ratio"], reverse=True)

    # Keep only the top performers (above average means ratio > 1.0)
    # Filter to truly outperforming (ratio > 1.0 means above average)
    truly_outperforming = [v for v in outperforming if v["performance_ratio"] > 1.0]

    logger.info(
        f"{channel_name}: avg={avg_views:.0f} views, "
        f"{len(truly_outperforming)}/{len(valid_videos)} outperforming"
    )

    return {
        "channel_name": channel_name,
        "handle": channel_data["handle"],
        "subscribers": channel_data["subscribers"],
        "avg_views": round(avg_views, 0),
        "total_videos_analyzed": len(valid_videos),
        "outperforming_videos": truly_outperforming,
    }


def analyze_all_channels(channels_data):
    """
    Analyze all channels and return combined results.

    Args:
        channels_data: list of channel data dicts from scraper

    Returns:
        list of analysis result dicts (only channels with outperforming videos)
    """
    results = []
    total_outperforming = 0

    for channel in channels_data:
        analysis = analyze_channel(channel)
        if analysis["outperforming_videos"]:
            results.append(analysis)
            total_outperforming += len(analysis["outperforming_videos"])

    # Sort by number of outperforming videos (most first)
    results.sort(key=lambda r: len(r["outperforming_videos"]), reverse=True)

    logger.info(
        f"Analysis complete: {total_outperforming} outperforming videos "
        f"across {len(results)} channels"
    )

    return results
