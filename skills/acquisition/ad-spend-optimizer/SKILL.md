---
name: ad-spend-optimizer
description: "Analyze paid advertising performance across channels and recommend budget reallocation to maximize ROAS and minimize CAC. Use when: planning quarterly ad budget allocation, diagnosing underperforming ad channels, deciding whether to scale spend on a channel, calculating marginal ROI across Google Ads, Meta, LinkedIn, or TikTok, rebalancing media mix after performance shifts, or setting up a test-and-scale framework for new channels."
license: MIT
metadata:
  author: ClawFu
  version: 1.1.0
  mcp-server: "@clawfu/mcp-skills"
---

# Ad Spend Optimizer

> Analyze paid advertising performance across channels and recommend budget reallocation to maximize ROAS and minimize CAC.

## When to Use This Skill

- **Quarterly budget planning** — reallocate spend based on performance data
- **Channel mix optimization** — find the right balance across platforms
- **Performance troubleshooting** — diagnose why CAC is rising or ROAS declining
- **Scaling decisions** — determine if a channel has headroom to scale
- **New channel testing** — structure test budgets with clear success criteria

## Methodology Foundation

| Aspect | Details |
|--------|---------|
| **Source** | Marginal ROI optimization + portfolio theory for marketing |
| **Core Principle** | Allocate each dollar where the marginal return is highest — shift spend from diminishing-returns channels to underspent ones |
| **Framework** | 70/20/10 — 70% proven channels, 20% optimization tests, 10% new channel experiments |

## What Claude Does vs What You Decide

| Claude Does | You Decide |
|-------------|------------|
| Calculates ROAS, CAC, and CPL per channel and campaign | Total budget constraints |
| Identifies diminishing returns and reallocation opportunities | Risk tolerance for new channels |
| Models projected outcomes for different allocation scenarios | Business priorities and brand considerations |
| Creates monitoring dashboards and alert thresholds | Platform selection and creative direction |

## Instructions

### Step 1: Audit Current Performance

Collect these metrics per channel and campaign:

| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| **ROAS** | Revenue ÷ Ad Spend | >3:1 for most B2B/B2C |
| **CAC** | Ad Spend ÷ New Customers | <LTV ÷ 3 |
| **CPL** | Ad Spend ÷ Leads | Varies by industry |
| **CTR** | Clicks ÷ Impressions | >1% search, >0.5% social |
| **Conv Rate** | Conversions ÷ Clicks | >2% landing pages |

**Validation checkpoint:** If data is missing for any channel, flag it — incomplete data leads to wrong reallocations.

### Step 2: Attribution Analysis

Choose the model that matches the business:

| Model | Best For | Trade-off |
|-------|----------|-----------|
| Last Click | Direct response, short cycles | Ignores awareness |
| First Click | Awareness campaigns | Ignores conversion assist |
| Linear | Balanced multi-touch view | Dilutes signal |
| Time Decay | Shorter sales cycles | Biases toward bottom-funnel |
| Position-Based | Balanced with emphasis | May miss mid-funnel |
| Data-Driven | Sophisticated, enough data | Requires volume |

### Step 3: Calculate Marginal ROI

For each channel, answer: **Where does the next $1 produce the most return?**

| Signal | Meaning | Action |
|--------|---------|--------|
| CAC well below target | Headroom to scale | Increase spend 50%, monitor weekly |
| CAC at target | Optimized | Maintain, test creative |
| CAC above target | Diminishing returns | Reduce spend, reallocate |
| Low volume, good CAC | Underinvested | Scale cautiously (2x) |
| High volume, rising CAC | Hitting ceiling | Cap spend, diversify |

### Step 4: Model Reallocation Scenarios

Build 3 scenarios (conservative, moderate, aggressive) showing projected leads, CAC, and ROAS at each budget level. Include:

- **Per-channel breakdowns** with expected performance
- **Warning thresholds** — CAC levels that trigger spend cuts
- **Implementation timeline** — weekly changes, not all at once

### Step 5: Implement and Monitor

**Weekly monitoring checklist:**
- [ ] Spend pacing vs. plan
- [ ] CAC by channel vs. target
- [ ] Lead volume vs. forecast
- [ ] Any channel crossing warning threshold?

**Scaling rule:** If CAC stays 15%+ below target for 2 consecutive weeks, increase spend by 25%. If CAC exceeds target for 2 weeks, reduce by 25%.

## Examples

### Example: B2B SaaS Budget Reallocation

**Input:** $100K/month — Google ($50K), Meta ($30K), LinkedIn ($15K), Other ($5K). Target: $200 CAC, 500 leads/month. Current: 395 leads, $253 CAC.

**Diagnosis:**
- Google Display ($15K → 30 leads, $500 CAC) — cut entirely
- Meta Lookalike ($15K → 85 leads, $176 CAC) — star performer, scale
- LinkedIn Lead Gen ($5K → 10 leads, $500 CAC) — cut

**Proposed reallocation:**

| Channel | Current | Proposed | Expected CAC |
|---------|---------|----------|-------------|
| Google Ads | $50K | $35K | $206 |
| Meta | $30K | $50K | $196 |
| LinkedIn | $15K | $8K | $286 |
| Testing | $5K | $7K | Variable |

**Projected result:** 473 leads (+20%), $211 CAC (-17%).

## Skill Boundaries

### What This Skill Does Well
- Analyzing multi-channel ad performance from provided data
- Recommending budget shifts based on marginal ROI
- Modeling reallocation scenarios with projected outcomes
- Creating monitoring frameworks with alert thresholds

### What This Skill Cannot Do
- Access ad platform accounts or pull live data
- Make real-time bid adjustments or campaign changes
- Evaluate creative quality (headlines, images, video)
- Account for brand lift or offline conversion effects

## References

- Google Ads Optimization Guide
- Meta Business Suite Best Practices
- LinkedIn Marketing Solutions
- Common Thread Collective — ad spend allocation methodology

## Related Skills

- `google-ads-expert` — Google-specific campaign optimization
- `aarrr-metrics` — Full funnel view beyond paid acquisition
- `growth-loops` — Sustainable growth beyond paid channels
