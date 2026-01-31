# scripts/youtube/queue.py
"""Queue management for YouTube video processing."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

QUEUE_FILE = Path(__file__).parent.parent.parent / "sources" / "youtube" / "queue.md"


@dataclass
class QueueItem:
    """A video item in the processing queue."""

    video_url: str
    channel: str
    title: Optional[str] = None
    priority: str = "medium"  # high, medium, low
    status: str = "pending"  # pending, processing, done, failed
    added_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    notes: str = ""


def parse_queue() -> list[QueueItem]:
    """
    Parse queue.md and return list of items.

    Expected format:
    | Channel | URL | Title | Priority | Status | Notes |
    |---------|-----|-------|----------|--------|-------|
    | ai-engineer | https://youtube.com/watch?v=xxx | Video Title | medium | pending | |
    """
    if not QUEUE_FILE.exists():
        return []

    content = QUEUE_FILE.read_text()
    items = []

    # Skip header rows and parse table
    in_table = False
    for line in content.split("\n"):
        line = line.strip()

        # Detect table start
        if line.startswith("| Channel") or line.startswith("| ---"):
            in_table = True
            continue

        if not in_table or not line.startswith("|"):
            continue

        # Skip separator line
        if "---" in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        # Remove empty first/last elements from split
        parts = [p for p in parts if p]

        if len(parts) >= 4 and ("youtube.com" in parts[1].lower() or "youtu.be" in parts[1].lower()):
            items.append(
                QueueItem(
                    channel=parts[0],
                    video_url=parts[1],
                    title=parts[2] if len(parts) > 2 and parts[2] else None,
                    priority=parts[3] if len(parts) > 3 and parts[3] else "medium",
                    status=parts[4] if len(parts) > 4 and parts[4] else "pending",
                    notes=parts[5] if len(parts) > 5 else "",
                )
            )

    return items


def add_to_queue(item: QueueItem) -> None:
    """Add a video to the queue."""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Create queue file if doesn't exist
    if not QUEUE_FILE.exists():
        header = """# YouTube Video Queue

Videos waiting to be processed by the transcript pipeline.

## Queue

| Channel | URL | Title | Priority | Status | Notes |
|---------|-----|-------|----------|--------|-------|
"""
        QUEUE_FILE.write_text(header)

    # Append new item
    content = QUEUE_FILE.read_text()
    new_row = f"| {item.channel} | {item.video_url} | {item.title or ''} | {item.priority} | {item.status} | {item.notes} |\n"
    QUEUE_FILE.write_text(content + new_row)


def get_next_pending() -> Optional[QueueItem]:
    """Get next pending item from queue, prioritizing high > medium > low."""
    items = parse_queue()
    pending = [i for i in items if i.status == "pending"]

    if not pending:
        return None

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(key=lambda x: priority_order.get(x.priority, 1))

    return pending[0]


def update_queue_status(video_url: str, new_status: str) -> bool:
    """
    Update the status of a video in the queue.

    Args:
        video_url: URL or video ID to match
        new_status: New status (pending, processing, done, failed)

    Returns:
        True if item was found and updated
    """
    if not QUEUE_FILE.exists():
        return False

    content = QUEUE_FILE.read_text()
    lines = content.split("\n")
    updated = False

    # Extract video ID for flexible matching
    video_id = None
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", video_url)
    if match:
        video_id = match.group(1)

    new_lines = []
    for line in lines:
        if video_url in line or (video_id and video_id in line):
            # Parse and update the line
            parts = line.split("|")
            if len(parts) >= 6:
                parts[5] = f" {new_status} "
                line = "|".join(parts)
                updated = True
        new_lines.append(line)

    if updated:
        QUEUE_FILE.write_text("\n".join(new_lines))

    return updated


def mark_done(video_url: str) -> bool:
    """Mark a video as processed."""
    return update_queue_status(video_url, "done")


def mark_failed(video_url: str) -> bool:
    """Mark a video as failed."""
    return update_queue_status(video_url, "failed")


def get_queue_stats() -> dict:
    """Get statistics about the queue."""
    items = parse_queue()
    return {
        "total": len(items),
        "pending": len([i for i in items if i.status == "pending"]),
        "processing": len([i for i in items if i.status == "processing"]),
        "done": len([i for i in items if i.status == "done"]),
        "failed": len([i for i in items if i.status == "failed"]),
    }
