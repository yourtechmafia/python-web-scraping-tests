import os

import requests
from bs4 import BeautifulSoup

response = requests.get(
    "https://app.scrapingbee.com/api/v1",
    params={"url": "https://books.toscrape.com/", "render_js": "false"},
    headers={"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"},
    timeout=60,
)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
for link in soup.select("article.product_pod h3 a"):
    print(link["title"])
