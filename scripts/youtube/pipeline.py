# scripts/youtube/pipeline.py
"""Full pipeline: extract → enrich → extract competencies → save."""

from typing import Optional

from .competencies import extract_competencies, save_competencies_to_kb
from .enricher import enrich_transcript
from .extractor import extract_single_video, format_timestamp
from .models import EnrichedTranscript


def process_video(
    url: str,
    channel: str,
    title: Optional[str] = None,
    tags: Optional[list[str]] = None,
    enrich: bool = True,
    extract_comps: bool = True,
    save_to_kb: bool = True,
) -> EnrichedTranscript:
    """
    Full pipeline for a single video:
    1. Extract transcript
    2. Enrich with LLM (summary, key points, frameworks)
    3. Extract competencies
    4. Save to knowledge base
    5. Generate markdown file

    Args:
        url: YouTube URL or video ID
        channel: Channel slug
        title: Video title (optional)
        tags: List of tags
        enrich: Whether to enrich with LLM
        extract_comps: Whether to extract competencies
        save_to_kb: Whether to save competencies to knowledge base

    Returns:
        EnrichedTranscript with all extracted data
    """
    print("[1/4] Extracting transcript...")
    transcript = extract_single_video(url, channel, title, tags)

    if enrich:
        print("[2/4] Enriching with LLM...")
        enriched = enrich_transcript(transcript)
    else:
        enriched = EnrichedTranscript(
            transcript=transcript,
            summary="",
            key_points=[],
            frameworks=[],
            notable_quotes=[],
        )

    if extract_comps and enrich:
        print("[3/4] Extracting competencies...")
        competencies = extract_competencies(enriched)
        enriched.competencies = competencies

        if save_to_kb and competencies:
            print("[4/4] Saving to knowledge base...")
            save_competencies_to_kb(
                competencies,
                source_video=f"{channel}/{transcript.metadata.video_id}",
            )

    return enriched


def generate_enriched_markdown(enriched: EnrichedTranscript) -> str:
    """Generate markdown with all enriched content."""
    meta = enriched.transcript.metadata

    # Format key points
    key_points_md = "\n".join(f"1. **{p}**" for p in enriched.key_points)
    if not key_points_md:
        key_points_md = "[No key points extracted]"

    # Format frameworks
    frameworks_md = ""
    for f in enriched.frameworks:
        frameworks_md += f"\n### {f.get('name', 'Unknown Framework')}\n"
        if f.get("description"):
            frameworks_md += f"{f['description']}\n"
        if f.get("steps"):
            frameworks_md += "\n".join(f"- {s}" for s in f["steps"])
            frameworks_md += "\n"

    if not frameworks_md:
        frameworks_md = "\n[No frameworks identified]\n"

    # Format quotes
    quotes_md = ""
    for q in enriched.notable_quotes:
        quote_text = q.get("quote", "")
        timestamp = q.get("timestamp", "")
        if quote_text:
            quotes_md += f'> "{quote_text}"'
            if timestamp:
                quotes_md += f" - {timestamp}"
            quotes_md += "\n\n"

    if not quotes_md:
        quotes_md = "> [No notable quotes extracted]\n"

    # Format competencies
    comps_md = ""
    if enriched.competencies:
        comps_md = "\n## Competencies Extracted\n\n"
        for c in enriched.competencies:
            comps_md += f"- **{c.name}** ({c.category}): {c.description}\n"
        comps_md += "\n"

    # Calculate duration display
    duration = format_timestamp(meta.duration_seconds)
    date = meta.extraction_date.strftime("%Y-%m-%d")
    tags_str = ", ".join(meta.tags) if meta.tags else "ai, transcript"

    # Build template
    template = f"""# {meta.title}

> Source: {meta.url}
> Channel: {meta.channel}
> Extraction date: {date}
> Duration: {duration}
> Tags: {tags_str}

## Summary

{enriched.summary if enriched.summary else "[No summary generated]"}

## Key Points

{key_points_md}

## Frameworks/Models Mentioned
{frameworks_md}
## Notable Quotes

{quotes_md}
{comps_md}## Transcript

{enriched.transcript.formatted_text}

## Extraction Notes

- **Source:** {meta.url}
- **Competencies extracted:** {len(enriched.competencies)}
"""

    if enriched.competencies:
        avg_confidence = sum(c.confidence for c in enriched.competencies) / len(
            enriched.competencies
        )
        template += f"- **Average confidence:** {avg_confidence:.0%}\n"

    return template
