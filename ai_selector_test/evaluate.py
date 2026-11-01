"""Run the assistant-written extract_products() on all four pages and compare with ground truth.

ai_written.py was written by Claude Sonnet 5.5, acting as a coding assistant, from laptops.html only.
Ground truth: every div.thumbnail card, full name from the link's title attribute, price from .price.
"""
import importlib.util
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("ai_written", HERE / "ai_written.py")
ai = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai)

for name in ["laptops", "tablets", "touch_phones", "home_featured"]:
    html = (HERE / "pages" / f"{name}.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    truth = [(c.select_one("a.title")["title"], c.select_one(".price").get_text(strip=True)) for c in soup.select("div.thumbnail")]
    truncated = sum(1 for c in soup.select("div.thumbnail a.title") if c.get_text(strip=True) != c["title"])
    got = ai.extract_products(html)
    names = sum(1 for g, t in zip(got, truth) if g["name"] == t[0])
    prices = sum(1 for g, t in zip(got, truth) if g["price"] == t[1])
    empty = sum(1 for g in got for v in g.values() if v is None)
    print(f"{name:14s} products {len(got)}/{len(truth)}  names {names}  prices {prices}  empty fields {empty}  "
          f"(visible name truncated on {truncated})")
