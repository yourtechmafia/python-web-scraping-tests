import os
from pathlib import Path

import requests

API_URL = "https://app.scrapingbee.com/api/v1"
HEADERS = {"Authorization": f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"}
TARGET = "https://quotes.toscrape.com/js/"

# Markdown: clean text for an LLM or a RAG index
markdown = requests.get(
    API_URL, headers=HEADERS, timeout=150,
    params={"url": TARGET, "wait_for": "div.quote", "return_page_markdown": "true"},
)
markdown.raise_for_status()
print(markdown.text[:180])

# Screenshot: see what the renderer saw when a selector comes back empty
shot = requests.get(
    API_URL, headers=HEADERS, timeout=150,
    params={"url": TARGET, "wait_for": "div.quote", "screenshot": "true"},
)
shot.raise_for_status()
Path("debug_screenshot.png").write_bytes(shot.content)
print("Saved debug_screenshot.png,", len(shot.content) // 1024, "KB")
