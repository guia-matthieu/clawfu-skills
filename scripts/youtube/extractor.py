# scripts/youtube/extractor.py
"""Core extraction logic for YouTube transcripts."""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )
except ImportError:
    print("Installing youtube-transcript-api...")
    import subprocess

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "youtube-transcript-api"]
    )
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )

from .models import ExtractedTranscript, TranscriptEntry, VideoMetadata

# Base path for sources
SOURCES_DIR = Path(__file__).parent.parent.parent / "sources" / "youtube"


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return as-is if already an ID."""
    if len(url_or_id) == 11 and not url_or_id.startswith("http"):
        return url_or_id

    parsed = urlparse(url_or_id)

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/v/"):
            return parsed.path.split("/")[2]
    elif parsed.hostname == "youtu.be":
        return parsed.path[1:]

    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def get_transcript_entries(video_id: str) -> list[TranscriptEntry]:
    """Fetch transcript entries from YouTube."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=["en", "en-US", "en-GB", "fr"])

        return [
            TranscriptEntry(
                text=entry.text, start=entry.start, duration=entry.duration
            )
            for entry in transcript
        ]

    except TranscriptsDisabled:
        raise ValueError(f"Transcripts are disabled for video {video_id}")
    except VideoUnavailable:
        raise ValueError(f"Video {video_id} is unavailable")
    except NoTranscriptFound:
        raise ValueError(f"No transcript found for video {video_id}")
    except Exception as e:
        raise ValueError(f"Error fetching transcript: {e}")


def format_transcript_text(entries: list[TranscriptEntry]) -> str:
    """Format transcript entries into readable text with timestamps."""
    lines = []
    current_paragraph = []
    last_time = 0.0

    for entry in entries:
        text = entry.text.strip()
        start = entry.start

        # Skip music/sound indicators
        if text.startswith("[") and text.endswith("]"):
            if current_paragraph:
                timestamp = format_timestamp(last_time)
                lines.append(f"{timestamp}\n{' '.join(current_paragraph)}")
                current_paragraph = []
            lines.append(f"{format_timestamp(start)}\n{text}")
            continue

        # Start new paragraph every ~30 seconds or on sentence end
        if start - last_time > 30 or (
            current_paragraph
            and text[0].isupper()
            and current_paragraph[-1].endswith(".")
        ):
            if current_paragraph:
                timestamp = format_timestamp(last_time)
                lines.append(f"{timestamp}\n{' '.join(current_paragraph)}")
                current_paragraph = []
                last_time = start

        if not current_paragraph:
            last_time = start

        current_paragraph.append(text)

    # Add remaining text
    if current_paragraph:
        timestamp = format_timestamp(last_time)
        lines.append(f"{timestamp}\n{' '.join(current_paragraph)}")

    return "\n\n".join(lines)


def get_raw_text(entries: list[TranscriptEntry]) -> str:
    """Get plain text without timestamps."""
    return " ".join(entry.text.strip() for entry in entries)


def calculate_duration_seconds(entries: list[TranscriptEntry]) -> float:
    """Calculate video duration from transcript entries."""
    if not entries:
        return 0.0
    last_entry = entries[-1]
    return last_entry.start + last_entry.duration


def extract_single_video(
    url_or_id: str,
    channel_slug: str,
    title: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> ExtractedTranscript:
    """
    Extract transcript from a single YouTube video.

    Args:
        url_or_id: YouTube URL or video ID
        channel_slug: Channel identifier (e.g., 'ai-engineer')
        title: Video title (optional, uses video ID if not provided)
        tags: List of tags for the video

    Returns:
        ExtractedTranscript with metadata and formatted transcript
    """
    video_id = extract_video_id(url_or_id)

    # Fetch transcript
    entries = get_transcript_entries(video_id)

    # Calculate duration
    duration_seconds = calculate_duration_seconds(entries)

    # Create metadata
    metadata = VideoMetadata(
        video_id=video_id,
        title=title or f"Video {video_id}",
        channel=channel_slug,
        channel_slug=channel_slug,
        duration_seconds=duration_seconds,
        tags=tags or [],
        url=f"https://www.youtube.com/watch?v={video_id}",
        extraction_date=datetime.now(),
    )

    # Format transcript
    formatted_text = format_transcript_text(entries)
    raw_text = get_raw_text(entries)

    return ExtractedTranscript(
        metadata=metadata,
        entries=entries,
        raw_text=raw_text,
        formatted_text=formatted_text,
    )


def save_transcript(
    transcript: ExtractedTranscript,
    output_dir: Optional[Path] = None,
) -> Path:
    """Save extracted transcript to markdown file."""
    meta = transcript.metadata

    if output_dir is None:
        output_dir = SOURCES_DIR / "channels" / meta.channel_slug

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create channel index if doesn't exist
    index_file = output_dir / "_index.md"
    if not index_file.exists():
        index_content = f"""# {meta.channel_slug} - YouTube Transcripts

> Channel: {meta.channel}
> Focus: [To complete]

## Transcribed Videos

| Date | Title | Tags | Related Skill |
|------|-------|------|---------------|

## Notes

[To complete]
"""
        index_file.write_text(index_content)

    # Generate markdown content
    content = generate_transcript_markdown(transcript)

    # Save transcript
    video_slug = slugify(meta.title) if meta.title != f"Video {meta.video_id}" else meta.video_id
    output_file = output_dir / f"{video_slug}.md"
    output_file.write_text(content)

    return output_file


def generate_transcript_markdown(transcript: ExtractedTranscript) -> str:
    """Generate markdown content from extracted transcript."""
    meta = transcript.metadata
    duration = format_timestamp(meta.duration_seconds)
    date = meta.extraction_date.strftime("%Y-%m-%d")
    tags_str = ", ".join(meta.tags) if meta.tags else "ai, transcript"

    return f"""# {meta.title}

> Source: {meta.url}
> Channel: {meta.channel}
> Extraction date: {date}
> Duration: {duration}
> Tags: {tags_str}

## Summary

[To complete - 3-5 sentences summarizing the content]

## Key Points

1. **[Point 1]** - [Explanation]
2. **[Point 2]** - [Explanation]
3. **[Point 3]** - [Explanation]

## Frameworks/Models Mentioned

### [Framework Name]
- Description
- Application

## Notable Quotes

> "[Quote]" - [Timestamp]

## Transcript

{transcript.formatted_text}

## Extraction Notes

- **Potential skills:** [to identify]
- **Related sources:** [links]
- **To explore:** [questions]
"""
