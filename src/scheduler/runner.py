import time
import logging
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
        on_new_post: Optional[Callable[[Post], None]] = None,
        on_suspension_alert: Optional[Callable[[Post], None]] = None,
    ):
        self.pages = pages
        self.db = db or PostDatabase()
        self.fetcher = fetcher or HybridFetcher(mode="auto")
        self.on_new_post = on_new_post
        self.on_suspension_alert = on_suspension_alert

    def poll_once(self) -> Dict[str, Any]:
        """
        Polls all configured pages once.
        Returns a summary dict.
        """
        summary = {
            "polled_pages": len(self.pages),
            "new_posts_found": 0,
            "suspensions_detected": 0,
            "details": []
        }

        for page in self.pages:
            logger.info(f"[MonitorRunner] Checking page: {page}")
            try:
                posts = self.fetcher.fetch_posts(page, limit=5)
            except Exception as e:
                logger.error(f"[MonitorRunner] Error fetching {page}: {e}")
                continue

            page_new_count = 0
            page_suspensions = 0

            for post in posts:
                # Check deduplication
                if self.db.exists(post.post_id):
                    continue

                # Run suspension classifier
                classification = SuspensionClassifier.classify(post.text)
                post.is_suspension = classification["is_suspension"]
                post.suspension_details = classification

                # Save to DB
                inserted = self.db.save_post(post)
                if inserted:
                    page_new_count += 1
                    logger.info(f"[MonitorRunner] NEW POST [{post.post_id}] from {page} (Suspension: {post.is_suspension})")
                    
                    if self.on_new_post:
                        try:
                            self.on_new_post(post)
                        except Exception as e:
                            logger.error(f"Error in on_new_post callback: {e}")

                    if post.is_suspension:
                        page_suspensions += 1
                        logger.warning(
                            f"\n{'='*50}\n🚨 CLASS SUSPENSION DETECTED!\nPage: {page}\nURL: {post.url}\nDetails: {classification}\nSnippet: {post.text[:200]}...\n{'='*50}\n"
                        )
                        if self.on_suspension_alert:
                            try:
                                self.on_suspension_alert(post)
                            except Exception as e:
                                logger.error(f"Error in on_suspension_alert callback: {e}")

            summary["new_posts_found"] += page_new_count
            summary["suspensions_detected"] += page_suspensions
            summary["details"].append({
                "page": page,
                "posts_checked": len(posts),
                "new_posts": page_new_count,
                "suspensions": page_suspensions
            })

        return summary

    def run_continuous(self, interval_seconds: int = 300):
        """
        Runs polling loop indefinitely every interval_seconds (default: 5 minutes).
        """
        logger.info(f"[MonitorRunner] Starting continuous monitor for {self.pages} every {interval_seconds}s...")
        try:
            while True:
                logger.info(f"[MonitorRunner] Starting poll iteration at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
                summary = self.poll_once()
                logger.info(f"[MonitorRunner] Poll summary: {summary['new_posts_found']} new posts, {summary['suspensions_detected']} suspensions.")
                logger.info(f"[MonitorRunner] Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("[MonitorRunner] Stopped by user.")
