from pathlib import Path
import csv


# ============================================================
# Paths
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
HW_DIR = SCRIPT_DIR.parent
RESULTS_DIR = HW_DIR / "results"


# ============================================================
# Load CSV files
# ============================================================

def load_results(filename):
    path = RESULTS_DIR / filename

    with path.open("r", newline="", encoding="utf-8") as f:
        return {
            row["standard"]: row
            for row in csv.DictReader(f)
        }


read1 = load_results("read1_results.csv")
read4 = load_results("read4_results.csv")
read16 = load_results("read16_results.csv")
copy = load_results("copy_results.csv")


STANDARDS = [
    "DDR3",
    "DDR4",
    "DDR5",
    "GDDR6",
    "GDDR7",
    "LPDDR5",
    "LPDDR6",
    "HBM1",
    "HBM2",
    "HBM3",
    "HBM4",
]


def num(value):
    return float(value)


def row_percentages(row):
    hits = num(row["row_hits"])
    misses = num(row["row_misses"])
    conflicts = num(row["row_conflicts"])

    total = hits + misses + conflicts

    return (
        100.0 * hits / total,
        100.0 * misses / total,
        100.0 * conflicts / total,
    )


# ============================================================
# TABLE A
# Absolute performance
# ============================================================

WIDTH = 78

print()
print("=" * WIDTH)
print("TABLE A — ABSOLUTE PERFORMANCE")
print("Each entry = Throughput (GB/s) / Avg. Read Latency (ns)")
print("COPY uses total throughput (read + write).")
print("=" * WIDTH)

print(
    f"{'DRAM':<8}"
    f"{'R1':>17}"
    f"{'R4':>17}"
    f"{'R16':>17}"
    f"{'COPY':>17}"
)

print("-" * WIDTH)

for standard in STANDARDS:

    r1 = read1[standard]
    r4 = read4[standard]
    r16 = read16[standard]
    cp = copy[standard]

    v1 = (
        f"{num(r1['throughput_GBps']):.2f}/"
        f"{num(r1['avg_read_latency_ns']):.1f}"
    )

    v4 = (
        f"{num(r4['throughput_GBps']):.2f}/"
        f"{num(r4['avg_read_latency_ns']):.1f}"
    )

    v16 = (
        f"{num(r16['throughput_GBps']):.2f}/"
        f"{num(r16['avg_read_latency_ns']):.1f}"
    )

    vcopy = (
        f"{num(cp['total_throughput_GBps']):.2f}/"
        f"{num(cp['avg_read_latency_ns']):.1f}"
    )

    print(
        f"{standard:<8}"
        f"{v1:>17}"
        f"{v4:>17}"
        f"{v16:>17}"
        f"{vcopy:>17}"
    )


# ============================================================
# TABLE B
# Normalized performance vs READ-1
# ============================================================

print()
print()
print("=" * WIDTH)
print("TABLE B — NORMALIZED PERFORMANCE VS READ-1")
print("Each entry = Throughput ratio / Read-latency ratio")
print("READ-1 baseline = 1.00 / 1.00")
print("=" * WIDTH)

print(
    f"{'DRAM':<8}"
    f"{'R1':>17}"
    f"{'R4':>17}"
    f"{'R16':>17}"
    f"{'COPY':>17}"
)

print("-" * WIDTH)

for standard in STANDARDS:

    r1 = read1[standard]
    r4 = read4[standard]
    r16 = read16[standard]
    cp = copy[standard]

    base_bw = num(r1["throughput_GBps"])
    base_lat = num(r1["avg_read_latency_ns"])

    r1_value = "1.00/1.00"

    r4_value = (
        f"{num(r4['throughput_GBps']) / base_bw:.2f}/"
        f"{num(r4['avg_read_latency_ns']) / base_lat:.2f}"
    )

    r16_value = (
        f"{num(r16['throughput_GBps']) / base_bw:.2f}/"
        f"{num(r16['avg_read_latency_ns']) / base_lat:.2f}"
    )

    copy_value = (
        f"{num(cp['total_throughput_GBps']) / base_bw:.2f}/"
        f"{num(cp['avg_read_latency_ns']) / base_lat:.2f}"
    )

    print(
        f"{standard:<8}"
        f"{r1_value:>17}"
        f"{r4_value:>17}"
        f"{r16_value:>17}"
        f"{copy_value:>17}"
    )


# ============================================================
# TABLE C
# Row-buffer behavior
# ============================================================

print()
print()
print("=" * WIDTH)
print("TABLE C — ROW-BUFFER BEHAVIOR")
print("Each entry = Hit % / Miss % / Conflict %")
print("=" * WIDTH)

print(
    f"{'DRAM':<8}"
    f"{'R1':>17}"
    f"{'R4':>17}"
    f"{'R16':>17}"
    f"{'COPY':>17}"
)

print("-" * WIDTH)

for standard in STANDARDS:

    rows = [
        read1[standard],
        read4[standard],
        read16[standard],
        copy[standard],
    ]

    values = []

    for row in rows:
        hit, miss, conflict = row_percentages(row)

        values.append(
            f"{hit:.1f}/{miss:.1f}/{conflict:.1f}"
        )

    print(
        f"{standard:<8}"
        f"{values[0]:>17}"
        f"{values[1]:>17}"
        f"{values[2]:>17}"
        f"{values[3]:>17}"
    )

# ============================================================
# TABLE D
# Simulated time
# ============================================================

TIME_WIDTH = 62

print()
print()
print("=" * TIME_WIDTH)
print("TABLE D — SIMULATED TIME (ms)")
print("=" * TIME_WIDTH)

print(
    f"{'DRAM':<8}"
    f"{'R1':>13}"
    f"{'R4':>13}"
    f"{'R16':>13}"
    f"{'COPY':>13}"
)

print("-" * TIME_WIDTH)

for standard in STANDARDS:

    t1 = num(read1[standard]["simulated_time_ns"]) / 1_000_000
    t4 = num(read4[standard]["simulated_time_ns"]) / 1_000_000
    t16 = num(read16[standard]["simulated_time_ns"]) / 1_000_000
    tcp = num(copy[standard]["simulated_time_ns"]) / 1_000_000

    print(
        f"{standard:<8}"
        f"{t1:>13.3f}"
        f"{t4:>13.3f}"
        f"{t16:>13.3f}"
        f"{tcp:>13.3f}"
    )

print()
