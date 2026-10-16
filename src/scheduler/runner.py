import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Optional, Dict, Any

from ..models import Post
from ..storage.db import PostDatabase
from ..classifier.suspension import SuspensionClassifier
from ..fetchers.hybrid import HybridFetcher

logger = logging.getLogger(__name__)

class MonitorRunner:
    def __init__(
        self,
        pages: List[str],
        db: Optional[PostDatabase] = None,
        fetcher: Optional[HybridFetcher] = None,
        webhook_url: Optional[str] = None,
        max_workers: int = 4,
        on_new_post: Optional[Callable[[Post], None]] = None,
        on_suspension_alert: Optional[Callable[[Post], None]] = None,
    ):
        self.pages = pages
        self.db = db or PostDatabase()
        self.fetcher = fetcher or HybridFetcher(mode="auto")
        self.webhook_url = webhook_url
        self.max_workers = max_workers
        self.on_new_post = on_new_post
        self.on_suspension_alert = on_suspension_alert

    def _dispatch_webhook(self, post: Post):
        if not self.webhook_url:
            return
        import httpx
        payload = {
            "event": "post.new",
            "page": post.page_name,
            "post": post.to_dict(),
            "is_suspension": post.is_suspension,
            "suspension_details": post.suspension_details
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                logger.info(f"[Webhook] Dispatched post {post.post_id} -> {self.webhook_url} ({resp.status_code})")
        except Exception as e:
            logger.error(f"[Webhook] Failed to dispatch post {post.post_id} to {self.webhook_url}: {e}")

    def _poll_single_page(self, page: str) -> Dict[str, Any]:
        """
        Polls a single Facebook page, checks SQLite deduplication,
        applies classification, and fires hooks/webhooks for new posts.
        """
        logger.info(f"[MonitorRunner] Checking page: {page}")
        result = {
            "page": page,
            "posts_checked": 0,
            "new_posts": 0,
            "duplicates_skipped": 0,
            "suspensions": 0,
            "error": None
        }

        try:
            posts = self.fetcher.fetch_posts(page, limit=5)
            result["posts_checked"] = len(posts)
        except Exception as e:
            logger.error(f"[MonitorRunner] Error fetching {page}: {e}")
            result["error"] = str(e)
            return result

        for post in posts:
            if self.db.exists(post.post_id):
                result["duplicates_skipped"] += 1
                continue

            classification = SuspensionClassifier.classify(post.text)
            post.is_suspension = classification["is_suspension"]
            post.suspension_details = classification

            inserted = self.db.save_post(post)
            if inserted:
                result["new_posts"] += 1
                logger.info(f"[MonitorRunner] NEW POST [{post.post_id}] from {page} (Suspension: {post.is_suspension})")

                if self.on_new_post:
                    try:
                        self.on_new_post(post)
                    except Exception as e:
                        logger.error(f"Error in on_new_post callback: {e}")

                self._dispatch_webhook(post)

                if post.is_suspension:
                    result["suspensions"] += 1
                    logger.warning(
                        f"\n{'='*50}\n[ALERT] CLASS SUSPENSION DETECTED!\nPage: {page}\nURL: {post.url}\nDetails: {classification}\nSnippet: {post.text[:200]}...\n{'='*50}\n"
                    )
                    if self.on_suspension_alert:
                        try:
                            self.on_suspension_alert(post)
                        except Exception as e:
                            logger.error(f"Error in on_suspension_alert callback: {e}")

        return result

    def poll_once(self) -> Dict[str, Any]:
        """
        Polls all configured pages. Uses concurrent worker pool if multiple pages are configured.
        Returns a summary dict.
        """
        summary = {
            "polled_pages": len(self.pages),
            "new_posts_found": 0,
            "duplicates_skipped": 0,
            "suspensions_detected": 0,
            "details": []
        }

        if len(self.pages) <= 1:
            for page in self.pages:
                res = self._poll_single_page(page)
                summary["new_posts_found"] += res["new_posts"]
                summary["duplicates_skipped"] += res["duplicates_skipped"]
                summary["suspensions_detected"] += res["suspensions"]
                summary["details"].append(res)
            return summary

        # Multi-page concurrent polling worker pool
        workers = min(len(self.pages), self.max_workers)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_page = {executor.submit(self._poll_single_page, page): page for page in self.pages}
            for future in as_completed(future_to_page):
                res = future.result()
                summary["new_posts_found"] += res["new_posts"]
                summary["duplicates_skipped"] += res["duplicates_skipped"]
                summary["suspensions_detected"] += res["suspensions"]
                summary["details"].append(res)

        return summary

    def run_continuous(self, interval_seconds: int = 300):
        """
        Runs polling loop indefinitely every interval_seconds (default: 5 minutes).
        """
        logger.info(f"[MonitorRunner] Starting continuous monitor for {self.pages} (pool size: {self.max_workers}) every {interval_seconds}s...")
        try:
            while True:
                logger.info(f"[MonitorRunner] Starting poll iteration at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
                summary = self.poll_once()
                logger.info(
                    f"[MonitorRunner] Poll summary: {summary['new_posts_found']} new posts, "
                    f"{summary['duplicates_skipped']} duplicates skipped, {summary['suspensions_detected']} suspensions."
                )
                logger.info(f"[MonitorRunner] Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("[MonitorRunner] Stopped by user.")
