"""End-to-end tests for the secret-guard command line."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SECRET = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"


class CliTest(unittest.TestCase):
    def run_cli(self, cwd, *args):
        return subprocess.run(
            [sys.executable, "-m", "secretguard", *args],
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False,
        )

    def test_scan_returns_one_on_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "secret.py").write_text(
                f"TOKEN = '{SECRET}'", encoding="utf-8"
            )
            result = self.run_cli(tmp, "scan", ".")
            self.assertEqual(result.returncode, 1)
            self.assertIn("GitHub Token", result.stdout)

    def test_scan_returns_zero_when_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "main.py").write_text("print('hello')\n", encoding="utf-8")
            result = self.run_cli(tmp, "scan", ".")
            self.assertEqual(result.returncode, 0)
            self.assertIn("0 total", result.stdout)

    def test_scan_json_emits_parseable_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "secret.py").write_text(
                f"TOKEN = '{SECRET}'", encoding="utf-8"
            )
            result = self.run_cli(tmp, "scan", "--json", ".")
            self.assertEqual(result.returncode, 1)
            self.assertIsNotNone(__import__("json").loads(result.stdout))

    def test_scan_excludes_extra_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "wip").mkdir()
            Path(tmp, "wip", "secret.py").write_text(
                f"TOKEN = '{SECRET}'", encoding="utf-8"
            )
            result = self.run_cli(tmp, "scan", "--exclude", "wip", ".")
            self.assertEqual(result.returncode, 0)

    def test_scan_detects_dotenv_secret_without_exposing_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text(
                f"GITHUB_TOKEN={SECRET}\n", encoding="utf-8"
            )
            result = self.run_cli(tmp, "scan", ".")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Environment File Secret", result.stdout)
            self.assertNotIn(SECRET, result.stdout)

    def test_help_lists_commands(self):
        result = self.run_cli(str(PROJECT_ROOT), "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("scan", result.stdout)
        self.assertIn("install-hook", result.stdout)


if __name__ == "__main__":
    unittest.main()