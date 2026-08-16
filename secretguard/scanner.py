"""Filesystem scanning with gitignore-aware filtering."""

import os

try:
    import pathspec

    HAS_PATHSPEC = True
except ImportError:  # pragma: no cover - optional dependency
    pathspec = None
    HAS_PATHSPEC = False

from .rules import (
    dotenv_secret_assignments,
    entropy_candidates,
    is_dotenv_path,
    matches_rules,
)

BINARY_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".tar",
    ".7z", ".exe", ".dll", ".so", ".dylib", ".bin", ".woff", ".woff2",
    ".ttf", ".eot", ".pyc", ".o", ".a", ".jar", ".class", ".sqlite",
    ".db", ".lock", ".min",
})

DEFAULT_EXCLUDES = frozenset({
    ".git", ".svn", ".hg", ".venv", "venv", "env", "node_modules",
    "dist", "build", "__pycache__", ".tox", ".nox", ".mypy_cache",
    ".pytest_cache", ".idea", ".vscode", "vendor", ".terraform",
})

Finding = dict


class Scanner:
    def __init__(self, root, excludes=None, include_entropy=True):
        self.root = os.path.abspath(root)
        self.extra_excludes = set(excludes or [])
        self.include_entropy = include_entropy
        self._spec = None
        self._load_gitignore()

    def _load_gitignore(self):
        """Build a pathspec matcher from .gitignore, if available."""

        gitignore = os.path.join(self.root, ".gitignore")
        if not HAS_PATHSPEC or not os.path.isfile(gitignore):
            return
        with open(gitignore, encoding="utf-8", errors="replace") as handle:
            self._spec = pathspec.PathSpec.from_lines(
                "gitignore", handle.read().splitlines()
            )

    def _is_ignored(self, rel_path):
        if self._spec is not None and self._spec.match_file(rel_path):
            return True
        parts = rel_path.replace(os.sep, "/").split("/")
        exclusions = DEFAULT_EXCLUDES | self.extra_excludes
        for part in parts:
            if part in exclusions:
                return True
        return False

    def _is_binary(self, rel_path):
        for ext in BINARY_EXTENSIONS:
            if rel_path.lower().endswith(ext):
                return True
        return False

    def iter_files(self):
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [
                d
                for d in dirnames
                if not self._is_ignored(os.path.join(dirpath, d))
            ]
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, self.root).replace(os.sep, "/")
                if self._is_ignored(rel):
                    continue
                if self._is_binary(rel):
                    continue
                yield full, rel

    def scan(self):
        findings = []
        for full_path, rel_path in self.iter_files():
            try:
                with open(full_path, encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
            except (OSError, PermissionError):
                continue
            findings.extend(self.scan_text(rel_path, text))
        return findings

    def scan_text(self, rel_path, text):
        """Scan a single text blob for secrets (used by scan and staged scans).

        Dotenv files are special-cased: secret-looking key assignments are
        reported by key name only, so the underlying value is never echoed.
        """

        findings = []
        key_lines = set()
        if is_dotenv_path(rel_path):
            base = os.path.basename(rel_path)
            for line_no, key, _value in dotenv_secret_assignments(text):
                findings.append(
                    self._make_finding(
                        rel_path,
                        key,
                        "Environment File Secret",
                        "high",
                        line_no,
                        f"Assigned in a {base} file (value masked).",
                        reveal=True,
                    )
                )
                key_lines.add(line_no)

        for rule, match in matches_rules(text):
            line = line_number(text, match.start())
            if line in key_lines:
                continue
            findings.append(
                self._make_finding(
                    rel_path,
                    match.group(),
                    rule["name"],
                    rule["severity"],
                    line,
                    rule["description"],
                )
            )

        if self.include_entropy:
            for start, _end, entropy, value in entropy_candidates(text):
                line = line_number(text, start)
                if line in key_lines:
                    continue
                findings.append(
                    self._make_finding(
                        rel_path,
                        value,
                        "High Entropy String",
                        "low",
                        line,
                        f"Detected via Shannon entropy ({entropy:.2f} bits/char).",
                    )
                )
        return findings

    @staticmethod
    def _make_finding(
        path, value, rule, severity, line, description, reveal=False
    ):
        finding = Finding(
            path=path,
            value=value,
            rule=rule,
            severity=severity,
            line=line,
            description=description,
        )
        if reveal:
            finding["reveal"] = True
        return finding


def line_number(text, index):
    return text.count("\n", 0, index) + 1