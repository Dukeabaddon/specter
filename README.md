<div align="center">

**English** · [Filipino](docs/readme/README_fil.md) · [简体中文](docs/readme/README_zh.md) · [繁體中文](docs/readme/README_zh-TW.md) · [日本語](docs/readme/README_ja.md) · [한국어](docs/readme/README_ko.md) · [Español](docs/readme/README_es.md) · [Français](docs/readme/README_fr.md) · [Deutsch](docs/readme/README_de.md) · [Русский](docs/readme/README_ru.md) · [Português](docs/readme/README_pt.md) · [Bahasa Indonesia](docs/readme/README_id.md)

# specter: Self-Hosted Facebook Public Page Scraper

### A resilient dual-mode engine for continuous Facebook public page monitoring.

**See a public page post. Extract it in sub-seconds without getting banned, paying for SaaS, or burning personal accounts.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/Dukeabaddon/specter/actions)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](#quick-start)
[![Integrations](https://img.shields.io/badge/Integrations-n8n%20%7C%20Discord%20%7C%20Telegram-FF6D5A.svg?style=flat-square)](docs/integrations/README.md)
[![Playwright](https://img.shields.io/badge/Playwright-Stealth-green.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4c430.svg?style=flat-square)](LICENSE)

<br/>

[Quick start](#quick-start) · [Integrations](docs/integrations/README.md) · [How specter works](#how-specter-works) · [Anti-ban architecture](#anti-ban-architecture) · [CLI reference](#cli-reference) · [FAQ](#faq)

<code>git clone https://github.com/Dukeabaddon/specter.git</code>

<br/><br/>

<img src="assets/banner.png" alt="specter banner" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />

</div>

---

> [!IMPORTANT]
> In late 2024, Meta permanently discontinued `mbasic.facebook.com`, which broke 95% of historical open-source Facebook scrapers. **specter** is an independent open-source engine built using the **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** skill to reverse-engineer Meta's modern Comet React SPA and Relay SSR data streams.

---

## The Modern Facebook Problem

If you have tried using open-source Facebook scrapers recently, you likely noticed that **almost all of them are dead**:

- **The Death of mbasic:** In late 2024, Meta permanently killed `mbasic.facebook.com`. 95% of historical Python libraries (`kevinzg/facebook-scraper` with 3.3k stars, `facebook2rss`, RSS-Bridge) stopped working overnight.
- **Comet React SPA and Relay:** Facebook now forces all web traffic through an obfuscated React Single-Page Application using Relay, rendering traditional CSS selectors (`div._5v64`, `article[data-ft]`) completely obsolete.
- **Immediate Bot Walls:** Standard HTTP requests to Facebook public pages now return `HTTP 400 Bad Request` or redirect to checkpoint login barriers.
- **Account Disabling:** Supplying personal authenticated cookies (`c_user` / `xs`) frequently triggers suspicious activity verification or permanent account disabling within 48 hours.
- **SaaS Lock-In:** Cloud scraper services (Apify, Bright Data, Scrapfly) charge upwards of $50–$150/month for basic scheduled page scraping.

`specter` was engineered to solve this challenge as a standalone, free, and self-hosted engine.

---

## How specter Works

<div align="center">
  <img src="assets/architecture.png" alt="specter Architecture Diagram" width="100%" style="border-radius: 8px; border: 1px solid #1e293b;" />
</div>

<br/>

Using the **Reverse Engineer Anything (REA)** methodology alongside deep inspection of commercial actors (Apify) and open-source codebases, we discovered three key architectural insights:

1. **Anonymous Visitor Cookies:** Public Facebook pages do not require account login. When an authentic browser visits a page, Meta edge servers issue ephemeral public visitor cookies (such as `datr` and `wd`).
2. **Inline Relay SSR Stream:** Modern Facebook pages do not initially load posts via GraphQL AJAX requests. Instead, the first batch of timeline posts is server-rendered directly into inline `<script type="application/json">` tags using Meta's `RelayPrefetchedStreamCache`.
3. **The Dual-Mode Hybrid Architecture:** By pairing a stealth browser engine with a lightweight HTTP client, we created a self-healing pipeline:
   - **Tier 1 (Fast HTTP):** Executes in ~500ms, consumes ~25MB of RAM, and parses the inline Relay SSR payload without launching Chromium.
   - **Tier 2 (Stealth Playwright):** Launches automatically when cookies expire, suppresses the login dialog overlay, unlocks DOM scrolling, scrapes live cards, and saves fresh visitor session tokens to `data/cookies.json` to re-arm Tier 1.

---

## Key Features

- **Sub-Second Fast Mode (Tier 1):** Parses inline Relay SSR JSON payloads via HTTP in **~500ms** with virtually zero CPU/memory overhead.
- **Stealth Headless Fallback (Tier 2):** When visitor cookies expire or Meta updates edge tokens, a stealth Playwright Chromium instance automatically launches, removes login dialog overlays, unlocks DOM scrolling, scrapes live virtualized feed cards, and refreshes the local cookie jar.
- **100% Cookieless and Account-Safe:** Runs strictly on anonymous visitor sessions. **No personal Facebook accounts, passwords, or session cookies are ever required.**
- **Deterministic SQLite Deduplication:** Content SHA-256 fingerprinting ensures that already-seen posts are never re-reported or duplicated.
- **Pluggable Downstream Pipeline:** Easily hook up downstream processors (custom notification webhooks, Discord/Telegram bots, event parsers, or keyword classifiers).

---

## Quick Start

### Option A: Docker Compose (Recommended)
Run a self-contained monitoring daemon with zero manual Python environment configuration:

```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

# Start daemon in background (polls every 5 minutes, persists to ./data)
docker compose up -d
```

### Option B: Local CLI / Python
```bash
git clone https://github.com/Dukeabaddon/specter.git
cd specter

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Run a live test scrape
python3 main.py --page QCGov --limit 3
```

---

## Automation & Workflow Integration

specter connects directly to **n8n**, **Discord**, **Telegram**, **Make**, **Zapier**, and custom HTTP microservices.

Explore the complete guides in the **[Integrations Hub](docs/integrations/README.md)**:

| Integration | Guide | Description |
|---|---|---|
| **n8n** | [n8n Workflow Guide](docs/integrations/n8n.md) | Ready-to-import workflow template for alerts and databases |
| **Discord** | [Discord Webhook Guide](docs/integrations/discord.md) | Push rich embed alert cards directly into Discord channels |
| **Telegram** | [Telegram Bot Guide](docs/integrations/telegram.md) | Broadcast instant post advisories to Telegram channels and groups |
| **HTTP Webhooks & APIs** | [Custom Webhooks Guide](docs/integrations/webhooks.md) | Standard JSON schema for Make, Zapier, FastAPI, and custom backends |

### 1. Webhook Dispatch (Universal HTTP POST)
Configure specter to POST structured JSON payloads to your webhook whenever a new post is published:

```bash
python3 main.py --page QCGov --monitor --webhook https://n8n.yourdomain.com/webhook/fb-posts
```

### 2. Unix Pipe & JSON Output
Stream structured JSON directly to `stdout` for piping into `jq`, CLI scripts, or automated processing nodes:

```bash
python3 main.py --page QCGov --limit 3 --json | jq '.[0].text'
```

---

## CLI Reference

| Command | Description |
|---|---|
| `python3 main.py --page <NAME>` | Poll a specific public page once (e.g. `QCGov`, `cnn`, `NASA`) |
| `python3 main.py --page <A,B>` | Monitor multiple pages simultaneously (comma-separated) |
| `python3 main.py --page <NAME> --monitor --interval 300` | Run continuous monitoring daemon every 5 minutes |
| `python3 main.py --page <NAME> --webhook <URL>` | Dispatch HTTP POST to webhook on every new post |
| `python3 main.py --page <NAME> --json` | Output structured JSON to stdout (suppresses logs) |
| `python3 main.py --mode auto` | **Default**: Fast HTTP first, stealth Playwright fallback |
| `python3 main.py --mode http` | Force Fast HTTP-only mode (~500ms) |
| `python3 main.py --mode playwright` | Force stealth Playwright Chromium mode |
| `python3 main.py --db-list` | Display recent stored posts from SQLite database |
| `python3 main.py --test-classifier` | Run built-in sample downstream event classification test |

---

## Anti-Ban Architecture: How It Survives

| Challenge | Naive Scrapers | specter Solution |
|---|---|---|
| **Account Ban Risk** | Use personal logged-in cookies | **Zero credentials used**. Runs on anonymous visitor sessions |
| **Login Modal Wall** | Scraper halts when modal appears | Injects script to delete `div[role="dialog"]` and restore `overflow: auto` |
| **Browser Bloat** | Runs heavy browser 24/7 | Playwright runs **once** to capture session; subsequent scrapes use **lightweight HTTP** |
| **IP Rate Limiting** | Spamming identical requests | Built-in polling intervals + randomized headers + automatic fallback cooling |
| **Cloud Datacenter IPs** | AWS/GCP IPs flagged by Meta WAF | Supports residential proxy forwarding via standard `HTTP_PROXY` env vars |

---

## Python API Usage

You can embed `specter` directly into your own applications:

```python
from src.fetchers.hybrid import HybridFetcher
from src.storage.db import PostDatabase

# Initialize dual-mode fetcher
fetcher = HybridFetcher(mode="auto")

# Fetch latest posts
posts = fetcher.fetch_posts("QCGov", limit=5)

for post in posts:
    print(f"[{post.post_id}] {post.url}")
    print(post.text[:200])
    print("Images:", post.images)
```

---

## FAQ

<details>
<summary><b>Why does specter report "0 new posts" on repeated polls?</b></summary>
<br/>

specter uses deterministic SHA-256 content fingerprinting stored in SQLite. When a post is detected for the first time, it is indexed and dispatched to configured webhooks. On subsequent polling cycles, identical posts are recognized as already indexed and skipped to prevent duplicate alerts or database bloat.
</details>

<details>
<summary><b>How many Facebook pages can I monitor simultaneously?</b></summary>
<br/>

You can pass multiple comma-separated page names (e.g. `--page QCGov,ManilaPIO,PasigInfo`). specter leverages a configurable multi-threaded worker pool (`--workers 4`) to poll all configured pages concurrently in parallel.
</details>

<details>
<summary><b>Do I need a Facebook account or personal cookies?</b></summary>
<br/>

No. specter operates exclusively on ephemeral public visitor sessions (`datr`). You never supply personal account credentials (`c_user` or `xs`), which completely eliminates account ban risks.
</details>

<details>
<summary><b>How do I send posts to n8n, Make, Discord, or Telegram?</b></summary>
<br/>

Pass `--webhook <URL>` to the CLI or set `SPECTER_WEBHOOK_URL` in Docker. Whenever a fresh post is indexed, specter immediately dispatches an HTTP POST payload with structured JSON containing post text, media links, and metadata. See the **[Integrations Hub](docs/integrations/README.md)** for n8n, Discord, Telegram, and custom webhook guides.
</details>

<details>
<summary><b>Can I run specter in Docker or on a self-hosted VPS?</b></summary>
<br/>

Yes. The repository includes an official `Dockerfile` and `docker-compose.yml` pre-configured with headless Chromium and persistent volume storage (`docker compose up -d`).
</details>

<details>
<summary><b>What happens if Meta updates its frontend layout?</b></summary>
<br/>

specter is self-healing. If Meta rotates visitor token schemas or edge parameters causing Fast HTTP (Tier 1) to encounter a barrier, the engine automatically falls back to stealth Playwright (Tier 2) to renew the session cookie jar.
</details>

---

## Ecosystem and Acknowledgments

- Built using the **[Reverse Engineer Anything (REA)](https://github.com/morluto/rea)** skill.
- Optimized with **[Gate-MCP](https://github.com/Dukeabaddon/Gate-MCP)** for context-efficient agent development.
- Designed as a robust data extraction subsystem for downstream civic and monitoring projects (such as OpenSuspension-PH).

---

## Disclaimer

This project is an independent open-source research tool designed for automated collection of publicly accessible web content. Users are responsible for complying with applicable website terms of service and local data protection regulations.

---

<div align="center">

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Dukeabaddon/specter&type=Date)](https://star-history.com/#Dukeabaddon/specter&Date)

</div>
