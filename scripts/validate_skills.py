#!/usr/bin/env python3
"""
Validate SKILL.md files for required structure and content.

Usage:
    python scripts/validate_skills.py                    # Validate all skills
    python scripts/validate_skills.py skills/audio/      # Validate category
    python scripts/validate_skills.py skills/audio/podcast-production/SKILL.md  # Single file
"""

import sys
import re
from pathlib import Path
from typing import NamedTuple


class ValidationResult(NamedTuple):
    path: Path
    valid: bool
    errors: list[str]
    warnings: list[str]


# Required sections in every SKILL.md
REQUIRED_SECTIONS = [
    "When to Use This Skill",
    "Methodology Foundation",
    "What This Skill Does",
    "How to Use",
    "Instructions",
    "Examples",
    "References",
]

# Optional but recommended sections (with variations)
RECOMMENDED_SECTIONS = [
    "Checklists & Templates",
    "Related Skills",
]

# Sections that can have variations in naming
FLEXIBLE_SECTIONS = {
    "Skill Metadata": ["Skill Metadata", "Skill Metadata (Internal Use)"],
}

# Required fields in metadata YAML block
METADATA_FIELDS = [
    "name",
    "category",
    "version",
    "tags",
]


def extract_sections(content: str) -> list[str]:
    """Extract all ## level headings from markdown."""
    return re.findall(r"^## (.+)$", content, re.MULTILINE)


def count_examples(content: str) -> int:
    """Count ### Example headings."""
    return len(re.findall(r"^### Example \d+", content, re.MULTILINE))


def has_metadata_block(content: str) -> tuple[bool, list[str]]:
    """Check for YAML metadata block and required fields.

    Looks for the LAST yaml block in the file (metadata is always at the end),
    and validates it has the 'name:' field to confirm it's the metadata block.
    """
    # Find all YAML blocks
    yaml_blocks = re.findall(r"```yaml\n(.+?)```", content, re.DOTALL)
    if not yaml_blocks:
        return False, ["No YAML metadata block found"]

    # Find the metadata block (last one that has 'name:' field)
    metadata_block = None
    for block in reversed(yaml_blocks):
        if "name:" in block:
            metadata_block = block
            break

    if not metadata_block:
        return False, ["No skill metadata YAML block found (must have 'name:' field)"]

    missing = []
    for field in METADATA_FIELDS:
        if f"{field}:" not in metadata_block:
            missing.append(f"Missing metadata field: {field}")

    return len(missing) == 0, missing


def validate_skill(path: Path) -> ValidationResult:
    """Validate a single SKILL.md file."""
    errors = []
    warnings = []

    if not path.exists():
        return ValidationResult(path, False, ["File does not exist"], [])

    content = path.read_text()

    # Check file starts with # title
    if not content.strip().startswith("# "):
        errors.append("File must start with # Title")

    # Check required sections
    sections = extract_sections(content)
    for required in REQUIRED_SECTIONS:
        if required not in sections:
            errors.append(f"Missing required section: ## {required}")

    # Check recommended sections
    for recommended in RECOMMENDED_SECTIONS:
        if recommended not in sections:
            warnings.append(f"Missing recommended section: ## {recommended}")

    # Check flexible sections (can have variations)
    for section_name, variations in FLEXIBLE_SECTIONS.items():
        if not any(var in sections for var in variations):
            warnings.append(f"Missing recommended section: ## {section_name}")

    # Check for minimum 2 examples
    example_count = count_examples(content)
    if example_count < 2:
        errors.append(f"Minimum 2 examples required, found {example_count}")

    # Check for metadata block
    has_meta, meta_issues = has_metadata_block(content)
    if not has_meta:
        errors.extend(meta_issues)

    # Check for one-liner description (> blockquote after title)
    if not re.search(r"^# .+\n\n> .+", content):
        warnings.append("Missing one-liner description (> blockquote)")

    # Check minimum length (skills should be substantial)
    word_count = len(content.split())
    if word_count < 500:
        warnings.append(f"Skill seems short ({word_count} words, recommend 500+)")

    valid = len(errors) == 0
    return ValidationResult(path, valid, errors, warnings)


def find_skills(path: Path) -> list[Path]:
    """Find all SKILL.md files under path."""
    if path.is_file() and path.name == "SKILL.md":
        return [path]
    elif path.is_dir():
        return sorted(path.rglob("SKILL.md"))
    else:
        return []


def main():
    # Default to skills/ directory
    search_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("skills")

    skills = find_skills(search_path)

    if not skills:
        print(f"No SKILL.md files found in {search_path}")
        sys.exit(1)

    print(f"Validating {len(skills)} skill(s)...\n")

    valid_count = 0
    warning_count = 0

    for skill_path in skills:
        result = validate_skill(skill_path)

        # Get relative path for cleaner output
        try:
            display_path = skill_path.relative_to(Path.cwd())
        except ValueError:
            display_path = skill_path

        if result.valid and not result.warnings:
            print(f"✅ {display_path}")
            valid_count += 1
        elif result.valid:
            print(f"⚠️  {display_path}")
            for warning in result.warnings:
                print(f"   └─ {warning}")
            valid_count += 1
            warning_count += 1
        else:
            print(f"❌ {display_path}")
            for error in result.errors:
                print(f"   └─ ERROR: {error}")
            for warning in result.warnings:
                print(f"   └─ WARN: {warning}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Total: {len(skills)} | Valid: {valid_count} | Warnings: {warning_count} | Invalid: {len(skills) - valid_count}")

    # Exit code
    if valid_count == len(skills):
        print("\n✅ All skills valid!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(skills) - valid_count} skill(s) have errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
