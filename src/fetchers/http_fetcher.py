import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ..models import Post
from .base import BaseFetcher

logger = logging.getLogger(__name__)

DEFAULT_COOKIES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "cookies.json"

class HttpFetcher(BaseFetcher):
    def __init__(self, cookies_path: Optional[Path] = None):
        self.cookies_path = cookies_path or DEFAULT_COOKIES_PATH
        self.session = requests.Session()
        self._init_session()

    def _init_session(self):
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
        })
        self._load_cookies()

    def _load_cookies(self):
        if self.cookies_path.exists():
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                for c in cookies:
                    self.session.cookies.set(
                        c["name"], c["value"],
                        domain=c.get("domain", ".facebook.com"),
                        path=c.get("path", "/")
                    )
                logger.info(f"[HttpFetcher] Loaded {len(cookies)} cookies into session")
            except Exception as e:
                logger.warning(f"[HttpFetcher] Failed to load cookies: {e}")

    def fetch_posts(self, page_name: str, limit: int = 5) -> List[Post]:
        url = f"https://www.facebook.com/{page_name.strip('/')}"
        logger.info(f"[HttpFetcher] GET {url}")
        
        try:
            resp = self.session.get(url, timeout=12)
        except Exception as e:
            logger.warning(f"[HttpFetcher] HTTP request failed: {e}")
            return []

        if resp.status_code != 200:
            logger.warning(f"[HttpFetcher] Unexpected HTTP status: {resp.status_code}")
            return []

        html = resp.text
        if len(html) < 2000 or "Sorry, something went wrong" in html:
            logger.warning("[HttpFetcher] Received error page or checkpoint HTML")
            return []

        posts = self._parse_relay_html(html, page_name, limit)
        logger.info(f"[HttpFetcher] Extracted {len(posts)} posts from HTTP response")
        return posts

    def _parse_relay_html(self, html: str, page_name: str, limit: int) -> List[Post]:
        """
        Parses modern Comet SSR script tags for post objects.
        """
        soup = BeautifulSoup(html, "html.parser")
        script_tags = soup.find_all("script", attrs={"type": "application/json"})
        
        extracted_posts: List[Post] = []
        seen_ids = set()

        for tag in script_tags:
            content = tag.string
            if not content or "RelayPrefetchedStreamCache" not in content and "comet_sections" not in content and "feedback" not in content:
                continue

            # Search for message text patterns inside Relay JSON
            # Pattern: "message":{"text":"..."}
            message_matches = re.finditer(r'"message":\s*\{\s*"text":\s*"([^"]+)"', content)
            url_matches = re.findall(r'https://www\.facebook\.com/' + re.escape(page_name) + r'/posts/([a-zA-Z0-9_-]+)', content)
            
            for m in message_matches:
                raw_text = m.group(1)
                try:
                    clean_text = json.loads(f'"{raw_text}"')
                except Exception:
                    clean_text = raw_text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
                clean_text = clean_text.strip()
                if len(clean_text) < 20:
                    continue

                # Generate deterministic post ID using sha256 of text if permalink ID not present
                import hashlib
                text_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()[:12]
                post_id = url_matches[len(extracted_posts)] if len(url_matches) > len(extracted_posts) else f"post_{text_hash}"
                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                post_url = f"https://www.facebook.com/{page_name}/posts/{post_id}" if not post_id.startswith("http_") else f"https://www.facebook.com/{page_name}"
                
                extracted_posts.append(Post(
                    post_id=post_id,
                    page_name=page_name,
                    text=clean_text,
                    url=post_url,
                    raw_metadata={"source": "http_relay_json"}
                ))
                if len(extracted_posts) >= limit:
                    break

            if len(extracted_posts) >= limit:
                break

        return extracted_posts
