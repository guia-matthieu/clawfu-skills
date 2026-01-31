# scripts/tests/youtube/test_batch.py
"""Tests for batch extraction functionality."""

from youtube.batch import extract_playlist_id, BatchConfig


def test_extract_playlist_id_from_full_url():
    """Test extracting playlist ID from full YouTube URL."""
    url = "https://www.youtube.com/playlist?list=PLtest123ABC"
    playlist_id = extract_playlist_id(url)
    assert playlist_id == "PLtest123ABC"


def test_extract_playlist_id_with_video():
    """Test extracting playlist ID from URL with video."""
    url = "https://www.youtube.com/watch?v=abc123&list=PLplaylist456"
    playlist_id = extract_playlist_id(url)
    assert playlist_id == "PLplaylist456"


def test_batch_config_defaults():
    """Test BatchConfig with default values."""
    config = BatchConfig(
        playlist_url="https://youtube.com/playlist?list=PLtest",
        channel_slug="ai-engineer",
    )
    assert config.max_videos == 50
    assert config.skip_existing is True
    assert config.output_dir is None


def test_batch_config_custom_values():
    """Test BatchConfig with custom values."""
    config = BatchConfig(
        playlist_url="https://youtube.com/playlist?list=PLtest",
        channel_slug="hormozi",
        max_videos=10,
        skip_existing=False,
    )
    assert config.max_videos == 10
    assert config.skip_existing is False
