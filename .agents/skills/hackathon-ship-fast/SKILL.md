---
name: hackathon-ship-fast
description: >-
  Use this skill to orchestrate the 5-hour hackathon execution plan, rapid GitHub template bootstrapping, Vercel zero-friction deployment, README generation, and the winning 3-5 minute demo video script.
---

# Hackathon Ship-Fast & 5-Hour Execution Manual

Designed specifically for tight 5-hour AI hackathons (like the DITE Hackathon 2026-27). Follow this exact protocol to guarantee on-time submission with maximum scoring potential.

---

## 1. The 5-Hour Timeline Battle Plan

```text
[HOUR 0-1]  Scaffold stack + Deploy Hello World on Vercel + Wire AI API
[HOUR 1-3]  Build the Single Core AI Loop (One killer feature working end-to-end)
[HOUR 3-4]  Apply UI/UX Pro Max (Bento layout, typography, micro-interactions, dark mode)
[HOUR 4-4.5] Smoke test deployed URL + Write polished README + Push final commit
[HOUR 4.5-5] Record 3-minute demo video + Upload to Google Drive + Submit Google Form
```

> **CRITICAL RULE**: Deploy to Vercel in **Hour 1**, NOT Hour 4.5. Continuous deployment means every push is live. If deployment fails at hour 4.5, you risk submitting nothing.

---

## 2. GitHub Starters & Rapid Bootstrapping

### Option 1: Next.js + Tailwind + Lucide (The #1 Fastest Hackathon Web App)
```bash
npx create-next-app@latest ./ --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
npm install lucide-react clsx tailwind-merge framer-motion @ai-sdk/google ai zod
```

### Option 2: Pre-built Vercel AI Chatbot / Agent Template
```bash
git clone https://github.com/vercel/ai-chatbot.git .
npm install
```

### Option 3: FastAPI + React Vite (If Team is Python-Dominant)
```bash
# Frontend
npm create vite@latest frontend -- --template react-ts
# Backend
pip install fastapi uvicorn google-genai python-dotenv pydantic
```

---

## 3. High-Scoring README Template (`README.md`)

When judges open your GitHub repo, the README should look like a $10M YC startup:

```markdown
# 🚀 [Project Name]
> **[One-sentence pitch explaining the exact superpower this app gives the user]**

[![Live Demo](https://img.shields.io/badge/Demo-Live%20App-emerald?style=for-the-badge&logo=vercel)](YOUR_VERCEL_URL)
[![Demo Video](https://img.shields.io/badge/Video-3%20Min%20Demo-red?style=for-the-badge&logo=google-drive)](YOUR_GDRIVE_URL)

---

## 💡 The Problem
A 2-3 sentence crisp explanation of a painful, real-world friction point.

## ✨ The Solution: [Project Name]
How your AI-powered system solves this friction 10x faster with intuitive visual workflows.

## ⚡ Key Features
- **Instant AI Processing**: Powered by [Gemini 1.5 Flash / Groq Llama 3.3] with sub-second generation.
- **Dynamic Interactive UI**: Real-time feedback, asymmetric bento layout, and zero latency.
- **Automated Verification**: Structured JSON schema output with 100% data fidelity.

## 🛠️ Architecture & Tech Stack
- **Frontend**: Next.js 15, Tailwind CSS, Lucide Icons, Framer Motion
- **AI Core**: Google Gemini / Groq API with structured JSON schemas
- **Deployment**: Vercel Edge Network

## 🚀 Getting Started Locally

```bash
# 1. Clone repository
git clone https://github.com/YOUR_TEAM/YOUR_REPO.git

# 2. Install dependencies
npm install

# 3. Setup environment variables
cp .env.example .env.local
# Add your GEMINI_API_KEY / GROQ_API_KEY in .env.local

# 4. Run development server
npm run dev
```

---

## 👥 The Team
- **[Member 1 Name]** - App Lead / UI-UX
- **[Member 2 Name]** - AI Lead / Model Integration
- **[Member 3 Name]** - Ship Lead / DevOps & Presentation
```

---

## 4. The 3-5 Minute Demo Video Script Formula

Hackathon judges grade on: **Problem, AI Innovation, Execution/Working Demo, Impact**.

| Time | Slide / Screen | What to Say / Show |
|---|---|---|
| **0:00 - 0:45** | Problem & Hook | "Every day, [X persona] struggles with [painful problem]. Existing tools do [bad solution]. Today we built [Project Name]." |
| **0:45 - 2:30** | Live Working Demo (The Hero Flow) | Don't explain code! Show the real user journey: input prompt/data, watch the real-time AI generation, highlight the unique output/insights. |
| **2:30 - 3:15** | Architecture & AI Depth | "Under the hood, we leverage [Model Name] with structured schema validation, streaming responses, and [special technique like agentic loop / RAG / multimodal analysis]." |
| **3:15 - 3:45** | Impact & Future Roadmap | Who benefits, how this scales, and immediate next features. |
| **3:45 - 4:00** | Wrap up | "Try it live at [Link]. Thank you!" |

---

## 5. Submission Checklist (DITE Hackathon Guidelines)
- [ ] Code pushed to public GitHub repository.
- [ ] README is polished with screenshots and live link.
- [ ] Web app is live on Vercel with zero 500 errors.
- [ ] Incognito check: Opened the live link in an incognito window without logging into anything.
- [ ] Demo video uploaded to Google Drive.
- [ ] **Google Drive link permission set to "Anyone with the link can view"** (TEST THIS IN INCOGNITO!).
- [ ] Google Form filled and submitted before the 5:00:00 mark.
