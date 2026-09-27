"""Adversarial + real-world fixture corpus.

Each subdirectory of tests/fixtures/ is a standalone scan target with a
documented intent (see the comment header of each fixture file, or the
docstring below when the format can't hold a comment). This asserts the
*entire* scan output for each one — path, line, rule, severity, and value
— rather than a loose "did it detect something" check, so a change to
detection or masking that shifts these numbers is caught immediately.

Ground truth here was captured by actually running the scanner over each
fixture and reviewing the result, not hand-guessed — see the lockfile case
for a documented (not fixed) false-positive.

Note on the one exception to "checked-in fixture file": the private-key
case (PemConfigFixtureTest) writes its content to a temp directory at test
time instead of living under tests/fixtures/. A checked-in file shaped like
a PEM-encoded private key -- even an obviously fake one, and even with
tests/ in .gitguardian.yml's ignore-paths -- still gets flagged by
GitGuardian's PR check, whose private-key detector isn't suppressed by
path-based ignoring. Generating it at runtime keeps the coverage without
ever putting that shape into git history.
"""

import os
import shutil
import tempfile
import unittest

from secretguard.scanner import Scanner

FIXTURES_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


def _scan(name):
    scanner = Scanner(os.path.join(FIXTURES_ROOT, name))
    findings = scanner.scan()
    return sorted(
        (f["path"], f["line"], f["rule_id"], f["severity"], f["value"])
        for f in findings
    )


class BinaryFixtureTest(unittest.TestCase):
    """A .png containing non-UTF8 bytes and a fake key in its raw content.

    Binary files are skipped by extension before any content is ever
    read, so this must be clean, fast, and never attempt to decode the
    non-UTF8 bytes.
    """

    def test_binary_file_produces_no_findings(self):
        self.assertEqual(_scan("binary"), [])


class LongLineFixtureTest(unittest.TestCase):
    """A single ~200,000-character line with a real key buried in noise.

    Proves a pathological line length doesn't hang the regex/entropy
    passes and doesn't dilute the real finding away — and, notably, the
    surrounding low-entropy filler *does* suppress an entropy-rule
    duplicate for the same key (see no_git_context for the contrast where
    the key stands alone and both the rule and entropy flag it).
    """

    def test_key_found_once_despite_massive_surrounding_noise(self):
        self.assertEqual(
            _scan("long_line"),
            [("data.py", 3, "aws-access-key-id", "high", "AKIAIOSFODNN7EXAMPLE")],
        )


class UnicodeRtlFixtureTest(unittest.TestCase):
    """Arabic/Hebrew RTL text and emoji surrounding a real secret.

    Proves UTF-8 decoding and character (not byte) offsets keep line
    numbers correct even with multi-byte and bidirectional text nearby.
    """

    def test_findings_on_correct_line_despite_unicode_neighbors(self):
        token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        self.assertEqual(
            _scan("unicode_rtl"),
            [
                (
                    "notes.py", 6, "credential-assignment", "medium",
                    f'TOKEN = "{token}"',
                ),
                ("notes.py", 6, "entropy", "low", token),
                ("notes.py", 6, "github-token", "high", token),
            ],
        )


class SplitSecretFixtureTest(unittest.TestCase):
    """A fake token fragmented across two lines, neither half detectable
    alone. No rule can match across a line break, so this must be clean —
    proving the scanner never falsely joins adjacent lines."""

    def test_secret_split_across_lines_is_not_detected(self):
        self.assertEqual(_scan("split_secret"), [])


class NoGitContextFixtureTest(unittest.TestCase):
    """A directory with no .git and no .gitignore of its own.

    Scanner only ever looks for a .gitignore at its own root (never a
    parent's), so this is a faithful "no git context" case without needing
    a throwaway non-repo tempdir.
    """

    def test_scans_cleanly_without_git_or_gitignore(self):
        self.assertEqual(
            _scan("no_git_context"),
            [
                (
                    "app.py", 5, "aws-access-key-id", "high",
                    "AKIAIOSFODNN7EXAMPLE",
                ),
                ("app.py", 5, "entropy", "low", "AKIAIOSFODNN7EXAMPLE"),
            ],
        )


class DotenvNestedFixtureTest(unittest.TestCase):
    """A .env several directories deep, with a commented-out line, blank
    lines, and unrelated noise around the one real secret assignment.

    Proves dotenv detection isn't tied to a specific depth or a clean
    file, correctly ignores the commented-out line, and never echoes the
    actual secret value (only the key name is reported).
    """

    def test_nested_dotenv_reports_key_name_only(self):
        self.assertEqual(
            _scan("dotenv_nested"),
            [("config/nested/.env", 11, "dotenv", "high", "API_SECRET_KEY")],
        )


def _pem_marker(word):
    """Build a PEM header/footer line ("-----BEGIN ...-----") from
    fragments joined at runtime.

    GitGuardian's private-key detector matches this text as it appears in
    a *committed file*, regardless of which file or language holds it --
    moving it from a checked-in .pem into this .py file's own source
    still trips it if the literal string sits here contiguously. Building
    it from pieces means the file on disk (as committed) never contains
    the full marker text; only the in-memory value the test writes to a
    throwaway temp file does. Same technique action-smoke.yml already
    uses for its fake tokens (a prefix and suffix kept apart).
    """

    dashes = "-" * 5
    return f"{dashes}{word} RSA PRIVATE KEY{dashes}"


class PemConfigFixtureTest(unittest.TestCase):
    """A private-key-shaped config file (service.pem), generated at test
    time rather than checked in -- see the module docstring for why.

    Proves the Private Key rule fires at critical severity on the BEGIN
    line; the base64-shaped body also legitimately trips the entropy
    heuristic on top of it, which is expected (both signals are real) not
    a bug to suppress.
    """

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._tmp, True)
        self.header = _pem_marker("BEGIN")
        footer = _pem_marker("END")
        body = (
            "MIIEpAIBAAKCAQEA1c7+9z5Pad7OejecsQ0bu3aumnAxuNbaBMIObHYD5PxKuNvW\n"
            "2ZBt5D0TNw7VAr5cLoIH1lqE7ZXGGWJfHnyf9AGx3ba/xhk6nMWr0DczCE9k9DDL\n"
            + "FAKE" * 16
        )
        with open(
            os.path.join(self._tmp, "service.pem"), "w", encoding="utf-8"
        ) as f:
            f.write(f"{self.header}\n{body}\n{footer}\n")

    def test_private_key_and_body_entropy_both_reported(self):
        scanner = Scanner(self._tmp)
        findings = sorted(
            (f["path"], f["line"], f["rule_id"], f["severity"], f["value"])
            for f in scanner.scan()
        )
        self.assertEqual(
            findings,
            [
                ("service.pem", 1, "private-key", "critical", self.header),
                (
                    "service.pem", 2, "entropy", "low",
                    "9z5Pad7OejecsQ0bu3aumnAxuNbaBMIObHYD5PxKuNvW",
                ),
                (
                    "service.pem", 3, "entropy", "low",
                    "2ZBt5D0TNw7VAr5cLoIH1lqE7ZXGGWJfHnyf9AGx3ba",
                ),
                ("service.pem", 3, "entropy", "low", "xhk6nMWr0DczCE9k9DDL"),
            ],
        )


class LockfileFixtureTest(unittest.TestCase):
    """A synthetic package-lock.json with a real-looking hex shasum and a
    base64 sha512 integrity string.

    This documents *current* behavior rather than asserting an ideal one:
    both the shasum and pieces of the integrity string are high-entropy
    by construction and currently trip the entropy heuristic exactly like
    any other high-entropy string would, with no lockfile-aware exclusion
    in place. That's a known, tracked false-positive shape (see issue
    discussion around lockfile noise), not something this corpus test
    silently papers over — if a future change adds lockfile awareness,
    this test should start failing and be updated to match, rather than
    finding out from a user's CI log.
    """

    def test_lockfile_hashes_currently_trip_entropy_detection(self):
        findings = _scan("lockfile")
        self.assertTrue(findings)
        self.assertTrue(all(rule_id == "entropy" for _, _, rule_id, _, _ in findings))
        self.assertTrue(
            any("5b8a3a7765dfe003645c69be026fd7a1de5b4959" == v for *_, v in findings)
        )


class FixtureCorpusIntegrityTest(unittest.TestCase):
    """Guards the corpus itself: every checked-in fixture directory is
    covered by a test above, so one added later can't silently go
    unchecked. pem_config is deliberately not in this set -- it's
    generated at test time, never checked in (see the module docstring)."""

    COVERED = {
        "binary", "long_line", "unicode_rtl", "split_secret",
        "no_git_context", "dotenv_nested", "lockfile",
    }

    def test_every_fixture_directory_has_a_test(self):
        on_disk = {
            name
            for name in os.listdir(FIXTURES_ROOT)
            if os.path.isdir(os.path.join(FIXTURES_ROOT, name))
        }
        self.assertEqual(on_disk, self.COVERED)


if __name__ == "__main__":
    unittest.main()
