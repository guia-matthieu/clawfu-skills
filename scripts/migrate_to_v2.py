#!/usr/bin/env python3
"""
Migrate SKILL.md files to v2 format by adding missing required sections.

This script adds:
- "What Claude Does vs What You Decide" section
- "Skill Boundaries" section
- Mode tag in metadata

It preserves existing content and inserts new sections in appropriate locations.
"""

import re
from pathlib import Path


def extract_skill_context(content: str) -> dict:
    """Extract context from skill to generate appropriate v2 sections."""
    context = {
        "name": "",
        "description": "",
        "domain": "",
        "has_examples": False,
        "has_instructions": False,
    }

    # Extract name from frontmatter
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_match = re.search(r"name:\s*(.+)", fm)
        desc_match = re.search(r"description:\s*(.+)", fm)
        if name_match:
            context["name"] = name_match.group(1).strip()
        if desc_match:
            context["description"] = desc_match.group(1).strip()

    # Detect domain from content
    if any(word in content.lower() for word in ["podcast", "audio", "voice", "sound"]):
        context["domain"] = "audio"
    elif any(word in content.lower() for word in ["video", "storyboard", "animation"]):
        context["domain"] = "video"
    elif any(word in content.lower() for word in ["copy", "writing", "headline", "persuasion"]):
        context["domain"] = "content"
    elif any(word in content.lower() for word in ["positioning", "strategy", "competitive"]):
        context["domain"] = "strategy"
    elif any(word in content.lower() for word in ["sales", "pitch", "negotiation", "deal"]):
        context["domain"] = "sales"
    elif any(word in content.lower() for word in ["analytics", "metrics", "data"]):
        context["domain"] = "analytics"
    else:
        context["domain"] = "general"

    context["has_examples"] = "## Example" in content or "### Example" in content
    context["has_instructions"] = "## Instructions" in content or "## How to Use" in content

    return context


def generate_claude_vs_you_section(context: dict) -> str:
    """Generate the 'What Claude Does vs What You Decide' section."""
    domain_specific = {
        "audio": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures production workflow | Final creative direction |\n"
            "| Suggests technical approaches | Equipment and tool choices |\n"
            "| Creates templates and checklists | Quality standards |\n"
            "| Identifies best practices | Brand/voice decisions |\n"
            "| Generates script outlines | Final script approval |"
        ),
        "video": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures video workflow | Final creative vision |\n"
            "| Suggests shot compositions | Equipment selection |\n"
            "| Creates storyboard templates | Brand aesthetics |\n"
            "| Generates script frameworks | Final approval |\n"
            "| Identifies technical requirements | Budget allocation |"
        ),
        "content": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures content frameworks | Final messaging |\n"
            "| Suggests persuasion techniques | Brand voice |\n"
            "| Creates draft variations | Version selection |\n"
            "| Identifies optimization opportunities | Publication timing |\n"
            "| Analyzes competitor approaches | Strategic direction |"
        ),
        "strategy": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures analysis frameworks | Strategic priorities |\n"
            "| Synthesizes market data | Competitive positioning |\n"
            "| Identifies opportunities | Resource allocation |\n"
            "| Creates strategic options | Final strategy selection |\n"
            "| Suggests implementation approaches | Execution decisions |"
        ),
        "sales": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures sales frameworks | Deal strategy |\n"
            "| Suggests discovery questions | Relationship approach |\n"
            "| Creates proposal templates | Pricing decisions |\n"
            "| Identifies objection patterns | Negotiation tactics |\n"
            "| Analyzes deal dynamics | Final deal terms |"
        ),
        "analytics": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures analysis frameworks | Metric definitions |\n"
            "| Identifies patterns in data | Business interpretation |\n"
            "| Creates visualization templates | Dashboard design |\n"
            "| Suggests optimization areas | Action priorities |\n"
            "| Calculates statistical measures | Decision thresholds |"
        ),
        "general": (
            "| Claude Does | You Decide |\n"
            "|-------------|------------|\n"
            "| Structures the process | Final decisions |\n"
            "| Suggests best practices | Implementation approach |\n"
            "| Creates templates | Customization |\n"
            "| Identifies opportunities | Priorities |\n"
            "| Provides analysis | Action steps |"
        ),
    }

    table = domain_specific.get(context.get("domain", "general"), domain_specific["general"])

    return f"""## What Claude Does vs What You Decide

{table}
"""


def generate_skill_boundaries_section(context: dict) -> str:
    """Generate the 'Skill Boundaries' section."""
    domain_specific = {
        "audio": (
            "### What This Skill Does Well\n"
            "- Structuring audio production workflows\n"
            "- Providing technical guidance\n"
            "- Creating quality checklists\n"
            "- Suggesting creative approaches\n\n"
            "### What This Skill Cannot Do\n"
            "- Replace audio engineering expertise\n"
            "- Make subjective creative decisions\n"
            "- Access or edit audio files directly\n"
            "- Guarantee commercial success"
        ),
        "video": (
            "### What This Skill Does Well\n"
            "- Structuring video production workflows\n"
            "- Creating storyboard frameworks\n"
            "- Suggesting technical approaches\n"
            "- Providing creative direction templates\n\n"
            "### What This Skill Cannot Do\n"
            "- Replace professional videography\n"
            "- Edit video files directly\n"
            "- Make final creative judgments\n"
            "- Guarantee audience engagement"
        ),
        "content": (
            "### What This Skill Does Well\n"
            "- Structuring persuasive content\n"
            "- Applying copywriting frameworks\n"
            "- Creating draft variations\n"
            "- Analyzing competitor approaches\n\n"
            "### What This Skill Cannot Do\n"
            "- Guarantee conversion rates\n"
            "- Replace brand voice development\n"
            "- Know your specific audience\n"
            "- Make final approval decisions"
        ),
        "strategy": (
            "### What This Skill Does Well\n"
            "- Structuring strategic analysis\n"
            "- Identifying market opportunities\n"
            "- Creating strategic frameworks\n"
            "- Synthesizing competitive data\n\n"
            "### What This Skill Cannot Do\n"
            "- Replace market research\n"
            "- Guarantee strategic success\n"
            "- Know proprietary competitor info\n"
            "- Make executive decisions"
        ),
        "sales": (
            "### What This Skill Does Well\n"
            "- Structuring sales conversations\n"
            "- Creating discovery frameworks\n"
            "- Analyzing deal dynamics\n"
            "- Suggesting negotiation approaches\n\n"
            "### What This Skill Cannot Do\n"
            "- Replace relationship building\n"
            "- Guarantee closed deals\n"
            "- Know specific buyer psychology\n"
            "- Make pricing decisions"
        ),
        "analytics": (
            "### What This Skill Does Well\n"
            "- Structuring data analysis\n"
            "- Identifying patterns and trends\n"
            "- Creating visualization frameworks\n"
            "- Calculating statistical measures\n\n"
            "### What This Skill Cannot Do\n"
            "- Access your actual data\n"
            "- Replace statistical expertise\n"
            "- Make business decisions\n"
            "- Guarantee prediction accuracy"
        ),
        "general": (
            "### What This Skill Does Well\n"
            "- Structuring processes and workflows\n"
            "- Providing best practice guidance\n"
            "- Creating reusable templates\n"
            "- Identifying optimization opportunities\n\n"
            "### What This Skill Cannot Do\n"
            "- Replace domain expertise\n"
            "- Make final decisions for you\n"
            "- Guarantee specific outcomes\n"
            "- Know your specific context"
        ),
    }

    content = domain_specific.get(context.get("domain", "general"), domain_specific["general"])

    return f"""## Skill Boundaries

{content}
"""


def add_mode_tag(content: str, context: dict) -> str:
    """Add Mode tag to Skill Metadata section if missing."""
    # Check if Mode already exists
    if re.search(r"\*\*Mode\*\*:\s*(centaur|cyborg|both)", content, re.IGNORECASE):
        return content

    # Determine appropriate mode based on domain
    mode_map = {
        "audio": "cyborg",
        "video": "cyborg",
        "content": "cyborg",
        "strategy": "centaur",
        "sales": "centaur",
        "analytics": "centaur",
        "general": "cyborg",
    }
    mode = mode_map.get(context.get("domain", "general"), "cyborg")

    # Find Skill Metadata section and add Mode
    metadata_pattern = r"(## Skill Metadata\s*\n)"
    if re.search(metadata_pattern, content):
        # Insert Mode after the heading
        replacement = rf"\1\n- **Mode**: {mode}\n"
        content = re.sub(metadata_pattern, replacement, content, count=1)

    return content


def migrate_skill(skill_path: Path, dry_run: bool = False) -> tuple:
    """Migrate a single skill to v2 format."""
    content = skill_path.read_text(encoding="utf-8")
    original_content = content
    changes = []

    context = extract_skill_context(content)

    # Check if already has required sections
    has_claude_vs_you = "What Claude Does vs What You Decide" in content
    has_boundaries = "Skill Boundaries" in content

    if has_claude_vs_you and has_boundaries:
        # Add mode tag if missing
        content = add_mode_tag(content, context)
        if content != original_content:
            changes.append("Added Mode tag")
        else:
            return (False, [])  # Already compliant

    # Insert "What Claude Does vs What You Decide" after "Methodology Foundation" or "When to Use"
    if not has_claude_vs_you:
        claude_section = generate_claude_vs_you_section(context)

        # Try to insert after Methodology Foundation
        if "## Methodology Foundation" in content:
            # Find the end of Methodology Foundation section
            pattern = r"(## Methodology Foundation.*?)(\n## )"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                insert_point = match.end(1)
                content = content[:insert_point] + "\n\n" + claude_section + content[insert_point:]
                changes.append("Added 'What Claude Does vs What You Decide' section")
        # Try after When to Use
        elif "## When to Use" in content:
            pattern = r"(## When to Use.*?)(\n## )"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                insert_point = match.end(1)
                content = content[:insert_point] + "\n\n" + claude_section + content[insert_point:]
                changes.append("Added 'What Claude Does vs What You Decide' section")
        else:
            # Insert after the first ## heading
            pattern = r"(^#[^#].*?\n)(.*?)(\n## )"
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                insert_point = match.start(3)
                content = content[:insert_point] + "\n\n" + claude_section + content[insert_point:]
                changes.append("Added 'What Claude Does vs What You Decide' section")

    # Insert "Skill Boundaries" before "References" or at the end
    if "Skill Boundaries" not in content:
        boundaries_section = generate_skill_boundaries_section(context)

        if "## References" in content:
            content = content.replace("## References", boundaries_section + "\n## References")
            changes.append("Added 'Skill Boundaries' section")
        elif "## Related Skills" in content:
            content = content.replace("## Related Skills", boundaries_section + "\n## Related Skills")
            changes.append("Added 'Skill Boundaries' section")
        elif "## Skill Metadata" in content:
            content = content.replace("## Skill Metadata", boundaries_section + "\n## Skill Metadata")
            changes.append("Added 'Skill Boundaries' section")
        else:
            content = content + "\n\n" + boundaries_section
            changes.append("Added 'Skill Boundaries' section (at end)")

    # Add mode tag
    content = add_mode_tag(content, context)
    if "Added Mode tag" not in changes and "Mode" not in original_content:
        changes.append("Added Mode tag")

    if changes and not dry_run:
        skill_path.write_text(content, encoding="utf-8")

    return (len(changes) > 0, changes)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate SKILL.md files to v2 format")
    parser.add_argument("path", nargs="?", default=".", help="Skills directory")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    path = Path(args.path)

    # Find skills directory
    if (path / "skills").is_dir():
        skills_dir = path / "skills"
    else:
        skills_dir = path

    skill_files = list(skills_dir.rglob("SKILL.md"))
    migrated = 0
    skipped = 0

    for skill_file in sorted(skill_files):
        changed, changes = migrate_skill(skill_file, dry_run=args.dry_run)

        if changed:
            migrated += 1
            if args.verbose:
                print(f"[MIGRATED] {skill_file.parent.name}")
                for change in changes:
                    print(f"  + {change}")
        else:
            skipped += 1
            if args.verbose:
                print(f"[SKIPPED] {skill_file.parent.name} (already v2 compliant)")

    action = "Would migrate" if args.dry_run else "Migrated"
    print(f"\n{action} {migrated} skills, skipped {skipped} (already compliant)")

    if args.dry_run and migrated > 0:
        print("\nRun without --dry-run to apply changes")


if __name__ == "__main__":
    main()
