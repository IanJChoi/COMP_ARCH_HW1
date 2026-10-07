from pathlib import Path

NUM_REQUESTS = 1_000_000
CACHE_LINE_BYTES = 64

NUM_ELEMENTS = NUM_REQUESTS // 2

# B and A use separate, non-overlapping address regions.
B_BASE_ADDR = 0x0
A_BASE_ADDR = NUM_ELEMENTS * CACHE_LINE_BYTES

output_path = (
    Path(__file__).resolve().parent.parent
    / "traces"
    / "copy.trace"
)

with output_path.open("w") as f:
    for i in range(NUM_ELEMENTS):
        b_addr = B_BASE_ADDR + i * CACHE_LINE_BYTES
        a_addr = A_BASE_ADDR + i * CACHE_LINE_BYTES

        # B[i] -> read
        f.write(f"LD 0x{b_addr:x}\n")

        # A[i] -> write
        f.write(f"ST 0x{a_addr:x}\n")

print(f"Generated {NUM_REQUESTS:,} requests")
print(f"Loads: {NUM_ELEMENTS:,}")
print(f"Stores: {NUM_ELEMENTS:,}")
print(f"Output: {output_path}")
