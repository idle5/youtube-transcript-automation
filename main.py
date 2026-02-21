 """
YouTube Playlist Transcript Automation Tool
Purpose: Bulk transcript extraction for technical certification study workflow
Developed during CCNA preparation to automate video content indexing
Author: Andriy Karp

"""

import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Optional

import youtube_transcript_api.formatters as formatters
from dotenv import load_dotenv
from pytubefix import Playlist
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("transcript_download.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration management for transcript downloader."""

    PLAYLIST_URL = os.getenv(
        "PLAYLIST_URL",
        "https://www.youtube.com/playlist?list=PLxbwE86jKRgMpuZuLBivzlM8s2Dk5lXBQ",
    )
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "transcripts")
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "0.5"))

    # Proxy configuration (optional)
    USE_PROXY = os.getenv("USE_PROXY", "false").lower() in ("true", "1", "yes")
    PROXY_USER = os.getenv("PROXY_USER")
    PROXY_PASS = os.getenv("PROXY_PASS")


@dataclass
class DownloadStats:
    """Track download statistics and success metrics."""

    total: int = 0
    success: int = 0
    skipped: int = 0
    failed: int = 0

    def print_summary(self):
        """Display formatted summary of download results."""
        logger.info(f"\n{'=' * 60}")
        logger.info("DOWNLOAD SUMMARY:")
        logger.info(f"  Total Videos:  {self.total}")
        logger.info(f"  Successful:    {self.success}")
        logger.info(f"  Skipped:       {self.skipped}")
        logger.info(f"  Failed:        {self.failed}")
        if self.total > 0:
            success_rate = ((self.success + self.skipped) / self.total) * 100
            logger.info(f"  Success Rate:  {success_rate:.1f}%")
        logger.info(f"  Output:        ./{Config.OUTPUT_FOLDER}/")
        logger.info(f"{'=' * 60}")


def validate_playlist_url(url: str) -> str:
    """
    Validates YouTube playlist URL format.

    Args:
        url: YouTube playlist URL to validate

    Returns:
        Validated URL

    Raises:
        ValueError: If URL format is invalid
    """
    pattern = r"(https?://)?(www\.)?(youtube\.com/playlist\?list=|youtu\.be/)[\w-]+"
    if not re.match(pattern, url):
        raise ValueError(f"Invalid playlist URL format: {url}")
    return url


def sanitize_filename(title: str) -> str:
    """
    Removes illegal characters from filenames.

    Args:
        title: Original video title

    Returns:
        Sanitized filename safe for all operating systems
    """
    # Remove illegal characters for Windows/macOS/Linux filesystems
    return re.sub(r'[\\/*?:"<>|]', "_", title)


def fetch_transcript_with_retry(
    yt_api: YouTubeTranscriptApi, video_id: str, max_retries: int = None
) -> Optional[list]:
    """
    Fetch transcript with exponential backoff retry logic.

    Args:
        yt_api: Configured YouTubeTranscriptApi instance
        video_id: YouTube video ID
        max_retries: Maximum number of retry attempts (defaults to Config.RETRY_ATTEMPTS)

    Returns:
        Transcript data or None if all attempts fail
    """
    if max_retries is None:
        max_retries = Config.RETRY_ATTEMPTS

    for attempt in range(max_retries):
        try:
            # Try English first (manual or auto-generated)
            return yt_api.fetch(video_id, languages=["en", "en-US"])
        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt - try generic fetch
                try:
                    return yt_api.fetch(video_id)
                except Exception:
                    logger.error(
                        f"  ✗ No transcript available after {max_retries} attempts"
                    )
                    return None

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2**attempt
            logger.warning(
                f"  Retry {attempt + 1}/{max_retries} after {wait_time}s: {str(e)[:50]}"
            )
            time.sleep(wait_time)

    return None


def initialize_api() -> Optional[YouTubeTranscriptApi]:
    """
    Initialize YouTube Transcript API with optional proxy configuration.

    Returns:
        Configured YouTubeTranscriptApi instance or None if initialization fails
    """
    # Check if proxy is requested
    if Config.USE_PROXY:
        if not Config.PROXY_USER or not Config.PROXY_PASS:
            logger.error("✗ Error: USE_PROXY is enabled but credentials not found.")
            logger.info("  Required: PROXY_USER and PROXY_PASS in .env file")
            logger.info("  Or set USE_PROXY=false to run without proxy")
            return None

        try:
            yt_api = YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
                    proxy_username=Config.PROXY_USER, proxy_password=Config.PROXY_PASS
                )
            )
            logger.info("✓ API initialized with proxy configuration")
            return yt_api
        except Exception as e:
            logger.error(f"✗ Error configuring proxy: {e}")
            return None
    else:
        # Initialize without proxy
        logger.info("✓ API initialized without proxy")
        logger.warning(
            "⚠️  Note: Without proxy, you may hit rate limits on large playlists"
        )
        return YouTubeTranscriptApi()


def fetch_playlist(url: str) -> Optional[Playlist]:
    """
    Fetch YouTube playlist and validate.

    Args:
        url: YouTube playlist URL

    Returns:
        Playlist object or None if fetch fails
    """
    try:
        validated_url = validate_playlist_url(url)
        logger.info(f"Fetching playlist from: {validated_url}")
        playlist = Playlist(validated_url)
        logger.info(f"✓ Found {len(playlist.videos)} videos in playlist")
        return playlist
    except ValueError as e:
        logger.error(f"✗ {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Error fetching playlist: {e}")
        return None


def process_video(
    yt_api: YouTubeTranscriptApi, video, index: int, total: int, output_folder: str
) -> bool:
    """
    Process a single video: fetch transcript, format, and save.

    Args:
        yt_api: Configured YouTube API instance
        video: Video object from playlist
        index: Current video number (1-indexed)
        total: Total number of videos
        output_folder: Directory to save transcripts

    Returns:
        True if successful, False otherwise
    """
    try:
        video_id = video.video_id
        title = sanitize_filename(video.title)
        filename = f"[{video_id}] - {title}.txt"
        output_path = os.path.join(output_folder, filename)

        # Check if already processed
        if os.path.exists(output_path):
            logger.info(f"[{index}/{total}] Skipping (exists): {title[:50]}...")
            return True

        logger.info(f"[{index}/{total}] Processing: {title[:50]}...")

        # Fetch transcript with retry logic
        transcript_data = fetch_transcript_with_retry(yt_api, video_id)

        if transcript_data is None:
            return False

        # Format and save transcript
        formatted_text = formatters.TextFormatter().format_transcript(transcript_data)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_text)

        logger.info("  ✓ Saved successfully")

        # Rate limiting - be polite to API
        time.sleep(Config.RATE_LIMIT_DELAY)
        return True

    except Exception as e:
        logger.error(f"[{index}/{total}] ✗ Error: {str(e)[:80]}")
        return False


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("YouTube Playlist Transcript Automation Tool")
    logger.info("=" * 60)

    # Ensure output directory exists
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
    logger.info(f"Output directory: ./{Config.OUTPUT_FOLDER}/")

    # Initialize API
    yt_api = initialize_api()
    if yt_api is None:
        return

    # Fetch playlist
    playlist = fetch_playlist(Config.PLAYLIST_URL)
    if playlist is None:
        return

    # Initialize statistics tracker
    stats = DownloadStats(total=len(playlist.videos))

    # Process each video
    logger.info("Starting transcript downloads...")
    logger.info("-" * 60)

    for i, video in enumerate(playlist.videos, 1):
        success = process_video(
            yt_api, video, i, len(playlist.videos), Config.OUTPUT_FOLDER
        )

        if success:
            # Check if file was newly created or skipped
            video_id = video.video_id
            title = sanitize_filename(video.title)
            filename = f"[{video_id}] - {title}.txt"
            output_path = os.path.join(Config.OUTPUT_FOLDER, filename)

            # If we just created it, it's a success; otherwise it was skipped earlier
            if os.path.exists(output_path):
                # Simple heuristic: if modified in last 5 seconds, we just created it
                mod_time = os.path.getmtime(output_path)
                if time.time() - mod_time < 5:
                    stats.success += 1
                else:
                    stats.skipped += 1
        else:
            stats.failed += 1

    # Print summary
    logger.info("-" * 60)
    stats.print_summary()
    logger.info("\nTranscript download process complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nProcess interrupted by user. Exiting gracefully...")
    except Exception as e:
        logger.error(f"\n\nUnexpected error: {e}", exc_info=True)
