#!/usr/bin/env python3
"""
Export micro-competencies to JSON and CSV formats.

Parses competences-exhaustives.md and skills-mapping.md to create:
- docs/micro-competencies.json (hierarchical)
- docs/micro-competencies.csv (flat)
"""

import json
import csv
import re
from pathlib import Path
from datetime import date


def parse_competencies_md(filepath: Path) -> dict:
    """Parse competences-exhaustives.md and extract hierarchical structure."""

    content = filepath.read_text(encoding='utf-8')

    domains = []
    current_domain = None
    current_cluster = None

    lines = content.split('\n')
    i = 0

    # Stop parsing when we hit the summary section
    stop_markers = [
        '## RÉSUMÉ STATISTIQUE',
        '## PROCHAINES ÉTAPES',
        '| Partie | Nombre de compétences |'
    ]

    while i < len(lines):
        line = lines[i].strip()

        # Stop at summary section
        if any(marker in line for marker in stop_markers):
            break

        # Match PARTIE headers: ## PARTIE X : NAME or ## PARTIE X: NAME
        partie_match = re.match(r'^## PARTIE (\d+)\s*[:\s]+\s*(.+)$', line)
        if partie_match:
            domain_id = int(partie_match.group(1))
            domain_name = partie_match.group(2).strip()
            current_domain = {
                "id": domain_id,
                "name": domain_name,
                "clusters": []
            }
            domains.append(current_domain)
            i += 1
            continue

        # Match cluster headers: ### X.X Name
        cluster_match = re.match(r'^### (\d+\.\d+)\s+(.+)$', line)
        if cluster_match and current_domain:
            cluster_id = cluster_match.group(1)
            cluster_name = cluster_match.group(2).strip()
            current_cluster = {
                "id": cluster_id,
                "name": cluster_name,
                "competencies": []
            }
            current_domain["clusters"].append(current_cluster)
            i += 1
            continue

        # Match table rows: | Compétence | Description |
        # Skip header rows and separator rows
        if line.startswith('|') and current_cluster:
            # Skip header and separator rows
            if 'Compétence' in line or 'Description' in line or '---' in line:
                i += 1
                continue

            # Skip rows that look like summary data (numbers only in first column)
            if re.match(r'\|\s*\d+\..*\|.*\|', line) and 'Stratégie' in line:
                i += 1
                continue

            # Parse competency row
            parts = [p.strip() for p in line.split('|')]
            # Filter out empty parts (from leading/trailing |)
            parts = [p for p in parts if p]

            if len(parts) >= 2:
                competency_name = parts[0]
                description = parts[1] if len(parts) > 1 else ""

                # Skip if it's a header row variant or invalid data
                skip_patterns = [
                    'Compétence',
                    '---',
                    '**TOTAL**',
                    'TOTAL',
                    'Partie',
                    'Nombre de compétences'
                ]
                if competency_name and not any(p in competency_name for p in skip_patterns):
                    # Skip if the competency name starts with a number followed by a period (summary rows)
                    if re.match(r'^\d+\.\s+[A-Z]', competency_name):
                        i += 1
                        continue

                    # Generate competency ID based on cluster
                    comp_num = len(current_cluster["competencies"]) + 1
                    comp_id = f"{current_cluster['id']}.{comp_num}"

                    current_cluster["competencies"].append({
                        "id": comp_id,
                        "name": competency_name,
                        "description": description
                    })

        i += 1

    return domains


def parse_skills_mapping(filepath: Path) -> dict:
    """Parse skills-mapping.md to get competency → skill mappings."""

    content = filepath.read_text(encoding='utf-8')

    # Build a mapping of skill names to their included competencies
    skill_to_competencies = {}
    competency_to_skills = {}
    skill_status = {}

    # Pattern to match skill rows: | Type | Skill | Compétences incluses | Source |
    # Example: | 🔶 | **positioning-dunford** | Analyse alternatives, attributs uniques, ... | April Dunford ✅ |

    skill_pattern = re.compile(
        r'\|\s*([🔶🔷])\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|'
    )

    for line in content.split('\n'):
        match = skill_pattern.search(line)
        if match:
            _ = match.group(1)  # skill_type (unused)
            skill_name = match.group(2).strip()
            competencies_str = match.group(3).strip()
            source = match.group(4).strip()

            # Determine status from source
            if '✅' in source:
                status = 'done'
            elif '🟢' in source:
                status = 'ready'
            elif '🟡' in source:
                status = 'identified'
            else:
                status = 'todo'

            skill_status[skill_name] = status

            # Parse competencies included in this skill
            competencies = [c.strip() for c in competencies_str.split(',')]
            skill_to_competencies[skill_name] = competencies

            # Build reverse mapping (partial match on competency name)
            for comp in competencies:
                comp_lower = comp.lower()
                if comp_lower not in competency_to_skills:
                    competency_to_skills[comp_lower] = []
                competency_to_skills[comp_lower].append(skill_name)

    return {
        "skill_to_competencies": skill_to_competencies,
        "competency_to_skills": competency_to_skills,
        "skill_status": skill_status
    }


def find_linked_skills(competency_name: str, competency_desc: str, mappings: dict) -> tuple:
    """Find skills linked to a competency by fuzzy matching."""

    linked_skills = []
    comp_lower = competency_name.lower()
    desc_lower = competency_desc.lower()

    # Check each skill's included competencies for partial match
    for skill_name, competencies in mappings["skill_to_competencies"].items():
        for comp in competencies:
            comp_check = comp.lower()
            # Match if the skill's listed competency appears in the competency name or description
            if (comp_check in comp_lower or
                comp_lower in comp_check or
                comp_check in desc_lower):
                if skill_name not in linked_skills:
                    linked_skills.append(skill_name)
                break

    # Get best status among linked skills
    if linked_skills:
        statuses = [mappings["skill_status"].get(s, 'todo') for s in linked_skills]
        # Priority: done > ready > identified > todo
        if 'done' in statuses:
            best_status = 'done'
        elif 'ready' in statuses:
            best_status = 'ready'
        elif 'identified' in statuses:
            best_status = 'identified'
        else:
            best_status = 'todo'
    else:
        best_status = 'unmapped'

    return linked_skills, best_status


def generate_json_output(domains: list, mappings: dict) -> dict:
    """Generate the hierarchical JSON structure."""

    total_competencies = 0
    total_clusters = 0

    # Add skill linkage to each competency
    for domain in domains:
        for cluster in domain["clusters"]:
            total_clusters += 1
            for comp in cluster["competencies"]:
                total_competencies += 1
                linked_skills, status = find_linked_skills(
                    comp["name"],
                    comp["description"],
                    mappings
                )
                comp["linked_skills"] = linked_skills
                comp["skill_status"] = status

    output = {
        "metadata": {
            "total_competencies": total_competencies,
            "total_domains": len(domains),
            "total_clusters": total_clusters,
            "generated": str(date.today())
        },
        "domains": domains
    }

    return output


def generate_csv_rows(data: dict) -> list:
    """Generate flat CSV rows from hierarchical data."""

    rows = []

    for domain in data["domains"]:
        for cluster in domain["clusters"]:
            for comp in cluster["competencies"]:
                row = {
                    "id": comp["id"],
                    "domain": domain["name"],
                    "domain_id": domain["id"],
                    "cluster": cluster["name"],
                    "cluster_id": cluster["id"],
                    "competency": comp["name"],
                    "description": comp["description"],
                    "linked_skills": ",".join(comp.get("linked_skills", [])),
                    "skill_status": comp.get("skill_status", "unmapped")
                }
                rows.append(row)

    return rows


def main():
    """Main function to parse and export competencies."""

    # Paths
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / "docs"

    competencies_file = docs_dir / "competences-exhaustives.md"
    mapping_file = docs_dir / "skills-mapping.md"

    json_output = docs_dir / "micro-competencies.json"
    csv_output = docs_dir / "micro-competencies.csv"

    print(f"Parsing {competencies_file}...")
    domains = parse_competencies_md(competencies_file)

    print(f"Parsing {mapping_file}...")
    mappings = parse_skills_mapping(mapping_file)

    print("Generating JSON output...")
    json_data = generate_json_output(domains, mappings)

    print("Generating CSV output...")
    csv_rows = generate_csv_rows(json_data)

    # Write JSON
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"Written: {json_output}")

    # Write CSV
    fieldnames = ["id", "domain", "domain_id", "cluster", "cluster_id",
                  "competency", "description", "linked_skills", "skill_status"]
    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Written: {csv_output}")

    # Print summary
    print("\n" + "=" * 50)
    print("EXPORT SUMMARY")
    print("=" * 50)
    print(f"Total domains: {json_data['metadata']['total_domains']}")
    print(f"Total clusters: {json_data['metadata']['total_clusters']}")
    print(f"Total competencies: {json_data['metadata']['total_competencies']}")
    print(f"CSV rows: {len(csv_rows)} (+ header)")

    # Count by status
    status_counts = {}
    for row in csv_rows:
        status = row["skill_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    print("\nCompetencies by skill status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    # Domain breakdown
    print("\nCompetencies by domain:")
    for domain in json_data["domains"]:
        comp_count = sum(len(c["competencies"]) for c in domain["clusters"])
        print(f"  {domain['id']}. {domain['name']}: {comp_count}")


if __name__ == "__main__":
    main()
