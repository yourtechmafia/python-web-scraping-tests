from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

URL = "https://quotes.toscrape.com/js-delayed/"  # renders quotes after a 10-second delay
WAIT_MS = 20_000


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_quotes(limit: int = 3) -> list[Quote]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(URL, wait_until="domcontentloaded")
            cards = page.locator("div.quote")
            cards.first.wait_for(timeout=WAIT_MS)  # waits for the element, not a guessed sleep
            quotes = []
            for card in cards.all()[:limit]:
                quotes.append(Quote(
                    text=card.locator(".text").inner_text(),
                    author=card.locator(".author").inner_text(),
                    tags=card.locator(".tag").all_inner_texts(),
                ))
            return quotes
        except PlaywrightTimeoutError as exc:
            raise RuntimeError(f"No quotes after {WAIT_MS / 1000:.0f} s") from exc
        finally:
            browser.close()


if __name__ == "__main__":
    for quote in scrape_quotes():
        print(quote.text)
        print(f"  {quote.author} | {', '.join(quote.tags)}")
