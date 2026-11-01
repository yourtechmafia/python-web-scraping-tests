"""One fetcher per client. Each returns (status_code, html, extra) for a URL.

Requests and httpx send our descriptive User-Agent, as the tutorial teaches.
curl_cffi and Playwright keep their browser User-Agent, because looking like a
browser is their point. On Wikipedia every client sends CONTACT_UA, as its
User-Agent policy asks (ScrapingBee forwards it with Spb-User-Agent).
"""
from __future__ import annotations

import os

import httpx
import requests
from curl_cffi import requests as curl_requests
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from sites import CONTACT_UA, Site

TIMEOUT_S = 30
SCRAPINGBEE_URL = "https://app.scrapingbee.com/api/v1"


class RequestsClient:
    name = "requests"

    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = CONTACT_UA

    def fetch(self, site: Site):
        r = self.s.get(site.url, timeout=TIMEOUT_S)
        return r.status_code, r.text, {}

    def close(self):
        self.s.close()


class HttpxClient:
    name = "httpx"

    def __init__(self):
        self.c = httpx.Client(headers={"User-Agent": CONTACT_UA}, timeout=TIMEOUT_S, follow_redirects=True)

    def fetch(self, site: Site):
        r = self.c.get(site.url)
        return r.status_code, r.text, {}

    def close(self):
        self.c.close()


class CurlCffiClient:
    name = "curl_cffi"

    def __init__(self):
        self.s = curl_requests.Session(impersonate="chrome")

    def fetch(self, site: Site):
        headers = {"User-Agent": CONTACT_UA} if site.contact_ua else None
        r = self.s.get(site.url, headers=headers, timeout=TIMEOUT_S)
        return r.status_code, r.text, {}

    def close(self):
        self.s.close()


class PlaywrightClient:
    name = "playwright"

    def __init__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)

    def fetch(self, site: Site):
        # A fresh context per request: empty cache and cookies, like the HTTP
        # clients, so repeat visits aren't served from the browser cache.
        ctx = self.browser.new_context(user_agent=CONTACT_UA) if site.contact_ua else self.browser.new_context()
        try:
            page = ctx.new_page()
            resp = page.goto(site.url, wait_until="domcontentloaded", timeout=TIMEOUT_S * 1000)
            timed_out = False
            try:
                page.locator(site.selector).first.wait_for(timeout=20_000)
            except PlaywrightTimeout:
                timed_out = True
            return (resp.status if resp else None), page.content(), {"wait_timed_out": timed_out}
        finally:
            ctx.close()

    def close(self):
        self.browser.close()
        self.pw.stop()


class _ScrapingBeeBase:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers["Authorization"] = f"Bearer {os.environ['SCRAPINGBEE_API_KEY']}"

    def params(self, site: Site) -> dict:
        raise NotImplementedError

    def fetch(self, site: Site):
        params = {"url": site.url, **self.params(site)}
        headers = {}
        if site.contact_ua:
            params["forward_headers"] = "true"
            headers["Spb-User-Agent"] = CONTACT_UA
        r = self.s.get(SCRAPINGBEE_URL, params=params, headers=headers, timeout=120)
        extra = {"credits": r.headers.get("Spb-cost"), "auto_cost": r.headers.get("Spb-auto-cost"),
                 "initial_status": r.headers.get("Spb-initial-status-code")}
        return r.status_code, r.text, extra

    def close(self):
        self.s.close()


class ScrapingBeeNoJS(_ScrapingBeeBase):
    name = "scrapingbee_nojs"

    def params(self, site):
        return {"render_js": "false"}


class ScrapingBeeAuto(_ScrapingBeeBase):
    name = "scrapingbee_auto"

    def params(self, site):
        # Auto Mode picks the cheapest setup that works but doesn't wait for late
        # content by itself, so we pass the same selector Playwright waits for.
        return {"mode": "auto", "max_cost": "25", "wait_for": site.selector}


CLIENTS = [RequestsClient, HttpxClient, CurlCffiClient, PlaywrightClient, ScrapingBeeNoJS, ScrapingBeeAuto]
