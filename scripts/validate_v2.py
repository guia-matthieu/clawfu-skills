#!/usr/bin/env python3
"""
Validate SKILL.md files against v2 quality checklist.

V2 Required Sections:
- "What Claude Does vs What You Decide"
- "Skill Boundaries"
- Mode tag in metadata (centaur/cyborg/both)
- At least 2 examples
- References section
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of validating a single skill."""

    skill_path: str
    skill_name: str = ""
    passed: bool = True
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def add_issue(self, issue: str):
        self.issues.append(issue)
        self.passed = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from skill content."""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_content = parts[1].strip()
            for line in fm_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def validate_skill(skill_path: Path) -> ValidationResult:
    """Validate a single skill against v2 checklist."""
    result = ValidationResult(skill_path=str(skill_path))

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        result.add_issue(f"Cannot read file: {e}")
        return result

    # Extract name from frontmatter
    frontmatter = extract_frontmatter(content)
    result.skill_name = frontmatter.get("name", skill_path.parent.name)

    # Check 1: Frontmatter exists with name and description
    if not frontmatter.get("name"):
        result.add_issue("Missing 'name' in frontmatter")
    if not frontmatter.get("description"):
        result.add_issue("Missing 'description' in frontmatter")

    # Check 2: "What Claude Does vs What You Decide" section
    if "What Claude Does vs What You Decide" not in content:
        result.add_issue("Missing 'What Claude Does vs What You Decide' section")

    # Check 3: "Skill Boundaries" section
    if "Skill Boundaries" not in content:
        result.add_issue("Missing 'Skill Boundaries' section")

    # Check 4: Mode tag in metadata
    mode_patterns = [
        r"\*\*Mode\*\*:\s*(centaur|cyborg|both)",
        r"Mode:\s*(centaur|cyborg|both)",
        r"- \*\*Mode\*\*:\s*(centaur|cyborg|both)",
    ]
    has_mode = any(re.search(p, content, re.IGNORECASE) for p in mode_patterns)
    if not has_mode:
        result.add_warning("Missing Mode tag in metadata (centaur/cyborg/both)")

    # Check 5: At least 2 examples
    example_count = len(re.findall(r"###\s+Example\s+\d", content))
    if example_count < 2:
        result.add_warning(f"Only {example_count} example(s) found (recommend 2+)")

    # Check 6: References section
    if "## References" not in content and "### References" not in content:
        result.add_warning("Missing References section")

    # Check 7: Related Skills section
    if "## Related Skills" not in content and "### Related Skills" not in content:
        result.add_warning("Missing Related Skills section")

    # Check 8: When to Use This Skill section
    if "## When to Use This Skill" not in content:
        result.add_warning("Missing 'When to Use This Skill' section")

    # Check 9: Methodology Foundation
    if "## Methodology Foundation" not in content:
        result.add_warning("Missing 'Methodology Foundation' section")

    # Check 10: Instructions section
    if "## Instructions" not in content:
        result.add_warning("Missing 'Instructions' section")

    return result


def validate_all_skills(skills_dir: Path, verbose: bool = False) -> list:
    """Validate all skills in directory."""
    results = []
    skill_files = list(skills_dir.rglob("SKILL.md"))

    for skill_file in sorted(skill_files):
        result = validate_skill(skill_file)
        results.append(result)

        if verbose:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.skill_name}")
            for issue in result.issues:
                print(f"  ❌ {issue}")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")

    return results


def generate_report(results: list) -> str:
    """Generate validation report."""
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    # Count issues
    issue_counts = {}
    warning_counts = {}
    for r in results:
        for issue in r.issues:
            key = issue.split(":")[0] if ":" in issue else issue
            issue_counts[key] = issue_counts.get(key, 0) + 1
        for warning in r.warnings:
            key = warning.split(":")[0] if ":" in warning else warning
            warning_counts[key] = warning_counts.get(key, 0) + 1

    report = []
    report.append("# V2 Validation Report")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append("| Metric | Count |")
    report.append("|--------|-------|")
    report.append(f"| Total Skills | {len(results)} |")
    report.append(f"| Passed | {len(passed)} |")
    report.append(f"| Failed | {len(failed)} |")
    report.append(f"| Pass Rate | {len(passed)/len(results)*100:.1f}% |")
    report.append("")

    if failed:
        report.append("## Failed Skills")
        report.append("")
        for r in failed:
            report.append(f"### {r.skill_name}")
            report.append(f"Path: `{r.skill_path}`")
            report.append("")
            for issue in r.issues:
                report.append(f"- ❌ {issue}")
            report.append("")

    report.append("## Issue Summary")
    report.append("")
    report.append("| Issue | Count |")
    report.append("|-------|-------|")
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
        report.append(f"| {issue} | {count} |")
    report.append("")

    report.append("## Warning Summary")
    report.append("")
    report.append("| Warning | Count |")
    report.append("|---------|-------|")
    for warning, count in sorted(warning_counts.items(), key=lambda x: -x[1]):
        report.append(f"| {warning} | {count} |")
    report.append("")

    return "\n".join(report)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate SKILL.md files against v2 checklist")
    parser.add_argument("path", nargs="?", default=".", help="Skills directory or single file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-r", "--report", action="store_true", help="Generate markdown report")
    parser.add_argument("-o", "--output", help="Output file for report")

    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file():
        results = [validate_skill(path)]
    elif path.is_dir():
        # Find skills directory
        if (path / "skills").is_dir():
            skills_dir = path / "skills"
        else:
            skills_dir = path
        results = validate_all_skills(skills_dir, verbose=args.verbose)
    else:
        print(f"Error: Path not found: {path}")
        sys.exit(1)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    print(f"\n{'='*50}")
    print(f"V2 Validation Summary: {passed}/{len(results)} passed ({passed/len(results)*100:.1f}%)")
    if failed:
        print(f"  {failed} skills need attention")
    print(f"{'='*50}")

    if args.report:
        report = generate_report(results)
        if args.output:
            Path(args.output).write_text(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
