---
name: backend-efficiency
description: >-
  Use this skill when designing, building, or optimizing the backend, API routes, AI model calls, streaming endpoints, caching, error resilience, and environment variables for maximum performance and reliability in hackathons.
---

# Backend Efficiency & Peak Performance Skill

In a 5-hour hackathon, backend efficiency is defined by **sub-second latency**, **zero CORS bugs**, **bulletproof resilience against rate limits**, and **predictable structured JSON outputs**.

---

## 1. Golden Architecture Rules for Hackathons

### Choice A: Monolithic Next.js Route Handlers (Recommended Default)
- **Why**: Zero separate backend to deploy, zero CORS issues, instant deployment on Vercel, unified TypeScript types from API to UI.
- **Where**: Put API endpoints in `app/api/[route]/route.ts`.
- **Runtime**: Use `export const runtime = 'edge'` or standard Node.js runtime.

### Choice B: FastAPI (When Heavy Python is Required)
- **Why**: Native support for LangGraph, scikit-learn, PyTorch, PyPDF, or complex Python agent pipelines.
- **Key setup**: Enable CORS properly:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 2. Choosing the Fastest AI Model / Provider

| Provider | Model | Latency / Speed | Best For | Free Quota |
|---|---|---|---|---|
| **Groq Cloud** | `llama-3.3-70b-versatile` | **500+ tokens/sec** | Instant chat, real-time agents, extraction | Generous free tier |
| **Google AI Studio** | `gemini-1.5-flash` / `gemini-2.0-flash` | **Sub-second** | Multimodal (images, audio, PDFs), massive context | 15 RPM free |
| **OpenAI** | `gpt-4o-mini` | **Fast & cheap** | Structured JSON outputs, function calling | Paid / Tier 1 |
| **OpenRouter** | Multi-model aggregator | Variable | Single API key for 50+ models fallback | Free & low-cost models |

---

## 3. Structured Outputs (Never Let Markdown Break Your UI)

Never ask an LLM to "return JSON" without enforcing schema validation.

### Next.js / TypeScript with Zod + AI SDK
```typescript
import { generateObject } from 'ai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { z } from 'zod';

const schema = z.object({
  summary: z.string(),
  sentiment: z.enum(['positive', 'neutral', 'negative']),
  keyPoints: z.array(z.string()),
  confidenceScore: z.number().min(0).max(100)
});

const { object } = await generateObject({
  model: google('gemini-1.5-flash'),
  schema,
  prompt: `Analyze the following: ${userInput}`,
});
```

### Python FastAPI with Pydantic
```python
from pydantic import BaseModel, Field
from typing import List

class AnalysisResponse(BaseModel):
    summary: str
    key_takeaways: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
```

---

## 4. The "Judge-Proof" Demo Mode (Offline / Fallback Resilience)

WiFi at hackathons is notoriously unstable, and AI APIs can hit rate limits right as judges stand in front of your screen.
Always implement an instant **Demo Mock Fallback**:

```typescript
// app/api/generate/route.ts
const USE_MOCK = process.env.DEMO_MOCK_FALLBACK === 'true' || !process.env.AI_API_KEY;

if (USE_MOCK) {
  // Return pre-baked, hyper-realistic demo response with simulated typing delay
  return new Response(JSON.stringify(mockDemoData), {
    headers: { 'Content-Type': 'application/json' }
  });
}
```

---

## 5. In-Memory Request Caching

Avoid re-calling APIs for identical demo queries:
```typescript
// Simple in-memory LRU or Map cache for hackathon speed
const cache = new Map<string, any>();

export async function getCachedAIResponse(prompt: string) {
  if (cache.has(prompt)) {
    return cache.get(prompt);
  }
  const result = await callAI(prompt);
  cache.set(prompt, result);
  return result;
}
```

---

## 6. Secure Environment Variables Protocol
- Keep `.env.local` in `.gitignore`.
- Provide a `.env.example` file:
```env
# AI Providers
GEMINI_API_KEY=
GROQ_API_KEY=
OPENAI_API_KEY=

# App Config
NEXT_PUBLIC_APP_URL=http://localhost:3000
DEMO_MOCK_FALLBACK=false
```
- In Vercel, navigate to **Project Settings -> Environment Variables** and paste the keys before the first build.
