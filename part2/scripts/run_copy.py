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

TRACE_PATH = HW_DIR / "traces" / "copy.trace"

RESULTS_DIR = HW_DIR / "results"
RESULTS_PATH = RESULTS_DIR / "copy_results.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if not TRACE_PATH.exists():
    raise FileNotFoundError(
        f"COPY trace does not exist:\n{TRACE_PATH}"
    )


# ============================================================
# Run COPY on one supplied DRAM configuration
# ============================================================

def run_copy(cfg):
    name = cfg["name"]

    print()
    print("=" * 72)
    print(f"COPY : {name}")
    print("=" * 72)
    print(f"Organization : {cfg['org_preset']}")
    print(f"Timing       : {cfg['timing_preset']}")
    print()

    # --------------------------------------------------------
    # LoadStoreTrace frontend
    #
    # Pattern:
    #   LD B[0]
    #   ST A[0]
    #   LD B[1]
    #   ST A[1]
    #   ...
    #
    # 500,000 loads + 500,000 stores
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
    simulated_time_ns = cycles * spec.time_unit_ns

    avg_read_latency_cycles = ctrl_stats["avg_read_latency"]
    avg_read_latency_ns = (
        avg_read_latency_cycles * spec.time_unit_ns
    )

    read_throughput_GBps = (
        ctrl_stats["read_throughput_MBps"] / 1000.0
    )

    write_throughput_GBps = (
        ctrl_stats["write_throughput_MBps"] / 1000.0
    )

    total_throughput_GBps = (
        ctrl_stats["total_throughput_MBps"] / 1000.0
    )

    read_requests = ctrl_stats["num_read_reqs"]
    write_requests = ctrl_stats["num_write_reqs"]

    # --------------------------------------------------------
    # Row-buffer statistics
    # --------------------------------------------------------

    row_hits = ctrl_stats["row_hits"]
    row_misses = ctrl_stats["row_misses"]
    row_conflicts = ctrl_stats["row_conflicts"]

    read_row_hits = ctrl_stats["read_row_hits"]
    read_row_misses = ctrl_stats["read_row_misses"]
    read_row_conflicts = ctrl_stats["read_row_conflicts"]

    write_row_hits = ctrl_stats["write_row_hits"]
    write_row_misses = ctrl_stats["write_row_misses"]
    write_row_conflicts = ctrl_stats["write_row_conflicts"]

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

    print()
    print(
        f"Read throughput:         "
        f"{read_throughput_GBps:.3f} GB/s"
    )
    print(
        f"Write throughput:        "
        f"{write_throughput_GBps:.3f} GB/s"
    )
    print(
        f"Total throughput:        "
        f"{total_throughput_GBps:.3f} GB/s"
    )

    print()
    print("Overall row statistics:")
    print(f"  Row hits:              {row_hits}")
    print(f"  Row misses:            {row_misses}")
    print(f"  Row conflicts:         {row_conflicts}")
    print(f"  Classified requests:   {classified_requests}")

    print()
    print("Read row statistics:")
    print(f"  Read row hits:         {read_row_hits}")
    print(f"  Read row misses:       {read_row_misses}")
    print(f"  Read row conflicts:    {read_row_conflicts}")

    print()
    print("Write row statistics:")
    print(f"  Write row hits:        {write_row_hits}")
    print(f"  Write row misses:      {write_row_misses}")
    print(f"  Write row conflicts:   {write_row_conflicts}")

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

        "read_throughput_GBps": read_throughput_GBps,
        "write_throughput_GBps": write_throughput_GBps,
        "total_throughput_GBps": total_throughput_GBps,

        "row_hits": row_hits,
        "row_misses": row_misses,
        "row_conflicts": row_conflicts,
        "row_classified_requests": classified_requests,

        "read_row_hits": read_row_hits,
        "read_row_misses": read_row_misses,
        "read_row_conflicts": read_row_conflicts,

        "write_row_hits": write_row_hits,
        "write_row_misses": write_row_misses,
        "write_row_conflicts": write_row_conflicts,
    }


# ============================================================
# Main
# ============================================================

def main():
    print(f"Ramulator2 root : {REPO_ROOT}")
    print(f"COPY trace      : {TRACE_PATH}")
    print(f"Output CSV      : {RESULTS_PATH}")

    results = []

    standards = sorted(STANDARDS.keys())

    print()
    print(
        f"Running COPY on "
        f"{len(standards)} supplied DRAM configurations..."
    )

    for standard in standards:
        cfg = STANDARDS[standard]
        result = run_copy(cfg)
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
    print("COPY COMPLETE")
    print("=" * 72)
    print(f"Configurations completed: {len(results)}")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
