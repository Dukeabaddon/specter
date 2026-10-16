# Discord Webhook Integration Guide

Route Facebook public page posts directly into a Discord channel using Discord Incoming Webhooks.

---

## 1. Setup in Discord (1 Minute)

1. Open your Discord server.
2. Go to **Server Settings** > **Integrations** > **Webhooks**.
3. Click **New Webhook**.
4. Choose the channel where alerts should appear.
5. Click **Copy Webhook URL** (e.g. `https://discord.com/api/webhooks/123456789/abcdef...`).

---

## 2. Option A: Route via n8n (Recommended for Rich Embeds)

Discord's native webhook endpoint expects a specific payload format (`{"content": "..."}` or `{"embeds": [...]}`).  
Using specter with [n8n](n8n.md) allows you to format posts into beautiful rich embed cards with clickable titles, high-resolution photo attachments, and suspension alert badges.

See the ready-to-import template in the **[n8n Automation Guide](n8n.md)**.

---

## 3. Option B: Direct CLI Pipeline (Unix Pipe)

You can pipe specter's structured JSON output directly to Discord via a lightweight shell script:

```bash
#!/usr/bin/env bash
DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"

python3 main.py --page QCGov --limit 1 --json | python3 -c "
import sys, json, requests

posts = json.load(sys.stdin)
if not posts:
    sys.exit(0)

post = posts[0]
title = f'[NEW POST] {post[\"page_name\"]}'
text_snippet = post['text'][:500]

payload = {
    'embeds': [{
        'title': title,
        'description': text_snippet,
        'url': post['url'],
        'color': 5814783,
        'timestamp': post.get('published_at') or post['scraped_at'],
        'image': {'url': post['images'][0]} if post.get('images') else None
    }]
}

requests.post('$DISCORD_WEBHOOK', json=payload)
"
```

---

## 4. Option C: Docker Environment Variable

Set up automated background monitoring with direct alerts:

```bash
export SPECTER_PAGE="QCGov,ManilaPIO"
export SPECTER_INTERVAL=300
export SPECTER_WEBHOOK_URL="http://your-webhook-transformer-or-n8n/webhook"

docker compose up -d
```
