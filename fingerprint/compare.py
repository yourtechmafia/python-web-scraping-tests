"""Supporting evidence for the fingerprint section (not in the article).

Compares: Requests (default UA), Requests with a copied Chrome UA, curl_cffi
impersonate="chrome", and real Google Chrome (system install, headless) on
tls.browserleaks.com/json.
"""
import json
from datetime import datetime, timezone

import requests
from curl_cffi import requests as curl_requests
from playwright.sync_api import sync_playwright

URL = "https://tls.browserleaks.com/json"
CHROME_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"

rows = {
    "requests": requests.get(URL, timeout=15).json(),
    "requests + Chrome UA": requests.get(URL, headers={"User-Agent": CHROME_UA}, timeout=15).json(),
    "curl_cffi chrome": curl_requests.get(URL, impersonate="chrome", timeout=15).json(),
}
with sync_playwright() as p:
    for label, kw in [("Google Chrome (headless)", {"channel": "chrome"}), ("Playwright Chromium (headless)", {})]:
        b = p.chromium.launch(headless=True, **kw)
        page = b.new_page()
        page.goto(URL)
        rows[label] = json.loads(page.locator("body").inner_text())
        rows[label]["browser_version"] = b.version
        b.close()

print(datetime.now(timezone.utc).isoformat(timespec="seconds"))
for k, d in rows.items():
    print(f"{k:32s} ja4={d['ja4']}  h2={d.get('akamai_hash') or '-':32s}  ua={d['user_agent'][:60]}  {d.get('browser_version', '')}")
json.dump(rows, open("results/fingerprint_compare.json", "w"), indent=2)
