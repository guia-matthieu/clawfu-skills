# AI Design Workflows - Deep Research (January 2026)

> Sources: Perplexity Pro (75+ sources), Gemini Pro
> Research Date: 2026-01-28

## Executive Summary

AI design tools have matured into production-ready workflows enabling rapid asset creation from concept to deployment. This research synthesizes expert methodologies and tool comparisons across five key domains.

---

## 1. Image-to-3D Pipeline

### Leading Tools (2026)

| Tool | Strengths | Best For |
|------|-----------|----------|
| **Tencent Hunyuan3D** | Open source, high fidelity, texture generation | Production 3D assets |
| **Rodin Gen-1** | Fastest generation, game-ready topology | Game characters |
| **Tripo AI** | Best UX, automatic rigging | Quick prototypes |
| **CSM (Common Sense Machines)** | Multi-view consistency | Complex objects |
| **Meshy** | Texture-first approach | Stylized assets |

### Standard Workflow

```
1. Concept Image Generation (Midjourney/DALL-E)
   ↓
2. Image Cleanup & Background Removal
   ↓
3. Multi-view Generation (if needed)
   ↓
4. 3D Model Generation (Hunyuan3D/Tripo)
   ↓
5. Mesh Optimization (reduce poly count)
   ↓
6. Texture Refinement
   ↓
7. Rigging (Mixamo for characters)
   ↓
8. Export (GLB/FBX for web/game engines)
```

### Key Insights

- **Hunyuan3D** produces best texture quality but requires more cleanup
- **Mixamo** remains the fastest path for character rigging (free, automatic)
- Multi-view consistency is the main challenge - solved by Character Sheet approach
- Typical turnaround: 2D concept → rigged 3D character in ~30 minutes

---

## 2. AI UI Generation

### Tool Landscape

| Tool | Technology | Output Quality | Integration |
|------|------------|----------------|-------------|
| **v0.dev** (Vercel) | GPT-4 + shadcn/ui | Production-ready React | Direct to Next.js |
| **Galileo AI** | Custom model | High-fidelity mockups | Figma export |
| **Claude Artifacts** | Claude 3+ | Functional prototypes | Copy-paste |
| **Gemini Pro** | Gemini 1.5 | Rapid iteration | Manual export |

### v0.dev Best Practices

1. **Start with clear constraints**: "shadcn/ui components only, Tailwind CSS"
2. **Provide design tokens**: Share color palette, typography scale upfront
3. **Iterate in conversation**: Refine specific sections, not full regeneration
4. **Export early**: Move to local dev for fine-tuning

### Design System Integration

```
Design Tokens (Figma/JSON)
        ↓
AI Prompt with Constraints
        ↓
Generated Component
        ↓
Manual Integration & Polish
        ↓
Production Component Library
```

### Gotcha
AI-generated UI tends toward generic aesthetics. Always apply brand-specific refinements post-generation.

---

## 3. Character Design Consistency

### The Multi-Image Problem

Generating the same character across multiple images/angles remains AI's biggest challenge. Three proven solutions:

### Solution 1: Character Sheet Method

```
Prompt: "Character sheet, [character description],
multiple poses, front view, side view, back view,
3/4 view, consistent design, white background,
reference sheet style"
```

Best tool: Midjourney v6+ with `--sref` (style reference)

### Solution 2: JSON Prompting (DALL-E 3)

```json
{
  "character": {
    "name": "Luna",
    "hair": "silver, shoulder-length, straight",
    "eyes": "amber, almond-shaped",
    "skin": "warm beige",
    "outfit": "navy blazer, white shirt, gold buttons"
  }
}
```

Embed JSON in prompt for parameter consistency.

### Solution 3: gen_ID (OpenAI)

New feature (late 2025) allowing character ID persistence across generations. Still in limited rollout.

### Tools for Consistency

- **Nano Banana**: Purpose-built for character design (used by Dilum Sanjaya)
- **Midjourney --sref**: Style reference from existing image
- **Stable Diffusion LoRA**: Train on specific character (requires 10-20 images)

---

## 4. Vibe Design Methodology

### Origin & Philosophy

Coined by **Andrej Karpathy** (2024) for code, adapted to design by practitioners like **Pieter Levels** and **Dilum Sanjaya**.

> "You fully give in to the vibes, embrace exponentials, and forget that the code even exists." — Karpathy

### Applied to Design

**Core Principles:**
1. Speed over perfection - ship fast, iterate visually
2. Let AI handle repetition - focus on creative direction
3. Embrace happy accidents - AI often suggests unexpected solutions
4. Stack tools iteratively - each tool adds a layer

### Vibe Design Workflow (Pieter Levels style)

```
1. Quick sketch/screenshot of idea
2. → v0.dev for initial UI
3. → Iterate with "make it more [adjective]"
4. → Polish specific sections manually
5. → Ship within hours, not days
```

### When NOT to Use Vibe Design

- Brand-critical assets requiring exact specifications
- Regulated industries (healthcare, finance UI)
- Design systems requiring pixel-perfect consistency

---

## 5. End-to-End Workflows

### Workflow A: Marketing Campaign Assets

```
Brief/Concept
    ↓
Midjourney: Key visual generation (hero image)
    ↓
DALL-E 3: Variations for different formats
    ↓
Canva/Figma: Layout adaptation (social, web, print)
    ↓
Runway: Motion versions (video ads)
    ↓
Delivery
```

**Time: 2-4 hours** (vs 2-3 days traditional)

### Workflow B: Game Character (Dilum Sanjaya Method)

```
1. Nano Banana: Generate character concept
2. Hunyuan3D: Convert to 3D model
3. Mixamo: Auto-rig for animation
4. Unity/Three.js: Integrate in engine
5. Gemini Pro: Generate selection screen UI
```

**Time: ~1 hour** for complete animated character

### Workflow C: Landing Page (Indie Hacker Style)

```
1. v0.dev: Generate full page structure
2. Claude: Refine copy and interactions
3. Midjourney: Hero images
4. Vercel: One-click deploy
```

**Time: 30 minutes** to live landing page

---

## Expert Practitioners

### Dilum Sanjaya (@DilumSanjaya)
- Specialty: Game UI, character design, vibe coding
- Stack: Nano Banana → Hunyuan3D → Mixamo → Three.js
- Notable: Game character selection screens in under 1 hour

### Pieter Levels (@levelsio)
- Specialty: Rapid MVP shipping, AI-first products
- Stack: v0.dev → Claude → minimal manual code
- Philosophy: "Ship daily, let users decide"

### Adetomiwa Ogundiran
- Specialty: AI art direction, brand consistency
- Focus: Enterprise-grade AI design workflows

### Theo Browne (@theo)
- Specialty: AI dev tools evaluation
- Coverage: v0.dev deep dives, tool comparisons

---

## Tool Selection Matrix

| Use Case | Primary Tool | Backup |
|----------|--------------|--------|
| 2D → 3D conversion | Hunyuan3D | Tripo AI |
| UI prototyping | v0.dev | Galileo AI |
| Character concepts | Midjourney v6 | Nano Banana |
| Character rigging | Mixamo | Blender (manual) |
| Motion/video | Runway Gen-3 | Kling |
| Copy/UX writing | Claude | GPT-4 |

---

## Learning Resources

### Official Documentation
- [v0.dev docs](https://v0.dev/docs)
- [Hunyuan3D GitHub](https://github.com/tencent/Hunyuan3D)
- [Mixamo](https://www.mixamo.com)

### Tutorials (YouTube)
- Dilum Sanjaya: Character to 3D workflows
- Theo Browne (t3.gg): v0.dev masterclass
- Pieter Levels: Indie hacking with AI

### Communities
- X/Twitter: #vibedesign, #aidesign
- Discord: Midjourney, Vercel

---

## Skill Development Priority

Based on research, recommended skill creation order:

1. **`image-to-3d-pipeline/`** - Most requested, clearest workflow
2. **`ai-ui-generation/`** - Highest daily utility for web work
3. **`vibe-coding-design/`** - Methodology skill (mindset + process)
4. **`character-design-ai/`** - Niche but complete workflow exists
5. **`ai-asset-workflow/`** - Meta-skill combining all above

---

*Research compiled: 2026-01-28*
*Next: Create structured skill for image-to-3d-pipeline*
