# scripts/youtube/enricher.py
"""LLM-based transcript enrichment via OpenRouter."""

import json
import os
from typing import Optional

import httpx

from .models import EnrichedTranscript, ExtractedTranscript

# Environment variable name for OpenRouter credentials
OPENROUTER_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class EnrichmentPrompts:
    """Prompts for transcript enrichment."""

    SUMMARY = """Analyse ce transcript de vidéo YouTube et génère:

1. **Résumé** (3-5 phrases): L'essentiel du contenu
2. **Points Clés** (5-10 bullet points): Les insights principaux
3. **Frameworks/Modèles**: Toute méthodologie, framework ou modèle mental mentionné
4. **Citations Notables**: 3-5 citations marquantes avec leur timestamp approximatif

Transcript:
{transcript}

Réponds en JSON avec cette structure:
{{
  "summary": "...",
  "key_points": ["point 1", "point 2", ...],
  "frameworks": [
    {{"name": "...", "description": "...", "steps": ["..."]}}
  ],
  "notable_quotes": [
    {{"quote": "...", "timestamp": "MM:SS", "context": "..."}}
  ]
}}
"""


def parse_enrichment_response(raw: str) -> dict:
    """
    Parse LLM response into structured data.

    Handles:
    - Pure JSON
    - JSON wrapped in markdown code blocks
    - Fallback for invalid JSON
    """
    content = raw.strip()

    # Try to extract JSON from markdown code block
    if "```json" in content:
        try:
            content = content.split("```json")[1].split("```")[0].strip()
        except IndexError:
            pass
    elif "```" in content:
        try:
            content = content.split("```")[1].split("```")[0].strip()
        except IndexError:
            pass

    # Try to parse as JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: return basic structure with raw content
        return {
            "summary": content[:500] if len(content) > 500 else content,
            "key_points": [],
            "frameworks": [],
            "notable_quotes": [],
        }


def enrich_transcript(
    transcript: ExtractedTranscript,
    model: str = "google/gemini-flash-1.5",
    api_key: Optional[str] = None,
) -> EnrichedTranscript:
    """
    Enrich a transcript with LLM-generated summary and insights.

    Args:
        transcript: ExtractedTranscript to enrich
        model: OpenRouter model ID (default: Gemini Flash for cost efficiency)
        api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)

    Returns:
        EnrichedTranscript with summary, key points, frameworks, quotes

    Raises:
        ValueError: If API key not configured
        httpx.HTTPStatusError: If API request fails
    """
    api_key = api_key or os.getenv(OPENROUTER_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"{OPENROUTER_KEY_ENV} not configured. "
            "Set the environment variable or pass api_key parameter."
        )

    # Truncate transcript if too long (keep first ~8000 words)
    raw_text = transcript.raw_text
    words = raw_text.split()
    if len(words) > 8000:
        raw_text = " ".join(words[:8000]) + "\n\n[... transcript truncated ...]"

    prompt = EnrichmentPrompts.SUMMARY.format(transcript=raw_text)

    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=120,
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    # Parse response
    data = parse_enrichment_response(content)

    return EnrichedTranscript(
        transcript=transcript,
        summary=data.get("summary", ""),
        key_points=data.get("key_points", []),
        frameworks=data.get("frameworks", []),
        notable_quotes=data.get("notable_quotes", []),
        competencies=[],  # Filled by competencies.py in Task 4
    )


def enrich_transcript_offline(
    transcript: ExtractedTranscript,
    summary: str = "",
    key_points: Optional[list[str]] = None,
    frameworks: Optional[list[dict]] = None,
    notable_quotes: Optional[list[dict]] = None,
) -> EnrichedTranscript:
    """
    Create an EnrichedTranscript without LLM call.
    Useful for testing or manual enrichment.
    """
    return EnrichedTranscript(
        transcript=transcript,
        summary=summary,
        key_points=key_points or [],
        frameworks=frameworks or [],
        notable_quotes=notable_quotes or [],
        competencies=[],
    )
