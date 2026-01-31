"""
Skill Generator
Transforms source documents into production-ready SKILL.md files

Usage:
    python skill_generator.py sources/books/brunson-dotcom-secrets.md --category content
    python skill_generator.py --from-source brunson-dotcom-secrets --category funnels
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from config import config
from openrouter_client import client


SKILL_TEMPLATE = '''# {title}

> {tagline}

## When to Use This Skill

{when_to_use}

## Methodology Foundation

| Aspect | Details |
|--------|---------|
| **Source** | {source_name} |
| **Expert** | {expert_name} |
| **Core Principle** | {core_principle} |

## What This Skill Does

{what_it_does}

## How to Use

{how_to_use}

## Instructions

{instructions}

## Examples

{examples}

## Checklists & Templates

{checklists}

## References

{references}

## Related Skills

{related_skills}
'''


SYSTEM_PROMPT = """You are an expert at creating actionable AI skill documents.

Your task is to transform marketing expert knowledge into a structured SKILL.md file that an AI assistant can use to help users.

Requirements:
- Be specific and actionable
- Include step-by-step instructions
- Provide concrete examples
- Use the expert's terminology
- Create useful templates and checklists
- Cross-reference related skills

The skill should enable an AI to apply the expert's methodology to real business problems."""


@dataclass
class SkillSpec:
    """Specification for a skill to generate."""
    source_path: Path
    skill_slug: str
    category: str
    title: str
    expert: str
    topic: str


@dataclass
class GeneratedSkill:
    """Result of skill generation."""
    content: str
    skill_path: Path
    word_count: int
    sections_generated: int


class SkillGenerator:
    """Generates SKILL.md files from source documents."""

    def __init__(self):
        self.config = config
        self.skills_dir = config.research.skills_dir

    def generate(
        self,
        source_path: Path,
        category: str,
        skill_slug: Optional[str] = None,
    ) -> GeneratedSkill:
        """
        Generate a SKILL.md from a source document.

        Args:
            source_path: Path to source document
            category: Skill category (content, strategy, sales, etc.)
            skill_slug: Optional custom slug

        Returns:
            GeneratedSkill with content and metadata
        """
        # Read source
        source_content = source_path.read_text()

        # Extract metadata from source
        expert, topic = self._extract_metadata(source_content, source_path)

        if not skill_slug:
            skill_slug = source_path.stem

        print(f"\n{'='*60}")
        print(f"GENERATING SKILL: {skill_slug}")
        print(f"Category: {category}")
        print(f"Expert: {expert}")
        print(f"{'='*60}\n")

        # Generate each section
        sections = {}

        print("Generating sections...")

        print("  - Title and tagline...")
        title_data = self._generate_title(expert, topic, source_content)
        sections.update(title_data)

        print("  - When to use...")
        sections["when_to_use"] = self._generate_section(
            source_content,
            "Create a 'When to Use' section. List 3-5 specific scenarios where this skill applies. "
            "Use bullet points starting with action verbs. Be specific about business situations."
        )

        print("  - Methodology foundation...")
        sections["source_name"] = topic
        sections["expert_name"] = expert
        sections["core_principle"] = self._generate_section(
            source_content,
            "Extract the ONE core principle in 1-2 sentences. What's the fundamental insight?"
        )

        print("  - What it does...")
        sections["what_it_does"] = self._generate_section(
            source_content,
            "Describe what this skill does for the user. Focus on outcomes and transformations. "
            "Use 2-3 short paragraphs."
        )

        print("  - How to use...")
        sections["how_to_use"] = self._generate_section(
            source_content,
            "Create a 'How to Use' section with 3-4 example prompts users might give. "
            "Format as: ### Prompt Examples\n```\n[prompt 1]\n```\netc."
        )

        print("  - Instructions...")
        sections["instructions"] = self._generate_section(
            source_content,
            "Create detailed step-by-step instructions based on the methodology. "
            "Use ### subheadings for major phases. Include numbered steps. "
            "This is the core of the skill - be thorough."
        )

        print("  - Examples...")
        sections["examples"] = self._generate_section(
            source_content,
            "Create 2 concrete examples showing the methodology applied. "
            "Use ### Example 1: [Title] format. Include before/after or input/output. "
            "Make examples from different industries (SaaS, e-commerce, coaching, etc.)."
        )

        print("  - Checklists...")
        sections["checklists"] = self._generate_section(
            source_content,
            "Create useful checklists and templates. Include: "
            "1. A quality checklist with [ ] items "
            "2. A fill-in template users can complete "
            "Format with ### subheadings."
        )

        print("  - References...")
        sections["references"] = self._generate_section(
            source_content,
            "List references: the main book/course, any mentioned resources, "
            "and the source file path. Format as bullet list with links where available."
        )

        print("  - Related skills...")
        sections["related_skills"] = self._suggest_related_skills(category, topic)

        # Assemble skill
        content = SKILL_TEMPLATE.format(**sections)

        # Determine output path
        skill_dir = self.skills_dir / category / skill_slug
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"

        # Save
        skill_path.write_text(content)
        print(f"\n✓ Saved to: {skill_path}")

        return GeneratedSkill(
            content=content,
            skill_path=skill_path,
            word_count=len(content.split()),
            sections_generated=len(sections),
        )

    def _extract_metadata(self, content: str, path: Path) -> tuple[str, str]:
        """Extract expert and topic from source content."""
        # Try to parse from first heading
        match = re.search(r'^#\s+(.+?)\s*-\s*(.+?):', content, re.MULTILINE)
        if match:
            return match.group(1).strip(), match.group(2).strip()

        # Fallback to filename
        parts = path.stem.replace("-", " ").title().split()
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])

        return "Expert", path.stem

    def _generate_title(self, expert: str, topic: str, source: str) -> dict:
        """Generate title and tagline."""
        prompt = f"""Based on this expert's methodology:

Expert: {expert}
Topic: {topic}

Source excerpt:
{source[:3000]}

Generate:
1. A compelling skill TITLE (3-5 words, action-oriented)
2. A one-line TAGLINE that captures the value proposition

Format your response EXACTLY as:
TITLE: [your title]
TAGLINE: [your tagline]"""

        response = client.complete(prompt, model="fast", max_tokens=200)
        content = response.content

        title = topic  # default
        tagline = f"Apply {expert}'s methodology"  # default

        if "TITLE:" in content:
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', content)
            if title_match:
                title = title_match.group(1).strip()

        if "TAGLINE:" in content:
            tagline_match = re.search(r'TAGLINE:\s*(.+?)(?:\n|$)', content)
            if tagline_match:
                tagline = tagline_match.group(1).strip()

        return {"title": title, "tagline": tagline}

    def _generate_section(self, source: str, instruction: str) -> str:
        """Generate a single section."""
        prompt = f"""Based on this source material:

{source[:15000]}

---

{instruction}

Write in clear, actionable Markdown. Be specific and practical."""

        response = client.complete(
            prompt,
            model="balanced",
            system_prompt=SYSTEM_PROMPT,
            max_tokens=2000,
            temperature=0.5,
        )

        return response.content.strip()

    def _suggest_related_skills(self, category: str, topic: str) -> str:
        """Suggest related skills based on category."""
        related = {
            "content": [
                "copy-frameworks", "headline-formulas", "landing-page-copy",
                "email-writing", "cta-writing"
            ],
            "strategy": [
                "positioning-dunford", "grand-slam-offers", "value-proposition-canvas"
            ],
            "sales": [
                "sales-pitch-dunford", "objection-handling", "discovery-call"
            ],
            "funnels": [
                "landing-page-copy", "email-writing", "cta-writing"
            ],
            "persuasion": [
                "cialdini-persuasion", "storytelling-storybrand", "copywriting-ogilvy"
            ],
        }

        skills = related.get(category, ["copy-frameworks", "positioning-dunford"])

        lines = []
        for skill in skills[:5]:
            lines.append(f"- **{skill}** - Complementary methodology")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    generator = SkillGenerator()

    if len(sys.argv) < 2:
        print("Usage: python skill_generator.py <source_path> --category <category>")
        print("       python skill_generator.py sources/books/expert-topic.md --category content")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    if not source_path.exists():
        # Try in sources/books/
        source_path = config.research.sources_dir / f"{sys.argv[1]}.md"
        if not source_path.exists():
            print(f"Source not found: {sys.argv[1]}")
            sys.exit(1)

    # Parse category
    category = "content"  # default
    if "--category" in sys.argv:
        idx = sys.argv.index("--category")
        if idx + 1 < len(sys.argv):
            category = sys.argv[idx + 1]

    # Parse slug
    skill_slug = None
    if "--slug" in sys.argv:
        idx = sys.argv.index("--slug")
        if idx + 1 < len(sys.argv):
            skill_slug = sys.argv[idx + 1]

    result = generator.generate(source_path, category, skill_slug)

    print(f"\n{'='*60}")
    print("SKILL GENERATED")
    print(f"  Path: {result.skill_path}")
    print(f"  Words: {result.word_count}")
    print(f"  Sections: {result.sections_generated}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
