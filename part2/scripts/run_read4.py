from pathlib import Path
import csv
import sys


# ============================================================
# Locate the Ramulator2 repository
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
HW_DIR = SCRIPT_DIR.parent
REPO_ROOT = HW_DIR.parent

RAMULATOR_PYTHON_DIR = REPO_ROOT / "python"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(RAMULATOR_PYTHON_DIR))


# These imports must happen AFTER sys.path is configured.
import ramulator

from tests.latency_throughput.testcases import STANDARDS
from tests.latency_throughput.utils.spec import resolve_spec


# ============================================================
# Input / output paths
# ============================================================

TRACE_PATH = HW_DIR / "traces" / "read4.trace"

RESULTS_DIR = HW_DIR / "results"
RESULTS_PATH = RESULTS_DIR / "read4_results.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if not TRACE_PATH.exists():
    raise FileNotFoundError(
        f"READ-4 trace does not exist:\n{TRACE_PATH}"
    )


# ============================================================
# Run READ-4 on one supplied DRAM configuration
# ============================================================

def run_read4(cfg):
    name = cfg["name"]

    print()
    print("=" * 72)
    print(f"READ-4 : {name}")
    print("=" * 72)
    print(f"Organization : {cfg['org_preset']}")
    print(f"Timing       : {cfg['timing_preset']}")
    print()

    # --------------------------------------------------------
    # LoadStoreTrace frontend
    # --------------------------------------------------------

    frontend = ramulator.frontend.LoadStoreTrace(
        clock_ratio=cfg["frontend_clock_ratio"],
        path=str(TRACE_PATH),
    )

    # --------------------------------------------------------
    # DRAM
    # --------------------------------------------------------

    dram_cls = getattr(
        ramulator.dram,
        cfg["dram_class"],
    )

    dram = dram_cls(
        org_preset=cfg["org_preset"],
        timing_preset=cfg["timing_preset"],
    )

    # --------------------------------------------------------
    # Controller
    # --------------------------------------------------------

    controller_cls = getattr(
        ramulator.controller,
        cfg["controller_class"],
    )

    scheduler_cls = getattr(
        ramulator.scheduler,
        cfg["scheduler_class"],
    )

    ctrl = controller_cls(
        dram=dram,
        scheduler=scheduler_cls(),
        refresh_manager=ramulator.refresh_manager.AllBank(),
        row_policy=ramulator.row_policy.Open(),
        addr_mapper=ramulator.addr_mapper.RoBaRaCoCh(),
        **cfg.get("controller_kwargs", {}),
    )

    # --------------------------------------------------------
    # Memory system
    # --------------------------------------------------------

    mem = ramulator.memory_system.GenericDRAM(
        clock_ratio=1,
        controllers=[ctrl],
        channel_mapper=ramulator.channel_mapper.CacheLineInterleave(),
    )

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    sim = ramulator.Simulation(frontend, mem)

    sim.run()
    sim.finalize()

    stats = sim.stats
    ctrl_stats = stats["memory_system"]["controller"]

    # --------------------------------------------------------
    # Convert cycle-based statistics to time
    # --------------------------------------------------------

    spec = resolve_spec(cfg)

    cycles = ctrl_stats["cycles"]

    simulated_time_ns = (
        cycles * spec.time_unit_ns
    )

    avg_read_latency_cycles = (
        ctrl_stats["avg_read_latency"]
    )

    avg_read_latency_ns = (
        avg_read_latency_cycles * spec.time_unit_ns
    )

    throughput_GBps = (
        ctrl_stats["total_throughput_MBps"] / 1000.0
    )

    read_requests = ctrl_stats["num_read_reqs"]
    write_requests = ctrl_stats["num_write_reqs"]

    row_hits = ctrl_stats["row_hits"]
    row_misses = ctrl_stats["row_misses"]
    row_conflicts = ctrl_stats["row_conflicts"]

    classified_requests = (
        row_hits
        + row_misses
        + row_conflicts
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print(f"Controller cycles:       {cycles}")
    print(f"Simulated time:          {simulated_time_ns:.2f} ns")

    print()
    print(f"Read requests:           {read_requests}")
    print(f"Write requests:          {write_requests}")

    print()
    print(
        f"Average read latency:    "
        f"{avg_read_latency_cycles:.2f} cycles"
    )
    print(
        f"Average read latency:    "
        f"{avg_read_latency_ns:.2f} ns"
    )
    print(
        f"Throughput:              "
        f"{throughput_GBps:.3f} GB/s"
    )

    print()
    print(f"Row hits:                {row_hits}")
    print(f"Row misses:              {row_misses}")
    print(f"Row conflicts:           {row_conflicts}")
    print(f"Row-classified requests: {classified_requests}")

    # --------------------------------------------------------
    # Result row for CSV
    # --------------------------------------------------------

    return {
        "standard": name,
        "dram_class": cfg["dram_class"],
        "org_preset": cfg["org_preset"],
        "timing_preset": cfg["timing_preset"],
        "frontend_clock_ratio": cfg["frontend_clock_ratio"],
        "controller_cycles": cycles,
        "simulated_time_ns": simulated_time_ns,
        "read_requests": read_requests,
        "write_requests": write_requests,
        "avg_read_latency_cycles": avg_read_latency_cycles,
        "avg_read_latency_ns": avg_read_latency_ns,
        "throughput_GBps": throughput_GBps,
        "row_hits": row_hits,
        "row_misses": row_misses,
        "row_conflicts": row_conflicts,
        "row_classified_requests": classified_requests,
    }


# ============================================================
# Main
# ============================================================

def main():
    print(f"Ramulator2 root : {REPO_ROOT}")
    print(f"READ-4 trace    : {TRACE_PATH}")
    print(f"Output CSV      : {RESULTS_PATH}")

    results = []

    standards = sorted(STANDARDS.keys())

    print()
    print(
        f"Running READ-4 on "
        f"{len(standards)} supplied DRAM configurations..."
    )

    for standard in standards:
        cfg = STANDARDS[standard]
        result = run_read4(cfg)
        results.append(result)

    # --------------------------------------------------------
    # Save summary CSV
    # --------------------------------------------------------

    with RESULTS_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys(),
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 72)
    print("READ-4 COMPLETE")
    print("=" * 72)
    print(f"Configurations completed: {len(results)}")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
