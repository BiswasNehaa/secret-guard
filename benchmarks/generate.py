"""Generate a synthetic corpus for the scan-performance benchmark.

The corpus mixes plain source-shaped noise with a low, fixed density of
real secret patterns (exactly one per file), so a scan over it exercises
both the "no match" fast path most lines take and real finding
construction, without depending on any actual project's files. Content is
seeded, so repeated runs generate byte-identical corpora.
"""

import os
import random

FILE_COUNT = 200
LINES_PER_FILE = 200
SEED = 20240517

NOISE_LINES = [
    "def handler(request):",
    "    return {'status': 'ok', 'id': request.id}",
    "# TODO: refactor this before the next release",
    "import os, sys, json",
    "class Widget:",
    "    def __init__(self, name):",
    "        self.name = name",
    "value = compute(a, b, c) + offset",
    "logger.info('processed %d items', count)",
    "",
]

SECRET_LINE = "AWS_KEY = 'AKIAABCDEFGHIJKLMNOP'  # rotate before shipping"


def generate(root, file_count=FILE_COUNT, lines_per_file=LINES_PER_FILE, seed=SEED):
    """Write a synthetic corpus of file_count files under root.

    Returns the total number of bytes written, for throughput calculation.
    """

    rng = random.Random(seed)
    total_bytes = 0
    os.makedirs(root, exist_ok=True)
    for i in range(file_count):
        lines = [rng.choice(NOISE_LINES) for _ in range(lines_per_file)]
        lines[rng.randrange(lines_per_file)] = SECRET_LINE
        content = "\n".join(lines) + "\n"
        path = os.path.join(root, f"module_{i:04d}.py")
        # newline="" disables platform newline translation, so the file on
        # disk is always exactly len(content.encode()) bytes -- otherwise
        # Windows silently writes \r\n and total_bytes undercounts what
        # was actually read back, inflating the computed MB/s.
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        total_bytes += len(content.encode("utf-8"))
    return total_bytes
