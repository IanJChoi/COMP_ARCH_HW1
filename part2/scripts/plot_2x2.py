import re
from pathlib import Path
import matplotlib.pyplot as plt

# ~/ramulator2
ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "read100_latency_throughput.txt"
OUTPUT = ROOT / "hw1_part2" / "results" / "latency_throughput_2x2.png"

data = {}
current = None

# Read the numerical results from the text output
with open(INPUT, "r") as f:
    for line in f:
        line = line.strip()

        # Example: === DDR4 ===
        match = re.match(r"^=== ([A-Za-z0-9]+) ===$", line)

        if match:
            current = match.group(1)

            data[current] = {
                "throughput": [],
                "latency": [],
            }

            continue

        # Example:
        # 20,16.034597,54.468535
        if current is not None:
            match = re.match(
                r"^(\d+),([0-9.]+),([0-9.]+)$",
                line
            )

            if match:
                throughput = float(match.group(2))
                latency = float(match.group(3))

                data[current]["throughput"].append(throughput)
                data[current]["latency"].append(latency)


families = {
    "DDR": ["DDR3", "DDR4", "DDR5"],
    "GDDR": ["GDDR6", "GDDR7"],
    "LPDDR": ["LPDDR5", "LPDDR6"],
    "HBM": ["HBM1", "HBM2", "HBM3", "HBM4"],
}


fig, axes = plt.subplots(
    2,
    2,
    figsize=(12, 9)
)

for ax, (family, standards) in zip(axes.flat, families.items()):

    for standard in standards:

        if standard not in data:
            continue

        ax.plot(
            data[standard]["throughput"],
            data[standard]["latency"],
            marker="o",
            markersize=3,
            linewidth=1.5,
            label=standard,
        )

    ax.set_title(
        family,
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("DRAM Throughput (GB/s)")
    ax.set_ylabel("DRAM Access Latency (ns)")

    ax.grid(
        True,
        linestyle="--",
        alpha=0.4
    )

    ax.legend()

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)


fig.suptitle(
    "Latency vs. Throughput — 100% Reads",
    fontsize=16,
    fontweight="bold"
)

fig.tight_layout()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(
    OUTPUT,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved: {OUTPUT}")
