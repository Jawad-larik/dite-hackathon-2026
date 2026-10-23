# Rule: Anti-AI Slop & Breathtaking UI Guidelines

## Philosophy
Judges review dozens of projects in a few minutes. If a project looks like a generic AI template—with purple/violet gradients, blurry drop shadows, generic Inter font, centered feature cards, and "Lorem ipsum" placeholders—it is instantly classified as "low effort AI slop".
Every interface must look intentional, handcrafted, razor-sharp, and visually unforgettable.

---

## 1. Explicit Banned Cliches (AI Slop Hall of Shame)
- ❌ **NO generic purple-to-indigo gradients** (`from-purple-600 to-indigo-600`) as background or button glow.
- ❌ **NO blurred colorful glowing orbs** behind dark background cards.
- ❌ **NO unstyled default Inter / Roboto / Arial** for primary headlines.
- ❌ **NO generic 3-column identical feature cards** with generic icons in circles.
- ❌ **NO mushy, heavy drop shadows** (`shadow-2xl` on transparent elements).
- ❌ **NO placeholder data**: No "John Doe", "Example Task 1", or "Lorem ipsum". Everything must use rich, realistic domain data.
- ❌ **NO plain spinners**: Replace full-page loading spinners with skeleton loaders or contextual micro-steps (e.g., "Analyzing document...", "Synthesizing vector embeddings...").

---

## 2. Breathtaking Design Principles

### A. High-Contrast Monochromatic + ONE Electric Accent
- Base: Deep carbon dark mode (`#09090b`, `#121214`, `#18181b`) or crisp editorial off-white (`#F8F8F6`, `#FFFFFF`).
- Borders: Crisp 1px solid hairline borders (`border border-zinc-800` or `border-zinc-200/80`). Avoid thick or blurry outlines.
- Accent: Pick **EXACTLY ONE** punchy accent color for key interactive highlights:
  - *Option 1: Electric Lime / Neon Cyber* (`#10b981` / `#22c55e` or `#bef264`)
  - *Option 2: Deep International Klein Blue* (`#2563eb` / `#3b82f6`)
  - *Option 3: Amber Glow / Safety Orange* (`#f97316` / `#fbbf24`)
  - *Option 4: Monochromatic Titanium* (pure white `#ffffff` on `#09090b` with zinc-400 secondary)

### B. Distinctive Typography & Scale
- Pair a character-rich font for hero text with a clean UI typeface:
  - Technical / Modern: **Space Grotesk**, **Syne**, **Cabinet Grotesk**, or **Outfit** for headings.
  - Code & Metadata: **JetBrains Mono** or **Geist Mono** for tags, timestamps, API badges, and counters.
  - Body: **Geist**, **Plus Jakarta Sans**, or **Inter** (with tight tracking).
- Use dramatic typographic scale: Massive tight headers (`text-4xl md:text-6xl font-bold tracking-tight`) contrasted with tiny tracked-out uppercase meta labels (`text-[11px] font-mono uppercase tracking-wider text-zinc-400`).

### C. Asymmetric Bento Grids
- Avoid uniform 3x3 grids.
- Use a **Bento layout** where:
  - Primary hero feature spans 2 columns or full width with a rich live preview/graph/interactive module.
  - Secondary features occupy 1x1 or tall 1x2 cards with distinct internal layouts (e.g., live streaming log terminal, metric counter with sparkline, visual comparison slider).

### D. Tactile Micro-Interactions & State Polish
- **Buttons**: Subtle scale-down on click (`active:scale-[0.98]`), crisp hover border brightening, clear disabled states.
- **Badges**: Pill-shaped status badges with pulsing live indicators (`relative flex h-2 w-2` with `animate-ping`).
- **Streaming**: AI text MUST stream smoothly word-by-word with an active typing cursor, not appear as a sudden clunky wall of text.
- **Copy / Export feedback**: Every action triggers a brief toast or checkmark change (`Copied! ✓`).
