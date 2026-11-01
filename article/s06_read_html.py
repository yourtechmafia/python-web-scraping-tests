from io import StringIO

import pandas as pd
import requests

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}

response = requests.get("https://www.scrapethissite.com/pages/forms/", headers=HEADERS, timeout=10)
response.raise_for_status()
teams = pd.read_html(StringIO(response.text))[0]
print(teams.shape)
print(teams[["Team Name", "Year", "Wins", "Losses"]].head(3))
