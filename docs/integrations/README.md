# specter Integrations Hub

Connect **specter** to your downstream automation pipelines, alert channels, and custom microservices.

---

## Supported Integrations & Guides

| Target | Guide | Description |
|---|---|---|
| **n8n** | [n8n Workflow Guide](n8n.md) | Ready-to-import n8n workflow for Discord, Telegram, and database routing |
| **Discord** | [Discord Webhook Guide](discord.md) | Push rich embed alert cards directly into Discord channels |
| **Telegram** | [Telegram Bot Guide](telegram.md) | Broadcast instant post advisories to Telegram channels and groups |
| **HTTP Webhooks** | [Custom Webhooks Guide](webhooks.md) | Standard JSON schema for Make.com, Zapier, FastAPI, and custom backends |

---

## How It Works

Specter features a universal webhook dispatcher. When a new post is detected and verified against the SQLite deduplication cache:

1. Specter serializes the post into standard JSON.
2. It sends an asynchronous HTTP POST request to your configured `--webhook <URL>` (or `SPECTER_WEBHOOK_URL`).
3. If configured with `--json`, it streams the post array directly to `stdout` for UNIX piping (`| jq` or bash scripts).

```
+-----------------------------------------------------------+
|                      specter Engine                       |
|   (Polls public page every 5m -> SQLite deduplication)    |
+-----------------------------+-----------------------------+
                              |
                     HTTP POST Webhook
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
   [n8n Workflow]      [Discord Channel]    [Telegram Bot / API]
```
