"""Comment-region detection.

A secret-looking value that only ever appears inside a comment (docs,
examples, a line commented out during debugging) is usually not a live
credential. ``scan_text`` uses this module to skip over comment regions
before running the regex/entropy rules, while the same value written in
executable code elsewhere in the file is unaffected — only the comment's
own character range is excluded.

Comment syntax is inferred from the file extension (or, for extensionless
files like ``Dockerfile``, from the basename). A file whose extension isn't
recognized gets no comment stripping at all, which just preserves prior
(pre-comment-awareness) scanning behavior for it.

This is a lightweight, string-literal-unaware stripper: a ``#`` or ``//``
inside a string literal is still treated as starting a comment. That's the
same kind of documented tradeoff already made for dotenv parsing in
rules.py, and keeps this simple — a real per-language tokenizer is out of
scope.
"""

import bisect
import re

HASH_EXTENSIONS = frozenset({
    "py", "rb", "sh", "bash", "zsh", "fish", "pl", "pm", "r", "yml", "yaml",
    "toml", "cfg", "ini", "conf", "properties", "tf", "tfvars", "ps1",
    "env", "gitignore", "dockerignore", "nginx",
})
SLASH_EXTENSIONS = frozenset({
    "js", "jsx", "mjs", "cjs", "ts", "tsx", "java", "c", "h", "cpp", "cc",
    "cxx", "hpp", "hh", "cs", "go", "rs", "swift", "kt", "kts", "php",
    "scala", "dart", "groovy", "m", "mm", "proto", "less",
})
BLOCK_ONLY_EXTENSIONS = frozenset({"css", "scss"})
HTML_EXTENSIONS = frozenset({"html", "htm", "xml", "vue", "svelte", "xhtml"})
SQL_EXTENSIONS = frozenset({"sql"})

HASH_BASENAMES = frozenset({
    "dockerfile", "makefile", "vagrantfile", "gemfile", "rakefile",
})

HASH_LINE_RE = re.compile(r"#[^\n]*")
SLASH_LINE_RE = re.compile(r"//[^\n]*")
SQL_LINE_RE = re.compile(r"--[^\n]*")
C_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
HTML_BLOCK_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _patterns_for(rel_path):
    """Which comment-matching regexes apply to this path, if any."""

    base = rel_path.rsplit("/", 1)[-1].lower()
    ext = base.rsplit(".", 1)[-1] if "." in base else base

    patterns = []
    if ext in HASH_EXTENSIONS or base in HASH_BASENAMES:
        patterns.append(HASH_LINE_RE)
    if ext in SLASH_EXTENSIONS:
        patterns.append(SLASH_LINE_RE)
        patterns.append(C_BLOCK_RE)
    if ext in BLOCK_ONLY_EXTENSIONS:
        patterns.append(C_BLOCK_RE)
    if ext in HTML_EXTENSIONS:
        patterns.append(HTML_BLOCK_RE)
    if ext in SQL_EXTENSIONS:
        patterns.append(SQL_LINE_RE)
    return patterns


def comment_ranges(text, rel_path):
    """Sorted, non-overlapping (start, end) character spans that are comments."""

    patterns = _patterns_for(rel_path)
    if not patterns:
        return []

    spans = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            spans.append((match.start(), match.end()))
    if not spans:
        return []

    spans.sort()
    merged = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


class CommentIndex:
    """Comment ranges for a file, with O(log n) "is this position in a
    comment?" lookups via ``pos in index``."""

    __slots__ = ("_ranges", "_starts")

    def __init__(self, ranges):
        self._ranges = ranges
        self._starts = [r[0] for r in ranges]

    def __contains__(self, pos):
        if not self._ranges:
            return False
        idx = bisect.bisect_right(self._starts, pos) - 1
        if idx < 0:
            return False
        start, end = self._ranges[idx]
        return start <= pos < end

    def __bool__(self):
        return bool(self._ranges)


def comment_index(text, rel_path):
    return CommentIndex(comment_ranges(text, rel_path))
