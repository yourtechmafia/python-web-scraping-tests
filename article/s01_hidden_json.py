import time

import requests

API_URL = "https://quotes.toscrape.com/api/quotes"
HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}

quotes, page = [], 1
with requests.Session() as session:
    session.headers.update(HEADERS)
    while True:
        response = session.get(API_URL, params={"page": page}, timeout=10)
        response.raise_for_status()
        data = response.json()
        quotes.extend(data["quotes"])
        if not data["has_next"]:
            break
        page += 1
        time.sleep(1)  # one request per second, even on an API

print(f"{len(quotes)} quotes from {page} JSON pages")
print(quotes[0]["text"], "by", quotes[0]["author"]["name"])
