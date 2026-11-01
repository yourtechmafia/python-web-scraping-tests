import os

import anthropic
import requests
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    price_gbp: float
    in_stock: int
    upc: str


# 1. Fetch the page as Markdown (static page, so no JavaScript rendering: 1 credit)
page = requests.get(
    "https://app.scrapingbee.com/api/v1",
    headers={"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"},
    params={
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "render_js": "false",
        "return_page_markdown": "true",
    },
    timeout=150,
)
page.raise_for_status()

# 2. Ask Claude to fill the schema; parse() validates the reply against it
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
response = client.messages.parse(
    model="claude-opus-5-5",
    max_tokens=1024,
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": f"Extract the book details from this page:\n\n{page.text}"}],
    output_format=Book,
)
book = response.parsed_output
print(book)
print(f"{len(page.text):,} characters of Markdown, "
      f"{response.usage.input_tokens:,} input tokens, {response.usage.output_tokens:,} output tokens")
