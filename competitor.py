import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote
from models.pydantic_models import BrandContext
from services.scraper import ShopifyScraper

async def fetch_competitors(brand_name: str, base_url: str) -> list[BrandContext]:
    search_query = f"site:*.myshopify.com {brand_name} competitors"
    search_url = f"https://www.google.com/search?q={quote(search_query)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status != 200:
                return []
            soup = BeautifulSoup(await response.text(), "html.parser")
            competitor_urls = []
            for link in soup.select("a[href*='.myshopify.com']")[:3]:  # Limit to 3 for performance
                href = link.get("href")
                if href.startswith("http"):
                    competitor_urls.append(href)
    
    competitors = []
    for url in competitor_urls:
        scraper = ShopifyScraper(url)
        competitors.append(scraper.scrape())
        await asyncio.sleep(1)  # Avoid overwhelming servers
    return competitors