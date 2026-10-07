from pathlib import Path

NUM_REQUESTS = 1_000_000
NUM_STREAMS = 4
CACHE_LINE_BYTES = 64

REQUESTS_PER_STREAM = NUM_REQUESTS // NUM_STREAMS

# Size occupied by one stream:
# 250,000 cache lines * 64 B = 16,000,000 B
STREAM_REGION_BYTES = REQUESTS_PER_STREAM * CACHE_LINE_BYTES

output_path = (
    Path(__file__).resolve().parent.parent
    / "traces"
    / "read4.trace"
)

with output_path.open("w") as f:
    for i in range(REQUESTS_PER_STREAM):
        for stream in range(NUM_STREAMS):
            base_addr = stream * STREAM_REGION_BYTES
            addr = base_addr + i * CACHE_LINE_BYTES
            f.write(f"LD 0x{addr:x}\n")

print(f"Generated {NUM_REQUESTS:,} requests")
print(f"Streams: {NUM_STREAMS}")
print(f"Requests per stream: {REQUESTS_PER_STREAM:,}")
print(f"Output: {output_path}")
