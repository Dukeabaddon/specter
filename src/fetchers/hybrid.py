import logging
from typing import List, Optional
from ..models import Post
from .base import BaseFetcher
from .http_fetcher import HttpFetcher
from .playwright_fetcher import PlaywrightFetcher

logger = logging.getLogger(__name__)

class HybridFetcher(BaseFetcher):
    def __init__(self, mode: str = "auto", headless: bool = True):
        """
        mode: 'auto' (Tier 1 HTTP -> fallback to Tier 2 Playwright),
              'http' (HTTP only),
              'playwright' (Playwright only)
        """
        self.mode = mode.lower()
        self.http_fetcher = HttpFetcher()
        self.playwright_fetcher = PlaywrightFetcher(headless=headless)

    def fetch_posts(self, page_name: str, limit: int = 5) -> List[Post]:
        if self.mode == "http":
            return self.http_fetcher.fetch_posts(page_name, limit)
        elif self.mode == "playwright":
            return self.playwright_fetcher.fetch_posts(page_name, limit)

        # Mode: 'auto' (Dual-Mode)
        logger.info(f"[HybridFetcher] Attempting Tier 1 (Fast HTTP) for '{page_name}'...")
        posts = self.http_fetcher.fetch_posts(page_name, limit)
        if posts:
            logger.info(f"[HybridFetcher] Tier 1 HTTP succeeded with {len(posts)} posts!")
            return posts

        logger.info(f"[HybridFetcher] Tier 1 yielded 0 posts. Seamlessly switching to Tier 2 (Stealth Playwright)...")
        posts = self.playwright_fetcher.fetch_posts(page_name, limit)
        if posts:
            logger.info(f"[HybridFetcher] Tier 2 Playwright succeeded with {len(posts)} posts and updated session cookies!")
        else:
            logger.warning(f"[HybridFetcher] Both Tier 1 and Tier 2 yielded 0 posts for '{page_name}'.")
            
        return posts
