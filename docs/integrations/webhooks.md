# Custom Webhooks & API Integration Specification

Connect specter to custom HTTP backends, FastAPI/Flask services, Node.js/Express APIs, Make.com, or Zapier.

---

## 1. Webhook Dispatch Architecture

When specter runs in daemon mode (`--monitor`), it evaluates each page against the local SQLite database.
When a newly detected post is inserted, specter dispatches an asynchronous HTTP POST to the URL specified by `--webhook <URL>` or `SPECTER_WEBHOOK_URL`.

- **HTTP Method:** `POST`
- **Content-Type:** `application/json`
- **Timeout:** 10.0 seconds
- **Delivery:** Immediate upon discovery

---

## 2. Complete JSON Payload Schema

```json
{
  "event": "post.new",
  "page": "QCGov",
  "post": {
    "post_id": "pfbid02cGhjwL7PuszhaTHCKPne12J4VLCGx5v9myQMy4EgNy91adyxU7eTaZ3hvfNAmc5yl",
    "page_name": "QCGov",
    "text": "Dininig namin ang inyong hiling, QCitizens! Ang Madulang Sabayang Pagbigkas Competition ay bukas na...",
    "url": "https://www.facebook.com/QCGov/posts/pfbid02cGhjwL7PuszhaTHCKPne12J4VLCGx5v9myQMy4EgNy91adyxU7eTaZ3hvfNAmc5yl",
    "published_at": "2026-10-16T08:00:00Z",
    "scraped_at": "2026-10-16T08:05:12.341209+00:00",
    "images": [
      "https://scontent.fmnl...jpg"
    ],
    "video": null,
    "is_suspension": false,
    "suspension_details": null,
    "raw_metadata": {
      "source": "http_relay_json"
    }
  },
  "is_suspension": false,
  "suspension_details": null
}
```

---

## 3. Fast FastAPI / Express Backend Example

### Python (FastAPI)
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/facebook-posts")
async def handle_post(request: Request):
    data = await request.json()
    post = data["post"]
    print(f"Received new post from {data['page']}: {post['post_id']}")
    print(f"Snippet: {post['text'][:100]}")
    return {"status": "ok"}
```

### Node.js (Express)
```javascript
const express = require("express");
const app = express();
app.use(express.json());

app.post("/webhook/facebook-posts", (req, res) => {
  const { page, post } = req.body;
  console.log(`New post from ${page}: ${post.url}`);
  res.sendStatus(200);
});

app.listen(3000);
```

---

## 4. Make.com / Zapier Setup
1. In Make or Zapier, create a **Custom Webhook** trigger module.
2. Copy the generated Webhook URL.
3. Launch specter:
   ```bash
   python main.py --page QCGov --monitor --webhook "https://hook.eu1.make.com/YOUR_WEBHOOK_KEY"
   ```
4. Perform a test run: the data structure maps automatically into variables for Google Sheets, Airtable, or email alerts.
