#!/usr/bin/env python3
"""
YouTube Pipeline CLI for MKTG_Skills

Commands:
    extract     Extract single video transcript
    batch       Extract from playlist
    queue-add   Add video to processing queue
    queue-list  Show queue status
    queue-process   Process pending videos from queue
    process     Full pipeline (extract + enrich + competencies)
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import typer
except ImportError:
    print("Installing typer...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "typer"])
    import typer

app = typer.Typer(
    help="YouTube transcript pipeline for MKTG_Skills",
    add_completion=False,
)


@app.command()
def extract(
    url: str,
    channel: str = typer.Option("unknown", "--channel", "-c", help="Channel slug"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    print_only: bool = typer.Option(False, "--print-only", "-p", help="Print to stdout"),
):
    """Extract transcript from a single video."""
    from youtube.extractor import extract_single_video, save_transcript, generate_transcript_markdown

    tag_list = tags.split(",") if tags else []
    transcript = extract_single_video(url, channel, title, tag_list)

    if print_only:
        content = generate_transcript_markdown(transcript)
        print("\n" + "=" * 60 + "\n")
        print(content)
    elif output:
        content = generate_transcript_markdown(transcript)
        output.write_text(content)
        print(f"Saved to: {output}")
    else:
        output_path = save_transcript(transcript)
        print(f"\nSaved to: {output_path}")
        print("\nNext steps:")
        print("  1. Review and add video title")
        print("  2. Write summary (3-5 sentences)")
        print("  3. Extract key points")


@app.command()
def batch(
    playlist_url: str,
    channel: str = typer.Option(..., "--channel", "-c", help="Channel slug"),
    max_videos: int = typer.Option(10, "--max", "-m", help="Max videos to extract"),
    enrich: bool = typer.Option(False, "--enrich/--no-enrich", help="Enrich with LLM"),
):
    """Extract transcripts from a YouTube playlist."""
    from youtube.batch import batch_extract, BatchConfig

    config = BatchConfig(
        playlist_url=playlist_url,
        channel_slug=channel,
        max_videos=max_videos,
    )

    results = batch_extract(config, enrich=enrich)
    print(f"\nExtracted {len(results)} videos")


@app.command("queue-add")
def queue_add(
    url: str,
    channel: str = typer.Option(..., "--channel", "-c", help="Channel slug"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priority: high, medium, low"),
):
    """Add a video to the processing queue."""
    from youtube.queue import add_to_queue, QueueItem

    item = QueueItem(
        video_url=url,
        channel=channel,
        title=title,
        priority=priority,
    )
    add_to_queue(item)
    print(f"Added to queue: {url}")
    print(f"  Channel: {channel}")
    print(f"  Priority: {priority}")


@app.command("queue-list")
def queue_list():
    """Show current queue status."""
    from youtube.queue import parse_queue, get_queue_stats

    stats = get_queue_stats()
    items = parse_queue()

    print("\nQueue Status:")
    print(f"  Total: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Processing: {stats['processing']}")
    print(f"  Done: {stats['done']}")
    print(f"  Failed: {stats['failed']}")

    pending = [i for i in items if i.status == "pending"]
    if pending:
        print(f"\nPending Videos ({len(pending)}):")
        for item in pending[:10]:
            title_display = item.title[:40] if item.title else item.video_url[-20:]
            print(f"  [{item.priority}] {item.channel}: {title_display}")
        if len(pending) > 10:
            print(f"  ... and {len(pending) - 10} more")


@app.command("queue-process")
def queue_process(
    max_videos: int = typer.Option(5, "--max", "-m", help="Max videos to process"),
    enrich: bool = typer.Option(True, "--enrich/--no-enrich", help="Enrich with LLM"),
    competencies: bool = typer.Option(True, "--competencies/--no-competencies", help="Extract competencies"),
):
    """Process pending videos from queue."""
    from youtube.queue import get_next_pending, mark_done, mark_failed
    from youtube.extractor import extract_single_video, save_transcript
    from youtube.enricher import enrich_transcript
    from youtube.competencies import extract_competencies, save_competencies_to_kb

    processed = 0
    while processed < max_videos:
        item = get_next_pending()
        if not item:
            print("No more pending videos in queue")
            break

        print(f"\n[{processed + 1}/{max_videos}] Processing: {item.video_url}")
        print(f"  Channel: {item.channel}")

        try:
            # Extract transcript
            print("  [1/4] Extracting transcript...")
            transcript = extract_single_video(
                url_or_id=item.video_url,
                channel_slug=item.channel,
                title=item.title,
            )

            # Save transcript
            output_path = save_transcript(transcript)
            print(f"  Saved: {output_path}")

            # Enrich if requested
            if enrich:
                print("  [2/4] Enriching with LLM...")
                enriched = enrich_transcript(transcript)
                print(f"    Summary: {len(enriched.summary)} chars")
                print(f"    Key points: {len(enriched.key_points)}")

                # Extract competencies if requested
                if competencies:
                    print("  [3/4] Extracting competencies...")
                    comps = extract_competencies(enriched)
                    print(f"    Found: {len(comps)} competencies")

                    if comps:
                        print("  [4/4] Saving to knowledge base...")
                        save_competencies_to_kb(
                            comps,
                            source_video=f"{item.channel}/{transcript.metadata.video_id}",
                        )

            mark_done(item.video_url)
            processed += 1
            print("  Done!")

        except Exception as e:
            print(f"  Failed: {e}")
            mark_failed(item.video_url)

    print(f"\nProcessed {processed} videos")


@app.command()
def process(
    url: str,
    channel: str = typer.Option(..., "--channel", "-c", help="Channel slug"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Video title"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
    no_enrich: bool = typer.Option(False, "--no-enrich", help="Skip LLM enrichment"),
    no_competencies: bool = typer.Option(False, "--no-competencies", help="Skip competency extraction"),
):
    """Full pipeline: extract, enrich, extract competencies."""
    from youtube.extractor import extract_single_video, save_transcript
    from youtube.enricher import enrich_transcript
    from youtube.competencies import extract_competencies, save_competencies_to_kb

    tag_list = tags.split(",") if tags else []

    print("[1/4] Extracting transcript...")
    transcript = extract_single_video(url, channel, title, tag_list)
    print(f"  Got {len(transcript.entries)} entries ({int(transcript.metadata.duration_seconds)}s)")

    enriched = None
    if not no_enrich:
        print("[2/4] Enriching with LLM...")
        enriched = enrich_transcript(transcript)
        print(f"  Summary: {len(enriched.summary)} chars")
        print(f"  Key points: {len(enriched.key_points)}")
        print(f"  Frameworks: {len(enriched.frameworks)}")

        if not no_competencies:
            print("[3/4] Extracting competencies...")
            comps = extract_competencies(enriched)
            enriched.competencies = comps
            print(f"  Found: {len(comps)} competencies")

            if comps:
                print("[4/4] Saving to knowledge base...")
                save_competencies_to_kb(
                    comps,
                    source_video=f"{channel}/{transcript.metadata.video_id}",
                )

    # Save transcript (basic markdown - enriched content printed to console)
    output_path = save_transcript(transcript)

    print(f"\nProcessed: {transcript.metadata.title}")
    print(f"  Saved to: {output_path}")
    if enriched:
        print(f"  Summary: {len(enriched.summary)} chars")
        print(f"  Key points: {len(enriched.key_points)}")
        print(f"  Competencies: {len(enriched.competencies)}")


if __name__ == "__main__":
    app()
