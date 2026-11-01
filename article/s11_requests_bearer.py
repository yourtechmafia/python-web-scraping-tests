import os

import requests

API_URL = "https://app.scrapingbee.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}

response = requests.get(
    API_URL,
    headers=HEADERS,
    params={"url": "https://books.toscrape.com/", "render_js": "false"},  # static page: 1 credit
    timeout=150,
)
response.raise_for_status()
print(response.status_code, "| credits:", response.headers.get("Spb-cost"))
print(response.text.count('class="product_pod"'), "books in the HTML")
