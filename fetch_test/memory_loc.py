"""Lines of code and peak memory for the minimal one-page scraper of each client.

LOC counts non-blank, non-comment lines. Peak memory is the highest combined
resident memory of the script's process tree (Playwright's browser processes
included), sampled every 20 ms with psutil. Each script runs 5 times; we keep
the median peak.
"""
import csv
import statistics
import subprocess
import sys
import time
from pathlib import Path

import psutil

HERE = Path(__file__).parent / "minimal"


def loc(path):
    return sum(1 for line in path.read_text().splitlines() if line.strip() and not line.strip().startswith("#"))


def peak_rss_mb(path):
    proc = subprocess.Popen([sys.executable, "-I", str(path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    root, peak = psutil.Process(proc.pid), 0
    while proc.poll() is None:
        try:
            total = root.memory_info().rss + sum(c.memory_info().rss for c in root.children(recursive=True))
            peak = max(peak, total)
        except psutil.Error:
            pass
        time.sleep(0.02)
    out = proc.stdout.read().decode()
    assert proc.returncode == 0 and out.count("\n") == 20, out[-300:]
    return peak / 1024 / 1024


rows = []
for path in sorted(HERE.glob("*.py")):
    peaks = []
    for _ in range(5):
        peaks.append(peak_rss_mb(path))
        time.sleep(2)
    rows.append({"client": path.stem.replace("_client", ""), "loc": loc(path),
                 "peak_mem_mb_median": round(statistics.median(peaks), 1),
                 "peak_mem_mb_runs": " ".join(f"{p:.1f}" for p in peaks)})
    print(rows[-1], flush=True)

out = Path(__file__).parents[1] / "results" / "memory_loc.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("wrote", out)
