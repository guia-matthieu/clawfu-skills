# scripts/youtube/models.py
"""Pydantic models for YouTube transcript pipeline."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class TranscriptEntry(BaseModel):
    """Single transcript entry with timing."""

    text: str
    start: float
    duration: float


class VideoMetadata(BaseModel):
    """Metadata for an extracted video."""

    video_id: str
    title: str
    channel: str
    channel_slug: str
    duration_seconds: float
    tags: list[str] = []
    url: HttpUrl
    extraction_date: datetime = datetime.now()


class ExtractedTranscript(BaseModel):
    """Complete extracted transcript with metadata."""

    metadata: VideoMetadata
    entries: list[TranscriptEntry]
    raw_text: str
    formatted_text: str


class ExtractedCompetency(BaseModel):
    """A marketing competency extracted from content."""

    name: str
    category: str  # strategy, content, sales, etc.
    description: str
    source_timestamp: Optional[str] = None
    related_skills: list[str] = []
    actionable: bool = True
    confidence: float = 0.8


class EnrichedTranscript(BaseModel):
    """Transcript enriched with LLM-generated insights."""

    transcript: ExtractedTranscript
    summary: str
    key_points: list[str]
    frameworks: list[dict]
    notable_quotes: list[dict]
    competencies: list[ExtractedCompetency] = []
