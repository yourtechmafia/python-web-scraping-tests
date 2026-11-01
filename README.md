# Python web scraping tests

Code, test harnesses and raw results behind ScrapingBee's [Python web scraping tutorial](https://www.scrapingbee.com/blog/web-scraping-101-with-python/). Every snippet in the article lives in `article/` and was run on Python 3.15.2 (macOS 26.7.1, Apple M3 Max) on November 1, 2026.

## What's here

| Folder | What it holds |
| --- | --- |
| `article/` | Every code block from the tutorial, as a runnable file |
| `fetch_test/` | The fetch test: 6 clients x 8 sites, success = the expected data is in the result |
| `parser_test/` | The parser benchmark: 6 parsers x 3 HTML files, 1,000 timed runs each |
| `fingerprint/` | TLS and HTTP/2 fingerprints of Requests, curl_cffi, Chrome and Playwright |
| `ai_selector_test/` | An AI assistant writes selectors from one page; we run them on four (`fetch_pages.py`, then `evaluate.py`) |
| `evidence/` | Smaller checks quoted in the article: httpx keep-alive, Auto Mode tiers, Retry-After, the MCP tool list, Scrapy logs, Python 3.14 runs |
| `scrapy_demo/` | The Scrapy 2.19 project from the tutorial |
| `charts/` | Scripts that turn the results into the article's charts and tables |
| `results/` | Raw CSVs (`partial/round<N>_<host>.csv`, one row per request), summaries and article run outputs |

## Run it yourself

```bash
uv sync
uv run playwright install chromium
export SCRAPINGBEE_API_KEY="your-api-key"     # only for the ScrapingBee clients and examples
export ANTHROPIC_API_KEY="your-api-key"       # only for article/s16_llm_extract.py

uv run python fetch_test/run.py 1             # one round; results/partial/round1_<host>.csv
uv run python parser_test/make_files.py && uv run python parser_test/bench.py 1000
uv run python fetch_test/memory_loc.py
uv run python charts/analyze.py
```

## Fetch test method

- **Clients:** Requests 2.34.2, httpx 0.28.1, curl_cffi 0.17.0 (`impersonate="chrome"`), Playwright 1.64.1 with headless Chromium (a fresh browser context per request, so nothing comes from the cache), and ScrapingBee two ways: `render_js=false`, and `mode=auto` with `max_cost=25` plus `wait_for` set to the data selector.
- **Sites:** see `fetch_test/sites.py`. Each site has a selector and a minimum match count; a request succeeds only if the status is 200 and the selector matches at least that many elements.
- **Pacing:** requests to one host run one at a time, at least 1 second apart. Hacker News asks for `Crawl-delay: 30` in robots.txt, so its requests are 30 seconds apart. Clients take turns request by request.
- **Volume:** 50 requests per client per site per round; 10 on Hacker News and Wikipedia.
- **User-Agent:** Requests and httpx send `python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)`. curl_cffi and Playwright keep their browser User-Agent. On Wikipedia every client sends the contact User-Agent, as its [User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy) asks.
- **Metrics:** success rate, median and p95 time per successful page, peak memory and lines of code of a one-page scraper (`fetch_test/minimal/`), and ScrapingBee credits from the `Spb-cost` header.

## Licence

MIT for the code. The sites belong to their owners, so the repo doesn't store copies of their pages: `parser_test/make_files.py` and `ai_selector_test/fetch_pages.py` download them again.
