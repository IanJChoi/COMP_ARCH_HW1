#!/usr/bin/env python3
"""Show MESS bandwidth/latency results and draw a BW-latency graph.

Usage:
    python3 show_mess.py run1

Expected input:
    result/run1/raw/bw/bw_100_*.txt
    result/run1/raw/lat/lat_100_*.txt

Outputs:
    result/run1/summary.txt
    result/run1/bandwidth_latency.png
"""

from pathlib import Path
from statistics import mean
import re
import sys

try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("matplotlib is required: sudo apt install python3-matplotlib")

result_dir = Path(__file__).resolve().parent
run = sys.argv[1] if len(sys.argv) > 1 else "run1"
run_dir = result_dir / run
source = run_dir / "raw"

if not (source / "bw").is_dir() or not (source / "lat").is_dir():
    sys.exit(
        f"Raw data not found in {source}\n"
        f"Expected: {source}/bw and {source}/lat"
    )


def bandwidth(path):
    samples = []

    for block in path.read_text().split("Performance counter stats for system wide:"):
        read = re.search(r"\b(\d+)\s+uncore_imc/data_reads/", block)
        write = re.search(r"\b(\d+)\s+uncore_imc/data_writes/", block)
        elapsed = re.search(r"([\d.]+)\s+seconds time elapsed", block)

        if read and write and elapsed:
            sec = float(elapsed.group(1))
            if sec > 0:
                rd = int(read.group(1)) * 64 / sec / 1e9
                wr = int(write.group(1)) * 64 / sec / 1e9
                samples.append((rd, wr))

    return samples


def latency(path):
    return [
        float(x)
        for x in re.findall(r"([\d.]+)\s+latency_direct_ns\b", path.read_text())
    ]


rows = []

for bwfile in sorted(
    (source / "bw").glob("bw_100_*.txt"),
    key=lambda p: int(p.stem.split("_")[-1]),
):
    pause = int(bwfile.stem.split("_")[-1])
    latfile = source / "lat" / f"lat_100_{pause}.txt"

    if not latfile.exists():
        print(f"Skipped pause={pause}: latency file missing", file=sys.stderr)
        continue

    bws = bandwidth(bwfile)
    lats = latency(latfile)

    if not bws or len(bws) != len(lats):
        print(
            f"Skipped pause={pause}: BW/LAT samples mismatch "
            f"({len(bws)} vs {len(lats)})",
            file=sys.stderr,
        )
        continue

    rd = mean(x[0] for x in bws)
    wr = mean(x[1] for x in bws)
    total = rd + wr
    lat = mean(lats)

    rows.append((pause, len(bws), rd, wr, total, lat))


if not rows:
    sys.exit(f"No valid MESS data found in {source}")


# Text table
lines = [
    f"{'Pause':>12} {'N':>3} {'Read GB/s':>12} {'Write GB/s':>12} "
    f"{'Total GB/s':>13} {'Latency ns':>13}",
    "-" * 73,
]

for pause, n, rd, wr, total, lat in rows:
    lines.append(
        f"{pause:>12} {n:>3} {rd:>12.3f} {wr:>12.3f} "
        f"{total:>13.3f} {lat:>13.2f}"
    )

table = "\n".join(lines) + "\n"
print(table, end="")

run_dir.mkdir(parents=True, exist_ok=True)

summary_path = run_dir / "summary.txt"
summary_path.write_text(table)


# Bandwidth-latency graph
plot_rows = sorted(rows, key=lambda row: row[4])

bandwidths = [row[4] for row in plot_rows]
latencies = [row[5] for row in plot_rows]

plt.figure(figsize=(8, 5))
plt.plot(bandwidths, latencies, marker="o")
plt.xlabel("Bandwidth (GB/s)")
plt.ylabel("Latency (ns)")
plt.title(f"MESS Bandwidth-Latency Curve ({run})")
plt.grid(True, alpha=0.3)
plt.tight_layout()

graph_path = run_dir / "bandwidth_latency.png"
plt.savefig(graph_path, dpi=180)
plt.close()

print(f"\nSaved: {summary_path}")
print(f"Saved: {graph_path}")
