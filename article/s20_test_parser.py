# test_parser.py: run with `uv run pytest`
from pathlib import Path

from hn_scraper import parse_stories


def test_parse_stories_reads_a_saved_front_page():
    html = Path("fixtures/hn_front_page.html").read_text(encoding="utf-8")
    stories = parse_stories(html, limit=30)
    assert len(stories) == 30
    assert all(story.title and story.url.startswith("http") for story in stories)
    assert sum(story.points for story in stories) > 0
