import asyncio
import time

import httpx
from bs4 import BeautifulSoup

PAGE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}
MAX_CONCURRENCY = 5  # at most 5 requests in flight at once


def parse_titles(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    return [link["title"] for link in soup.select("article.product_pod h3 a")]


async def fetch_titles(client: httpx.AsyncClient, limit: asyncio.Semaphore, url: str) -> list[str]:
    async with limit:
        response = await client.get(url)
        response.raise_for_status()
        return parse_titles(response.text)


async def main() -> list[str]:
    limit = asyncio.Semaphore(MAX_CONCURRENCY)
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        pages = await asyncio.gather(
            *(fetch_titles(client, limit, PAGE_URL.format(n)) for n in range(1, 51))
        )
    return [title for page in pages for title in page]


start = time.perf_counter()
titles = asyncio.run(main())
print(f"{len(titles)} titles from 50 pages in {time.perf_counter() - start:.1f} s")
