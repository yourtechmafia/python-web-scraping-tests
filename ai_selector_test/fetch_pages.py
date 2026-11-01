"""Save the four webscraper.io test-shop pages used in the AI selector test."""
import time
from pathlib import Path

import requests

UA = "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"
PAGES = {
    "laptops": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    "tablets": "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets",
    "touch_phones": "https://webscraper.io/test-sites/e-commerce/allinone/phones/touch",
    "home_featured": "https://webscraper.io/test-sites/e-commerce/allinone",
}
out = Path(__file__).parent / "pages"
out.mkdir(exist_ok=True)
with requests.Session() as s:
    s.headers["User-Agent"] = UA
    for name, url in PAGES.items():
        r = s.get(url, timeout=20)
        r.raise_for_status()
        (out / f"{name}.html").write_text(r.text, encoding="utf-8")
        time.sleep(1)
