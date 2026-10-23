# Antigravity Rules — DITE Hackathon 2026-27

## 0. Prime directive
Ship a working AI web app in 5 hours with: public GitHub repo + README,
live deployed URL, 3–5 min demo video on Drive (anyone-with-link view),
submitted via Google Form before the deadline. Nothing else matters.

## 1. Clock discipline
- T+0:00–0:20  Scaffold + deploy skeleton LIVE (AI call stubbed OK).
- T+0:20–3:30  Build features, deploy on every meaningful commit.
- T+3:30–4:30  Freeze features. README, demo video, link checks.
- T+4:30–5:00  Submit form, verify incognito, keep confirmation.
- At T+3:30 STOP adding features. Ship mode only. No exceptions.

## 2. Always load these skills
- `.agents/rules/anti-ai-slop.md`
- `.agents/rules/hackathon-rules.md`

## 3. Load task-specific skills only when the task needs them
- Design/UI work          → `.agents/skills/design-taste-frontend/SKILL.md`,
                            `.agents/skills/ui-ux-pro-max/SKILL.md`
- DB / persistence        → `.agents/skills/database-mastery/SKILL.md`
- API / streaming         → `.agents/skills/backend-efficiency/SKILL.md`
- Deploy / README / video → `.agents/skills/hackathon-ship-fast/SKILL.md`

## 4. Hard prohibitions (YES/NO, no negotiation)
- NO API keys or secrets in code. Env vars only. If missing, stop and ask.
- NO purple gradients. NO generic AI-slop UI. 1px hairline borders,
  Space Grotesk / JetBrains Mono typography per anti-ai-slop.
- NO new libraries or models not already validated in the kit.
- NO local-only demos. Every feature must work on the deployed URL.
- NO code pushed after the deadline.
- NO feature work after T+3:30.

## 5. AI model policy
- Primary chat/code: `cohere/north-mini-code:free`
- Backup chat: `nvidia/nemotron-3.5-lightning:free`
- Embeddings: `liquid/lfm-2.5-embedding-350m:free`
- DO NOT use `google/gemma-4-31b-it:free` (429 rate-limited).
- Every AI call wrapped in try/catch with offline fallback response.

## 6. Build order (deploy-first)
1. Minimal app that renders + one stubbed AI call.
2. Deploy to Vercel. Confirm public URL works in incognito.
3. Push to public GitHub with README stub.
4. Build real features, redeploy after each.
5. Final README, demo video, link audit, submit.

## 7. Definition of done (per task)
A task is done only when:
- It works on the deployed URL (not just localhost), AND
- Code is committed and pushed, AND
- No secrets in the diff.
If any is false, the task is not done. Say so.

## 8. Failure protocol
- Same approach fails twice → switch to offline fallback, report in one line.
- Deploy fails → fix deploy before any new feature.
- Requirement at risk (repo/deploy/video/form) → flag immediately, one line.

## 9. Communication contract
- Report results as: DONE / NOT DONE + one-line reason + next action.
- No essays. No option menus. One recommendation, YES or NO.
- Ask a question only if a hard blocker; otherwise proceed on stated assumption.

## 10. Submission ritual (Ship lead owns)
1. Push final code, complete README.
2. Deploy web app, copy live URL (or upload APK to Drive, copy link).
3. Upload demo video to Drive, copy link.
4. Set every Drive link to "Anyone with the link can view".
5. Open every link in incognito — verify.
6. Fill Google Form, Submit, keep confirmation.
