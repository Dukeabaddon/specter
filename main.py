#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
from pathlib import Path

from src.models import Post
from src.storage.db import PostDatabase
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

    parser = argparse.ArgumentParser(
        description="specter: Self-hosted, ban-resilient Facebook public page scraper and monitor."
    )
    parser.add_argument(
        "--page",
        default=default_page,
        help="Target Facebook page handle or slug, or comma-separated list of pages (e.g. 'QCGov,ManilaPIO')."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "http", "playwright"],
        default="auto",
        help="Fetching mode: 'auto' (fast HTTP relay first, stealth browser fallback), 'http', or 'playwright'."
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run continuously as a monitoring daemon, polling at set intervals."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=default_interval,
        help="Poll interval in seconds when running in --monitor mode (default: 300)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum posts to extract per check (default: 5)"
    )
    parser.add_argument(
        "--webhook",
        default=default_webhook,
        help="Webhook URL to HTTP POST newly discovered posts (e.g. for n8n, Discord, Make)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output extracted posts as clean structured JSON to stdout for piping (suppresses logs)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Max concurrent worker threads for multi-page polling (default: 4)"
    )
    parser.add_argument(
        "--db-list",
        action="store_true",
        help="List stored posts from local SQLite database"
    )

    args = parser.parse_args()
    setup_logging(json_mode=args.json)
    db = PostDatabase()

    if args.db_list:
        posts = db.get_latest_posts(limit=20)
        if args.json:
            print(json.dumps([p.to_dict() for p in posts], indent=2))
        else:
            print(f"\n=== Stored Posts in Database ({len(posts)} total) ===")
            for p in posts:
                print(f"[{p.post_id}] {p.page_name} | {p.scraped_at}")
                print(f"    URL: {p.url}")
                print(f"    Text: {p.text[:120].replace(chr(10), ' ')}...")
        return

    pages = [p.strip() for p in args.page.split(",") if p.strip()]
    fetcher = HybridFetcher(mode=args.mode)
    runner = MonitorRunner(
        pages=pages,
        db=db,
        fetcher=fetcher,
        webhook_url=args.webhook,
        max_workers=args.workers
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
            print(f"\nRunning poll on {pages} with mode='{args.mode}'...")
            print(f"\n=== Poll Complete ===")
            print(f"New Posts Indexed: {summary['new_posts_found']}")
            print(f"Duplicates Skipped (Already in SQLite): {summary['duplicates_skipped']}")
            if args.webhook:
                print(f"Webhook Configured: {args.webhook}")

            print(f"\n--- Latest Posts ({len(latest)} retrieved) ---")
            for i, p in enumerate(latest):
                print(f"\nPost #{i+1}:")
                print(f"  ID: {p.post_id}")
                print(f"  Page: {p.page_name}")
                print(f"  URL: {p.url}")
                print(f"  Images: {len(p.images)} found")
                print(f"  Snippet: {p.text[:200].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    main()
