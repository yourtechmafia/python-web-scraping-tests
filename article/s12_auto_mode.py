import os

import requests

API_URL = "https://app.scrapingbee.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}

for url, wait_for in [("https://books.toscrape.com/", None),
                      ("https://quotes.toscrape.com/js/", "div.quote")]:
    params = {"url": url, "mode": "auto", "max_cost": "25"}
    if wait_for:
        params["wait_for"] = wait_for  # Auto Mode won't wait for late content on its own
    response = requests.get(API_URL, headers=HEADERS, params=params, timeout=150)
    print(url)
    print("  status:", response.status_code,
          "| Spb-cost:", response.headers.get("Spb-cost"),
          "| Spb-auto-cost:", response.headers.get("Spb-auto-cost"))
