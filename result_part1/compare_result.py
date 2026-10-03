#!/usr/bin/env python3
import os
import re
import matplotlib.pyplot as plt

RUNS = ["run3", "run4", "run5", "run6", "run7"]
SUMMARY_NAME = "summary.txt"
OUTPUT_NAME = "combined.png"


def parse_summary(summary_path):
    xs = []  # Total GB/s
    ys = []  # Latency ns

    with open(summary_path, "r") as f:
        for line in f:
            line = line.strip()

            # 숫자로 시작하는 데이터 줄만 처리
            if not line or not line[0].isdigit():
                continue

            parts = line.split()
            # 형식:
            # Pause N ReadGB/s WriteGB/s TotalGB/s Latencyns
            # 예: 0 3 27.997 0.001 27.998 134.18
            if len(parts) < 6:
                continue

            total_gbs = float(parts[4])
            latency_ns = float(parts[5])

            xs.append(total_gbs)
            ys.append(latency_ns)

    return xs, ys


def main():
    plt.figure(figsize=(8, 6))

    for run in RUNS:
        summary_path = os.path.join(run, SUMMARY_NAME)

        if not os.path.isfile(summary_path):
            print(f"Skipping {run}: {summary_path} not found")
            continue

        xs, ys = parse_summary(summary_path)

        if not xs:
            print(f"Skipping {run}: no valid data")
            continue

        plt.plot(xs, ys, linestyle="--", label=run)

    plt.xlabel("Bandwidth (GB/s)")
    plt.ylabel("Latency (ns)")
    plt.title("Bandwidth-Latency Curves")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_NAME, dpi=200)

    print(f"Saved: {OUTPUT_NAME}")


if __name__ == "__main__":
    main()
