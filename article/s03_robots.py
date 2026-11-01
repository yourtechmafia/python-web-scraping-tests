from urllib.robotparser import RobotFileParser

import requests

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}


def load_robots(session: requests.Session, site: str) -> RobotFileParser:
    parser = RobotFileParser()
    response = session.get(f"{site}/robots.txt", timeout=10)
    if response.status_code in (404, 410):
        parser.parse([])  # no robots.txt: RFC 9309 says everything is allowed
    elif response.status_code in (401, 403):
        parser.parse(["User-agent: *", "Disallow: /"])  # refused: treat the site as off-limits
    else:
        response.raise_for_status()  # 429 or 5xx: back off and try again later
        parser.parse(response.text.splitlines())
    return parser


with requests.Session() as session:
    session.headers.update(HEADERS)
    for site, path in [("https://news.ycombinator.com", "/"),
                       ("https://news.ycombinator.com", "/login"),
                       ("https://books.toscrape.com", "/catalogue/page-2.html")]:
        robots = load_robots(session, site)
        agent = HEADERS["User-Agent"]
        if robots.can_fetch(agent, site + path):
            delay = robots.crawl_delay(agent)
            print(f"OK to fetch {site}{path}" + (f", waiting {delay} s between requests" if delay else ""))
        else:
            print(f"Skipping {site}{path}: robots.txt doesn't allow it")
