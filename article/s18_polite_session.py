import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {"User-Agent": "my-first-scraper/1.0 (+https://example.com/contact)"}


def polite_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,                       # retries at once, then after 2 s and 4 s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,        # a server's Retry-After wins over backoff
        raise_on_status=False,                  # hand back the last response instead of raising
    )
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def crawl(urls: list[str], delay: float = 1.0, max_blocked: int = 3):
    blocked = 0
    with polite_session() as session:
        for url in urls:
            started = time.perf_counter()
            response = session.get(url, timeout=(5, 15))
            print(f"{response.status_code} {url} ({time.perf_counter() - started:.1f} s)")
            if response.status_code in (403, 429):
                blocked += 1
                if blocked >= max_blocked:
                    print(f"Stopping: {blocked} blocked responses in a row. Slow down or rethink the approach.")
                    return
            else:
                blocked = 0
                if response.ok:  # a 5xx that survived the retries is skipped, not kept
                    yield response
            time.sleep(delay)


pages = list(crawl([
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/503",   # retried 3 times with backoff, then given up
    "https://httpbin.org/status/403",   # not retried: a 403 won't fix itself
    "https://httpbin.org/status/403",
    "https://httpbin.org/status/403",
    "https://httpbin.org/status/200",   # never reached
]))
print(f"Kept {len(pages)} page(s)")
