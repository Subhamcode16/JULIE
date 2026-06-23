"""Browser automation tools using CloakBrowser."""

import asyncio
import os
from typing import Dict, Any
from loguru import logger
from cloakbrowser import launch_persistent_context_async

_browser_context = None

async def get_browser_context():
    """Get or create a persistent headed CloakBrowser context."""
    global _browser_context
    if _browser_context is None:
        profile_path = os.path.abspath("./data/cloak_profile")
        os.makedirs(profile_path, exist_ok=True)
        # The user requested HEADED VISIBLE BROWSER
        _browser_context = await launch_persistent_context_async(
            user_data_dir=profile_path,
            headless=False,
            humanize=True,
            args=["--mute-audio=false"]
        )
    return _browser_context

async def scrape_url(url: str) -> Dict[str, Any]:
    """Visit a URL and scrape its text content."""
    logger.info(f"Scraping URL: {url}")
    if not url.startswith("http"):
        url = "https://" + url

    try:
        context = await get_browser_context()
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        
        # Simple sanitization/text extraction
        content = await page.evaluate('''() => {
            const scripts = document.querySelectorAll('script, style, noscript, svg');
            scripts.forEach(s => s.remove());
            return document.body.innerText;
        }''')
        
        # Truncate content to avoid blowing up token limits
        if content and len(content) > 15000:
            content = content[:15000] + "\n...[truncated]"
            
        title = await page.title()
        
        # We can close the tab after scraping
        await page.close()
        
        return {
            "success": True,
            "title": title,
            "content": content
        }
    except Exception as e:
        logger.error(f"Browser scrape error: {e}")
        return {"success": False, "error": str(e)}

async def google_search(query: str) -> Dict[str, Any]:
    """Perform a google search and return the text."""
    url = f"https://www.google.com/search?q={query}"
    return await scrape_url(url)

async def youtube_search_and_play(query: str) -> Dict[str, Any]:
    """Search YouTube and play the first result in a headed browser."""
    logger.info(f"YouTube Search and Play: {query}")
    try:
        context = await get_browser_context()
        page = await context.new_page()
        url = f"https://www.youtube.com/results?search_query={query}"
        await page.goto(url, wait_until="domcontentloaded")
        
        # Playwright wait for the first video title link to appear
        # We use humanize=True features by using page.locator().click()
        first_video_selector = "ytd-video-renderer a#video-title"
        locator = page.locator(first_video_selector).first
        await locator.wait_for(state="visible", timeout=10000)
        await locator.click()
        
        return {
            "success": True,
            "message": f"Successfully playing first YouTube result for '{query}'"
        }
    except Exception as e:
        logger.error(f"YouTube play error: {e}")
        return {"success": False, "error": str(e)}

async def open_tab(url: str) -> Dict[str, Any]:
    """Open a new tab with the given URL."""
    try:
        context = await get_browser_context()
        page = await context.new_page()
        if not url.startswith("http"):
            url = "https://" + url
        await page.goto(url)
        return {"success": True, "message": f"Opened tab: {url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
