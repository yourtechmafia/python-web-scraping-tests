import json
import os

import requests

API_URL = "https://app.scrapingbee.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}

extract_rules = {
    "quotes": {
        "selector": "div.quote",
        "type": "list",
        "output": {"text": ".text", "author": ".author", "tags": {"selector": ".tag", "type": "list"}},
    }
}

response = requests.get(
    API_URL,
    headers=HEADERS,
    params={
        "url": "https://quotes.toscrape.com/js/",
        "wait_for": "div.quote",
        "extract_rules": json.dumps(extract_rules),
    },
    timeout=150,
)
response.raise_for_status()
data = response.json()
print(len(data["quotes"]), "quotes | credits:", response.headers.get("Spb-cost"))
print(json.dumps(data["quotes"][0], indent=2, ensure_ascii=False))
