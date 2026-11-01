"""Why httpx looked slower in the fetch test: its default keepalive_expiry is 5 s.
Requests vs httpx (default) vs httpx (keepalive_expiry=30), 4 requests each, 7 s apart."""
import time

import httpx
import requests

UA = {"User-Agent": "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"}
URL = "https://quotes.toscrape.com/"
clients = {
    "requests": requests.Session(),
    "httpx default (keepalive_expiry=5)": httpx.Client(timeout=30),
    "httpx keepalive_expiry=30": httpx.Client(timeout=30, limits=httpx.Limits(keepalive_expiry=30)),
}
for c in clients.values():
    c.headers.update(UA)
for i in range(4):
    for name, c in clients.items():
        t = time.perf_counter()
        c.get(URL, timeout=30)
        print(f"#{i} {name:36s} {time.perf_counter() - t:.3f} s")
    time.sleep(7)
