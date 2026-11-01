from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}
CHALLENGE_MARKERS = ("just a moment", "captcha", "access denied", "verify you are human")


def select_or_fail(html: str, selector: str, url: str, minimum: int = 1) -> list:
    found = BeautifulSoup(html, "lxml").select(selector)
    if len(found) >= minimum:
        return found
    Path("debug_page.html").write_text(html, encoding="utf-8")
    if any(marker in html.lower() for marker in CHALLENGE_MARKERS):
        raise RuntimeError(f"{url} returned a bot challenge, not the page. Saved debug_page.html")
    raise RuntimeError(f"{selector!r} matched {len(found)} elements on {url} (expected {minimum}+). "
                       "The layout changed or the data needs JavaScript. Saved debug_page.html")


url = "https://quotes.toscrape.com/js/"
response = requests.get(url, headers=HEADERS, timeout=10)
quotes = select_or_fail(response.text, "div.quote", url, minimum=10)
