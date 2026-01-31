# scripts/tests/youtube/test_extractor.py
"""Tests for YouTube extractor models."""

from youtube.models import VideoMetadata, TranscriptEntry, ExtractedCompetency


def test_video_metadata_creation():
    """Test VideoMetadata can be created with valid data."""
    metadata = VideoMetadata(
        video_id="CEvIs9y1uog",
        title="Test Video",
        channel="AI Engineer",
        channel_slug="ai-engineer",
        duration_seconds=978.5,
        tags=["ai", "skills"],
        url="https://www.youtube.com/watch?v=CEvIs9y1uog",
    )
    assert metadata.video_id == "CEvIs9y1uog"
    assert metadata.channel_slug == "ai-engineer"
    assert metadata.duration_seconds == 978.5


def test_transcript_entry():
    """Test TranscriptEntry model."""
    entry = TranscriptEntry(text="Hello world", start=0.0, duration=2.5)
    assert entry.text == "Hello world"
    assert entry.start == 0.0
    assert entry.duration == 2.5


def test_extracted_competency():
    """Test ExtractedCompetency model with defaults."""
    competency = ExtractedCompetency(
        name="Value Equation Calculation",
        category="strategy",
        description="Calculate perceived value using Alex Hormozi's formula",
    )
    assert competency.name == "Value Equation Calculation"
    assert competency.category == "strategy"
    assert competency.actionable is True
    assert competency.confidence == 0.8
    assert competency.related_skills == []


def test_video_metadata_tags_default():
    """Test VideoMetadata defaults to empty tags list."""
    metadata = VideoMetadata(
        video_id="test123",
        title="Test",
        channel="Test Channel",
        channel_slug="test-channel",
        duration_seconds=100.0,
        url="https://www.youtube.com/watch?v=test123",
    )
    assert metadata.tags == []
