import os

from scrapingbee import ScrapingBeeClient

client = ScrapingBeeClient(api_key=os.environ["SCRAPINGBEE_API_KEY"])
response = client.html_api(
    "https://quotes.toscrape.com/js/",
    params={"wait_for": "div.quote"},  # JavaScript rendering is on by default
    timeout=150,
)
print(response.status_code, "| credits:", response.headers.get("Spb-cost"))
print(response.text.count('class="quote"'), "quotes in the rendered HTML")
