"""Decision flow image for 'Match each kind of page to a tool'."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("decision_flow.png")
SURFACE, INK, INK2, LINE = "#fcfcfb", "#0b0b0b", "#52514e", "#c3c2b7"
Q_FILL, A_FILL, A_EDGE = "#f1f0ec", "#e8f1fb", "#2a78d6"
plt.rcParams.update({"font.family": "Helvetica", "font.size": 12})

fig, ax = plt.subplots(figsize=(12, 8.2), dpi=200)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
ax.set_xlim(0, 12); ax.set_ylim(0, 8.2); ax.axis("off")

def box(x, y, w, h, text, fill, edge, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=fill, edgecolor=edge, linewidth=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=12, color=INK, fontweight="bold" if bold else "normal", linespacing=1.35)

def arrow(x1, y1, x2, y2, label=None, lx=0, ly=0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.3, shrinkA=0, shrinkB=0))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=11, color=INK2, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none"))

QX, AX = 3.2, 9.0
qs = [(6.7, "Official API or a JSON endpoint\nin the Network tab?"),
      (5.2, "Is the data in View Source\n(the raw HTML)?"),
      (3.7, "Does plain Requests\nget blocked?"),
      (2.2, "Hundreds of pages\nor a whole site?")]
ans = {6.7: "Request the JSON directly\n(Requests)", 5.2: "Playwright, or a scraping API\nthat renders JavaScript",
       3.7: "curl_cffi, then a scraping API\nif it's still blocked", 2.2: "Scrapy, or asyncio with httpx"}
for i, (y, q) in enumerate(qs):
    box(QX, y, 4.6, 1.05, q, Q_FILL, LINE)
    yes_text = ans[y]
    label = "No" if y == 5.2 else "Yes"
    box(AX, y, 4.6, 1.05, yes_text, A_FILL, A_EDGE)
    arrow(QX + 2.3, y, AX - 2.3, y, label, ly=0.22)
    if i < len(qs) - 1:
        arrow(QX, y - 0.53, QX, qs[i + 1][0] + 0.53, "Yes" if y == 5.2 else "No", lx=0.35)
box(QX, 0.75, 4.6, 0.9, "Requests and Beautiful Soup", A_FILL, A_EDGE, bold=True)
arrow(QX, 2.2 - 0.53, QX, 0.75 + 0.45, "No", lx=0.35)
ax.text(0.65, 8.05, "Pick the smallest tool that gets the data", fontsize=16, fontweight="bold", color=INK, va="top")
fig.savefig(OUT, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.2)
print("wrote", OUT)
