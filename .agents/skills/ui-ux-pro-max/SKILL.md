---
name: ui-ux-pro-max
description: >-
  Use this skill when designing or implementing frontend UI, landing pages, interactive dashboards, animations, typography, and styling to guarantee a breathtaking, modern, award-winning look and eliminate AI slop. Includes Lenis smooth scroll, GSAP suite, Disney animation principles, and React Bits components.
---

# UI/UX Pro Max: Anti-Slop, Animations & Elite Components

Use this skill whenever designing, building, or refining interfaces to make them visually breathtaking, tactile, and unforgettable for hackathon judges.

---

## 1. Aesthetic Archetypes (Pick One)

| Archetype | Best For | Color Theme | Key Elements |
|---|---|---|---|
| **Linear Technical** | DevTools, AI agents, Productivity | Carbon `#09090b`, Hairline zinc-800 borders, JetBrains Mono tags | Monochromatic, keyboard shortcut badges (`⌘K`), subtle grid lines |
| **Cyber Emerald** | FinTech, Security, Data Intelligence | Deep obsidian `#050505`, Neon Emerald `#10b981`, Mint glow | Dynamic metrics, glowing pulse status indicators, dark glass cards |
| **Editorial Prestige** | Creative tools, Writing, Legal, Education | Warm off-white `#F9F9F7` or Rich Espresso `#12100E`, Cream text | High-contrast serif headlines (Instrument Serif), generous whitespace |
| **Solar Horizon** | Consumer AI, Lifestyle, Media | Dark Slate `#0B0F19`, Amber/Orange accent `#F97316` | Warm gradients, expressive typography, high-impact bento cards |

---

## 2. Typography Pairings
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```
- **Display Headlines**: `'Space Grotesk', sans-serif` (`tracking-tight font-bold`)
- **Body & Controls**: `'Plus Jakarta Sans', sans-serif`
- **Code / Badges / Numbers**: `'JetBrains Mono', monospace`

---

## 3. Darkroom Engineering Lenis Smooth Scroll

Install: `npm install lenis`

```jsx
// components/SmoothScroll.tsx
'use client';
import { ReactLenis } from 'lenis/react';
import 'lenis/dist/lenis.css';

export default function SmoothScroll({ children }: { children: React.ReactNode }) {
  return (
    <ReactLenis root options={{ duration: 1.2, smoothWheel: true }}>
      {children}
    </ReactLenis>
  );
}
```

### Syncing Lenis with GSAP ScrollTrigger
```jsx
'use client';
import { useEffect, useRef } from 'react';
import { ReactLenis } from 'lenis/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function LenisGSAPProvider({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<any>(null);

  useEffect(() => {
    function update(time: number) {
      lenisRef.current?.lenis?.raf(time * 1000);
    }
    gsap.ticker.add(update);
    gsap.ticker.lagSmoothing(0);
    return () => gsap.ticker.remove(update);
  }, []);

  return (
    <ReactLenis ref={lenisRef} root options={{ autoRaf: false }}>
      {children}
    </ReactLenis>
  );
}
```

---

## 4. GSAP Animation Engine & Registered Plugins

Install: `npm install gsap @gsap/react`

```javascript
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";

import { CustomEase } from "gsap/CustomEase";
import { CustomBounce } from "gsap/CustomBounce";
import { CustomWiggle } from "gsap/CustomWiggle";
import { RoughEase, ExpoScaleEase, SlowMo } from "gsap/EasePack";
    
import { Draggable } from "gsap/Draggable";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { EaselPlugin } from "gsap/EaselPlugin";
import { Flip } from "gsap/Flip";
import { GSDevTools } from "gsap/GSDevTools";
import { InertiaPlugin } from "gsap/InertiaPlugin";
import { MotionPathHelper } from "gsap/MotionPathHelper";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import { MorphSVGPlugin } from "gsap/MorphSVGPlugin";
import { Observer } from "gsap/Observer";
import { Physics2DPlugin } from "gsap/Physics2DPlugin";
import { PhysicsPropsPlugin } from "gsap/PhysicsPropsPlugin";
import { PixiPlugin } from "gsap/PixiPlugin";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ScrollSmoother } from "gsap/ScrollSmoother";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { SplitText } from "gsap/SplitText";
import { TextPlugin } from "gsap/TextPlugin";

gsap.registerPlugin(
  useGSAP, Draggable, DrawSVGPlugin, EaselPlugin, Flip, GSDevTools,
  InertiaPlugin, MotionPathHelper, MotionPathPlugin, MorphSVGPlugin,
  Observer, Physics2DPlugin, PhysicsPropsPlugin, PixiPlugin,
  ScrambleTextPlugin, ScrollTrigger, ScrollSmoother, ScrollToPlugin,
  SplitText, TextPlugin, RoughEase, ExpoScaleEase, SlowMo,
  CustomEase, CustomBounce, CustomWiggle
);
```

### Clean React GSAP Animation with `useGSAP()`
```jsx
'use client';
import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';

export function AnimatedHero() {
  const container = useRef(null);

  useGSAP(() => {
    gsap.from('.stagger-item', {
      y: 40,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      ease: 'power3.out',
    });
  }, { scope: container });

  return (
    <div ref={container}>
      <h1 className="stagger-item text-5xl font-bold tracking-tight">AI Agent Studio</h1>
      <p className="stagger-item text-zinc-400 mt-2">Autonomous workflows that ship in seconds.</p>
    </div>
  );
}
```

---

## 5. Disney's 12 Animation Principles in Code

1. **Squash & Stretch**:
   - Buttons: `active:scale-95 transition-transform duration-100 ease-out`
   - Cards during drag: `transform: scale(1.02, 0.98)`
2. **Anticipation**:
   - Hover pulls element back or elevates slightly: `hover:-translate-y-1 transition-all duration-200`
3. **Slow In & Slow Out (Ease-in-out)**:
   - Never use `linear`. Use `cubic-bezier(0.16, 1, 0.3, 1)` (snappy spring) or `ease: "power2.out"`.
4. **Follow Through & Overlapping Action**:
   - Stagger card children entrance by `0.08s`.
   - Modals: backdrop fades in first, modal card scales up 50ms later.

---

## 6. React Bits Component Integration (`react-bits`)

Source: [https://github.com/DavidHDev/react-bits](https://github.com/DavidHDev/react-bits) (or [reactbits.dev](https://reactbits.dev))

### A. Spotlight Card (The Ultimate Anti-Slop Card)
```tsx
'use client';
import React, { useRef, useState } from 'react';

export function SpotlightCard({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  const divRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950/70 p-6 backdrop-blur-md ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(16, 185, 129, 0.12), transparent 40%)`,
        }}
      />
      {children}
    </div>
  );
}
```

### B. Shiny / Decrypted Text
```tsx
'use client';
export function ShinyText({ text, className = '' }: { text: string; className?: string }) {
  return (
    <span
      className={`inline-block bg-[linear-gradient(110deg,#a1a1aa,45%,#ffffff,55%,#a1a1aa)] bg-[length:200%_100%] bg-clip-text text-transparent animate-[shine_3s_linear_infinite] font-semibold ${className}`}
    >
      {text}
    </span>
  );
}
```
Add to `tailwind.config.js`:
```js
keyframes: {
  shine: {
    '0%': { backgroundPosition: '200% 0' },
    '100%': { backgroundPosition: '-200% 0' },
  },
},
```

---

## 7. Submission Checklist
- [ ] No purple-to-indigo gradient blobs.
- [ ] Lenis smooth scroll active on root layout.
- [ ] GSAP animations scoped cleanly with `useGSAP()`.
- [ ] Real mock data loaded (financial, code, or medical context).
- [ ] Mobile responsive: tested with DevTools device toggle.
- [ ] High-contrast, sharp 1px borders on all cards.
