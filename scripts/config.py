"""
Configuration for MKTG Skills Research Agent
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class OpenRouterConfig:
    """OpenRouter API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    base_url: str = "https://openrouter.ai/api/v1"
    referer: str = "https://guia.corsica"
    title: str = "MKTG Skills Research Agent"

    # Models par usage
    models: dict = field(default_factory=lambda: {
        "fast": "google/gemini-2.0-flash-001",        # Queries, classification
        "balanced": "anthropic/claude-sonnet-4",   # Synthesis, writing
        "deep": "google/gemini-2.5-pro-preview",          # Deep analysis
        "cheap": "google/gemini-2.0-flash-001",           # High volume tasks
    })

    # Limites
    max_tokens_default: int = 4000
    max_tokens_synthesis: int = 8000
    timeout: int = 120


@dataclass
class BrightdataConfig:
    """Brightdata Web Scraping configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("BRIGHTDATA_API_KEY", ""))

    # Sources prioritaires pour book summaries
    priority_domains: list = field(default_factory=lambda: [
        "fs.blog",
        "fourminutebooks.com",
        "samuelthomasdavies.com",
        "jamesclear.com",
        "nateliason.com",
        "dropdeadcopy.com",
        "gregfaxon.com",
        "copyblogger.com",
    ])

    # Domaines à éviter
    blocked_domains: list = field(default_factory=lambda: [
        "amazon.com",
        "goodreads.com",
        "audible.com",
        "scribd.com",
    ])


@dataclass
class ResearchConfig:
    """Research pipeline configuration."""
    # Paths
    sources_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "sources" / "books")
    skills_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "skills")
    reports_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "reports")

    # Research settings
    max_sources_per_expert: int = 5
    max_content_length: int = 50000  # chars per source
    min_content_length: int = 1000   # skip thin content

    # Quality thresholds
    min_principles: int = 5
    min_techniques: int = 3

    def __post_init__(self):
        """Ensure directories exist."""
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Main configuration container."""
    openrouter: OpenRouterConfig = field(default_factory=OpenRouterConfig)
    brightdata: BrightdataConfig = field(default_factory=BrightdataConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)

    def validate(self) -> list[str]:
        """Validate configuration, return list of errors."""
        errors = []
        if not self.openrouter.api_key:
            errors.append("OPENROUTER_API_KEY not set")
        return errors


# Global config instance
config = Config()
