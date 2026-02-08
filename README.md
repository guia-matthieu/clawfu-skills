# ClawFu Skills

**159 expert marketing methodologies for AI.** Free. Open source. MIT licensed.

Dunford on positioning. Schwartz on copywriting. Cialdini on persuasion. Ogilvy on advertising. Hormozi on offers. Voss on negotiation. And 150+ more — encoded as structured AI instructions.

## Install

### Claude Desktop / Claude Code (MCP)

```bash
npx @clawfu/mcp-skills
```

### Cursor / Windsurf

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "clawfu": {
      "command": "npx",
      "args": ["@clawfu/mcp-skills"]
    }
  }
}
```

### Git Clone

```bash
git clone https://github.com/guia-matthieu/clawfu-skills.git
```

### Individual Skills

Browse and download individual skills at [clawfu.com/skills](https://clawfu.com/skills/).

## Catalog

159 skills across 28 categories:

| Category | Skills | Examples |
|----------|--------|----------|
| Content | 22 | copywriting (Schwartz), storytelling (StoryBrand), persuasion (Cialdini) |
| Strategy | 17 | positioning (Dunford), competitive analysis, JTBD, six thinking hats |
| Audio | 16 | podcast production, sonic branding, sound design |
| Automation | 10 | workflow builder, zapier architect, n8n orchestrator |
| Validation | 8 | mom test, customer discovery, landing page test |
| RevOps | 8 | pipeline analyzer, forecast validator, pricing strategy |
| Sales | 6 | sales pitch (Dunford), SPIN selling, MEDDIC, negotiation (Voss) |
| SDR Automation | 6 | lead enrichment, outreach sequencer, ICP scoring |
| Customer Success | 6 | health score, churn predictor, onboarding |
| Video | 5 | AI storyboard, video concept, editing |
| SEO Tools | 5 | keyword research, content optimization, technical audit |
| Legal | 5 | contract review, GDPR compliance, terms generator |
| HR-Ops | 5 | resume screener, onboarding guide, job description |
| Social | 4 | community building, social listening, content calendar |
| Growth | 4 | growth loops (Reforge), PLG, referral systems |
| Crisis | 4 | crisis detector, response coordinator, post-mortem |
| Analytics | 4 | A/B testing, cohort analysis, funnel analyzer |
| Thinking | 3 | first principles, inversion, pre-mortem |
| Startup | 3 | pitch deck, lean canvas, fundraising |
| Product | 3 | PRD generator, feature prioritization, roadmap |
| Leadership | 3 | meeting facilitator, decision framework, feedback |
| Funnels | 3 | funnel architect, conversion optimizer, lead scoring |
| Email | 2 | email sequence, newsletter strategy |
| Branding | 2 | brand voice, visual identity |
| Acquisition | 2 | ad spend optimizer, Google Ads expert |
| Meta | 1 | skill orchestrator (multi-skill workflows) |
| DevOps | 1 | CI/CD pipeline |
| AI Design | 1 | image-to-3D pipeline |

## Skill Format

Each skill is a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: positioning-expert
description: Apply April Dunford's positioning methodology
mode: centaur
---

# Positioning Expert

> Position products using April Dunford's "Obviously Awesome" framework.

## When to Use This Skill
...

## What Claude Does vs What You Decide
...
```

### Quality Standards (v2)

All skills include:

- **Expert attribution** — named source methodology, not generic checklists
- **"What Claude Does vs What You Decide"** — clear human/AI division
- **"Skill Boundaries"** — known limitations and edge cases
- **Mode tag** — `centaur` (divided work), `cyborg` (integrated), or `both`

## Scripts

```bash
# Validate v2 compliance
python scripts/validate_v2.py

# Package skills
python scripts/package_skills.py
```

## License

MIT — see [LICENSE](LICENSE).

## Built by

[Guia](https://guia.fr) — AI visibility consulting.

Browse all skills at [clawfu.com](https://clawfu.com).
