"""Fetch test: every client requests every site, and we check the data is there.

Usage: uv run python fetch_test/run.py <round> [--sites a,b] [--clients x,y] [--n N]

One worker process per host, so pacing holds per host while different hosts run
in parallel. Inside a worker, clients take turns request by request (round-robin)
so no client gets a quieter time of day than another. Raw rows go to
results/fetch_round<round>.csv.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from itertools import groupby
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))
from clients import CLIENTS  # noqa: E402
from sites import SITES, host  # noqa: E402

FIELDS = ["round", "ts_utc", "host", "site", "client", "i", "status", "ok", "matches", "elapsed_s",
          "bytes", "credits", "auto_cost", "initial_status", "wait_timed_out", "error"]


def run_host(round_no: int, sites, client_names, n_override):
    clients = [c() for c in CLIENTS if c.name in client_names]
    rows, last = [], 0.0
    partial = Path(__file__).parents[1] / "results" / "partial" / f"round{round_no}_{host(sites[0])}.csv"
    partial.parent.mkdir(parents=True, exist_ok=True)
    pf = partial.open("w", newline="", encoding="utf-8")
    pw = csv.DictWriter(pf, fieldnames=FIELDS)
    pw.writeheader()
    try:
        for site in sites:
            n = n_override or site.requests
            for i in range(n):
                for client in clients:
                    gap = site.interval_s - (time.monotonic() - last)
                    if gap > 0:
                        time.sleep(gap)
                    last = time.monotonic()
                    row = {"round": round_no, "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                           "host": host(site), "site": site.key, "client": client.name, "i": i}
                    t0 = time.perf_counter()
                    try:
                        status, html, extra = client.fetch(site)
                        row["elapsed_s"] = round(time.perf_counter() - t0, 3)
                        matches = len(BeautifulSoup(html, "lxml").select(site.selector))
                        row.update(status=status, matches=matches, bytes=len(html.encode()),
                                   ok=int(status == 200 and matches >= site.min_matches), **extra)
                    except Exception as exc:  # record every failure, never stop the run
                        row.update(elapsed_s=round(time.perf_counter() - t0, 3), ok=0,
                                   error=f"{type(exc).__name__}: {str(exc)[:160]}")
                    rows.append(row)
                    pw.writerow(row)
                    pf.flush()
                    print(f"[{row['site']:22s}] {client.name:17s} #{i:02d} ok={row['ok']} "
                          f"m={row.get('matches')} {row['elapsed_s']}s cr={row.get('credits')} {row.get('error', '')}", flush=True)
    finally:
        pf.close()
        for c in clients:
            try:
                c.close()
            except Exception:
                pass
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round", type=int)
    ap.add_argument("--sites")
    ap.add_argument("--clients")
    ap.add_argument("--n", type=int)
    args = ap.parse_args()
    sites = [s for s in SITES if not args.sites or s.key in args.sites.split(",")]
    client_names = args.clients.split(",") if args.clients else [c.name for c in CLIENTS]
    groups = [list(g) for _, g in groupby(sorted(sites, key=host), key=host)]
    out = Path(__file__).parents[1] / "results" / f"fetch_round{args.round}.csv"
    with ProcessPoolExecutor(max_workers=len(groups)) as pool:
        futures = [pool.submit(run_host, args.round, g, client_names, args.n) for g in groups]
        rows = [r for f in futures for r in f.result()]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
