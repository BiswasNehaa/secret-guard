"""Unit tests for comment-region detection."""

import unittest

from secretguard.comments import comment_index, comment_ranges


class CommentRangesTest(unittest.TestCase):
    def test_unknown_extension_yields_no_ranges(self):
        self.assertEqual(comment_ranges("# not a comment here", "notes.txt"), [])

    def test_hash_comment_range(self):
        text = "x = 1\n# secret = abc\ny = 2"
        ranges = comment_ranges(text, "a.py")
        start = text.index("#")
        end = text.index("\n", start)
        self.assertEqual(ranges, [(start, end)])

    def test_hash_comment_stops_at_newline(self):
        text = "# one line\ncode_after = 1"
        ranges = comment_ranges(text, "a.sh")
        self.assertEqual(len(ranges), 1)
        self.assertNotIn(text.index("code_after"), range(*ranges[0]))

    def test_slash_line_comment(self):
        text = "let x = 1;\n// secret = abc\nlet y = 2;"
        ranges = comment_ranges(text, "a.js")
        start = text.index("//")
        end = text.index("\n", start)
        self.assertEqual(ranges, [(start, end)])

    def test_block_comment_spans_multiple_lines(self):
        text = "a();\n/*\nsecret\n*/\nb();"
        ranges = comment_ranges(text, "a.c")
        self.assertEqual(len(ranges), 1)
        start, end = ranges[0]
        self.assertEqual(text[start:end], "/*\nsecret\n*/")

    def test_html_comment(self):
        text = "<p>hi</p>\n<!-- secret -->\n<p>bye</p>"
        ranges = comment_ranges(text, "page.html")
        self.assertEqual(len(ranges), 1)
        start, end = ranges[0]
        self.assertEqual(text[start:end], "<!-- secret -->")

    def test_overlapping_ranges_are_merged(self):
        # A // inside a /* */ block should not create a second, separate span.
        text = "/* outer // inner */"
        ranges = comment_ranges(text, "a.js")
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0], (0, len(text)))

    def test_dockerfile_uses_hash_comments(self):
        text = "FROM python\n# a secret\nRUN echo hi"
        ranges = comment_ranges(text, "Dockerfile")
        self.assertEqual(len(ranges), 1)


class CommentIndexTest(unittest.TestCase):
    def test_contains_position_inside_range(self):
        text = "code\n# comment\nmore code"
        index = comment_index(text, "a.py")
        hash_pos = text.index("#")
        self.assertIn(hash_pos, index)
        self.assertIn(hash_pos + 3, index)

    def test_does_not_contain_position_outside_range(self):
        text = "code\n# comment\nmore code"
        index = comment_index(text, "a.py")
        self.assertNotIn(0, index)
        self.assertNotIn(text.index("more code"), index)

    def test_empty_index_contains_nothing(self):
        index = comment_index("no comments here", "notes.txt")
        self.assertFalse(index)
        self.assertNotIn(0, index)


if __name__ == "__main__":
    unittest.main()
