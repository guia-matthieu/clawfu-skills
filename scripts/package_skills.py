#!/usr/bin/env python3
"""
Package SKILL.md files into distributable .skill format.

The .skill format extends the SKILL.md with additional frontmatter:
- version: semantic version
- author: creator name/org
- license: usage license
- pricing: free/premium/enterprise
- category: domain category
- tags: searchable tags
"""

import re
from pathlib import Path
from datetime import datetime


def extract_frontmatter(content: str) -> tuple:
    """Extract existing frontmatter and body from skill content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2].strip()
    return "", content


def determine_category(skill_path: Path) -> str:
    """Determine category from skill path."""
    # Get parent directory name
    parts = skill_path.parts
    for i, part in enumerate(parts):
        if part == "skills" and i + 1 < len(parts):
            return parts[i + 1]
    return "general"


def determine_tags(content: str, category: str) -> list:
    """Extract tags from content analysis."""
    tags = [category]

    # Common tag patterns
    tag_patterns = {
        "AI": r"\b(AI|artificial intelligence|machine learning|LLM)\b",
        "strategy": r"\b(strategy|strategic|positioning|competitive)\b",
        "sales": r"\b(sales|selling|deal|revenue|pipeline)\b",
        "marketing": r"\b(marketing|campaign|brand|content)\b",
        "analytics": r"\b(analytics|metrics|data|analysis)\b",
        "automation": r"\b(automation|automate|script|workflow)\b",
        "customer-success": r"\b(customer success|retention|churn|health score)\b",
        "crisis": r"\b(crisis|emergency|reputation|PR)\b",
        "legal": r"\b(legal|contract|compliance|GDPR|NDA)\b",
        "HR": r"\b(HR|hiring|onboarding|employee|resume)\b",
    }

    for tag, pattern in tag_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            if tag not in tags:
                tags.append(tag)

    return tags[:5]  # Limit to 5 tags


def determine_pricing(category: str, skill_name: str) -> str:
    """Determine pricing tier based on category and skill."""
    premium_categories = {"automation", "revops", "customer-success", "crisis", "legal"}
    premium_skills = {
        "positioning",
        "grand-slam-offers",
        "never-split-difference",
        "meddic-scorecard",
        "pipeline-forecasting",
    }

    if category in premium_categories:
        return "premium"
    if skill_name in premium_skills:
        return "premium"
    return "free"


def package_skill(skill_path: Path, output_dir: Path, version: str = "2.0.0") -> Path:
    """Package a single skill as .skill file."""
    content = skill_path.read_text(encoding="utf-8")
    old_fm, body = extract_frontmatter(content)

    # Parse existing frontmatter
    existing = {}
    for line in old_fm.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            existing[key.strip()] = value.strip()

    skill_name = existing.get("name", skill_path.parent.name)
    category = determine_category(skill_path)
    tags = determine_tags(content, category)
    pricing = determine_pricing(category, skill_name)

    # Build extended frontmatter
    new_fm_lines = [
        f'name: {existing.get("name", skill_name)}',
        f'description: {existing.get("description", "")}',
        f"version: {version}",
        "author: ClawFu (GUIA)",
        "license: CC-BY-NC-4.0",
        f"pricing: {pricing}",
        f"category: {category}",
        f"tags: [{', '.join(tags)}]",
        f'created: {datetime.now().strftime("%Y-%m-%d")}',
        "source: clawfu.com",
    ]

    # Build .skill content
    skill_content = f"""---
{chr(10).join(new_fm_lines)}
---

{body}
"""

    # Write .skill file
    output_path = output_dir / f"{skill_name}.skill"
    output_path.write_text(skill_content, encoding="utf-8")

    return output_path


def generate_catalog(skills: list, output_path: Path):
    """Generate a catalog manifest of all packaged skills."""
    catalog = {
        "name": "ClawFu Marketing Skills",
        "version": "2.0.0",
        "description": "159 expert marketing skills for Claude AI",
        "author": "GUIA",
        "license": "CC-BY-NC-4.0",
        "website": "https://clawfu.com",
        "generated": datetime.now().isoformat(),
        "skills": [],
    }

    for skill_path in skills:
        content = skill_path.read_text(encoding="utf-8")
        fm, _ = extract_frontmatter(content)

        skill_info = {}
        for line in fm.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                skill_info[key.strip()] = value.strip()

        catalog["skills"].append(
            {
                "name": skill_info.get("name", skill_path.stem),
                "description": skill_info.get("description", ""),
                "category": skill_info.get("category", ""),
                "pricing": skill_info.get("pricing", "free"),
                "tags": skill_info.get("tags", "[]"),
                "file": skill_path.name,
            }
        )

    # Generate markdown catalog
    md_lines = [
        f"# {catalog['name']}",
        "",
        f"**Version:** {catalog['version']}",
        f"**Skills:** {len(catalog['skills'])}",
        f"**Generated:** {catalog['generated'][:10]}",
        "",
        "## Skills by Category",
        "",
    ]

    # Group by category
    by_category = {}
    for skill in catalog["skills"]:
        cat = skill.get("category", "general")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for category in sorted(by_category.keys()):
        skills_list = by_category[category]
        md_lines.append(f"### {category.replace('-', ' ').title()}")
        md_lines.append("")
        md_lines.append("| Skill | Description | Tier |")
        md_lines.append("|-------|-------------|------|")
        for skill in sorted(skills_list, key=lambda x: x["name"]):
            tier = "Premium" if skill["pricing"] == "premium" else "Free"
            desc = skill["description"][:60] + "..." if len(skill["description"]) > 60 else skill["description"]
            md_lines.append(f"| {skill['name']} | {desc} | {tier} |")
        md_lines.append("")

    # Write catalog
    output_path.write_text("\n".join(md_lines), encoding="utf-8")

    return catalog


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Package SKILL.md files as .skill")
    parser.add_argument("path", nargs="?", default=".", help="Skills directory")
    parser.add_argument("-o", "--output", default="dist", help="Output directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--version", default="2.0.0", help="Version number")

    args = parser.parse_args()

    path = Path(args.path)

    # Find skills directory
    if (path / "skills").is_dir():
        skills_dir = path / "skills"
    else:
        skills_dir = path

    # Create output directory
    output_dir = path / args.output
    output_dir.mkdir(exist_ok=True)

    # Package all skills
    skill_files = list(skills_dir.rglob("SKILL.md"))
    packaged = []

    for skill_file in sorted(skill_files):
        output_path = package_skill(skill_file, output_dir, version=args.version)
        packaged.append(output_path)

        if args.verbose:
            print(f"[PACKAGED] {output_path.name}")

    # Generate catalog
    catalog_path = output_dir / "CATALOG.md"
    generate_catalog(packaged, catalog_path)

    print(f"\nPackaged {len(packaged)} skills to {output_dir}")
    print(f"Catalog: {catalog_path}")


if __name__ == "__main__":
    main()
