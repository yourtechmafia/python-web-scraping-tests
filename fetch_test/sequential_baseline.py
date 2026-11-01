"""Supporting timing for the asyncio section: the same 50 pages fetched one by one
with no delay (the article's pagination loop adds a 1 s pause on purpose)."""
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}
start = time.perf_counter()
titles = []
with requests.Session() as s:
    s.headers.update(HEADERS)
    for n in range(1, 51):
        r = s.get(f"https://books.toscrape.com/catalogue/page-{n}.html", timeout=10)
        r.raise_for_status()
        titles += [a["title"] for a in BeautifulSoup(r.text, "lxml").select("article.product_pod h3 a")]
print(f"{len(titles)} titles from 50 pages in {time.perf_counter() - start:.1f} s (sequential, no delay)")
