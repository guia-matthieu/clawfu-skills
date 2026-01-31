# scripts/youtube/batch.py
"""Batch extraction for YouTube playlists."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from .extractor import extract_single_video, save_transcript
from .models import ExtractedTranscript


@dataclass
class BatchConfig:
    """Configuration for batch extraction."""

    playlist_url: str
    channel_slug: str
    max_videos: int = 50
    skip_existing: bool = True
    output_dir: Optional[Path] = None


def extract_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube URL."""
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError(f"Could not extract playlist ID from: {url}")
    return match.group(1)


def get_playlist_video_ids(playlist_id: str, max_videos: int = 50) -> list[str]:
    """
    Get video IDs from a YouTube playlist.
    Uses YouTube's RSS feed (no API key needed).
    """
    # YouTube RSS feed for playlists
    rss_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"

    try:
        response = httpx.get(rss_url, timeout=30)
        response.raise_for_status()

        # Parse video IDs from RSS XML
        video_ids = re.findall(r"<yt:videoId>([^<]+)</yt:videoId>", response.text)
        return video_ids[:max_videos]
    except httpx.HTTPStatusError as e:
        print(f"Error fetching playlist (HTTP {e.response.status_code}): {e}")
        return []
    except httpx.RequestError as e:
        print(f"Error fetching playlist: {e}")
        return []


def batch_extract(
    config: BatchConfig,
    enrich: bool = False,
) -> list[ExtractedTranscript]:
    """
    Extract transcripts from all videos in a playlist.

    Args:
        config: BatchConfig with playlist URL and settings
        enrich: Whether to enrich transcripts with LLM (requires Task 3)

    Returns:
        List of ExtractedTranscript objects
    """
    playlist_id = extract_playlist_id(config.playlist_url)
    video_ids = get_playlist_video_ids(playlist_id, config.max_videos)

    if not video_ids:
        print("No videos found in playlist")
        return []

    print(f"Found {len(video_ids)} videos in playlist")

    results = []
    for i, video_id in enumerate(video_ids, 1):
        print(f"[{i}/{len(video_ids)}] Processing {video_id}...")

        try:
            transcript = extract_single_video(
                url_or_id=video_id,
                channel_slug=config.channel_slug,
            )
            results.append(transcript)

            # Save transcript
            output_path = save_transcript(transcript, config.output_dir)
            print(f"  Extracted: {transcript.metadata.title[:50]}...")
            print(f"  Saved to: {output_path}")

        except ValueError as e:
            print(f"  Failed: {e}")
        except Exception as e:
            print(f"  Failed (unexpected): {e}")

    return results


def get_existing_video_ids(channel_slug: str, sources_dir: Optional[Path] = None) -> set[str]:
    """Get set of video IDs already extracted for a channel."""
    if sources_dir is None:
        sources_dir = Path(__file__).parent.parent.parent / "sources" / "youtube"

    channel_dir = sources_dir / "channels" / channel_slug
    if not channel_dir.exists():
        return set()

    existing = set()
    for md_file in channel_dir.glob("*.md"):
        if md_file.name.startswith("_"):
            continue
        # Try to extract video ID from file content
        content = md_file.read_text()
        match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", content)
        if match:
            existing.add(match.group(1))

    return existing
