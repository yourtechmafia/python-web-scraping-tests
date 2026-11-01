from bs4 import BeautifulSoup
from curl_cffi import requests

response = requests.get("https://books.toscrape.com/", impersonate="chrome", timeout=10)
response.raise_for_status()
soup = BeautifulSoup(response.text, "lxml")
for link in soup.select("article.product_pod h3 a"):
    print(link["title"])
