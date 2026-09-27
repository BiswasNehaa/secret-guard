"""Correctness tests for the benchmark tooling itself.

Not a performance assertion (that's benchmarks/run.py's own job, run as a
dedicated CI job, not part of this suite) — just proof that the generator
and runner are wired together correctly and don't crash or drift.
"""

import os
import shutil
import tempfile
import unittest

from benchmarks.generate import generate
from benchmarks.run import run_once


class GenerateCorpusTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._tmp, True)

    def test_writes_requested_file_count(self):
        generate(self._tmp, file_count=5, lines_per_file=10)
        self.assertEqual(
            len([n for n in os.listdir(self._tmp) if n.endswith(".py")]), 5
        )

    def test_returns_total_bytes_written(self):
        total = generate(self._tmp, file_count=3, lines_per_file=10)
        on_disk = sum(
            os.path.getsize(os.path.join(self._tmp, name))
            for name in os.listdir(self._tmp)
        )
        self.assertEqual(total, on_disk)

    def test_deterministic_for_a_fixed_seed(self):
        tmp_a = tempfile.mkdtemp()
        tmp_b = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp_a, True)
        self.addCleanup(shutil.rmtree, tmp_b, True)
        generate(tmp_a, file_count=4, lines_per_file=10, seed=42)
        generate(tmp_b, file_count=4, lines_per_file=10, seed=42)

        for name in sorted(os.listdir(tmp_a)):
            with open(os.path.join(tmp_a, name), encoding="utf-8") as f:
                content_a = f.read()
            with open(os.path.join(tmp_b, name), encoding="utf-8") as f:
                content_b = f.read()
            self.assertEqual(content_a, content_b)

    def test_each_file_has_exactly_one_seeded_secret_line(self):
        generate(self._tmp, file_count=5, lines_per_file=20)
        for name in os.listdir(self._tmp):
            with open(os.path.join(self._tmp, name), encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content.count("AKIAABCDEFGHIJKLMNOP"), 1)


class RunOnceTest(unittest.TestCase):
    def test_reports_positive_throughput_and_expected_finding_count(self):
        mb_per_second, findings_count = run_once()
        self.assertGreater(mb_per_second, 0)
        # One AWS-key rule match plus one entropy match per generated file,
        # at the default file_count=200 used when generate() is called
        # with no overrides (as run_once() does).
        self.assertEqual(findings_count, 400)


if __name__ == "__main__":
    unittest.main()
