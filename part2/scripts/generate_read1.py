from pathlib import Path

NUM_REQUESTS = 1_000_000
CACHE_LINE_BYTES = 64
BASE_ADDR = 0x0

# hw1_part2/traces/read1.trace
output_path = Path(__file__).resolve().parent.parent / "traces" / "read1.trace"

with output_path.open("w") as f:
    for i in range(NUM_REQUESTS):
        addr = BASE_ADDR + i * CACHE_LINE_BYTES
        f.write(f"LD 0x{addr:x}\n")

print(f"Generated {NUM_REQUESTS:,} requests")
print(f"Output: {output_path}")
