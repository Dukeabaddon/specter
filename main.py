#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
from pathlib import Path

from src.models import Post
from src.storage.db import PostDatabase
from src.classifier.suspension import SuspensionClassifier
from src.fetchers.hybrid import HybridFetcher
from src.scheduler.runner import MonitorRunner

def setup_logging(json_mode: bool = False):
    level = logging.WARNING if json_mode else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr if json_mode else sys.stdout
    )

def main():
    default_page = os.environ.get("SPECTER_PAGE", "QCGov")
    default_webhook = os.environ.get("SPECTER_WEBHOOK_URL", None)
    default_interval = int(os.environ.get("SPECTER_INTERVAL", "300"))
    default_mode = os.environ.get("SPECTER_MODE", "auto")

    parser = argparse.ArgumentParser(
        description="specter: Self-hosted Facebook Public Page Monitoring Engine"
    )
    parser.add_argument(
        "--page",
        type=str,
        default=default_page,
        help=f"Target Facebook page(s), comma-separated (default: {default_page})"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["auto", "http", "playwright"],
        default=default_mode,
        help="Fetcher engine mode (default: auto)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of latest posts to inspect (default: 5)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (default behavior unless --monitor is set)"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run continuous daemon loop"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=default_interval,
        help=f"Monitoring poll interval in seconds (default: {default_interval})"
    )
    parser.add_argument(
        "--webhook",
        type=str,
        default=default_webhook,
        help="Webhook URL to POST when a new post is detected (e.g. n8n, Discord, Make)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as structured JSON to stdout for piping or automation"
    )
    parser.add_argument(
        "--db-list",
        action="store_true",
        help="List stored posts from local SQLite database"
    )
    parser.add_argument(
        "--db-suspensions",
        action="store_true",
        help="List detected class suspension announcements from DB"
    )
    parser.add_argument(
        "--test-classifier",
        action="store_true",
        help="Run verification test suite on Philippine class suspension classifier"
    )

    args = parser.parse_args()
    setup_logging(json_mode=args.json)
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
        if args.json:
            print(json.dumps([p.to_dict() for p in posts], indent=2))
        else:
            print(f"\n=== Stored Posts in Database ({len(posts)} total) ===")
            for p in posts:
                susp_mark = "🚨 [SUSPENSION]" if p.is_suspension else "  "
                print(f"{susp_mark} [{p.post_id}] {p.page_name} | {p.scraped_at}")
                print(f"    URL: {p.url}")
                print(f"    Text: {p.text[:120].replace(chr(10), ' ')}...")
        return

    if args.db_suspensions:
        posts = db.get_suspension_posts(limit=20)
        if args.json:
            print(json.dumps([p.to_dict() for p in posts], indent=2))
        else:
            print(f"\n=== Detected Class Suspension Announcements ({len(posts)} found) ===")
            for p in posts:
                print(f"🚨 [{p.post_id}] {p.page_name} | {p.scraped_at}")
                print(f"    URL: {p.url}")
                print(f"    Details: {p.suspension_details}")
                print(f"    Text: {p.text}\n")
        return

    pages = [p.strip() for p in args.page.split(",") if p.strip()]
    fetcher = HybridFetcher(mode=args.mode)
    runner = MonitorRunner(
        pages=pages,
        db=db,
        fetcher=fetcher,
        webhook_url=args.webhook
    )

    if args.monitor:
        runner.run_continuous(interval_seconds=args.interval)
    else:
        summary = runner.poll_once()
        latest = []
        for page in pages:
            latest.extend(db.get_latest_posts(page_name=page, limit=args.limit))

        if args.json:
            print(json.dumps([p.to_dict() for p in latest], indent=2))
        else:
            print(f"\nRunning single poll on {pages} with mode='{args.mode}'...")
            print(f"\n=== Poll Complete ===")
            print(f"New Posts Stored: {summary['new_posts_found']}")
            print(f"Suspensions Detected: {summary['suspensions_detected']}")
            if args.webhook:
                print(f"Webhook Configured: {args.webhook}")

            print(f"\n--- Latest Posts ({len(latest)} retrieved) ---")
            for i, p in enumerate(latest):
                flag = " [CLASS SUSPENSION!]" if p.is_suspension else ""
                print(f"\nPost #{i+1}{flag}:")
                print(f"  ID: {p.post_id}")
                print(f"  Page: {p.page_name}")
                print(f"  URL: {p.url}")
                print(f"  Images: {len(p.images)} found")
                print(f"  Snippet: {p.text[:200].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    main()
