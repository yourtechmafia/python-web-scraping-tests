"""Parser benchmark: parse each HTML file and extract the same fields, 6 ways.

Usage:
  uv run python parser_test/bench.py [runs]          # timing, default 1,000 runs per pair
  uv run python parser_test/bench.py --mem PARSER FILE   # peak memory for one pair (fresh process)

Timing: timeit.repeat(number=1, repeat=runs), reported as median and p95 in ms.
Memory: peak resident memory added by one parse + extract, measured in a fresh
process with resource.getrusage, because tracemalloc can't see memory that
lxml, html5lib's tree builders or lexbor allocate in C.
"""
from __future__ import annotations

import csv
import json
import resource
import statistics
import subprocess
import sys
import timeit
from pathlib import Path

HERE = Path(__file__).parent
FILES = ["books.html", "wikipedia.html", "generated_1mb.html"]


# ---- extraction tasks: the same fields from every parser -------------------
# books: title + price per product card
# wikipedia: h2/h3 heading text + every link href inside the article body
# generated: name + price per product card

def bs4_task(parser_name):
    from bs4 import BeautifulSoup

    def run(html, kind):
        soup = BeautifulSoup(html, parser_name)
        if kind == "books":
            return [(a["title"], p.get_text(strip=True)) for a, p in
                    zip(soup.select("article.product_pod h3 a"), soup.select("article.product_pod .price_color"))]
        if kind == "wikipedia":
            body = soup.select_one("#mw-content-text")
            return ([h.get_text(strip=True) for h in body.select("h2, h3")],
                    [a["href"] for a in body.select("a[href]")])
        return [(a.get_text(strip=True), p.get_text(strip=True)) for a, p in
                zip(soup.select("article.product h3 a"), soup.select("article.product .price"))]
    return run


def lxml_task():
    import lxml.html

    def run(html, kind):
        tree = lxml.html.fromstring(html)
        if kind == "books":
            return [(a.get("title"), p.text_content().strip()) for a, p in
                    zip(tree.xpath('//article[contains(@class,"product_pod")]//h3/a'),
                        tree.xpath('//article[contains(@class,"product_pod")]//p[contains(@class,"price_color")]'))]
        if kind == "wikipedia":
            body = tree.xpath('//*[@id="mw-content-text"]')[0]
            return ([h.text_content().strip() for h in body.xpath('.//h2 | .//h3')],
                    body.xpath('.//a/@href'))
        return [(a.text_content().strip(), p.text_content().strip()) for a, p in
                zip(tree.xpath('//article[@class="product"]/h3/a'), tree.xpath('//article[@class="product"]/p[@class="price"]'))]
    return run


def parsel_task():
    from parsel import Selector

    def run(html, kind):
        sel = Selector(text=html)
        if kind == "books":
            return list(zip(sel.css("article.product_pod h3 a::attr(title)").getall(),
                            [t.strip() for t in sel.css("article.product_pod .price_color::text").getall()]))
        if kind == "wikipedia":
            body = sel.css("#mw-content-text")
            return ([" ".join(h.css("::text").getall()).strip() for h in body.css("h2, h3")],
                    body.css("a::attr(href)").getall())
        return list(zip([t.strip() for t in sel.css("article.product h3 a::text").getall()],
                        [t.strip() for t in sel.css("article.product .price::text").getall()]))
    return run


def selectolax_task():
    from selectolax.lexbor import LexborHTMLParser

    def run(html, kind):
        tree = LexborHTMLParser(html)
        if kind == "books":
            return [(a.attributes["title"], p.text(strip=True)) for a, p in
                    zip(tree.css("article.product_pod h3 a"), tree.css("article.product_pod .price_color"))]
        if kind == "wikipedia":
            body = tree.css_first("#mw-content-text")
            return ([h.text(strip=True) for h in body.css("h2, h3")],
                    [a.attributes["href"] for a in body.css("a[href]")])
        return [(a.text(strip=True), p.text(strip=True)) for a, p in
                zip(tree.css("article.product h3 a"), tree.css("article.product .price"))]
    return run


PARSERS = {
    "bs4 + html.parser": lambda: bs4_task("html.parser"),
    "bs4 + lxml": lambda: bs4_task("lxml"),
    "bs4 + html5lib": lambda: bs4_task("html5lib"),
    "lxml.html": lxml_task,
    "parsel": parsel_task,
    "selectolax (lexbor)": selectolax_task,
}


def kind_of(fname):
    return fname.split(".")[0].split("_")[0]


def load(fname):
    return (HERE / "html" / fname).read_text(encoding="utf-8")


def summarize(result):
    """A small fingerprint of the extracted data, to prove every parser agrees."""
    if isinstance(result, tuple):
        heads, links = result
        return {"headings": len(heads), "links": len(links), "first_heading": heads[0] if heads else None}
    return {"records": len(result), "first": list(result[0]) if result else None}


def mem(parser, fname):
    fn = PARSERS[parser]()
    html = load(fname)
    fn("<html><body><p>warm up</p></body></html>", "generated")
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    fn(html, kind_of(fname))
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == "darwin" else 1024  # macOS reports bytes, Linux KB
    print((after - before) * scale / 1024 / 1024)


def main(runs):
    rows = []
    for fname in FILES:
        html, kind = load(fname), kind_of(fname)
        for name, make in PARSERS.items():
            fn = make()
            check = summarize(fn(html, kind))
            times = timeit.repeat(lambda: fn(html, kind), number=1, repeat=runs)
            times_ms = sorted(t * 1000 for t in times)
            peak = float(subprocess.check_output(
                [sys.executable, "-I", __file__, "--mem", name, fname], text=True).strip())
            row = {"file": fname, "parser": name, "runs": runs,
                   "median_ms": round(statistics.median(times_ms), 3),
                   "p95_ms": round(times_ms[int(0.95 * len(times_ms)) - 1], 3),
                   "peak_mem_mb": round(peak, 1), "check": json.dumps(check, ensure_ascii=False)}
            rows.append(row)
            print(f"{fname:20s} {name:20s} median {row['median_ms']:9.3f} ms  p95 {row['p95_ms']:9.3f} ms  "
                  f"+{row['peak_mem_mb']:6.1f} MB  {check}", flush=True)
    out = HERE.parent / "results" / "parser_benchmark.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mem":
        mem(sys.argv[2], sys.argv[3])
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
