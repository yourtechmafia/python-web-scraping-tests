"""Summarise the fetch test and parser benchmark, and draw the article charts.

Usage: uv run python charts/analyze.py [image_dir]
Reads results/partial/round*.csv, results/memory_loc.csv and results/parser_benchmark.csv.
Writes results/summary_*.csv, results/summary.md and three PNG charts.
"""
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

REPO = Path(__file__).resolve().parents[1]
RES = REPO / "results"
IMG = Path(sys.argv[1]) if len(sys.argv) > 1 else RES / "charts"
IMG.mkdir(parents=True, exist_ok=True)

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e8e7e3"
BLUE = "#2a78d6"
plt.rcParams.update({"font.family": "Helvetica", "font.size": 12, "text.color": INK, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": INK,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})

CLIENTS = ["requests", "httpx", "curl_cffi", "playwright", "scrapingbee_nojs", "scrapingbee_auto"]
CLIENT_NAMES = {"requests": "Requests", "httpx": "httpx", "curl_cffi": "curl_cffi (chrome)",
                "playwright": "Playwright (Chromium)", "scrapingbee_nojs": "ScrapingBee, no JS",
                "scrapingbee_auto": "ScrapingBee, Auto Mode"}
SITES = ["books", "quotes", "scrapethissite_forms", "webscraper_ecommerce", "hacker_news", "wikipedia_table",
         "quotes_js", "quotes_js_delayed"]
SITE_NAMES = {"books": "Books to Scrape", "quotes": "Quotes to Scrape", "scrapethissite_forms": "Scrapethissite forms",
              "webscraper_ecommerce": "webscraper.io shop", "hacker_news": "Hacker News",
              "wikipedia_table": "Wikipedia table", "quotes_js": "Quotes /js/", "quotes_js_delayed": "Quotes /js-delayed/"}
JS_SITES = {"quotes_js", "quotes_js_delayed"}

rows = [r for f in sorted((RES / "partial").glob("round*.csv")) if not f.name.startswith("round0")
        for r in csv.DictReader(open(f, encoding="utf-8"))]
rounds = sorted({r["round"] for r in rows})
by = defaultdict(list)
for r in rows:
    by[(r["client"], r["site"])].append(r)


def pct(xs):
    return 100 * sum(int(x["ok"]) for x in xs) / len(xs) if xs else float("nan")


def times(xs, ok_only=True):
    return [float(x["elapsed_s"]) for x in xs if x["elapsed_s"] and (int(x["ok"]) or not ok_only)]


def p95(v):
    v = sorted(v)
    return v[max(0, int(round(0.95 * len(v))) - 1)] if v else float("nan")


# ---- per client x site -----------------------------------------------------
cell = []
for c in CLIENTS:
    for s in SITES:
        xs = by[(c, s)]
        t = times(xs)
        credits = [int(x["credits"]) for x in xs if x.get("credits")]
        auto = [x["auto_cost"] for x in xs if x.get("auto_cost")]
        cell.append({"client": c, "site": s, "requests": len(xs), "ok": sum(int(x["ok"]) for x in xs),
                     "success_pct": round(pct(xs), 1),
                     "median_s": statistics.median(t) if t else "", "p95_s": round(p95(t), 3) if t else "",
                     "credits_total": sum(credits) if credits else "",
                     "auto_costs": " ".join(f"{k}x{auto.count(k)}" for k in sorted(set(auto), key=int)) if auto else "",
                     "errors": len([x for x in xs if x.get("error")])})
with open(RES / "summary_by_site.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cell[0]))
    w.writeheader()
    w.writerows(cell)

mem = {r["client"]: r for r in csv.DictReader(open(RES / "memory_loc.csv"))}
mem_key = {"requests": "requests", "httpx": "httpx", "curl_cffi": "curl_cffi", "playwright": "playwright",
           "scrapingbee_nojs": "scrapingbee", "scrapingbee_auto": "scrapingbee"}
overall = []
for c in CLIENTS:
    xs = [x for s in SITES for x in by[(c, s)]]
    static = [x for s in SITES if s not in JS_SITES for x in by[(c, s)]]
    js = [x for s in JS_SITES for x in by[(c, s)]]
    ts, tj = times(static), times(js)
    credits = [int(x["credits"]) for x in xs if x.get("credits")]
    overall.append({"client": c, "requests": len(xs), "success_pct_all": round(pct(xs), 1),
                    "success_pct_static": round(pct(static), 1), "success_pct_js": round(pct(js), 1),
                    "median_s_static": round(statistics.median(ts), 3) if ts else "", "p95_s_static": round(p95(ts), 3) if ts else "",
                    "median_s_js": round(statistics.median(tj), 3) if tj else "", "p95_s_js": round(p95(tj), 3) if tj else "",
                    "loc": mem[mem_key[c]]["loc"], "peak_mem_mb": mem[mem_key[c]]["peak_mem_mb_median"],
                    "credits_total": sum(credits) if credits else "",
                    "credits_per_ok": round(sum(credits) / max(1, sum(int(x["ok"]) for x in xs)), 2) if credits else ""})
with open(RES / "summary_by_client.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(overall[0]))
    w.writeheader()
    w.writerows(overall)

# ---- markdown summary --------------------------------------------------------
md = [f"Rounds: {', '.join(rounds)} | rows: {len(rows)}", "",
      "| Client | " + " | ".join(SITE_NAMES[s] for s in SITES) + " |",
      "|---" * (len(SITES) + 1) + "|"]
for c in CLIENTS:
    md.append(f"| {CLIENT_NAMES[c]} | " + " | ".join(
        f"{next(x for x in cell if x['client'] == c and x['site'] == s)['success_pct']:.0f}%" for s in SITES) + " |")
md += ["", "| Client | Median s (static) | p95 s (static) | Median s (JS) | p95 s (JS) | LOC | Peak MB | Credits |",
       "|---|---|---|---|---|---|---|---|"]
for o in overall:
    md.append(f"| {CLIENT_NAMES[o['client']]} | {o['median_s_static']} | {o['p95_s_static']} | {o['median_s_js'] or '–'} | "
              f"{o['p95_s_js'] or '–'} | {o['loc']} | {o['peak_mem_mb']} | {o['credits_total'] or '–'} |")
(RES / "summary.md").write_text("\n".join(md) + "\n")
print("\n".join(md))

# ---- chart 1: success grid ---------------------------------------------------
cmap = LinearSegmentedColormap.from_list("blue", ["#f1f5fb", "#9cc2ee", BLUE, "#174a87"])
fig, ax = plt.subplots(figsize=(13, 5.4), dpi=200)
gap = 0.06
for i, c in enumerate(CLIENTS):
    for j, s in enumerate(SITES):
        v = next(x for x in cell if x["client"] == c and x["site"] == s)["success_pct"]
        ax.add_patch(FancyBboxPatch((j + gap, i + gap), 1 - 2 * gap, 1 - 2 * gap,
                                    boxstyle="round,pad=0,rounding_size=0.06", facecolor=cmap(v / 100), linewidth=0))
        ax.text(j + 0.5, i + 0.5, f"{v:.0f}%", ha="center", va="center", fontsize=12,
                color="#ffffff" if v >= 60 else INK, fontweight="bold" if v in (0, 100) else "normal")
ax.set_xlim(0, len(SITES))
ax.set_ylim(len(CLIENTS), 0)
ax.set_xticks([j + 0.5 for j in range(len(SITES))])
ax.set_xticklabels([SITE_NAMES[s].replace(" /", "\n/") for s in SITES], fontsize=10.5, color=INK2)
ax.xaxis.tick_top()
ax.set_yticks([i + 0.5 for i in range(len(CLIENTS))])
ax.set_yticklabels([CLIENT_NAMES[c] for c in CLIENTS], fontsize=11.5)
for side in ax.spines.values():
    side.set_visible(False)
ax.tick_params(length=0)
ax.axvline(6, color=INK2, lw=1, ls=(0, (2, 3)))
ax.text(7, len(CLIENTS) + 0.45, "JavaScript pages", ha="center", va="center", fontsize=10.5, color=INK2)
ax.text(3, len(CLIENTS) + 0.45, "Static pages", ha="center", va="center", fontsize=10.5, color=INK2)
fig.suptitle("Share of requests that returned the expected data", x=0.012, ha="left", fontsize=16, fontweight="bold", y=0.99)
n_note = "50 requests per client per site per round (10 on Hacker News and Wikipedia)"
fig.text(0.012, 0.915, f"6 setups x 8 sites, {len(rounds)} round{'s' if len(rounds) != 1 else ''} on Nov 1, 2026. {n_note}.", fontsize=10.5, color=INK2)
fig.text(0.012, 0.012, "The 95% and 99% cells are misses during a 3-minute network outage on the test machine (21:17 to 21:21 UTC). Data and code: github.com/yourtechmafia/python-web-scraping-tests", fontsize=9, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 0.9))
fig.savefig(IMG / "fetch-test-success-by-site.png", facecolor=SURFACE)
plt.close(fig)


# ---- chart 2: median time per page --------------------------------------------
def hbar(ax, labels, values, fmt, note):
    ys = list(range(len(labels)))[::-1]
    top = max(v for v in values if v == v) * 1.3
    for y, v in zip(ys, values):
        if v != v:  # nan: no successful requests
            ax.text(top * 0.01, y, "no data returned", va="center", fontsize=10.5, color=MUTED, style="italic")
            continue
        ax.add_patch(FancyBboxPatch((0, y - 0.28), v, 0.56, boxstyle="round,pad=0,rounding_size=0.004",
                                    mutation_aspect=0.02, linewidth=0, facecolor=BLUE))
        ax.text(v + top * 0.015, y, fmt.format(v), va="center", fontsize=10.5, color=INK)
    ax.set_xlim(0, top)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=11)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=10)
    ax.text(0, 1.02, note, transform=ax.transAxes, fontsize=9.5, color=MUTED)


def site_median(c, site):
    t = times(by[(c, site)])
    return statistics.median(t) if t else float("nan")


fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(15, 5.4), dpi=200)
labels = [CLIENT_NAMES[c] for c in CLIENTS]
hbar(a1, labels, [float(o["median_s_static"]) if o["median_s_static"] != "" else float("nan") for o in overall],
     "{:.2f} s", "6 static sites, successful requests only")
a1.set_title("Static pages", loc="left", fontsize=13, fontweight="bold", pad=22)
hbar(a2, labels, [site_median(c, "quotes_js") for c in CLIENTS], "{:.2f} s", "renders right after the page loads")
a2.set_title("Quotes /js/", loc="left", fontsize=13, fontweight="bold", pad=22)
hbar(a3, labels, [site_median(c, "quotes_js_delayed") for c in CLIENTS], "{:.1f} s", "renders after a deliberate 10 s delay")
a3.set_title("Quotes /js-delayed/", loc="left", fontsize=13, fontweight="bold", pad=22)
for ax in (a2, a3):
    ax.set_yticklabels([])
fig.suptitle("Median time per page, lower is faster", x=0.012, ha="left", fontsize=16, fontweight="bold", y=0.99)
fig.text(0.012, 0.012, "Measured on a MacBook Pro (M3 Max), Python 3.15.2, Nov 1, 2026. Data: github.com/yourtechmafia/python-web-scraping-tests",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 0.93), w_pad=3)
fig.savefig(IMG / "fetch-test-median-time.png", facecolor=SURFACE)
plt.close(fig)

# ---- article tables -------------------------------------------------------------
def fmt_s(v, nd=2):
    return "–" if v != v else f"{v:.{nd}f} s"


art = ["| Setup | " + " | ".join(SITE_NAMES[s] for s in SITES) + " |", "| ----- " * (len(SITES) + 1) + "|"]
for c in CLIENTS:
    art.append(f"| {CLIENT_NAMES[c]} | " + " | ".join(
        f"{next(x for x in cell if x['client'] == c and x['site'] == s)['success_pct']:.0f}%" for s in SITES) + " |")
art += ["", "| Setup | Median, static pages | p95, static pages | Median, /js/ | Median, /js-delayed/ | Peak memory, one page | Lines of code | Credits used |",
        "| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |"]
for o in overall:
    c = o["client"]
    art.append(f"| {CLIENT_NAMES[c]} | {fmt_s(float(o['median_s_static']))} | {fmt_s(float(o['p95_s_static']))} | "
               f"{fmt_s(site_median(c, 'quotes_js'))} | {fmt_s(site_median(c, 'quotes_js_delayed'), 1)} | "
               f"{float(o['peak_mem_mb']):.1f} MB | {o['loc']} | {o['credits_total'] if o['credits_total'] != '' else '–'} |")
(RES / "article_tables.md").write_text("\n".join(art) + "\n")
print("\n".join(art))

# ---- chart 3: parser benchmark --------------------------------------------------
pb = list(csv.DictReader(open(RES / "parser_benchmark.csv")))
FILES = [("books.html", "Books to Scrape listing (50 KB)"), ("wikipedia.html", "Long Wikipedia article (2 MB)"),
         ("generated_1mb.html", "Generated product grid (1 MB)")]
PARSERS = ["bs4 + html.parser", "bs4 + html5lib", "bs4 + lxml", "parsel", "lxml.html", "selectolax (lexbor)"]
fig, axes = plt.subplots(1, 3, figsize=(14, 5.4), dpi=200)
for ax, (fname, title) in zip(axes, FILES):
    vals = [float(next(r for r in pb if r["file"] == fname and r["parser"] == p)["median_ms"]) for p in PARSERS]
    hbar(ax, PARSERS, vals, "{:.1f} ms" if max(vals) > 20 else "{:.2f} ms", "median of 1,000 runs, parse + extract")
    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", pad=22)
    if ax is not axes[0]:
        ax.set_yticklabels([])
fig.suptitle("HTML parser speed, lower is faster", x=0.012, ha="left", fontsize=16, fontweight="bold", y=0.99)
fig.text(0.012, 0.012, "Same fields extracted by every parser. Python 3.15.2, M3 Max, Nov 1, 2026. Data: github.com/yourtechmafia/python-web-scraping-tests",
         fontsize=9, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 0.93), w_pad=2.5)
fig.savefig(IMG / "parser-benchmark-median-time.png", facecolor=SURFACE)
plt.close(fig)
print("charts written to", IMG)
