---
name: automation-agents
description: >-
  Use this skill when building multi-agent swarms with Ruflo, stealth browser automation with Camofox and Playwright, simulation engines with MiroFish, or integrating MCP servers into hackathon projects.
---

# Automation, Agent Swarms & Stealth Browser Skill

This skill provides step-by-step guidance and copy-paste code for **Ruflo agent swarms**, **Camofox stealth browser automation**, and **Playwright integration**.

---

## 1. Ruflo Multi-Agent Swarm Harness (`ruvnet/ruflo`)

Source: [https://github.com/ruvnet/ruflo](https://github.com/ruvnet/ruflo)

Ruflo is an AI agent orchestration harness that coordinates multi-agent swarms, self-learning vector memory, and federated communications.

### Installation & Quick Start
```bash
# Run Ruflo directly or install globally
npx ruflo@latest init
# Or clone for custom orchestration:
git clone https://github.com/ruvnet/ruflo.git
cd ruflo
npm install
```

### Ruflo MCP Server Integration
Add Ruflo to your agent / Claude / Cursor / Antigravity MCP config:
```json
{
  "mcpServers": {
    "ruflo": {
      "command": "npx",
      "args": ["-y", "ruflo@latest", "mcp"]
    }
  }
}
```

---

## 2. Stealth Browser Automation: Camofox + Playwright

Source: [https://github.com/jo-inc/camofox-browser](https://github.com/jo-inc/camofox-browser)

Camofox bypasses Cloudflare, Turnstile, and anti-bot systems at the **C++ layer** by modifying Firefox (`camoufox`), spoofing WebGL, audio fingerprinting, and hardware concurrency before JS executes. It also outputs compact accessibility snapshots for LLMs.

### Spinning Up the Camofox Server
```bash
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start
# Server runs on http://localhost:9377
```

### Playwright Integration with Camofox
To connect Playwright to Camofox's stealth browser session or CDP endpoint:

```typescript
// scripts/stealth-scrape.ts
import { chromium, firefox } from 'playwright';

export async function runStealthAutomation(targetUrl: string) {
  // Option A: Connect directly via Camofox HTTP Server API (Tokens & Element refs)
  const response = await fetch('http://localhost:9377/api/navigate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: targetUrl }),
  });
  const snapshot = await response.json();
  console.log('Stealth DOM Snapshot for LLM:', snapshot.accessibilityTree);
  return snapshot;
}

// Option B: Playwright with Camoufox spoofing headers & stealth
export async function launchCamofoxPlaywright() {
  const browser = await firefox.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled'],
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    viewport: { width: 1440, height: 900 },
    locale: 'en-US',
  });
  const page = await context.newPage();
  return { browser, page };
}
```

---

## 3. MiroFish Swarm Simulation (`666ghj/MiroFish`)

Source: [https://github.com666ghj/MiroFish](https://github.com/666ghj/MiroFish)

MiroFish builds a dynamic knowledge graph from unstructured seed documents and simulates hundreds of AI personas interacting in a swarm to forecast sentiment and outcomes.

### Quick Clone & Local Setup
```bash
git clone https://github.com/666ghj/MiroFish.git
cd MiroFish
pip install -r requirements.txt
python main.py
```

---

## 4. MCP Servers Workspace Configuration
You can register local and remote MCP servers in `.agents/plugins/agent-tools/mcp_config.json`.
When loaded, the agent automatically exposes these tools in its context.
