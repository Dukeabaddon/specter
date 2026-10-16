# n8n Automation & Webhook Integration Guide

Connect **specter** to [n8n](https://n8n.io) to automate downstream workflows (Discord alerts, Telegram bots, SMS, Google Sheets, or custom databases) whenever target Facebook pages publish new posts.

---

## Architecture Overview

```
+-----------------------------------------------------------+
|                      specter Engine                       |
|   (Polls public page every 5m -> SQLite deduplication)    |
+-----------------------------+-----------------------------+
                              |
                     HTTP POST Webhook
                              |
                              v
+-----------------------------------------------------------+
|                     n8n Webhook Node                      |
|                  Path: /webhook/fb-posts                  |
+-----------------------------+-----------------------------+
                              |
                              v
             +----------------+----------------+
             |                                 |
             v                                 v
   [Discord / Telegram Alert]         [Database / CRM Sync]
```

---

## 1. Webhook Payload Schema

When a new post is detected and saved, specter sends an HTTP POST request with `Content-Type: application/json`:

```json
{
  "event": "post.new",
  "page": "QCGov",
  "post": {
    "post_id": "pfbid02cGhjwL7PuszhaTHCKPne12J4VLCGx5v9myQMy4EgNy91adyxU7eTaZ3hvfNAmc5yl",
    "page_name": "QCGov",
    "text": "ADVISORY: Dahil sa inaasahang mataas na Heat Index bukas, suspendido ang klase sa lahat ng antas...",
    "url": "https://www.facebook.com/QCGov/posts/pfbid02cGhjwL7PuszhaTHCKPne12J4VLCGx5v9myQMy4EgNy91adyxU7eTaZ3hvfNAmc5yl",
    "published_at": "2026-10-16T08:00:00Z",
    "scraped_at": "2026-10-16T08:05:12.341209+00:00",
    "images": [
      "https://scontent.fmnl...jpg"
    ],
    "video": null,
    "is_suspension": true,
    "suspension_details": {
      "is_suspension": true,
      "confidence": 0.95,
      "levels": ["all_levels"],
      "reasons": ["heat_index"]
    }
  },
  "is_suspension": true,
  "suspension_details": {
    "is_suspension": true,
    "confidence": 0.95,
    "levels": ["all_levels"],
    "reasons": ["heat_index"]
  }
}
```

---

## 2. Setting Up in n8n (2 Minutes)

### Step 1: Create a Webhook Node in n8n
1. Open your n8n workspace and add a **Webhook** node.
2. Configure:
   - **HTTP Method:** `POST`
   - **Path:** `fb-posts`
   - **Response Mode:** `On Received`
   - **Response Code:** `200`
3. Copy the **Production Webhook URL** (e.g. `http://n8n:5678/webhook/fb-posts` or `https://n8n.yourdomain.com/webhook/fb-posts`).

### Step 2: Configure specter with the Webhook
Pass the webhook URL via the CLI or environment variable:

```bash
# Via CLI argument
python main.py --page QCGov --monitor --interval 300 --webhook https://n8n.yourdomain.com/webhook/fb-posts

# Or via Environment Variable
export SPECTER_WEBHOOK_URL="https://n8n.yourdomain.com/webhook/fb-posts"
python main.py --monitor
```

---

## 3. Ready-to-Import n8n Workflow

You can copy the JSON block below and paste it directly onto your n8n canvas (`Ctrl+V` / `Cmd+V`):

```json
{
  "name": "specter Facebook Post Monitor",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "fb-posts",
        "options": {}
      },
      "id": "webhook-trigger",
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.body.is_suspension }}",
              "value2": true
            }
          ]
        }
      },
      "id": "filter-suspension",
      "name": "Is Class Suspension?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "content": "=[ALERT] CLASS SUSPENSION DETECTED!\n\nPage: {{ $json.body.page }}\nDetails: {{ $json.body.post.text }}\n\nPost Link: {{ $json.body.post.url }}"
      },
      "id": "discord-alert",
      "name": "Send Discord Alert",
      "type": "n8n-nodes-base.discord",
      "typeVersion": 2,
      "position": [700, 200]
    },
    {
      "parameters": {
        "content": "=New Facebook Post from {{ $json.body.page }}:\n\n{{ $json.body.post.text }}\n\nURL: {{ $json.body.post.url }}"
      },
      "id": "general-notification",
      "name": "Log Standard Post",
      "type": "n8n-nodes-base.discord",
      "typeVersion": 2,
      "position": [700, 400]
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [
        [
          {
            "node": "Is Class Suspension?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is Class Suspension?": {
      "main": [
        [
          {
            "node": "Send Discord Alert",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Log Standard Post",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 4. Docker Compose: Running specter with n8n

To run both `specter` and `n8n` together on the same Docker bridge network:

```yaml
version: "3.8"

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n-server
    restart: unless-stopped
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n

  specter:
    build: .
    container_name: specter-monitor
    restart: unless-stopped
    environment:
      - SPECTER_PAGE=QCGov,ManilaPIO
      - SPECTER_INTERVAL=300
      - SPECTER_WEBHOOK_URL=http://n8n:5678/webhook/fb-posts
    volumes:
      - specter_data:/app/data
    depends_on:
      - n8n

volumes:
  n8n_data:
  specter_data:
```

Once running with `docker compose up -d`:
- specter checks target pages every 5 minutes.
- When a new post is verified, it immediately POSTs to `http://n8n:5678/webhook/fb-posts`.
- Deduplication is preserved across container restarts via the `specter_data` SQLite volume.

---

## 5. Alternative: n8n "Execute Command" Node

If you prefer executing on-demand rather than running a background daemon:
1. Add an **Execute Command** node in n8n.
2. Set Command to:
   ```bash
   python /path/to/specter/main.py --page QCGov --limit 1 --json
   ```
3. Enable **JSON Output Parsing**. The post objects become native n8n items ready for immediate downstream mapping.
