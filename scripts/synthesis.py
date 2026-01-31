"""
Source Synthesis Module
Transforms raw scraped content into structured source documents
"""

from dataclasses import dataclass
from typing import Optional

from openrouter_client import client
from web_research import ScrapedContent
from config import config


SYSTEM_PROMPT = """You are an expert at synthesizing marketing knowledge into actionable source documents.

Your task is to create comprehensive, well-structured source documents that will be used to build marketing skills for AI assistants.

Requirements:
- Be thorough but concise
- Include specific frameworks, steps, and techniques
- Use the expert's actual terminology and concepts
- Include memorable quotes when available
- Focus on actionable, practical knowledge
- Cite specific examples and case studies

Output format: Clean Markdown with clear sections."""


SOURCE_TEMPLATE = """# {expert} - {topic}: Summary & Key Principles

> Source document for the {skill_slug} skill

## Background

{background}

## Core Framework

{framework}

## Key Principles

{principles}

## Techniques & Tactics

{techniques}

## Key Quotes

{quotes}

## Common Mistakes to Avoid

{mistakes}

## Case Studies / Examples

{examples}

## Sources

{sources}
"""


@dataclass
class SynthesisResult:
    """Result of source synthesis."""
    content: str
    word_count: int
    sections: dict
    quality_score: float
    issues: list[str]


class Synthesizer:
    """Synthesizes scraped content into structured source documents."""

    def __init__(self):
        self.config = config.research

    def synthesize(
        self,
        expert: str,
        topic: str,
        scraped_content: list[ScrapedContent],
        skill_slug: Optional[str] = None,
    ) -> SynthesisResult:
        """
        Synthesize multiple scraped sources into one structured document.

        Args:
            expert: Expert name
            topic: Topic/book name
            scraped_content: List of scraped content
            skill_slug: Optional skill identifier

        Returns:
            SynthesisResult with content and quality metrics
        """
        if not skill_slug:
            skill_slug = f"{expert.lower().replace(' ', '-')}-{topic.lower().replace(' ', '-').replace('$', '').replace('100m', 'offers')}"

        # Combine raw content
        combined_raw = self._prepare_raw_content(scraped_content)

        # Generate each section
        sections = {}

        print("  Generating background...")
        sections["background"] = self._generate_section(
            expert, topic, combined_raw,
            "Write a 2-3 paragraph background about {expert} and why {topic} matters. Include their credentials and the core premise of their work."
        )

        print("  Generating core framework...")
        sections["framework"] = self._generate_section(
            expert, topic, combined_raw,
            "Extract and describe the CORE FRAMEWORK or methodology from {topic} by {expert}. Use numbered steps if applicable. Be specific about each step/phase."
        )

        print("  Generating principles...")
        sections["principles"] = self._generate_section(
            expert, topic, combined_raw,
            "List the KEY PRINCIPLES from {topic} by {expert}. Format as numbered list with principle name in bold, then explanation. Minimum 5 principles."
        )

        print("  Generating techniques...")
        sections["techniques"] = self._generate_section(
            expert, topic, combined_raw,
            "List SPECIFIC TECHNIQUES and TACTICS from {topic} by {expert}. These should be actionable methods, not just concepts. Format with subheadings for categories."
        )

        print("  Generating quotes...")
        sections["quotes"] = self._generate_section(
            expert, topic, combined_raw,
            "Extract 3-5 MEMORABLE QUOTES from {expert} about {topic}. Format as blockquotes with attribution. If exact quotes aren't available, paraphrase key insights."
        )

        print("  Generating common mistakes...")
        sections["mistakes"] = self._generate_section(
            expert, topic, combined_raw,
            "List COMMON MISTAKES people make when applying {topic} by {expert}. What do they get wrong? Format as numbered list."
        )

        print("  Generating examples...")
        sections["examples"] = self._generate_section(
            expert, topic, combined_raw,
            "Describe 2-3 CASE STUDIES or EXAMPLES that illustrate {topic} by {expert}. Include specific details about the situation, application, and results."
        )

        # Format sources
        sources_list = "\n".join([
            f"- [{c.title[:60]}...]({c.url})" if len(c.title) > 60 else f"- [{c.title}]({c.url})"
            for c in scraped_content if c.success
        ])
        sections["sources"] = sources_list

        # Assemble final document
        content = SOURCE_TEMPLATE.format(
            expert=expert,
            topic=topic,
            skill_slug=skill_slug,
            **sections
        )

        # Quality check
        quality_score, issues = self._assess_quality(sections)

        return SynthesisResult(
            content=content,
            word_count=len(content.split()),
            sections=sections,
            quality_score=quality_score,
            issues=issues,
        )

    def _prepare_raw_content(self, scraped: list[ScrapedContent]) -> str:
        """Prepare combined raw content for synthesis."""
        parts = []
        for i, sc in enumerate(scraped):
            if sc.success and sc.content:
                # Truncate each source to keep total manageable
                content = sc.content[:15000]
                parts.append(f"=== SOURCE {i+1}: {sc.title} ===\n{content}")

        return "\n\n".join(parts)

    def _generate_section(
        self,
        expert: str,
        topic: str,
        raw_content: str,
        instruction: str,
    ) -> str:
        """Generate a single section using LLM."""
        prompt = f"""Based on the following source material about {expert}'s {topic}:

---
{raw_content[:25000]}
---

{instruction.format(expert=expert, topic=topic)}

Write in clear, professional Markdown. Be specific and include examples where possible."""

        response = client.complete(
            prompt,
            model="balanced",
            system_prompt=SYSTEM_PROMPT,
            max_tokens=2000,
            temperature=0.5,
        )

        return response.content.strip()

    def _assess_quality(self, sections: dict) -> tuple[float, list[str]]:
        """Assess quality of synthesized content."""
        issues = []
        score = 1.0

        # Check framework has steps
        if "1." not in sections.get("framework", "") and "step" not in sections.get("framework", "").lower():
            issues.append("Framework may lack clear steps")
            score -= 0.1

        # Check principles count
        principles = sections.get("principles", "")
        principle_count = principles.count("**") // 2  # Bold markers
        if principle_count < self.config.min_principles:
            issues.append(f"Only {principle_count} principles (need {self.config.min_principles})")
            score -= 0.15

        # Check techniques exist
        techniques = sections.get("techniques", "")
        if len(techniques) < 500:
            issues.append("Techniques section may be thin")
            score -= 0.1

        # Check quotes exist
        if ">" not in sections.get("quotes", ""):
            issues.append("No blockquote quotes found")
            score -= 0.05

        # Check examples
        examples = sections.get("examples", "")
        if len(examples) < 300:
            issues.append("Examples section may be thin")
            score -= 0.1

        return max(0, score), issues

    def enhance_existing(
        self,
        existing_content: str,
        scraped_content: list[ScrapedContent],
    ) -> str:
        """Enhance an existing source document with new scraped content."""
        combined_new = self._prepare_raw_content(scraped_content)

        prompt = f"""You have an existing source document and new research material.
Enhance the existing document by:
1. Adding any missing information from the new sources
2. Adding more specific examples
3. Including additional quotes
4. Filling any thin sections

EXISTING DOCUMENT:
{existing_content}

NEW RESEARCH MATERIAL:
{combined_new[:20000]}

Return the enhanced document in the same format. Keep the same structure, just add depth."""

        response = client.complete(
            prompt,
            model="deep",
            system_prompt=SYSTEM_PROMPT,
            max_tokens=config.openrouter.max_tokens_synthesis,
            temperature=0.3,
        )

        return response.content


# Singleton
synthesizer = Synthesizer()
