"""Which tier Auto Mode picks, with and without wait_for (costs about 20 credits)."""
import os
import time

import requests

H = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}
CASES = [
    ("quotes homepage (static), no wait_for", "https://quotes.toscrape.com/", {}),
    ("quotes homepage (static), no wait_for", "https://quotes.toscrape.com/", {}),
    ("quotes homepage (static), wait_for", "https://quotes.toscrape.com/", {"wait_for": "div.quote"}),
    ("quotes homepage (static), render_js=false (not Auto Mode)", "https://quotes.toscrape.com/", {"render_js": "false"}),
    ("js-delayed, no wait_for", "https://quotes.toscrape.com/js-delayed/", {}),
    ("js-delayed, wait_for", "https://quotes.toscrape.com/js-delayed/", {"wait_for": "div.quote"}),
]
for label, url, extra in CASES:
    params = {"url": url, **extra} if "render_js" in extra else {"url": url, "mode": "auto", "max_cost": "25", **extra}
    r = requests.get("https://app.scrapingbee.com/api/v1", headers=H, params=params, timeout=150)
    print(f"{label:58s} status {r.status_code} Spb-cost {r.headers.get('Spb-cost')} "
          f"Spb-auto-cost {r.headers.get('Spb-auto-cost')} quotes {r.text.count('class=\"quote\"')}")
    time.sleep(1)
