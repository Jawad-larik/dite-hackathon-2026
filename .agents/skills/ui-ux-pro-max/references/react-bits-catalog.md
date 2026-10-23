# React Bits Component Catalog & Copy-Paste Reference

Source: [https://github.com/DavidHDev/react-bits](https://github.com/DavidHDev/react-bits) | Live Demos: [reactbits.dev](https://reactbits.dev)

React Bits is a collection of 70+ animated, interactive, and customizable React components. During a 5-hour hackathon, use these pre-made components to inject instant wow-factor into your app.

---

## 1. Top Text Animations

### A. Blur Text (Smooth In-View Text Reveal)
```tsx
'use client';
import { useRef, useEffect, useState } from 'react';
import { useSprings, animated } from '@react-spring/web';

export const BlurText = ({
  text = '',
  delay = 200,
  className = '',
  animateBy = 'words', // 'words' or 'letters'
  direction = 'top',
  threshold = 0.1,
  rootMargin = '0px',
}: any) => {
  const elements = animateBy === 'words' ? text.split(' ') : text.split('');
  const [inView, setInView] = useState(false);
  const ref = useRef<any>();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.unobserve(ref.current);
        }
      },
      { threshold, rootMargin }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  const springs = useSprings(
    elements.length,
    elements.map((_: any, i: number) => ({
      from: {
        filter: 'blur(10px)',
        opacity: 0,
        transform: direction === 'top' ? 'translate3d(0,-20px,0)' : 'translate3d(0,20px,0)',
      },
      to: inView
        ? async (next: any) => {
            await next({
              filter: 'blur(5px)',
              opacity: 0.5,
              transform: direction === 'top' ? 'translate3d(0,5px,0)' : 'translate3d(0,-5px,0)',
            });
            await next({ filter: 'blur(0px)', opacity: 1, transform: 'translate3d(0,0,0)' });
          }
        : { filter: 'blur(10px)', opacity: 0 },
      delay: i * delay,
    }))
  );

  return (
    <p ref={ref} className={`inline-block ${className}`}>
      {springs.map((props: any, index: number) => (
        <animated.span
          key={index}
          style={props}
          className="inline-block will-change-[transform,filter,opacity]"
        >
          {elements[index] === ' ' ? '\u00A0' : elements[index]}
          {animateBy === 'words' && index < elements.length - 1 && '\u00A0'}
        </animated.span>
      ))}
    </p>
  );
};
```

### B. Decrypted / Scramble Text (Cyber Hacker Effect)
```tsx
'use client';
import { useEffect, useState, useRef } from 'react';

const CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+';

export function DecryptedText({ text, speed = 50, className = '' }: { text: string; speed?: number; className?: string }) {
  const [displayText, setDisplayText] = useState(text);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText(
        text
          .split('')
          .map((char, index) => {
            if (index < iteration) return text[index];
            return CHARACTERS[Math.floor(Math.random() * CHARACTERS.length)];
          })
          .join('')
      );
      if (iteration >= text.length) clearInterval(interval);
      iteration += 1 / 3;
    }, speed);
    return () => clearInterval(interval);
  }, [text, isHovered, speed]);

  return (
    <span
      onMouseEnter={() => setIsHovered(!isHovered)}
      className={`font-mono cursor-pointer ${className}`}
    >
      {displayText}
    </span>
  );
}
```

---

## 2. Top Animated Backgrounds

### Aurora Subtle Background
```tsx
'use client';
export function AuroraBackground({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex flex-col min-h-screen bg-zinc-950 text-slate-100 overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-40">
        <div className="absolute -inset-[10px] opacity-50">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>
      </div>
      <div className="relative z-10 w-full">{children}</div>
    </div>
  );
}
```

---

## 3. Top Interactive Cards

### Tilted Card (3D Mouse Parallax)
```tsx
'use client';
import React, { useRef, useState } from 'react';

export function TiltedCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setRotateX(-y / 15);
    setRotateY(x / 15);
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
        transition: 'transform 0.1s ease-out',
      }}
      className={`rounded-2xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-md p-6 shadow-xl ${className}`}
    >
      {children}
    </div>
  );
}
```

---

## 4. Cursor Follower (Splash / Magnet)
```tsx
'use client';
import { useRef, useState } from 'react';

export function MagnetButton({ children, onClick, className = '' }: any) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    const { clientX, clientY } = e;
    const { left, top, width, height } = buttonRef.current!.getBoundingClientRect();
    const x = (clientX - (left + width / 2)) * 0.35;
    const y = (clientY - (top + height / 2)) * 0.35;
    setPosition({ x, y });
  };

  const handleMouseLeave = () => setPosition({ x: 0, y: 0 });

  return (
    <button
      ref={buttonRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
        transition: 'transform 0.15s cubic-bezier(0.2, 0, 0.2, 1)',
      }}
      className={`px-5 py-2.5 rounded-lg font-medium border border-zinc-700 bg-zinc-900 hover:border-emerald-500 hover:text-emerald-400 active:scale-95 transition-colors ${className}`}
    >
      {children}
    </button>
  );
}
```
