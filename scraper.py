"""
ScrapingDog YouTube API client.
Fetches channel data (videos, views, subscribers) from ScrapingDog's YouTube Channel API.
"""

import time
import logging
import requests
from config import SCRAPINGDOG_API_KEY, CHANNEL_ENDPOINT

logger = logging.getLogger(__name__)

# ─── Retry / Rate-limit settings ────────────────────────────
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubles each retry
REQUEST_DELAY = 1.5  # seconds between API calls


def _parse_view_count(views_str):
    """
    Parse view count from various formats returned by ScrapingDog.
    Examples: "876,754,415 views", "3M", 33, "33", "3,903,884 views"
    Returns an integer view count or 0 if unparsable.
    """
    if isinstance(views_str, (int, float)):
        return int(views_str)

    if not isinstance(views_str, str):
        return 0

    # Remove commas, "views" text, and whitespace
    cleaned = views_str.lower().replace(",", "").replace("views", "").strip()

    if not cleaned:
        return 0

    # Handle shorthand like "3M", "1.2K", "19M"
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    last_char = cleaned[-1]
    if last_char in multipliers:
        try:
            number = float(cleaned[:-1])
            return int(number * multipliers[last_char])
        except ValueError:
            return 0

    # Plain number
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _parse_published_time(published_str):
    """
    Parse relative time strings like '3 months ago', '1 day ago', '2 years ago'
    into approximate number of days.
    Returns int (days) or None if unparsable.
    """
    if not isinstance(published_str, str):
        return None

    parts = published_str.lower().strip().split()
    if len(parts) < 3:
        return None

    try:
        number = int(parts[0])
    except ValueError:
        return None

    unit = parts[1]
    if "hour" in unit:
        return 0
    elif "day" in unit:
        return number
    elif "week" in unit:
        return number * 7
    elif "month" in unit:
        return number * 30
    elif "year" in unit:
        return number * 365
    return None


def fetch_channel_data(channel_handle):
    """
    Fetch channel data from ScrapingDog YouTube Channel API.

    Args:
        channel_handle: YouTube channel handle (e.g., '@MattWolfe')

    Returns:
        dict with keys:
            - 'channel_name': str
            - 'handle': str
            - 'subscribers': int
            - 'total_videos_count': int
            - 'videos': list of dicts with keys:
                - 'id': str
                - 'title': str
                - 'link': str
                - 'views': int
                - 'published_time': str (original)
                - 'days_ago': int or None
                - 'thumbnail': str
                - 'length': str
        Returns None if the request fails after all retries.
    """
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "channel_id": channel_handle,
    }

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                wait_time = RETRY_BACKOFF * (2 ** (attempt - 1))
                logger.warning(f"Retry {attempt}/{MAX_RETRIES} for {channel_handle}, waiting {wait_time}s...")
                time.sleep(wait_time)

            logger.info(f"Fetching channel data for {channel_handle} (attempt {attempt + 1})")
            response = requests.get(CHANNEL_ENDPOINT, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                return _parse_channel_response(data, channel_handle)
            else:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.warning(f"API error for {channel_handle}: {last_error}")

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            logger.warning(f"Request failed for {channel_handle}: {last_error}")
        except Exception as e:
            last_error = str(e)
            logger.error(f"Unexpected error for {channel_handle}: {last_error}")

    logger.error(f"All {MAX_RETRIES} attempts failed for {channel_handle}: {last_error}")
    return None


def _parse_channel_response(data, channel_handle):
    """
    Parse the raw ScrapingDog channel API response into a clean structure.
    """
    # Extract channel info
    channel_info = data.get("channel", {})
    about_info = data.get("about", {})

    channel_name = channel_info.get("title", channel_handle)
    subscribers = about_info.get("subscribers", 0)
    if isinstance(subscribers, str):
        subscribers = _parse_view_count(subscribers)
    total_videos_count = about_info.get("videos", 0)

    # Collect all videos from all sections
    all_videos = []
    seen_ids = set()  # Avoid duplicates across sections

    # Process video sections
    video_sections = data.get("videos_sections", [])
    for section in video_sections:
        section_videos = section.get("videos", [])
        for vid in section_videos:
            vid_id = vid.get("id", "")
            if vid_id and vid_id not in seen_ids:
                seen_ids.add(vid_id)
                views = _parse_view_count(vid.get("views", 0))
                published_time = vid.get("published_time", "")
                days_ago = _parse_published_time(published_time)

                all_videos.append({
                    "id": vid_id,
                    "title": vid.get("title", "Untitled"),
                    "link": vid.get("link", f"https://www.youtube.com/watch?v={vid_id}"),
                    "views": views,
                    "published_time": published_time,
                    "days_ago": days_ago,
                    "thumbnail": vid.get("thumbnail", ""),
                    "length": vid.get("length", ""),
                })

    logger.info(f"Parsed {channel_name}: {len(all_videos)} videos, {subscribers} subscribers")

    return {
        "channel_name": channel_name,
        "handle": channel_handle,
        "subscribers": subscribers,
        "total_videos_count": total_videos_count,
        "videos": all_videos,
    }


def fetch_all_channels(channel_handles):
    """
    Fetch data for multiple channels with rate limiting.

    Args:
        channel_handles: list of YouTube channel handles

    Returns:
        list of channel data dicts (None entries are filtered out)
    """
    results = []
    for i, handle in enumerate(channel_handles):
        data = fetch_channel_data(handle)
        if data:
            results.append(data)
        else:
            logger.warning(f"Skipping {handle} — failed to fetch data")

        # Rate limiting between requests
        if i < len(channel_handles) - 1:
            time.sleep(REQUEST_DELAY)

    logger.info(f"Successfully fetched {len(results)}/{len(channel_handles)} channels")
    return results
