# ClawFu Skills

**175 expert marketing methodologies for AI agents.** Free. Open source. MIT licensed.

Dunford on positioning. Schwartz on copywriting. Cialdini on persuasion. Ogilvy on advertising. Hormozi on offers. Voss on negotiation. And 160+ more — encoded as structured, agent-readable instructions.

Skills compound. Prompts don't.

## Install

### Claude Desktop / Claude Code / Copilot (MCP)

```bash
npx @clawfu/mcp-skills
```

### Cursor / Windsurf

Add to your MCP config:

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

### Clone as Claude Code skills directory

```bash
git clone https://github.com/guia-matthieu/clawfu-skills.git
# Then use --add-dir or copy to ~/.claude/skills/
```

### Browse & download individual skills

[clawfu.com/skills](https://clawfu.com/skills/)

## Catalog

175 skills across 28 categories:

| Category | Count | Highlights |
|----------|-------|------------|
| Content | 24 | copywriting (Schwartz), storytelling (StoryBrand), persuasion (Cialdini), SEO writing |
| Strategy | 17 | positioning (Dunford), competitive analysis (Porter), JTBD, cognitive biases |
| Audio | 16 | podcast production (Ira Glass), sonic branding, sound design (Murch) |
| Automation | 10 | workflow builder, data visualizer, report generator |
| SEO Tools | 8 | schema markup, lighthouse audit, link checker, keyword clustering |
| RevOps | 8 | pipeline forecasting, forecast scenarios, revenue attribution |
| Validation | 8 | mom test, customer discovery, lean canvas, pricing validation |
| Sales | 6 | sales narrative (Dunford), SPIN selling, MEDDIC, negotiation (Voss) |
| SDR Automation | 6 | lead enrichment, outbound sequencer, ICP scoring |
| Customer Success | 6 | health score, churn predictor, onboarding orchestrator |
| Video | 5 | AI storyboard, video concept, voice design, video QA |
| AI Design | 5 | image-to-3D, web design director, minimalist image director |
| HR-Ops | 5 | resume screener, onboarding guide, interview scheduler |
| Social | 5 | social listening, sentiment analyzer, hashtag analyzer |
| Legal | 5 | contract review, GDPR compliance, terms analyzer |
| Branding | 4 | brand strategy (Neumeier), brand voice, naming |
| Meta | 4 | skill orchestrator, RLM (large codebase), context engineering |
| Crisis | 4 | crisis detector, response coordinator, reputation recovery |
| Growth | 4 | growth loops (Reforge), PLG (Wes Bush), referral systems |
| Thinking | 4 | first principles, inversion, pre-mortem, second-order thinking |
| Analytics | 4 | A/B testing, cohort analysis, funnel analyzer |
| Product | 3 | product discovery (Cagan), design sprint (GV), Shape Up |
| Leadership | 3 | high-output management (Grove), radical candor, one-on-ones |
| Funnels | 3 | DotCom Secrets (Brunson), launch formula, nurture sequences |
| Startup | 3 | YC pitch deck, startup metrics, fundraising narrative |
| Acquisition | 2 | ad spend optimizer, Google Ads (Perry Marshall) |
| Email | 2 | email writing, deliverability checker |
| DevOps | 1 | DNS zonefile config |

## How it works

Each skill is a `SKILL.md` file following the [Agent Skills](https://agentskills.io) open standard:

```yaml
---
name: positioning
description: "Master product positioning using April Dunford's 5+1 framework. Use when: launching a new product; customers don't 'get it'; facing wrong competitor comparisons; pivoting to a new market"
---
```

The description tells agents **when** to use the skill. The body provides the full methodology — frameworks, steps, examples, and output format.

Skills work across **Claude, ChatGPT, Copilot, Cursor, Windsurf** — any tool that supports the Agent Skills standard or MCP.

## Quality

All skills are reviewed against [Anthropic's skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

- **Expert attribution** — named source methodology (Dunford, Schwartz, Cialdini...), not generic checklists
- **Agent-first descriptions** — "Use when:" trigger terms for reliable discovery
- **Concise** — methodology only, no explanations Claude already knows
- **Output contracts** — declared output format for composability between skills

Automated quality checks run on every PR via [Tessl Skill Review](https://github.com/tesslio/skill-review).

## Security

Skills are **context, not code**. They contain markdown instructions only — no executable scripts, no network calls, no file system access.

- 100% open source and auditable
- No community uploads or marketplace — curated library only
- No hidden HTML, comments, or obfuscated content
- MIT licensed

## Contributing

Found an issue? Want to improve a skill? PRs welcome.

Quality bar: every modified `SKILL.md` is automatically reviewed by the Tessl GitHub Action. Aim for 80%+ score.

## License

MIT — see [LICENSE](LICENSE).

## Links

- [clawfu.com](https://clawfu.com) — browse and download skills
- [@clawfu/mcp-skills](https://www.npmjs.com/package/@clawfu/mcp-skills) — npm package (MCP server)
- [Guia](https://guia.fr) — AI systems consulting

Built by [Matthieu Credou](https://credou.bzh) at [Guia](https://guia.fr).
