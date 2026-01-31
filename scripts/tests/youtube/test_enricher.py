# scripts/tests/youtube/test_enricher.py
"""Tests for LLM enrichment functionality."""

from youtube.enricher import EnrichmentPrompts, parse_enrichment_response


def test_enrichment_prompts_exist():
    """Test that enrichment prompts are defined."""
    assert EnrichmentPrompts.SUMMARY is not None
    assert len(EnrichmentPrompts.SUMMARY) > 100  # Should be substantial


def test_parse_enrichment_response_json():
    """Test parsing a well-formed JSON response."""
    raw = """{
        "summary": "This video explains how to create skills for AI agents.",
        "key_points": [
            "Skills are organized folders with scripts as tools",
            "MCP provides connectivity while skills provide expertise"
        ],
        "frameworks": [
            {"name": "Progressive Disclosure", "description": "Only show metadata initially"}
        ],
        "notable_quotes": [
            {"quote": "Skills are knowledge, MCP is connectivity", "timestamp": "5:23"}
        ]
    }"""
    result = parse_enrichment_response(raw)
    assert "skills" in result["summary"].lower()
    assert len(result["key_points"]) == 2
    assert len(result["frameworks"]) == 1
    assert result["frameworks"][0]["name"] == "Progressive Disclosure"


def test_parse_enrichment_response_markdown_wrapped():
    """Test parsing JSON wrapped in markdown code block."""
    raw = """Here's the analysis:

```json
{
    "summary": "Video about marketing strategies.",
    "key_points": ["Point one", "Point two"],
    "frameworks": [],
    "notable_quotes": []
}
```

Hope this helps!"""
    result = parse_enrichment_response(raw)
    assert "marketing" in result["summary"].lower()
    assert len(result["key_points"]) == 2


def test_parse_enrichment_response_fallback():
    """Test fallback when JSON parsing fails."""
    raw = "This is not valid JSON at all, just plain text about marketing skills."
    result = parse_enrichment_response(raw)
    # Should return a fallback structure
    assert "summary" in result
    assert "key_points" in result
    assert isinstance(result["key_points"], list)
