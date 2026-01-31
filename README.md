# ClawFu Skills

> "I know ClawFu" - Download marketing skills directly into Claude.

Like Neo downloading Kung Fu in The Matrix, ClawFu lets you instantly acquire expert marketing capabilities.

## Stats

- **159 skills** across 20 domains
- **25+ expert methodologies** (Dunford, Schwartz, Ogilvy, Cialdini, Hormozi)
- **50+ templates** ready to use
- **25 automation scripts**

## Domains

| Domain | Skills | Examples |
|--------|--------|----------|
| Strategy | 16 | positioning, competitive-analysis, jobs-to-be-done |
| Content | 18 | copywriting-schwartz, storytelling-storybrand |
| Audio | 16 | podcast-production, sonic-branding |
| Video | 5 | ai-video-concept, ai-storyboard |
| Sales | 7 | sales-pitch-dunford, spin-selling, meddic-scorecard |
| Validation | 8 | mom-test, customer-discovery |
| Legal | 5 | contract-review, gdpr-compliance |
| HR-Ops | 5 | resume-screener, onboarding-guide |
| Crisis | 4 | crisis-detector, response-coordinator |
| RevOps | 3 | pipeline-analyzer, forecast-validator |
| Customer Success | 3 | health-score-analyzer, churn-predictor |
| SDR Automation | 3 | lead-enrichment, outreach-sequencer |
| + 8 more domains | ... | ... |

## Usage

Each skill is a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: positioning-expert
description: Apply April Dunford's positioning methodology
mode: centaur
---

# Positioning Expert

> Helps you position products using April Dunford's "Obviously Awesome" framework.

## When to Use This Skill
...
```

### In Claude Code

```bash
# Copy a skill to your project
cp skills/strategy/positioning/SKILL.md .claude/skills/

# Or reference directly
claude --skill skills/strategy/positioning/SKILL.md
```

### In Claude.ai

Paste the skill content at the start of your conversation.

## Skill Quality (v2 Format)

All skills include:

- **"What Claude Does vs What You Decide"** - Clear human/AI division
- **"Skill Boundaries"** - Known limitations
- **Mode tag** - `centaur` (divided work), `cyborg` (integrated), or `both`

## Scripts

Validation and packaging tools:

```bash
# Validate v2 compliance
python scripts/validate_v2.py

# Package skills as .skill files
python scripts/package_skills.py
```

## License

MIT

## Author

[GUIA](https://guia.fr) - Marketing AI Agency
