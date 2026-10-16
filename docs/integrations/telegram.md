# Telegram Bot Integration Guide

Broadcast real-time Facebook page updates to a Telegram channel or group using the Telegram Bot API.

---

## 1. Prerequisites (Get Bot Token & Chat ID)

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`, choose a name, and copy the **API Token** (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
3. Add your new bot as an **Administrator** in your target Telegram Channel or Group.
4. Obtain your `CHAT_ID` (for public channels, this is `@channel_name`; for private channels, it begins with `-100...`).

---

## 2. Option A: Route via n8n (Recommended)

The easiest and most flexible method is routing specter through n8n:
1. specter sends the standard post JSON payload to n8n.
2. In n8n, use the **Telegram** node with the action **Send Message** or **Send Photo**.
3. Map `{{ $json.body.post.text }}` to the message text and `{{ $json.body.post.images[0] }}` to the photo attachment.

See the ready-to-import template in the **[n8n Automation Guide](n8n.md)**.

---

## 3. Option B: Direct Telegram Script via CLI JSON Pipe

For zero-dependency deployments on Linux or macOS, pipe specter directly to Telegram's REST API:

```bash
#!/usr/bin/env bash
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID="YOUR_CHAT_ID_OR_CHANNEL"

python3 main.py --page QCGov --limit 1 --json | python3 -c "
import sys, json, requests

posts = json.load(sys.stdin)
if not posts:
    sys.exit(0)

p = posts[0]
msg = f\"<b>[NEW POST] {p['page_name']}</b>\n\n{p['text'][:400]}...\n\n<a href='{p['url']}'>Read on Facebook</a>\"

if p.get('images'):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    requests.post(url, data={'chat_id': CHAT_ID, 'caption': msg, 'parse_mode': 'HTML', 'photo': p['images'][0]})
else:
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': False})
"
```
