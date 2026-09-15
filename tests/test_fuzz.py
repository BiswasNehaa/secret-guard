"""Fuzz testing for the detection rules and scanner.

Property under test: scanning any input, however hostile, never raises,
never takes an unreasonable amount of time (no catastrophic regex
backtracking), and produces the same result every time for a fixed seed.

No third-party fuzzing library is used, to keep this project's
zero-dependency principle intact for the parts of the toolchain that ship
with it — a small seeded random-string generator plays the role the issue
suggested ("hypothesis (or a small strategy)"), and needs no extra install
step in CI.
"""

import os
import random
import string
import tempfile
import time
import unittest

from secretguard.scanner import Scanner

# Wall-clock budget per fuzzed input. Generous enough to never flake on a
# slow CI runner, tight enough to still catch a genuine catastrophic
# regex-backtracking regression (which would take seconds, not
# milliseconds, even on a fast machine).
PER_CASE_BUDGET_SECONDS = 3.0

SEED = 20240517  # fixed so any discovered crash or hang is reproducible

# Alphabets chosen to be adversarial in different ways: full printable
# ASCII, near-misses on real rule prefixes (so the regex engine has to do
# real work rejecting almost-matches), regex/comment metacharacter soup,
# and non-ASCII/RTL/emoji text.
ADVERSARIAL_ALPHABETS = [
    string.printable,
    "AKIA0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ghp_-=:.",
    "-----BEGIN PRIVATE KEY-----\n",
    "aA0 \t\n#/*<>!-\"'\\",
    "🔑🔒😀مرحباשלום",
    "a",
]


def _random_strings(rng, count, max_len):
    for _ in range(count):
        alphabet = rng.choice(ADVERSARIAL_ALPHABETS)
        length = rng.randint(0, max_len)
        yield "".join(rng.choice(alphabet) for _ in range(length))


class FuzzDetectionRulesTest(unittest.TestCase):
    def _scan(self, text, rel_path="fuzz.txt"):
        scanner = Scanner(".")
        start = time.monotonic()
        try:
            findings = scanner.scan_text(rel_path, text)
        except Exception as exc:  # noqa: BLE001 - the property under test
            self.fail(
                f"scan_text raised {exc!r} on input of length {len(text)} "
                f"starting {text[:60]!r}"
            )
        elapsed = time.monotonic() - start
        self.assertLess(
            elapsed,
            PER_CASE_BUDGET_SECONDS,
            f"scan took {elapsed:.2f}s on input of length {len(text)} "
            "-- possible catastrophic backtracking",
        )
        return findings

    def test_random_short_strings_never_crash_or_hang(self):
        rng = random.Random(SEED)
        for text in _random_strings(rng, count=300, max_len=500):
            self._scan(text)

    def test_random_long_strings_never_crash_or_hang(self):
        rng = random.Random(SEED + 1)
        for text in _random_strings(rng, count=10, max_len=200_000):
            self._scan(text)

    def test_random_dotenv_content_never_crashes_or_hangs(self):
        rng = random.Random(SEED + 2)
        for text in _random_strings(rng, count=100, max_len=300):
            self._scan(text, rel_path=".env")

    def test_empty_and_degenerate_inputs(self):
        degenerate = (
            "", " ", "\n", "\x00", "a" * 100_000, "#" * 5_000, "/" * 5_000,
            "=" * 5_000, "-" * 5_000, "\\" * 5_000,
        )
        for text in degenerate:
            self._scan(text)

    def test_findings_are_deterministic_for_a_fixed_seed(self):
        rng = random.Random(SEED)
        texts = list(_random_strings(rng, count=50, max_len=500))

        def fingerprint(text):
            return [
                (f["rule_id"], f["line"], f["value"])
                for f in self._scan(text)
            ]

        first_pass = [fingerprint(t) for t in texts]
        second_pass = [fingerprint(t) for t in texts]
        self.assertEqual(first_pass, second_pass)

    def test_fuzzed_files_on_disk_via_full_scan(self):
        rng = random.Random(SEED + 3)
        with tempfile.TemporaryDirectory() as tmp:
            for i, text in enumerate(_random_strings(rng, count=25, max_len=2000)):
                path = os.path.join(tmp, f"fuzz_{i}.py")
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(text)
            start = time.monotonic()
            try:
                Scanner(tmp).scan()
            except Exception as exc:  # noqa: BLE001 - the property under test
                self.fail(f"Scanner.scan() raised {exc!r} over fuzzed files")
            elapsed = time.monotonic() - start
            self.assertLess(elapsed, PER_CASE_BUDGET_SECONDS * 25)


if __name__ == "__main__":
    unittest.main()
