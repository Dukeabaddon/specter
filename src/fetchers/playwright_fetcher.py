import asyncio
import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, BrowserContext, Page
from ..models import Post
from .base import BaseFetcher

logger = logging.getLogger(__name__)

DEFAULT_COOKIES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "cookies.json"

class PlaywrightFetcher(BaseFetcher):
    def __init__(self, cookies_path: Optional[Path] = None, headless: bool = True):
        self.cookies_path = cookies_path or DEFAULT_COOKIES_PATH
        self.cookies_path.parent.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    def fetch_posts(self, page_name: str, limit: int = 5) -> List[Post]:
        """
        Synchronous wrapper around async runner.
        """
        return asyncio.run(self.fetch_posts_async(page_name, limit))

    async def fetch_posts_async(self, page_name: str, limit: int = 5) -> List[Post]:
        url = f"https://www.facebook.com/{page_name.strip('/')}"
        logger.info(f"[PlaywrightFetcher] Navigating to {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900},
                locale="en-US",
            )
            
            # Load stored cookies if available
            if self.cookies_path.exists():
                try:
                    with open(self.cookies_path, "r") as f:
                        saved_cookies = json.load(f)
                    if saved_cookies:
                        await context.add_cookies(saved_cookies)
                        logger.info(f"[PlaywrightFetcher] Loaded {len(saved_cookies)} cookies")
                except Exception as e:
                    logger.warning(f"[PlaywrightFetcher] Failed to load cookies: {e}")

            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception as e:
                logger.warning(f"[PlaywrightFetcher] Network idle timeout, proceeding with DOM: {e}")

            # Kill login / cookie dialogs
            await self._dismiss_modals(page)
            
            accumulated_posts: Dict[str, Dict[str, Any]] = {}
            
            # Scroll loop to collect up to limit posts
            max_scrolls = max(3, limit * 2)
            for scroll_idx in range(max_scrolls):
                if len(accumulated_posts) >= limit:
                    break

                # Expand 'See more'
                await self._expand_see_more(page)
                
                # Extract visible posts from DOM
                extracted = await self._extract_visible_posts(page)
                for post_dict in extracted:
                    if post_dict["post_id"] not in accumulated_posts:
                        accumulated_posts[post_dict["post_id"]] = post_dict
                        logger.info(f"[PlaywrightFetcher] Found post {post_dict['post_id']} ({len(accumulated_posts)}/{limit})")
                        if len(accumulated_posts) >= limit:
                            break

                # Scroll down
                await page.mouse.wheel(0, 1200)
                await page.wait_for_timeout(1800)
                await self._dismiss_modals(page)

            # Persist refreshed cookies
            try:
                fresh_cookies = await context.cookies()
                with open(self.cookies_path, "w") as f:
                    json.dump(fresh_cookies, f, indent=2)
                logger.info(f"[PlaywrightFetcher] Saved {len(fresh_cookies)} cookies to {self.cookies_path}")
            except Exception as e:
                logger.warning(f"[PlaywrightFetcher] Could not save cookies: {e}")

            await browser.close()

            # Convert to Post dataclass
            posts = []
            for item in list(accumulated_posts.values())[:limit]:
                posts.append(Post(
                    post_id=item["post_id"],
                    page_name=page_name,
                    text=item["text"],
                    url=item["url"],
                    published_at=item.get("published_at"),
                    images=item.get("images", []),
                    raw_metadata={"source": "playwright", "extracted_raw": item}
                ))

            logger.info(f"[PlaywrightFetcher] Completed fetch. Total posts: {len(posts)}")
            return posts

    async def _dismiss_modals(self, page: Page):
        await page.evaluate("""() => {
            const dialogs = document.querySelectorAll('div[role="dialog"], div[class*="x1ypdohk"]');
            dialogs.forEach(d => {
                const text = d.innerText || '';
                if (text.includes('Log In') || text.includes('See more on Facebook') || text.includes('Cookie')) {
                    d.remove();
                }
            });
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        }""")

    async def _expand_see_more(self, page: Page):
        await page.evaluate("""() => {
            const elements = document.querySelectorAll('div[role="button"], span');
            elements.forEach(el => {
                const text = (el.innerText || '').trim();
                if (['See more', 'Tumingin pa', 'See More'].includes(text)) {
                    try { el.click(); } catch (err) {}
                }
            });
        }""")

    async def _extract_visible_posts(self, page: Page) -> List[Dict[str, Any]]:
        return await page.evaluate("""() => {
            const results = [];
            const containers = document.querySelectorAll('div[role="feed"] > div, div[role="article"]');
            
            containers.forEach(container => {
                const fullText = (container.innerText || '').trim();
                if (fullText.length < 25) return;
                
                // Find post permalinks
                const links = Array.from(container.querySelectorAll('a[href]'));
                const postLinkEl = links.find(a => 
                    a.href.includes('/posts/') || 
                    a.href.includes('story_fbid=') ||
                    (a.href.includes('/videos/') && !a.href.includes('/watch/'))
                );
                
                if (!postLinkEl) return;
                
                const href = postLinkEl.href;
                let cleanUrl = href;
                let postId = '';
                
                try {
                    const u = new URL(href);
                    u.search = '';
                    cleanUrl = u.toString();
                    
                    // Extract ID
                    const postMatch = cleanUrl.match(/\/posts\/([a-zA-Z0-9_-]+)/);
                    if (postMatch) {
                        postId = postMatch[1];
                    } else {
                        const storyMatch = href.match(/story_fbid=([0-9]+)/);
                        if (storyMatch) postId = storyMatch[1];
                        else postId = cleanUrl;
                    }
                } catch (e) {
                    postId = href;
                }
                
                // Clean body text (remove standard Facebook UI buttons)
                const uiTokens = new Set([
                    'Like', 'Comment', 'Share', 'I-like', 'Mag-comment', 'I-share',
                    'Tumingin pa', 'See more', 'See More', 'Follow', 'Sundan',
                    'Shared with Public', 'Pampubliko', 'Quezon City Government'
                ]);
                
                const lines = fullText.split('\\n')
                    .map(l => l.trim())
                    .filter(l => l.length > 0 && !uiTokens.has(l));
                    
                const cleanedText = lines.join('\\n');
                
                // Extract images
                const imgs = Array.from(container.querySelectorAll('img[src]'))
                    .map(i => i.src)
                    .filter(src => src.includes('scontent') || src.includes('fbcdn'));
                    
                results.push({
                    post_id: postId,
                    url: cleanUrl,
                    text: cleanedText,
                    images: imgs,
                    published_at: null
                });
            });
            
            return results;
        }""")
