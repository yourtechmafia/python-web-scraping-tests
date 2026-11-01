import csv
import json
import sqlite3
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



books = scrape_books(max_pages=2)

# CSV: opens in any spreadsheet
with open("books.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=books[0].keys())
    writer.writeheader()
    writer.writerows(books)

# JSON Lines: one record per line, safe to append on every run
with open("books.jsonl", "a", encoding="utf-8") as f:
    for book in books:
        f.write(json.dumps(book, ensure_ascii=False) + "\n")

# SQLite: query, dedupe and update over time
with sqlite3.connect("books.db") as db:
    db.execute("""CREATE TABLE IF NOT EXISTS books (
        url TEXT PRIMARY KEY, title TEXT, price TEXT, source_url TEXT, scraped_at TEXT)""")
    db.executemany(
        "INSERT OR REPLACE INTO books VALUES (:url, :title, :price, :source_url, :scraped_at)", books)
    print(db.execute("SELECT COUNT(*) FROM books").fetchone()[0], "books in books.db")
