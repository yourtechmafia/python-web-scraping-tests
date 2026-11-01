import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}


def scrape_books(max_pages: int = 50) -> list[dict]:
    books, url, pages = [], START_URL, 0
    with requests.Session() as session:
        session.headers.update(HEADERS)
        while url and pages < max_pages:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "lxml")  # bytes: let Beautiful Soup read the page's charset
            scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            for card in soup.select("article.product_pod"):
                link = card.select_one("h3 a")
                price = card.select_one(".price_color")
                if link is None or price is None:
                    continue
                books.append({
                    "title": link["title"],
                    "price": price.get_text(strip=True),
                    "url": urljoin(url, link["href"]),
                    "source_url": url,
                    "scraped_at": scraped_at,
                })
            pages += 1
            next_link = soup.select_one("li.next a")
            url = urljoin(url, next_link["href"]) if next_link else None
            if url:
                time.sleep(1)  # one request per second is plenty for a small site
    print(f"Scraped {len(books)} books from {pages} pages")
    return books


if __name__ == "__main__":
    start = time.perf_counter()
    books = scrape_books()
    print(books[0])
    print(f"Took {time.perf_counter() - start:.1f} s")
