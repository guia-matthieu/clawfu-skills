# MKTG Skills - Scripts

Outils d'automatisation pour la production de skills marketing.

## Scripts Disponibles

| Script | Usage | Output |
|--------|-------|--------|
| `youtube_extractor.py` | Pipeline YouTube complet | `sources/youtube/`, `sources/competencies/` |
| `research_agent.py` | Recherche web sur experts | `sources/books/` |
| `skill_generator.py` | Génération de skills | `skills/` |

---

# YouTube Pipeline

Pipeline complet pour extraire, enrichir et analyser des vidéos YouTube:
1. **Extract** - Récupère les transcripts via youtube-transcript-api
2. **Enrich** - Génère résumé, points clés, frameworks via LLM (OpenRouter)
3. **Competencies** - Extrait les compétences marketing actionnables
4. **Knowledge Base** - Sauvegarde les compétences dans `sources/competencies/extracted.json`

## Installation

```bash
cd VIBE_CODE_GUIA/MKTG_Skills/scripts
pip install -r requirements.txt

# Configure OpenRouter API (for enrichment)
# Set OPENROUTER_API_KEY environment variable with your key
```

## Commands

### Extract (Single Video)

```bash
# Basic extraction
python youtube_extractor.py extract "https://youtube.com/watch?v=VIDEO_ID"

# With metadata
python youtube_extractor.py extract "URL" \
  --channel ai-engineer \
  --title "Video Title" \
  --tags "marketing,strategy"

# Print to stdout
python youtube_extractor.py extract "URL" --print-only
```

### Process (Full Pipeline)

```bash
# Full pipeline: extract + enrich + competencies
python youtube_extractor.py process "URL" \
  --channel ai-engineer \
  --title "Video Title"

# Skip enrichment (just extract)
python youtube_extractor.py process "URL" -c channel --no-enrich

# Skip competency extraction
python youtube_extractor.py process "URL" -c channel --no-competencies
```

### Batch (Playlist)

```bash
# Extract from playlist
python youtube_extractor.py batch "https://youtube.com/playlist?list=PLxxx" \
  --channel ai-engineer \
  --max 10

# With enrichment
python youtube_extractor.py batch "PLAYLIST_URL" -c channel --enrich
```

### Queue Management

```bash
# Add video to queue
python youtube_extractor.py queue-add "URL" \
  --channel ai-engineer \
  --title "Video Title" \
  --priority high

# Show queue status
python youtube_extractor.py queue-list

# Process pending videos
python youtube_extractor.py queue-process --max 5 --enrich
```

## Output Locations

| Type | Location |
|------|----------|
| Transcripts | `sources/youtube/channels/{channel}/{video}.md` |
| Competencies | `sources/competencies/extracted.json` |
| Queue | `sources/youtube/queue.md` |

## Cost Estimates (OpenRouter)

| Operation | Model | Cost |
|-----------|-------|------|
| Enrichment | Gemini Flash | ~$0.01/video |
| Competency extraction | Gemini Flash | ~$0.005/video |
| **Total per video** | | **~$0.015** |
| Batch 50 videos | | ~$0.75 |

## Package Structure

```
scripts/
├── youtube_extractor.py    # CLI entry point
├── youtube/                # Package
│   ├── __init__.py
│   ├── models.py           # Pydantic models
│   ├── extractor.py        # Transcript extraction
│   ├── batch.py            # Playlist batch extraction
│   ├── enricher.py         # LLM enrichment
│   ├── competencies.py     # Competency extraction
│   ├── pipeline.py         # Full pipeline orchestration
│   └── queue.py            # Queue management
└── tests/
    └── youtube/            # Tests for each module
```

## Chaînes Prioritaires

| Chaîne | Slug | Focus |
|--------|------|-------|
| AI Engineer | `ai-engineer` | AI, skills, agents |
| Alex Hormozi | `alex-hormozi` | Offers, sales |
| My First Million | `my-first-million` | Business ideas |
| The Futur | `the-futur` | Branding, design |

## Workflow

1. **Add to queue** - `queue-add` videos to process
2. **Process batch** - `queue-process` runs full pipeline
3. **Review** - Check generated transcripts and competencies
4. **Create skills** - Use competencies to guide skill creation

---

# Research Agent

Automated research pipeline for collecting and synthesizing marketing expert knowledge.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH AGENT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   SEARCH     │ -> │   SCRAPE     │ -> │  SYNTHESIZE  │       │
│  │  DuckDuckGo  │    │   Direct     │    │  OpenRouter  │       │
│  │  (Brightdata)│    │ (Brightdata) │    │   Claude/    │       │
│  └──────────────┘    └──────────────┘    │   Gemini     │       │
│                                          └──────────────┘       │
│                              │                                   │
│                              v                                   │
│                      sources/books/                              │
│                      expert-topic.md                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Setup

```bash
cd VIBE_CODE_GUIA/MKTG_Skills/scripts

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp ../.env.example ../.env
# Edit .env and add your OPENROUTER_API_KEY
```

### 2. Get OpenRouter API Key

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Create an account if needed
3. Generate a new API key
4. Add to `.env` file

### 3. Run Research

```bash
# Single expert
python research_agent.py "Russell Brunson" "DotCom Secrets"

# Batch mode (all queued experts)
python research_agent.py --batch

# List queue
python research_agent.py --list
```

## Files

| File | Purpose |
|------|---------|
| `config.py` | Configuration management |
| `openrouter_client.py` | OpenRouter API client |
| `web_research.py` | Search and scraping |
| `synthesis.py` | Content synthesis |
| `research_agent.py` | Main pipeline orchestrator |

## Cost Estimates

Per expert research (~5 sources):

| Model | Usage | Cost |
|-------|-------|------|
| Gemini Flash | Search queries | ~$0.01 |
| Claude Sonnet | Synthesis (7 sections) | ~$0.15 |
| **Total** | | **~$0.20** |

Batch of 8 experts: ~$1.60

## Output Format

Generated source documents follow this structure:

```markdown
# Expert - Topic: Summary & Key Principles

> Source document for the skill-slug skill

## Background
[Expert bio and why this matters]

## Core Framework
[Main methodology with steps]

## Key Principles
[5+ numbered principles]

## Techniques & Tactics
[Specific actionable methods]

## Key Quotes
[3-5 memorable quotes]

## Common Mistakes to Avoid
[What people get wrong]

## Case Studies / Examples
[2-3 concrete examples]

## Sources
[URLs used for research]
```

## Research Queue

Default queue in `research_agent.py`:

| Expert | Topic | Slug |
|--------|-------|------|
| Russell Brunson | DotCom Secrets | brunson-dotcom-secrets |
| Russell Brunson | Expert Secrets | brunson-expert-secrets |
| Jeff Walker | Product Launch Formula | walker-launch-formula |
| Dan Kennedy | No BS Direct Marketing | kennedy-direct-marketing |
| Perry Marshall | Google Ads | marshall-google-ads |
| Marty Neumeier | The Brand Gap | neumeier-brand-gap |
| Wes Bush | Product-Led Growth | bush-product-led-growth |
| Joe Pulizzi | Content Inc | pulizzi-content-inc |

## Extending

### Add New Expert to Queue

Edit `RESEARCH_QUEUE` in `research_agent.py`:

```python
RESEARCH_QUEUE = [
    # ... existing ...
    {"expert": "New Expert", "topic": "Their Book", "skill_slug": "expert-book"},
]
```

### Custom Synthesis Template

Edit `SOURCE_TEMPLATE` in `synthesis.py` to modify output structure.

### Add Priority Domains

Edit `priority_domains` in `config.py` to prioritize certain sources.

## Troubleshooting

### "OPENROUTER_API_KEY not configured"

Add your API key to `.env` file in the project root.

### "No sources could be scraped"

- Check internet connection
- Try a different expert/topic
- Some sites may block scraping

### Low Quality Score

- Source content may be thin
- Try adding more priority domains
- Use `--enhance` flag to improve existing sources

## Next Steps

After research completes:

1. Review generated source in `sources/books/`
2. Use `/produce-skill` command to generate SKILL.md
3. Add skill to catalog
