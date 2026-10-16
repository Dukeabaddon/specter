#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

from src.models import Post
from src.storage.db import PostDatabase
from src.classifier.suspension import SuspensionClassifier
from src.fetchers.hybrid import HybridFetcher
from src.scheduler.runner import MonitorRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fb-post-monitor")

def main():
    parser = argparse.ArgumentParser(description="fb-post-monitor: Self-hosted Facebook Page Monitoring System")
    parser.add_argument("--page", type=str, default="QCGov", help="Facebook page name (e.g. QCGov)")
    parser.add_argument("--mode", type=str, choices=["auto", "http", "playwright"], default="auto", help="Fetcher engine mode")
    parser.add_argument("--limit", type=int, default=5, help="Number of latest posts to inspect")
    parser.add_argument("--once", action="store_true", help="Run once and output results (default if not --monitor)")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring loop")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds (default 300 = 5 mins)")
    parser.add_argument("--db-list", action="store_true", help="List stored posts from SQLite database")
    parser.add_argument("--db-suspensions", action="store_true", help="List detected class suspension announcements from DB")
    parser.add_argument("--test-classifier", action="store_true", help="Run self-test on Philippine class suspension classifier")

    args = parser.parse_args()
    db = PostDatabase()

    if args.test_classifier:
        print("=== Testing Class Suspension Classifier ===")
        test_samples = [
            ("WALANG PASOK: Dahil sa Bagyong Kristine, suspendido ang klase sa lahat ng antas, pampubliko at pribado sa Quezon City bukas.", True),
            ("ADVISORY: Dahil sa mataas na Heat Index na aabot sa 43C, walang pasok sa pre-school hanggang senior high school bukas.", True),
            ("Inaanyayahan ang lahat sa QC Pangkabuhayan Fair ngayong darating na Sabado sa QC Hall.", False),
            ("Suspension of classes in all levels (public and private) due to heavy rainfall warning.", True),
            ("Congratulations to our QC athletes for winning the championship!", False),
        ]
        all_passed = True
        for text, expected in test_samples:
            res = SuspensionClassifier.classify(text)
            status = "PASS" if res["is_suspension"] == expected else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"[{status}] Expected: {expected} | Got: {res['is_suspension']} (Conf: {res['confidence']})")
            print(f"   Snippet: {text[:80]}...")
            if res["is_suspension"]:
                print(f"   Details: Levels={res['levels']}, Reasons={res['reasons']}")
        print(f"\nClassifier test finished: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
        return

    if args.db_list:
        posts = db.get_latest_posts(limit=20)
        print(f"\n=== Stored Posts in Database ({len(posts)} total) ===")
        for p in posts:
            susp_mark = "🚨 [SUSPENSION]" if p.is_suspension else "  "
            print(f"{susp_mark} [{p.post_id}] {p.page_name} | {p.scraped_at}")
            print(f"    URL: {p.url}")
            print(f"    Text: {p.text[:120].replace(chr(10), ' ')}...")
        return

    if args.db_suspensions:
        posts = db.get_suspension_posts(limit=20)
        print(f"\n=== Detected Class Suspension Announcements ({len(posts)} found) ===")
        for p in posts:
            print(f"🚨 [{p.post_id}] {p.page_name} | {p.scraped_at}")
            print(f"    URL: {p.url}")
            print(f"    Details: {p.suspension_details}")
            print(f"    Text: {p.text}\n")
        return

    fetcher = HybridFetcher(mode=args.mode)
    runner = MonitorRunner(pages=[args.page], db=db, fetcher=fetcher)

    if args.monitor:
        runner.run_continuous(interval_seconds=args.interval)
    else:
        print(f"\nRunning single poll on '{args.page}' with mode='{args.mode}'...")
        summary = runner.poll_once()
        print(f"\n=== Poll Complete ===")
        print(f"New Posts Stored: {summary['new_posts_found']}")
        print(f"Suspensions Detected: {summary['suspensions_detected']}")
        
        # Display latest posts
        latest = db.get_latest_posts(page_name=args.page, limit=args.limit)
        print(f"\n--- Latest Posts for {args.page} ---")
        for i, p in enumerate(latest):
            flag = " [CLASS SUSPENSION!]" if p.is_suspension else ""
            print(f"\nPost #{i+1}{flag}:")
            print(f"  ID: {p.post_id}")
            print(f"  URL: {p.url}")
            print(f"  Images: {len(p.images)} found")
            print(f"  Snippet: {p.text[:250].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    main()
