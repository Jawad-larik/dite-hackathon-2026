# Rule: DITE Hackathon 2026-27 Constraints & Ship Standards

## Hard Rules & Constraints (Non-Negotiable)
1. **5-Hour Total Clock**: Speed to a working, deployed URL is the #1 priority. Never over-engineer when a simpler, working approach wins.
2. **AI Requirement**: The application MUST call an AI model or API (e.g. Gemini 1.5/2.0 Flash, Groq Llama 3.3, OpenAI, or local embedding/model).
3. **Live Web Deployment**: Must be deployed to a public URL (e.g. Vercel) that opens for anyone in an incognito window.
4. **Environment Variables**: NEVER hardcode API keys or credentials. Use `.env.local` / `.env` and configure Vercel environment variables. Include `.env.example` with blank keys.
5. **Public GitHub Repo & README**: The repository must be public with a polished README containing:
   - Project Title & Tagline
   - Problem Statement & Solution
   - Key Features & Architecture Diagram
   - Live Demo Link
   - Setup & Run Instructions
6. **Demo Video Preparedness**: The core user journey must be demonstrable in 3 to 5 minutes with zero awkward bugs or loading freezes.
