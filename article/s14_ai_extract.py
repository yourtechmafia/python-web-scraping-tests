import json
import os

import requests

API_URL = "https://app.scrapingbee.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}

ai_rules = {
    "title": "the book title",
    "price": {"description": "price including tax, as a number", "type": "number"},
    "stock": {"description": "how many copies are in stock", "type": "number"},
}

response = requests.get(
    API_URL,
    headers=HEADERS,
    params={
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "render_js": "false",
        "ai_extract_rules": json.dumps(ai_rules),
    },
    timeout=150,
)
response.raise_for_status()
print(response.json(), "| credits:", response.headers.get("Spb-cost"))
