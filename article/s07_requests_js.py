import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}

response = requests.get("https://quotes.toscrape.com/js/", headers=HEADERS, timeout=10)
soup = BeautifulSoup(response.text, "lxml")
print("Status:", response.status_code)
print("Quotes found:", len(soup.select("div.quote")))
print("Quote text sits in a script:", "var data" in response.text)
