from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HN_URL = "https://news.ycombinator.com/"
HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}
TIMEOUT = (5, 15)  # 5 s to connect, then give up after 15 s with no data


@dataclass
class Story:
    rank: int
    title: str
    url: str
    points: int
    author: str
    comments: int


def extract_number(text: str | None) -> int:
    """Return the first whole number in a string like '31 points', or 0."""
    if not text:
        return 0
    match = re.search(r"\d+", text.replace("\xa0", " "))
    return int(match.group()) if match else 0


def fetch_html(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def parse_stories(html: str, limit: int = 5) -> list[Story]:
    soup = BeautifulSoup(html, "lxml")
    stories = []
    for row in soup.select("tr.athing.submission")[:limit]:
        title_link = row.select_one(".titleline > a")
        if title_link is None:  # layout changed or a special row: skip it
            continue
        subtext = row.find_next_sibling("tr")
        score = subtext.select_one(".score") if subtext else None
        author = subtext.select_one(".hnuser") if subtext else None
        comment_links = subtext.find_all("a", string=re.compile("comment")) if subtext else []
        rank = row.select_one(".rank")
        stories.append(Story(
            rank=extract_number(rank.get_text() if rank else None),
            title=title_link.get_text(strip=True),
            url=urljoin(HN_URL, title_link["href"]),
            points=extract_number(score.get_text() if score else None),
            author=author.get_text(strip=True) if author else "unknown",
            comments=extract_number(comment_links[0].get_text() if comment_links else None),
        ))
    return stories


def main() -> None:
    with requests.Session() as session:
        session.headers.update(HEADERS)
        html = fetch_html(session, HN_URL)
    for story in parse_stories(html):
        print(f"{story.rank}. {story.title}")
        print(f"   {story.url}")
        print(f"   {story.points} points by {story.author}, {story.comments} comments")


if __name__ == "__main__":
    main()
