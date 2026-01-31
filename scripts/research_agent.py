"""
MKTG Skills Research Agent
Complete pipeline: Search → Scrape → Synthesize → Save

Usage:
    python research_agent.py "Russell Brunson" "DotCom Secrets"
    python research_agent.py --batch
    python research_agent.py --list
"""

import sys
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

from config import config
from web_research import researcher
from synthesis import synthesizer, SynthesisResult


@dataclass
class ResearchResult:
    """Complete research result for an expert/topic."""
    expert: str
    topic: str
    skill_slug: str
    status: str  # success, partial, failed
    source_path: Optional[str]
    sources_found: int
    sources_scraped: int
    word_count: int
    quality_score: float
    issues: list[str]
    duration_seconds: float
    timestamp: str


class ResearchAgent:
    """Orchestrates the complete research pipeline."""

    def __init__(self):
        self.config = config

    def research(
        self,
        expert: str,
        topic: str,
        skill_slug: Optional[str] = None,
        enhance_existing: bool = False,
    ) -> ResearchResult:
        """
        Execute complete research pipeline for an expert/topic.

        Args:
            expert: Expert name (e.g., "Russell Brunson")
            topic: Topic/book (e.g., "DotCom Secrets")
            skill_slug: Optional skill identifier
            enhance_existing: If True, enhance existing source instead of replacing

        Returns:
            ResearchResult with status and metadata
        """
        start_time = datetime.now()

        if not skill_slug:
            skill_slug = self._generate_slug(expert, topic)

        print(f"\n{'='*60}")
        print(f"RESEARCH: {expert} - {topic}")
        print(f"Skill: {skill_slug}")
        print(f"{'='*60}\n")

        # Check for existing source
        source_path = self.config.research.sources_dir / f"{skill_slug}.md"
        existing_content = None
        if source_path.exists() and enhance_existing:
            existing_content = source_path.read_text()
            print("Found existing source, will enhance")

        # Step 1: Research
        print("Step 1: Searching and scraping sources...")
        scraped = researcher.research_topic(
            expert, topic,
            max_sources=self.config.research.max_sources_per_expert
        )

        if not scraped:
            return ResearchResult(
                expert=expert,
                topic=topic,
                skill_slug=skill_slug,
                status="failed",
                source_path=None,
                sources_found=0,
                sources_scraped=0,
                word_count=0,
                quality_score=0,
                issues=["No sources could be scraped"],
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now().isoformat(),
            )

        print(f"\n  Scraped {len(scraped)} sources successfully\n")

        # Step 2: Synthesize
        print("Step 2: Synthesizing source document...")
        if existing_content:
            content = synthesizer.enhance_existing(existing_content, scraped)
            synthesis = SynthesisResult(
                content=content,
                word_count=len(content.split()),
                sections={},
                quality_score=0.8,
                issues=[],
            )
        else:
            synthesis = synthesizer.synthesize(
                expert, topic, scraped, skill_slug
            )

        print(f"\n  Generated {synthesis.word_count} words")
        print(f"  Quality score: {synthesis.quality_score:.0%}")
        if synthesis.issues:
            print(f"  Issues: {', '.join(synthesis.issues)}")

        # Step 3: Save
        print(f"\nStep 3: Saving to {source_path}...")
        source_path.write_text(synthesis.content)
        print("  ✓ Saved")

        # Generate result
        duration = (datetime.now() - start_time).total_seconds()
        status = "success" if synthesis.quality_score >= 0.7 else "partial"

        result = ResearchResult(
            expert=expert,
            topic=topic,
            skill_slug=skill_slug,
            status=status,
            source_path=str(source_path),
            sources_found=len(scraped),
            sources_scraped=len([s for s in scraped if s.success]),
            word_count=synthesis.word_count,
            quality_score=synthesis.quality_score,
            issues=synthesis.issues,
            duration_seconds=duration,
            timestamp=datetime.now().isoformat(),
        )

        print(f"\n{'='*60}")
        print(f"COMPLETE: {status.upper()} in {duration:.1f}s")
        print(f"{'='*60}\n")

        return result

    def _generate_slug(self, expert: str, topic: str) -> str:
        """Generate skill slug from expert and topic."""
        # Handle special cases
        topic_clean = topic.lower()
        topic_clean = topic_clean.replace("$100m ", "").replace("$100m", "")
        topic_clean = topic_clean.replace(" ", "-")

        expert_clean = expert.lower().split()[-1]  # Last name

        return f"{expert_clean}-{topic_clean}"

    def batch_research(self, queue: list[dict]) -> list[ResearchResult]:
        """
        Execute batch research for multiple experts.

        Args:
            queue: List of {"expert": str, "topic": str} dicts

        Returns:
            List of ResearchResults
        """
        results = []

        print(f"\n{'#'*60}")
        print(f"BATCH RESEARCH: {len(queue)} items")
        print(f"{'#'*60}\n")

        for i, item in enumerate(queue, 1):
            print(f"\n[{i}/{len(queue)}] Processing: {item['expert']} - {item['topic']}")

            try:
                result = self.research(
                    item["expert"],
                    item["topic"],
                    item.get("skill_slug"),
                )
                results.append(result)
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(ResearchResult(
                    expert=item["expert"],
                    topic=item["topic"],
                    skill_slug=item.get("skill_slug", "unknown"),
                    status="failed",
                    source_path=None,
                    sources_found=0,
                    sources_scraped=0,
                    word_count=0,
                    quality_score=0,
                    issues=[str(e)],
                    duration_seconds=0,
                    timestamp=datetime.now().isoformat(),
                ))

        # Save batch report
        report_path = self.config.research.reports_dir / f"batch_{datetime.now():%Y%m%d_%H%M}.json"
        report_data = [asdict(r) for r in results]
        report_path.write_text(json.dumps(report_data, indent=2))

        # Print summary
        success = sum(1 for r in results if r.status == "success")
        partial = sum(1 for r in results if r.status == "partial")
        failed = sum(1 for r in results if r.status == "failed")

        print(f"\n{'#'*60}")
        print("BATCH COMPLETE")
        print(f"  Success: {success}")
        print(f"  Partial: {partial}")
        print(f"  Failed:  {failed}")
        print(f"  Report:  {report_path}")
        print(f"{'#'*60}\n")

        return results


# Default research queue
RESEARCH_QUEUE = [
    {"expert": "Russell Brunson", "topic": "DotCom Secrets", "skill_slug": "brunson-dotcom-secrets"},
    {"expert": "Russell Brunson", "topic": "Expert Secrets", "skill_slug": "brunson-expert-secrets"},
    {"expert": "Jeff Walker", "topic": "Product Launch Formula", "skill_slug": "walker-launch-formula"},
    {"expert": "Dan Kennedy", "topic": "No BS Direct Marketing", "skill_slug": "kennedy-direct-marketing"},
    {"expert": "Perry Marshall", "topic": "Ultimate Guide to Google Ads", "skill_slug": "marshall-google-ads"},
    {"expert": "Marty Neumeier", "topic": "The Brand Gap", "skill_slug": "neumeier-brand-gap"},
    {"expert": "Wes Bush", "topic": "Product-Led Growth", "skill_slug": "bush-product-led-growth"},
    {"expert": "Joe Pulizzi", "topic": "Content Inc", "skill_slug": "pulizzi-content-inc"},
]


def main():
    """CLI entry point."""
    agent = ResearchAgent()

    # Validate config
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for e in errors:
            print(f"  - {e}")
        print("\nPlease set up your .env file. See .env.example")
        sys.exit(1)

    if len(sys.argv) == 1 or sys.argv[1] == "--help":
        print(__doc__)
        print("\nResearch Queue:")
        for item in RESEARCH_QUEUE:
            print(f"  - {item['expert']}: {item['topic']}")
        sys.exit(0)

    if sys.argv[1] == "--batch":
        agent.batch_research(RESEARCH_QUEUE)

    elif sys.argv[1] == "--list":
        print("Research Queue:")
        for i, item in enumerate(RESEARCH_QUEUE, 1):
            print(f"  {i}. {item['expert']} - {item['topic']}")

    elif len(sys.argv) >= 3:
        expert = sys.argv[1]
        topic = sys.argv[2]
        skill_slug = sys.argv[3] if len(sys.argv) > 3 else None
        agent.research(expert, topic, skill_slug)

    else:
        print("Usage: python research_agent.py 'Expert Name' 'Topic'")
        print("       python research_agent.py --batch")
        sys.exit(1)


if __name__ == "__main__":
    main()
