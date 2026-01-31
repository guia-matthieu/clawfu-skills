# MKTG Skills Library

Premium marketing skills library for Claude, based on expert methodologies.

**94 Skills | 17 Categories | Anthropic-Compatible Format**

---

## Quick Start

All skills have YAML frontmatter compatible with Claude Code:

```yaml
---
name: skill-name
description: "Trigger description explaining when to use this skill..."
---
```

### Using Skills

**In Claude Code:** Skills auto-trigger based on matching user requests.

**In Claude Desktop:** Copy SKILL.md content to "Project Instructions".

---

## Categories

| Category | Skills | Focus Area |
|----------|--------|------------|
| **strategy** | 16 | Positioning, pricing, competitive analysis |
| **content** | 18 | Copywriting, storytelling, persuasion |
| **audio** | 16 | Podcast, voice, sound design |
| **video** | 5 | AI video production |
| **validation** | 8 | Customer discovery, interviews |
| **sales** | 4 | Sales methodologies |
| **thinking** | 3 | Decision frameworks |
| **startup** | 3 | Pitch decks, metrics |
| **product** | 3 | Discovery, sprints |
| **leadership** | 3 | Management |
| **funnels** | 2 | Launch, nurture |
| **growth** | 2 | PLG, loops |
| **branding** | 1 | Brand strategy |
| **acquisition** | 1 | Google Ads |
| **meta** | 1 | Skill orchestration |
| **devops** | 1 | DNS configuration |
| **ai-design** | 1 | Image to 3D |

---

## Skills with Automation Scripts

These skills include Python CLI tools in their `scripts/` directory:

| Skill | Script | Use Case |
|-------|--------|----------|
| `startup-metrics` | Unit economics calculator | LTV, CAC, payback |
| `pricing-validation` | Van Westendorp PSM | Price range discovery |
| `competitive-analysis` | Five Forces analysis | Industry assessment |
| `customer-discovery` | Interview tracker | Validation scorecard |
| `product-led-growth` | PQL scorer | Churn risk assessment |

### Running Scripts

```bash
# Example: Calculate unit economics
cd skills/startup/startup-metrics/scripts
pip install -r requirements.txt
python main.py unit-economics 50000 100 500 --churn 0.05

# Example: Run Five Forces analysis
cd skills/strategy/competitive-analysis/scripts
python main.py five-forces --interactive
```

---

## Premium Skills (High Value)

Top skills for sale or premium access:

| Skill | Price Target | Value Proposition |
|-------|--------------|-------------------|
| `grand-slam-offers` | $49 | Hormozi offer creation framework |
| `copywriting-schwartz` | $39 | Breakthrough Advertising levels |
| `startup-metrics` | $39 | A16Z/YC metrics + calculator |
| `pricing-validation` | $39 | Van Westendorp + Gabor-Granger |
| `competitive-analysis` | $29 | Porter's Five Forces + profiler |
| `customer-discovery` | $29 | Steve Blank methodology + tracker |

---

## Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Main skill file (with YAML frontmatter)
├── scripts/          # Optional Python automation
│   ├── main.py
│   └── requirements.txt
└── references/       # Optional supplementary docs
```

### SKILL.md Template

```markdown
---
name: skill-name
description: "When to use this skill..."
---

# Skill Title

> One-line expert source tagline

## When to Use This Skill
- Scenario 1
- Scenario 2

## Methodology Foundation
| Aspect | Details |
|--------|---------|
| Source | Expert/Book |

## Instructions
...

## Examples
...

## References
...
```

---

## Contributing

To add or improve skills:

1. Follow the template in `templates/skill-template-v2.md`
2. Include YAML frontmatter with name and description
3. Reference expert sources
4. Add concrete examples

---

## License

MKTG Skills is proprietary. Contact for licensing.

---

*Last updated: 2026-01-30*
