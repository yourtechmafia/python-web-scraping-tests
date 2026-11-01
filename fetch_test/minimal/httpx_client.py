import httpx
from bs4 import BeautifulSoup

response = httpx.get("https://books.toscrape.com/", headers={"User-Agent": "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"}, timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
for link in soup.select("article.product_pod h3 a"):
    print(link["title"])
