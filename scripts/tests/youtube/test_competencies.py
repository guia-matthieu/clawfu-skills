# scripts/tests/youtube/test_competencies.py
"""Tests for competency extraction functionality."""

from youtube.competencies import (
    CompetencyCategory,
    parse_competencies_response,
    COMPETENCY_PROMPT,
)


def test_competency_categories_exist():
    """Test that all expected competency categories are defined."""
    assert CompetencyCategory.STRATEGY is not None
    assert CompetencyCategory.CONTENT is not None
    assert CompetencyCategory.SALES is not None
    assert CompetencyCategory.ACQUISITION is not None
    assert CompetencyCategory.ANALYTICS is not None
    assert CompetencyCategory.BRANDING is not None
    assert CompetencyCategory.FUNNELS is not None
    assert CompetencyCategory.GROWTH is not None


def test_competency_category_values():
    """Test competency category string values."""
    assert CompetencyCategory.STRATEGY.value == "strategy"
    assert CompetencyCategory.CONTENT.value == "content"
    assert CompetencyCategory.SALES.value == "sales"


def test_competency_prompt_exists():
    """Test that competency extraction prompt is defined."""
    assert COMPETENCY_PROMPT is not None
    assert "compétence" in COMPETENCY_PROMPT.lower() or "competenc" in COMPETENCY_PROMPT.lower()
    assert "{summary}" in COMPETENCY_PROMPT
    assert "{key_points}" in COMPETENCY_PROMPT


def test_parse_competencies_response_json():
    """Test parsing a well-formed JSON response."""
    raw = """{
        "competencies": [
            {
                "name": "Value Equation Calculation",
                "category": "strategy",
                "description": "Calculate perceived value using Hormozi's formula",
                "related_skills": ["grand-slam-offers"],
                "actionable": true,
                "confidence": 0.9
            },
            {
                "name": "Headline Writing with 4U",
                "category": "content",
                "description": "Write headlines using Useful, Urgent, Unique, Ultra-specific",
                "related_skills": ["headline-formulas", "copywriting-ogilvy"],
                "actionable": true,
                "confidence": 0.85
            }
        ]
    }"""
    result = parse_competencies_response(raw)
    assert len(result) == 2
    assert result[0]["name"] == "Value Equation Calculation"
    assert result[0]["category"] == "strategy"
    assert result[1]["category"] == "content"


def test_parse_competencies_response_markdown_wrapped():
    """Test parsing JSON wrapped in markdown."""
    raw = """Here are the competencies:

```json
{
    "competencies": [
        {
            "name": "Sales Pitch Structure",
            "category": "sales",
            "description": "Structure sales presentations effectively",
            "actionable": true,
            "confidence": 0.8
        }
    ]
}
```
"""
    result = parse_competencies_response(raw)
    assert len(result) == 1
    assert result[0]["name"] == "Sales Pitch Structure"


def test_parse_competencies_response_empty():
    """Test parsing response with no competencies."""
    raw = """{"competencies": []}"""
    result = parse_competencies_response(raw)
    assert result == []


def test_parse_competencies_response_invalid():
    """Test parsing invalid JSON returns empty list."""
    raw = "This is not JSON at all"
    result = parse_competencies_response(raw)
    assert result == []
