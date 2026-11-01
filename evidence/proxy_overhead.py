"""Does the local Safe-chain proxy (HTTPS_PROXY on the test machine) change timings?
Requests and httpx, 10 rounds, a fresh-connection-free Session each, proxied vs direct, 2 s apart."""
import statistics
import time

import httpx
import requests

import os

PROXY = os.environ["HTTPS_PROXY"]  # Safe-chain sets this for processes started with `uv run`
UA = {"User-Agent": "python-web-scraping-tests/1.0 (+https://github.com/yourtechmafia/python-web-scraping-tests)"}
URL = "https://books.toscrape.com/"
direct_s = requests.Session(); direct_s.trust_env = False
proxied_s = requests.Session(); proxied_s.trust_env = False; proxied_s.proxies = {"https": PROXY}
direct_h = httpx.Client(trust_env=False, timeout=30)
proxied_h = httpx.Client(trust_env=False, proxy=PROXY, timeout=30)
res = {k: [] for k in ("requests direct", "requests proxied", "httpx direct", "httpx proxied")}
for i in range(10):
    for k, f in (("requests direct", lambda: direct_s.get(URL, headers=UA, timeout=30)),
                 ("requests proxied", lambda: proxied_s.get(URL, headers=UA, timeout=30)),
                 ("httpx direct", lambda: direct_h.get(URL, headers=UA)),
                 ("httpx proxied", lambda: proxied_h.get(URL, headers=UA))):
        t = time.perf_counter(); f().raise_for_status(); res[k].append(time.perf_counter() - t)
    time.sleep(2)
for k, v in res.items():
    print(f"{k:18s} median {statistics.median(v):.3f} s  (first {v[0]:.3f} s)")
