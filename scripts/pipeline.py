"""
Complete Skill Production Pipeline
Research → Synthesize → Generate Skill → Update Catalog

Usage:
    python pipeline.py "Russell Brunson" "DotCom Secrets" --category funnels
    python pipeline.py --batch
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from config import config
from research_agent import ResearchAgent
from skill_generator import SkillGenerator


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""
    expert: str
    topic: str
    skill_slug: str
    category: str
    status: str
    source_path: str
    skill_path: str
    research_duration: float
    generation_duration: float
    total_duration: float
    timestamp: str


class SkillPipeline:
    """End-to-end skill production pipeline."""

    def __init__(self):
        self.researcher = ResearchAgent()
        self.generator = SkillGenerator()
        self.config = config

    def produce(
        self,
        expert: str,
        topic: str,
        category: str = "content",
        skill_slug: str = None,
    ) -> PipelineResult:
        """
        Complete pipeline: research → synthesize → generate skill.

        Args:
            expert: Expert name
            topic: Topic/book name
            category: Skill category
            skill_slug: Optional custom slug

        Returns:
            PipelineResult with all metadata
        """
        start_time = datetime.now()

        print(f"\n{'#'*60}")
        print("SKILL PRODUCTION PIPELINE")
        print(f"Expert: {expert}")
        print(f"Topic: {topic}")
        print(f"Category: {category}")
        print(f"{'#'*60}\n")

        # Step 1: Research
        print("=" * 40)
        print("PHASE 1: RESEARCH")
        print("=" * 40)

        research_start = datetime.now()
        research_result = self.researcher.research(expert, topic, skill_slug)
        research_duration = (datetime.now() - research_start).total_seconds()

        if research_result.status == "failed":
            return PipelineResult(
                expert=expert,
                topic=topic,
                skill_slug=research_result.skill_slug,
                category=category,
                status="failed_research",
                source_path="",
                skill_path="",
                research_duration=research_duration,
                generation_duration=0,
                total_duration=research_duration,
                timestamp=datetime.now().isoformat(),
            )

        # Step 2: Generate Skill
        print("\n" + "=" * 40)
        print("PHASE 2: SKILL GENERATION")
        print("=" * 40)

        gen_start = datetime.now()
        source_path = Path(research_result.source_path)
        skill_result = self.generator.generate(
            source_path,
            category,
            research_result.skill_slug,
        )
        gen_duration = (datetime.now() - gen_start).total_seconds()

        total_duration = (datetime.now() - start_time).total_seconds()

        # Step 3: Summary
        print("\n" + "#" * 60)
        print("PIPELINE COMPLETE")
        print("#" * 60)
        print(f"  Source: {research_result.source_path}")
        print(f"  Skill:  {skill_result.skill_path}")
        print(f"  Research: {research_duration:.1f}s")
        print(f"  Generation: {gen_duration:.1f}s")
        print(f"  Total: {total_duration:.1f}s")
        print("#" * 60 + "\n")

        return PipelineResult(
            expert=expert,
            topic=topic,
            skill_slug=research_result.skill_slug,
            category=category,
            status="success",
            source_path=str(research_result.source_path),
            skill_path=str(skill_result.skill_path),
            research_duration=research_duration,
            generation_duration=gen_duration,
            total_duration=total_duration,
            timestamp=datetime.now().isoformat(),
        )

    def batch_produce(self, queue: list[dict]) -> list[PipelineResult]:
        """Execute batch pipeline for multiple experts."""
        results = []

        print(f"\n{'#'*60}")
        print(f"BATCH PIPELINE: {len(queue)} skills")
        print(f"{'#'*60}\n")

        for i, item in enumerate(queue, 1):
            print(f"\n[{i}/{len(queue)}] {item['expert']} - {item['topic']}")

            try:
                result = self.produce(
                    item["expert"],
                    item["topic"],
                    item.get("category", "content"),
                    item.get("skill_slug"),
                )
                results.append(result)
            except Exception as e:
                print(f"ERROR: {e}")
                results.append(PipelineResult(
                    expert=item["expert"],
                    topic=item["topic"],
                    skill_slug=item.get("skill_slug", "unknown"),
                    category=item.get("category", "content"),
                    status="error",
                    source_path="",
                    skill_path="",
                    research_duration=0,
                    generation_duration=0,
                    total_duration=0,
                    timestamp=datetime.now().isoformat(),
                ))

        # Save batch report
        report_path = config.research.reports_dir / f"pipeline_{datetime.now():%Y%m%d_%H%M}.json"
        report_data = [asdict(r) for r in results]
        report_path.write_text(json.dumps(report_data, indent=2))

        # Summary
        success = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if "fail" in r.status or r.status == "error")

        print(f"\n{'#'*60}")
        print("BATCH COMPLETE")
        print(f"  Success: {success}/{len(queue)}")
        print(f"  Failed:  {failed}/{len(queue)}")
        print(f"  Report:  {report_path}")
        print(f"{'#'*60}\n")

        return results


# Extended queue with categories
PIPELINE_QUEUE = [
    {"expert": "Russell Brunson", "topic": "DotCom Secrets", "category": "funnels", "skill_slug": "dotcom-secrets"},
    {"expert": "Russell Brunson", "topic": "Expert Secrets", "category": "funnels", "skill_slug": "expert-secrets"},
    {"expert": "Jeff Walker", "topic": "Product Launch Formula", "category": "funnels", "skill_slug": "launch-formula"},
    {"expert": "Dan Kennedy", "topic": "No BS Direct Marketing", "category": "content", "skill_slug": "kennedy-direct"},
    {"expert": "Perry Marshall", "topic": "Ultimate Guide to Google Ads", "category": "acquisition", "skill_slug": "google-ads-marshall"},
    {"expert": "Marty Neumeier", "topic": "The Brand Gap", "category": "branding", "skill_slug": "brand-gap"},
    {"expert": "Wes Bush", "topic": "Product-Led Growth", "category": "strategy", "skill_slug": "product-led-growth"},
    {"expert": "Joe Pulizzi", "topic": "Content Inc", "category": "content", "skill_slug": "content-inc"},
]


def main():
    """CLI entry point."""
    pipeline = SkillPipeline()

    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print(__doc__)
        print("\nQueue:")
        for item in PIPELINE_QUEUE:
            print(f"  - {item['expert']}: {item['topic']} ({item['category']})")
        sys.exit(0)

    if sys.argv[1] == "--batch":
        pipeline.batch_produce(PIPELINE_QUEUE)

    elif len(sys.argv) >= 3:
        expert = sys.argv[1]
        topic = sys.argv[2]

        category = "content"
        if "--category" in sys.argv:
            idx = sys.argv.index("--category")
            if idx + 1 < len(sys.argv):
                category = sys.argv[idx + 1]

        pipeline.produce(expert, topic, category)

    else:
        print("Usage: python pipeline.py 'Expert' 'Topic' --category <category>")
        print("       python pipeline.py --batch")
        sys.exit(1)


if __name__ == "__main__":
    main()
