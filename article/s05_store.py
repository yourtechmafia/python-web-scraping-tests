import csv
import json
import sqlite3

from s04_books_pagination import scrape_books

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
