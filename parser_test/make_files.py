"""Save the three HTML files the parser benchmark reads.

1. books.html: a Books to Scrape listing page (20 products).
2. wikipedia.html: a long Wikipedia article.
3. generated_1mb.html: a generated product grid of about 1 MB.
"""
import random
from pathlib import Path

import requests

UA = "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"
OUT = Path(__file__).parent / "html"
OUT.mkdir(exist_ok=True)

with requests.Session() as s:
    s.headers["User-Agent"] = UA
    for name, url in [("books.html", "https://books.toscrape.com/"),
                      ("wikipedia.html", "https://en.wikipedia.org/wiki/History_of_the_United_States")]:
        r = s.get(url, timeout=30)
        r.raise_for_status()
        (OUT / name).write_bytes(r.content)

random.seed(42)
cards = []
i = 0
body = ""
while len(body.encode()) < 1_000_000:
    i += 1
    cards.append(
        f'<article class="product"><h3><a href="/p/{i}" title="Product {i}">Product {i}</a></h3>'
        f'<p class="price">£{random.uniform(5, 99):.2f}</p>'
        f'<p class="desc">{" ".join(random.choice(["fast", "blue", "cotton", "steel", "eco", "large"]) for _ in range(12))}</p></article>'
    )
    body = "".join(cards)
(OUT / "generated_1mb.html").write_text(
    f"<!doctype html><html><head><title>Generated</title></head><body><main>{body}</main></body></html>", encoding="utf-8")

for f in sorted(OUT.iterdir()):
    print(f"{f.name:20s} {f.stat().st_size / 1024:8.1f} KB")
