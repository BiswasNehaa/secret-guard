"""Run the scan-performance benchmark and check it against a stored
baseline throughput.

Usage:
    python -m benchmarks.run                  # check against the stored baseline
    python -m benchmarks.run --update-baseline # record this run as the new baseline

Fails (exit code 1) if this run's throughput drops below half the stored
baseline. That factor is deliberately generous — it absorbs normal
CI-runner variance while still catching a genuine multi-x regression, per
the project's guard-against-silent-regressions goal for this suite.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import time

from secretguard.scanner import Scanner

from .generate import generate

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "baseline.json")
REGRESSION_FACTOR = 2.0  # this run's MB/s must stay above baseline / this


def _load_baseline():
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)["mb_per_second"]


def _save_baseline(mb_per_second):
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump({"mb_per_second": round(mb_per_second, 2)}, f, indent=2)
        f.write("\n")


def run_once():
    """Generate the corpus, scan it, and return (mb_per_second, findings_count).

    The very first read of a just-written file is measurably slower than
    later ones on some filesystems (page cache, on Windows often real-time
    antivirus scanning of new files) — a one-time cost unrelated to the
    scanner's own performance. An untimed warm-up scan absorbs that cost so
    the timed run measures the scanner, not the filesystem's first touch.
    """

    tmp = tempfile.mkdtemp(prefix="secret-guard-bench-")
    try:
        total_bytes = generate(tmp)
        megabytes = total_bytes / (1024 * 1024)

        Scanner(tmp).scan()  # warm-up, not timed

        scanner = Scanner(tmp)
        start = time.perf_counter()
        findings = scanner.scan()
        elapsed = time.perf_counter() - start
        mb_per_second = megabytes / elapsed if elapsed > 0 else float("inf")
        return mb_per_second, len(findings)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-baseline", action="store_true",
        help=(
            "Record this run's throughput as the new stored baseline "
            "instead of checking against the existing one."
        ),
    )
    args = parser.parse_args(argv)

    mb_per_second, findings_count = run_once()
    print(f"scanned corpus at {mb_per_second:.1f} MB/s ({findings_count} findings)")

    if args.update_baseline:
        _save_baseline(mb_per_second)
        print(f"baseline updated to {mb_per_second:.2f} MB/s")
        return 0

    baseline = _load_baseline()
    floor = baseline / REGRESSION_FACTOR
    print(f"baseline: {baseline:.2f} MB/s, floor: {floor:.2f} MB/s")
    if mb_per_second < floor:
        print(
            f"FAIL: throughput {mb_per_second:.2f} MB/s is more than "
            f"{REGRESSION_FACTOR:g}x slower than the {baseline:.2f} MB/s "
            "stored baseline.",
            file=sys.stderr,
        )
        return 1
    print("OK: throughput is within the regression threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
