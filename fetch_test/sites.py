"""The 8 practice and public pages in the fetch test, and what counts as success.

Success means the expected data is in the result: at least `min_matches`
elements match `selector`. An HTTP 200 on its own doesn't count.
"""
from dataclasses import dataclass

CONTACT_UA = "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"


@dataclass(frozen=True)
class Site:
    key: str
    url: str
    selector: str
    min_matches: int
    requests: int = 50          # requests per client per round
    interval_s: float = 1.0     # minimum gap between requests to this host
    contact_ua: bool = False    # every client sends CONTACT_UA (Wikipedia policy)
    js: bool = False            # data only appears after JavaScript runs


SITES = [
    Site("books", "https://books.toscrape.com/", "article.product_pod h3 a", 20),
    Site("quotes", "https://quotes.toscrape.com/", "div.quote", 10),
    Site("quotes_js", "https://quotes.toscrape.com/js/", "div.quote", 10, js=True),
    Site("quotes_js_delayed", "https://quotes.toscrape.com/js-delayed/", "div.quote", 10, js=True),
    Site("scrapethissite_forms", "https://www.scrapethissite.com/pages/forms/", "tr.team", 25),
    Site("webscraper_ecommerce", "https://webscraper.io/test-sites/e-commerce/allinone", "div.thumbnail a.title", 3),
    # robots.txt asks for Crawl-delay: 30
    Site("hacker_news", "https://news.ycombinator.com/", "tr.athing.submission", 30, requests=10, interval_s=30.0),
    Site("wikipedia_table", "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population",
         "table.wikitable tbody tr", 200, requests=10, contact_ua=True),
]

# Requests to the same host run one after another, so the pacing holds per host.
def host(site: Site) -> str:
    return site.url.split("/")[2]
