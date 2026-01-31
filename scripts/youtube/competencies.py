# scripts/youtube/competencies.py
"""Extract structured competencies from enriched transcripts."""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import httpx

from .models import EnrichedTranscript, ExtractedCompetency

# Environment variable name for OpenRouter credentials
OPENROUTER_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class CompetencyCategory(str, Enum):
    """Categories for marketing competencies."""

    STRATEGY = "strategy"
    CONTENT = "content"
    ACQUISITION = "acquisition"
    ANALYTICS = "analytics"
    BRANDING = "branding"
    SALES = "sales"
    FUNNELS = "funnels"
    GROWTH = "growth"


COMPETENCY_PROMPT = """Analyse ce contenu et extrait les COMPÉTENCES MARKETING concrètes enseignées.

Une compétence est une capacité actionnable qu'un marketeur peut apprendre et appliquer.

Exemples de bonnes compétences:
- "Écrire des headlines selon la méthode 4U" (category: content)
- "Calculer la Value Equation d'une offre" (category: strategy)
- "Structurer un pitch de vente en 8 étapes" (category: sales)

Contenu à analyser:

Résumé: {summary}

Points clés:
{key_points}

Frameworks mentionnés:
{frameworks}

Réponds en JSON avec cette structure:
{{
  "competencies": [
    {{
      "name": "Nom court de la compétence",
      "category": "strategy|content|acquisition|analytics|branding|sales|funnels|growth",
      "description": "Description en 1-2 phrases de ce que permet cette compétence",
      "related_skills": ["skill-existant-1", "skill-existant-2"],
      "actionable": true,
      "confidence": 0.9
    }}
  ]
}}

Ne retourne QUE des compétences marketing actionnables. Ignore les concepts trop généraux.
"""

# Reference to existing skills for matching
EXISTING_SKILLS = [
    "positioning-dunford",
    "sales-pitch-dunford",
    "grand-slam-offers",
    "breakthrough-advertising",
    "ogilvy-copywriting",
    "boron-letters",
    "copy-frameworks",
    "headline-formulas",
    "storybrand-framework",
    "cialdini-persuasion",
    "jobs-to-be-done",
    "buyer-personas",
    "competitive-analysis",
    "pricing-strategy",
    "email-writing",
    "landing-page-copy",
    "cta-writing",
    "category-design",
]


def parse_competencies_response(raw: str) -> list[dict]:
    """
    Parse LLM response into list of competency dicts.

    Args:
        raw: Raw LLM response text

    Returns:
        List of competency dictionaries
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
        data = json.loads(content)
        return data.get("competencies", [])
    except json.JSONDecodeError:
        return []


def extract_competencies(
    enriched: EnrichedTranscript,
    model: str = "google/gemini-flash-1.5",
    api_key: Optional[str] = None,
) -> list[ExtractedCompetency]:
    """
    Extract structured competencies from enriched transcript.

    Args:
        enriched: EnrichedTranscript with summary, key points, frameworks
        model: OpenRouter model ID
        api_key: OpenRouter API key (defaults to env var)

    Returns:
        List of ExtractedCompetency objects
    """
    api_key = api_key or os.getenv(OPENROUTER_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"{OPENROUTER_KEY_ENV} not configured. "
            "Set the environment variable or pass api_key parameter."
        )

    # Format inputs
    key_points_str = "\n".join(f"- {p}" for p in enriched.key_points)
    frameworks_str = "\n".join(
        f"- {f['name']}: {f.get('description', '')}" for f in enriched.frameworks
    )

    prompt = COMPETENCY_PROMPT.format(
        summary=enriched.summary,
        key_points=key_points_str or "[None extracted]",
        frameworks=frameworks_str or "[None identified]",
    )

    response = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    # Parse response
    competency_dicts = parse_competencies_response(content)

    # Convert to ExtractedCompetency objects
    competencies = []
    for c in competency_dicts:
        try:
            competencies.append(
                ExtractedCompetency(
                    name=c["name"],
                    category=c["category"],
                    description=c["description"],
                    related_skills=c.get("related_skills", []),
                    actionable=c.get("actionable", True),
                    confidence=c.get("confidence", 0.8),
                )
            )
        except (KeyError, ValueError):
            # Skip malformed entries
            continue

    return competencies


def save_competencies_to_kb(
    competencies: list[ExtractedCompetency],
    source_video: str,
    kb_path: Optional[Path] = None,
) -> None:
    """
    Save extracted competencies to the knowledge base.

    Args:
        competencies: List of ExtractedCompetency objects
        source_video: Source identifier (e.g., "channel/video-id")
        kb_path: Path to knowledge base JSON file
    """
    if kb_path is None:
        kb_path = (
            Path(__file__).parent.parent.parent
            / "sources"
            / "competencies"
            / "extracted.json"
        )

    kb_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing KB
    if kb_path.exists():
        with open(kb_path) as f:
            kb = json.load(f)
    else:
        kb = {"competencies": [], "sources": []}

    # Add new competencies
    existing_names = {e["name"].lower() for e in kb["competencies"]}

    for c in competencies:
        # Check for duplicates by name
        if c.name.lower() in existing_names:
            continue

        entry = {
            **c.model_dump(),
            "source": source_video,
            "extraction_date": datetime.now().isoformat(),
        }
        kb["competencies"].append(entry)
        existing_names.add(c.name.lower())

    # Track source
    if source_video not in kb["sources"]:
        kb["sources"].append(source_video)

    # Save
    with open(kb_path, "w") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    print(f"Knowledge base updated: {len(kb['competencies'])} total competencies")


def load_competencies_from_kb(
    kb_path: Optional[Path] = None,
) -> list[dict]:
    """Load competencies from the knowledge base."""
    if kb_path is None:
        kb_path = (
            Path(__file__).parent.parent.parent
            / "sources"
            / "competencies"
            / "extracted.json"
        )

    if not kb_path.exists():
        return []

    with open(kb_path) as f:
        kb = json.load(f)

    return kb.get("competencies", [])
