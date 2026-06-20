"""Browser automation tools using Camoufox."""

import asyncio
from typing import Dict, Any
from loguru import logger
from camoufox.async_api import AsyncCamoufox

async def scrape_url(url: str) -> Dict[str, Any]:
    """Visit a URL and scrape its text content."""
    logger.info(f"Scraping URL: {url}")
    if not url.startswith("http"):
        url = "https://" + url

    try:
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
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
